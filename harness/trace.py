"""Normalise a run directory (raw.jsonl + flight.ulg) into the URC-03 trace format and validate it against the schema."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

from jsonschema.validators import validator_for

from harness.modes import NAV_STATE

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


def build_trace(out: Path, row: dict, args, matrix: dict) -> dict:
    rows = [json.loads(l) for l in (out / "raw.jsonl").read_text().splitlines() if l.strip()]
    msgs = [r for r in rows if r.get("kind") == "msg" and r.get("src") == 1]
    hb = [r for r in msgs if r["mavpackettype"] == "HEARTBEAT"]
    # clock: vehicle time_boot_ms is on SYS_STATUS-less messages; use LOCAL_POSITION_NED/GLOBAL_POSITION_INT time_boot_ms
    timed = [r for r in msgs if "time_boot_ms" in r][:10]
    offsets = [r["t_host_s"] - r["time_boot_ms"] / 1000.0 for r in timed]
    offset = sum(offsets) / len(offsets) if offsets else 0.0
    def tv(r): return round(max(0.0, r["t_host_s"] - offset), 3)
    export = next((r["values"] for r in rows if r.get("kind") == "param_export"), {})
    params_sha = hashlib.sha256(json.dumps({k: (int(v) if float(v).is_integer() else float(v)) for k, v in sorted(export.items())}, sort_keys=True).encode()).hexdigest()
    events, samples = [], []
    last_nav = None
    for r in msgs:
        t = tv(r)
        if r["mavpackettype"] == "HEARTBEAT":
            armed = bool(r["base_mode"] & 128)
            samples.append(dict(t_vehicle_s=t, t_host_s=r["t_host_s"], nav_state=r["nav_state"], armed=armed, selected_action=None, hazard_flags={}, pos_ned_m=None, vel_ned_mps=None, lat_deg=None, lon_deg=None, alt_amsl_m=None, battery_remaining=None, statustext=None))
            if last_nav is not None and r["nav_state"] != last_nav:
                events.append(dict(name="native_transition", t_vehicle_s=t, t_host_s=r["t_host_s"], detail={"from": last_nav, "to": r["nav_state"]}))
            last_nav = r["nav_state"]
        elif r["mavpackettype"] == "LOCAL_POSITION_NED":
            samples.append(dict(t_vehicle_s=round(r["time_boot_ms"] / 1000.0, 3), t_host_s=r["t_host_s"], nav_state=last_nav or "UNKNOWN", armed=True, selected_action=None, hazard_flags={}, pos_ned_m=[r["x"], r["y"], r["z"]], vel_ned_mps=[r["vx"], r["vy"], r["vz"]], lat_deg=None, lon_deg=None, alt_amsl_m=None, battery_remaining=None, statustext=None))
        elif r["mavpackettype"] == "GLOBAL_POSITION_INT":
            samples.append(dict(t_vehicle_s=round(r["time_boot_ms"] / 1000.0, 3), t_host_s=r["t_host_s"], nav_state=last_nav or "UNKNOWN", armed=True, selected_action=None, hazard_flags={}, pos_ned_m=None, vel_ned_mps=None, lat_deg=r["lat"] / 1e7, lon_deg=r["lon"] / 1e7, alt_amsl_m=r["alt"] / 1000.0, battery_remaining=None, statustext=None))
        elif r["mavpackettype"] == "STATUSTEXT":
            samples.append(dict(t_vehicle_s=t, t_host_s=r["t_host_s"], nav_state=last_nav or "UNKNOWN", armed=True, selected_action=None, hazard_flags={}, pos_ned_m=None, vel_ned_mps=None, lat_deg=None, lon_deg=None, alt_amsl_m=None, battery_remaining=None, statustext=r["text"]))
            if "Failsafe" in r["text"]:
                events.append(dict(name="failsafe_notice", t_vehicle_s=t, t_host_s=r["t_host_s"], detail={"text": r["text"]}))
    for r in rows:
        if r.get("kind") == "event":
            name = {"arm": "arm", "takeoff_complete": "takeoff_complete", "injection": "injection", "reconnect_event": "reconnect_event", "last_valid_setpoint": "last_valid_setpoint", "last_heartbeat_sent": "last_heartbeat_sent"}[r["name"]]
            events.append(dict(name=name, t_vehicle_s=round(max(0.0, r.get("t", r["t_host_s"]) - offset), 3), t_host_s=r["t_host_s"], detail={k: v for k, v in r.items() if k not in ("kind", "name", "t_host_s")}))
    ulog = out / "flight.ulg"
    if ulog.exists():
        flags, nav = read_ulog_flags(ulog)
        inj = next((e for e in events if e["name"] == "injection"), None)
        prev = {}
        for t_s, f in flags:
            for k, v in f.items():
                if v and not prev.get(k) and (inj is None or t_s >= inj["t_vehicle_s"] - 1.0):
                    events.append(dict(name="hazard_flag", t_vehicle_s=round(t_s, 3), t_host_s=round(t_s + offset, 3), detail={"flag": k, "value": v}))
            prev = f
    events.sort(key=lambda e: e["t_vehicle_s"])
    reasons = []
    hb_t = [r["t_host_s"] for r in hb]
    if any(b - a > 2.0 for a, b in zip(hb_t, hb_t[1:])): reasons.append("no_vehicle_heartbeat_2s")
    if not any(e["name"] == "takeoff_complete" for e in events) and getattr(args, "event", "none") != "none": reasons.append("injection_before_takeoff")
    trace = dict(schema_version="2026-09-16",
                 manifest=dict(configuration_id=row["configuration_id"], firmware_commit=matrix["firmware"]["commit"], firmware_tag=matrix["firmware"]["tag"], airframe=matrix["vehicle"]["airframe"], simulator="sihsim", lockstep=True, parameters_sha256=params_sha, seed=int(args.seed),
                               injection=dict(**{"class": args.event}, method={"offboard_loss": "stream_stopped", "datalink_loss": "heartbeat_stopped", "rc_loss": "stream_stopped", "gps_loss": "failure_injection", "battery_critical": "failure_injection", "battery_emergency": "failure_injection", "geofence_breach": "fence_upload_and_fly_out", "none": "none"}[args.event], scheduled_t_s=float(args.inject_at), restore_t_s=(float(args.inject_at + args.restore_at) if args.restore_at > 0 else None)),
                               run_id=args.run_id or out.name, evidence_state="simulation"),
                 clock=dict(host_to_vehicle_offset_s=round(offset, 4), offset_samples=max(1, len(offsets))),
                 events=events, samples=samples or [dict(t_vehicle_s=0.0, t_host_s=0.0, nav_state="UNKNOWN", armed=False)],
                 validity=dict(valid=not reasons, reasons=reasons))
    errs = [e.message for e in VALIDATOR.iter_errors(trace)]
    if errs:
        trace["validity"] = dict(valid=False, reasons=sorted(set(reasons + ["schema_failure"])))
        (out / "schema-errors.txt").write_text("\n".join(errs))
    return trace
