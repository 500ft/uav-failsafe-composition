"""Normalise a run directory (raw.jsonl + flight.ulg) into the URC-03 trace format and validate it against the schema.

Every instant carries where its number came from (`t_source`), because this run has two clocks:

    vehicle_observation  the vehicle's own clock, read at that instant (injector events, time_boot_ms)
    autopilot_log        a native uLog timestamp, already on the vehicle clock
    host_reconstructed   host time minus the median offset, which is an estimate and not a measurement

A host-reconstructed instant also carries `t_vehicle_interval_s`, the two nearest real vehicle-clock readings
that bracket it in host time. Both clocks advance monotonically, so the true vehicle instant lies inside that
interval; the point estimate is only the median-offset guess clamped into it. If either side is missing the
bound is open (null) and nothing downstream may treat the instant as measured. The earlier normaliser subtracted
a single median offset everywhere and then compared the result against native uLog times, which mixes the two
routes; the offset spread it reported is a dispersion, not a calibrated uncertainty (critique 2026-09-24, F1).
"""
from __future__ import annotations
import bisect, hashlib, json
from pathlib import Path

from jsonschema.validators import validator_for

from harness.modes import NAV_STATE, decode_custom_mode

# PX4 does not publish the failsafe framework's selected action over MAVLink, so no sample ever observes one.
# `None` is a real PX4 Action; JSON null is the absence of an observation. They are not the same fact (F3).
UNOBSERVED = "unobserved"

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "protocols/trace-schema.json").read_text())
_V = validator_for(SCHEMA); _V.check_schema(SCHEMA); VALIDATOR = _V(SCHEMA)
FLAGS = ("manual_control_signal_lost", "gcs_connection_lost", "offboard_control_signal_lost", "geofence_breached", "position_accuracy_low",
         "local_position_invalid", "global_position_invalid", "battery_warning", "battery_unhealthy", "mission_failure", "navigator_failure")


def read_ulog_flags(path: Path):
    """(t_s, {flag: value}) samples from the failsafe_flags topic, plus (t_s, nav_state) from vehicle_status; [] if pyulog is absent."""
    try:
        from pyulog import ULog
    except ImportError:
        return [], []
    u = ULog(str(path), message_name_filter_list=["failsafe_flags", "vehicle_status"])
    flags, nav = [], []
    for d in u.data_list:
        if d.name == "failsafe_flags":
            ts = d.data["timestamp"]
            for i in range(len(ts)):
                flags.append((ts[i] / 1e6, {f: int(d.data[f][i]) for f in FLAGS if f in d.data}))
        elif d.name == "vehicle_status":
            ts = d.data["timestamp"]
            for i in range(len(ts)):
                nav.append((ts[i] / 1e6, NAV_STATE.get(int(d.data["nav_state"][i]), str(int(d.data["nav_state"][i]))), bool(d.data["failsafe"][i]) if "failsafe" in d.data else None))
    return flags, nav


def build_trace(out: Path, case: dict, matrix: dict) -> dict:
    rows = [json.loads(l) for l in (out / "raw.jsonl").read_text().splitlines() if l.strip()]
    msgs = [r for r in rows if r.get("kind") == "msg" and r.get("src") == 1]
    hb = [r for r in msgs if r["mavpackettype"] == "HEARTBEAT"]
    # clock: vehicle time_boot_ms is on SYS_STATUS-less messages; use LOCAL_POSITION_NED/GLOBAL_POSITION_INT time_boot_ms
    # The offset is the median over EVERY message carrying a vehicle timestamp, not the first few: an estimate
    # taken during start-up is biased by launch latency. The spread is reported so a consumer can see what a
    # heartbeat-derived timestamp is worth (frame and clock probe, 2026-09-21).
    timed = sorted(((r["t_host_s"], r["time_boot_ms"] / 1000.0) for r in msgs if "time_boot_ms" in r))
    offsets = sorted(h - v for h, v in timed)
    offset = offsets[len(offsets) // 2] if offsets else 0.0
    offset_spread = round(offsets[-1] - offsets[0], 4) if offsets else 0.0
    anchor_host = [h for h, _ in timed]

    def bracket(t_host: float):
        """The two nearest real vehicle-clock readings either side of this host instant, or None where absent."""
        i = bisect.bisect_left(anchor_host, t_host)
        lo = timed[i - 1][1] if i > 0 else None
        hi = timed[i][1] if i < len(timed) else None
        return lo, hi

    def host_instant(t_host: float) -> dict:
        """An instant known only in host time: point estimate, its provenance, and the interval that bounds it."""
        lo, hi = bracket(t_host)
        est = max(0.0, t_host - offset)
        if lo is not None:
            est = max(est, lo)
        if hi is not None:
            est = min(est, hi)
        return dict(t_vehicle_s=round(est, 3), t_host_s=t_host, t_source="host_reconstructed",
                    t_vehicle_interval_s=[None if lo is None else round(lo, 3), None if hi is None else round(hi, 3)])

    def vehicle_instant(t_vehicle: float, t_host: float, source: str = "vehicle_observation") -> dict:
        """An instant the vehicle itself timed. Its interval is the point, so a consumer can treat both alike."""
        t = round(max(0.0, t_vehicle), 3)
        return dict(t_vehicle_s=t, t_host_s=t_host, t_source=source, t_vehicle_interval_s=[t, t])
    export = next((r["values"] for r in rows if r.get("kind") == "param_export"), {})
    params_sha = hashlib.sha256(json.dumps({k: (int(v) if float(v).is_integer() else float(v)) for k, v in sorted(export.items())}, sort_keys=True).encode()).hexdigest()
    events, samples, unmapped = [], [], set()
    last_nav = None

    def sample(instant: dict, **fields) -> None:
        base = dict(nav_state=last_nav or "UNKNOWN", armed=True, selected_action=UNOBSERVED, hazard_flags={},
                    pos_ned_m=None, vel_ned_mps=None, lat_deg=None, lon_deg=None, alt_amsl_m=None,
                    battery_remaining=None, statustext=None)
        samples.append(dict(base, **{k: v for k, v in instant.items() if k != "t_vehicle_interval_s"}, **fields))

    for r in msgs:
        if r["mavpackettype"] == "HEARTBEAT":
            at = host_instant(r["t_host_s"])          # HEARTBEAT carries no vehicle timestamp at all
            r.setdefault("nav_state", decode_custom_mode(r["custom_mode"]))
            sample(at, nav_state=r["nav_state"], armed=bool(r["base_mode"] & 128))
            if last_nav is not None and r["nav_state"] != last_nav:
                events.append(dict(name="native_transition", **at, detail={"from": last_nav, "to": r["nav_state"]}))
            last_nav = r["nav_state"]
        elif r["mavpackettype"] == "LOCAL_POSITION_NED":
            sample(vehicle_instant(r["time_boot_ms"] / 1000.0, r["t_host_s"]),
                   pos_ned_m=[r["x"], r["y"], r["z"]], vel_ned_mps=[r["vx"], r["vy"], r["vz"]])
        elif r["mavpackettype"] == "GLOBAL_POSITION_INT":
            sample(vehicle_instant(r["time_boot_ms"] / 1000.0, r["t_host_s"]),
                   lat_deg=r["lat"] / 1e7, lon_deg=r["lon"] / 1e7, alt_amsl_m=r["alt"] / 1000.0)
        elif r["mavpackettype"] == "STATUSTEXT":
            at = host_instant(r["t_host_s"])
            sample(at, statustext=r["text"])
            if "Failsafe" in r["text"]:
                announced = None
                if "switching to " in r["text"]:
                    announced = r["text"].split("switching to ", 1)[1].split(" in ")[0].strip().rstrip(".\t")
                events.append(dict(name="failsafe_notice", **at,
                                   detail={"text": r["text"], "announced_action": announced}))
    for r in rows:
        if r.get("kind") == "event":
            known = {"arm", "takeoff_complete", "injection", "reconnect_event", "last_valid_setpoint",
                     "last_heartbeat_sent", "horizon_reached", "terminal_state"}
            if r["name"] not in known:      # kept in raw.jsonl; the schema's vocabulary is not widened silently
                unmapped.add(r["name"])
                continue
            # The runner reads the vehicle clock when it records these, so `t_vehicle_s` here is an observation,
            # not a reconstruction. The old code looked for a key named "t", never found it, and silently
            # replaced a measured instant with host-minus-offset (critique 2026-09-24, F1).
            at = (vehicle_instant(r["t_vehicle_s"], r["t_host_s"]) if "t_vehicle_s" in r
                  else host_instant(r["t_host_s"]))
            events.append(dict(name=r["name"], **at,
                               detail={k: v for k, v in r.items() if k not in ("kind", "name", "t_host_s")}))
    mode_source, entry_state = "mavlink_heartbeat", None
    ulog = out / "flight.ulg"
    if ulog.exists():
        flags, nav = read_ulog_flags(ulog)
        if nav:
            # Replace the heartbeat-derived transitions with the autopilot's own vehicle_status sequence, which
            # is published far faster than the 1 Hz HEARTBEAT stream. The heartbeat samples stay in `samples`.
            events = [e for e in events if e["name"] != "native_transition"]
            mode_source = "autopilot_log_vehicle_status"
            last, last_fs = None, None
            for t_s, state, fs in nav:
                at = vehicle_instant(t_s, round(t_s + offset, 3), source="autopilot_log")
                if last is not None and state != last:
                    events.append(dict(name="native_transition", **at,
                                       detail={"from": last, "to": state, "vehicle_status_failsafe": fs}))
                if fs is not None and last_fs is not None and fs != last_fs:
                    # vehicle_status.failsafe is the autopilot's own statement that a failsafe is active. It is
                    # not a hazard input flag, and losing it made "no action was selected" unfalsifiable (F3).
                    events.append(dict(name="failsafe_state", **at,
                                       detail={"failsafe": fs, "nav_state": state}))
                last, last_fs = state, fs
        inj = next((e for e in events if e["name"] == "injection"), None)
        prev, entry_state = {}, None
        for t_s, f in flags:
            if inj is not None and entry_state is None and t_s >= inj["t_vehicle_s"]:
                entry_state = dict(t_vehicle_s=round(t_s, 3), flags={k: bool(v) for k, v in f.items()})
            for k, v in f.items():
                if k not in prev or bool(v) == bool(prev[k]):
                    continue
                # Both edges. A hazard that clears and re-raises is the mechanism the interaction study is
                # after; keeping only the rising edge deleted the history the properties need (F3, F6).
                events.append(dict(name="hazard_flag", **vehicle_instant(t_s, round(t_s + offset, 3), source="autopilot_log"),
                                   detail={"flag": k, "value": bool(v), "edge": "rising" if v else "falling"}))
            prev = f
    events.sort(key=lambda e: e["t_vehicle_s"])
    samples.sort(key=lambda s: s["t_vehicle_s"])
    reasons = []
    hb_t = [r["t_host_s"] for r in hb]
    if any(b - a > 2.0 for a, b in zip(hb_t, hb_t[1:])):
        reasons.append("no_vehicle_heartbeat_2s")
    if case["event"] != "none" and not any(e["name"] == "takeoff_complete" for e in events):
        reasons.append("injection_before_takeoff")
    if any(r.get("kind") == "failure" for r in rows):
        reasons.append("simulator_crash" if any("heartbeat" in str(r.get("detail", "")) for r in rows if r.get("kind") == "failure") else "schema_failure")
    method = {"offboard_loss": "stream_stopped", "datalink_loss": "heartbeat_stopped", "rc_loss": "stream_stopped",
              "gps_loss": "failure_injection", "battery_critical": "failure_injection", "battery_emergency": "failure_injection",
              "geofence_breach": "fence_upload_and_fly_out", "none": "none"}[case["event"]]
    inj = next((e for e in events if e["name"] == "injection"), None)
    intended_mode, intended_mode_source = case.get("intended_mode"), "case"
    if intended_mode is None:
        # Older runs predate `intended_mode` in case.json. DO_SET_MODE (176) in the capture is a primary
        # observation of what was asked for; a derived trace.json or summary is not, and is never used here.
        set_mode = next((r for r in rows if r.get("kind") == "command" and r.get("cmd") == 176), None)
        if set_mode:
            main, sub = int(set_mode["params"][1]), int(set_mode["params"][2])
            intended_mode = {(6, 0): "offboard", (4, 3): "auto_loiter"}.get((main, sub))
            intended_mode_source = "raw_capture_do_set_mode" if intended_mode else "unavailable"
        if intended_mode is None:
            intended_mode_source = "unavailable"
    trace = dict(
        schema_version="2026-09-24",
        manifest=dict(configuration_id=case["configuration_id"], firmware_commit=case["firmware_commit"],
                      firmware_tag=case["firmware_tag"], airframe=case["airframe"], simulator="sihsim", lockstep=True,
                      parameters_sha256=params_sha, seed=int(case["seed"]),
                      injection=dict(**{"class": case["event"]}, method=method,
                                     scheduled_t_s=float(case["inject_at_vehicle_s"]),
                                     restore_t_s=None),
                      run_id=case["case_id"], evidence_state="simulation", intended_mode=intended_mode),
        clock=dict(host_to_vehicle_offset_s=round(offset, 4), offset_samples=max(1, len(offsets)),
                   offset_spread_s=offset_spread, offset_estimator="median over every message carrying time_boot_ms"),
        events=events,
        samples=samples or [dict(t_vehicle_s=0.0, t_host_s=0.0, t_source="host_reconstructed",
                                 nav_state="UNKNOWN", armed=False, selected_action=UNOBSERVED)],
        validity=dict(valid=not reasons, reasons=sorted(set(reasons))),
        conversion=dict(raw_lines=len(rows), raw_vehicle_messages=len(msgs), samples_written=len(samples),
                        events_written=len(events), mode_source=mode_source,
                        unmapped_event_names=sorted(unmapped), raw_retained_at=str(out / "raw.jsonl"),
                        intended_mode_source=intended_mode_source,
                        instants_by_source={k: sum(1 for e in events if e["t_source"] == k)
                                            for k in ("vehicle_observation", "autopilot_log", "host_reconstructed")}),
        stages=[s for s in (next((r["stages"] for r in rows if r.get("kind") == "stages"), None) or [])])
    if inj is not None:
        trace["injection_observed_vehicle_s"] = inj["t_vehicle_s"]
        if entry_state:
            trace["flags_at_injection"] = entry_state
        streams = next((r.get("streams") for r in rows if r.get("kind") == "event" and r.get("name") == "injection"), None)
        if streams:
            trace["streams_at_injection"] = streams
    errs = [e.message for e in VALIDATOR.iter_errors(trace)]
    if errs:
        trace["validity"] = dict(valid=False, reasons=sorted(set(reasons + ["schema_failure"])))
        (out / "schema-errors.txt").write_text("\n".join(errs))
    return trace
