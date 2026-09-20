"""One registered scenario against pinned PX4 SIH SITL: launch, configure, take off, inject, observe, record.

usage (from the repo root, with the venv python):
  python -m harness.run --px4-build ~/.cache/uav-failsafe-composition/px4/PX4-Autopilot/build/px4_sitl_default \
      --config px4-v1.17.0-sih-quadx-rtl --event datalink_loss --out evidence/harness-2026-09-16/run-001

Every step and its baseline: GCS link at 1 Hz heartbeat [B5]; offboard stream at 10 Hz (≥ 2 Hz proof of life) [B4];
RC emulated by MANUAL_CONTROL at 10 Hz (COM_RC_IN_MODE=3 accepts MAVLink manual control) [B10]; GPS/battery via
MAV_CMD_INJECT_FAILURE with SYS_FAILURE_EN=1 [B3]; geofence via GF_MAX_HOR_DIST and a fly-out [B1]. Records the raw
MAVLink stream as JSONL, copies the uLog, and writes a schema-valid trace (protocols/trace-schema.json).
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, signal, subprocess, sys, threading, time
from pathlib import Path

from pymavlink import mavutil
from pymavlink.dialects.v20 import common as mav

from harness.modes import decode_custom_mode, encode_custom_mode
from harness.trace import build_trace

ROOT = Path(__file__).resolve().parents[1]
MATRIX = json.loads((ROOT / "protocols/configuration-matrix.json").read_text())
INSTANCE = int(os.environ.get("PX4_INSTANCE", "0"))
GCS_PORT, OFFB_PORT = 14550 + INSTANCE, 14540 + INSTANCE
FAILURE_UNIT = {"gps": 4, "battery": 100, "rc_signal": 104, "mavlink_signal": 105}  # MAVLink FAILURE_UNIT enum
FAILURE_TYPE = {"ok": 0, "off": 1, "wrong": 4}


class Streams:
    """Background 1 Hz GCS heartbeat, 10 Hz offboard setpoints, 10 Hz manual control; each can be stopped = injection."""

    def __init__(self, gcs, offb):
        self.gcs, self.offb = gcs, offb
        self.heartbeat = self.setpoints = self.manual = False
        self.last_heartbeat_t = self.last_setpoint_t = None
        self.target = [0.0, 0.0, -10.0]
        self._stop = False
        self._th = threading.Thread(target=self._loop, daemon=True); self._th.start()

    def _loop(self):
        n = 0
        while not self._stop:
            if self.heartbeat and n % 10 == 0:
                self.gcs.mav.heartbeat_send(mav.MAV_TYPE_GCS, mav.MAV_AUTOPILOT_INVALID, 0, 0, 0); self.last_heartbeat_t = time.monotonic()
            if self.setpoints:
                self.offb.mav.set_position_target_local_ned_send(0, 1, 1, mav.MAV_FRAME_LOCAL_NED, 0b0000111111111000, *self.target, 0, 0, 0, 0, 0, 0, 0, 0)
                self.last_setpoint_t = time.monotonic()
            if self.manual:
                self.gcs.mav.manual_control_send(1, 0, 0, 500, 0, 0)
            n += 1; time.sleep(0.1)

    def stop(self): self._stop = True


def wait_heartbeat(conn, timeout=60):
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        m = conn.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
        if m and m.get_srcSystem() == 1:
            return m
    raise RuntimeError("no vehicle heartbeat")


def set_param(conn, name, value, log):
    ptype = mav.MAV_PARAM_TYPE_REAL32 if isinstance(value, float) else mav.MAV_PARAM_TYPE_INT32
    for _ in range(5):
        conn.mav.param_set_send(1, 1, name.encode(), float(value), ptype)
        m = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=2)
        while m and m.param_id.rstrip("\x00") != name:
            m = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=2)
        if m and abs(m.param_value - float(value)) < 1e-6:
            log(dict(kind="param_set", name=name, value=value)); return
    raise RuntimeError(f"param {name} not confirmed")


def read_param(conn, name):
    for _ in range(5):
        conn.mav.param_request_read_send(1, 1, name.encode(), -1)
        m = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=2)
        while m and m.param_id.rstrip("\x00") != name:
            m = conn.recv_match(type="PARAM_VALUE", blocking=True, timeout=2)
        if m: return m.param_value
    raise RuntimeError(f"param {name} not read")


def command(conn, cmd, *params, log=None):
    p = list(params) + [0] * (7 - len(params))
    conn.mav.command_long_send(1, 1, cmd, 0, *p)
    ack = conn.recv_match(type="COMMAND_ACK", blocking=True, timeout=3)
    if log: log(dict(kind="command", cmd=cmd, params=p, ack=(ack.result if ack else None)))
    return ack


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--px4-build", required=True); ap.add_argument("--config", required=True); ap.add_argument("--event", required=True,
        choices=["none", "offboard_loss", "datalink_loss", "rc_loss", "gps_loss", "battery_critical", "battery_emergency", "geofence_breach"])
    ap.add_argument("--out", required=True); ap.add_argument("--inject-at", type=float, default=30.0); ap.add_argument("--restore-at", type=float, default=0.0)
    ap.add_argument("--observe", type=float, default=45.0); ap.add_argument("--seed", type=int, default=1); ap.add_argument("--run-id", default=None)
    a = ap.parse_args(argv)
    row = next(r for r in MATRIX["rows"] if r["configuration_id"] == a.config)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    raw = (out / "raw.jsonl").open("w"); t_start = time.monotonic()
    def log(d): d["t_host_s"] = round(time.monotonic() - t_start, 4); raw.write(json.dumps(d) + "\n"); raw.flush()

    build = Path(a.px4_build); work = out / "px4-work"; shutil.rmtree(work, ignore_errors=True); work.mkdir()
    env = dict(os.environ, PX4_SIM_MODEL="sihsim_quadx", PX4_SIMULATOR="sihsim", PX4_SYS_AUTOSTART="10040")
    px4 = subprocess.Popen([str(build / "bin/px4"), "-d", str(build / "etc"), "-s", "etc/init.d-posix/rcS", "-i", str(INSTANCE), "-w", str(work)],
                           cwd=build, env=env, stdout=(out / "px4.log").open("w"), stderr=subprocess.STDOUT)
    log(dict(kind="launch", pid=px4.pid, build=str(build)))
    gcs = mavutil.mavlink_connection(f"udpin:0.0.0.0:{GCS_PORT}", source_system=255, source_component=190)
    offb = mavutil.mavlink_connection(f"udpin:0.0.0.0:{OFFB_PORT}", source_system=2, source_component=191)
    streams = Streams(gcs, offb)
    try:
        hb = wait_heartbeat(gcs); log(dict(kind="vehicle_heartbeat", custom_mode=hb.custom_mode))
        streams.heartbeat = True; streams.manual = True
        # offboard link must announce itself as an onboard controller, not a GCS, so its heartbeat does not count as C2 Link [B1 gcs_connection_lost]
        offb.mav.heartbeat_send(mav.MAV_TYPE_ONBOARD_CONTROLLER, mav.MAV_AUTOPILOT_INVALID, 0, 0, 0)
        time.sleep(2)
        params = dict(MATRIX["common_params"]); params.update({k: (float(v) if isinstance(v, float) else int(v)) for k, v in row["deltas_from_defaults"].items()})
        if a.event == "geofence_breach": params["GF_MAX_HOR_DIST"] = 20.0
        if a.event == "battery_emergency": params["SYS_FAIL_BAT_LVL"] = 3
        if a.event == "battery_critical": params["SYS_FAIL_BAT_LVL"] = 2
        for k, v in params.items(): set_param(gcs, k, v, log)
        # full parameter identity: read back every matrix parameter and hash (the matrix hash covers common+deltas only)
        export = {k: read_param(gcs, k) for k in sorted(set(MATRIX["common_params"]) | set(row["deltas_from_defaults"]))}
        log(dict(kind="param_export", values=export))
        for _ in range(3): command(gcs, mav.MAV_CMD_SET_MESSAGE_INTERVAL, mav.MAVLINK_MSG_ID_LOCAL_POSITION_NED, 100000, log=log)
        command(gcs, mav.MAV_CMD_SET_MESSAGE_INTERVAL, mav.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 100000, log=log)
        command(gcs, mav.MAV_CMD_SET_MESSAGE_INTERVAL, mav.MAVLINK_MSG_ID_EXTENDED_SYS_STATE, 500000, log=log)
        # wait for a global position estimate, then arm and take off in OFFBOARD (setpoints streaming first) [B4]
        t0 = time.monotonic()
        while time.monotonic() - t0 < 60:
            m = gcs.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=2)
            if m and m.lat != 0: break
        # wait until the autopilot's own pre-arm checks pass (MAV_SYS_STATUS_PREARM_CHECK bit in SYS_STATUS health) [B5 SYS_STATUS]
        t0 = time.monotonic(); ready = False
        while time.monotonic() - t0 < 120:
            m = gcs.recv_match(type="SYS_STATUS", blocking=True, timeout=2)
            if m and (m.onboard_control_sensors_health & mav.MAV_SYS_STATUS_PREARM_CHECK):
                ready = True; break
        log(dict(kind="prearm_ready", ready=ready, waited_s=round(time.monotonic() - t0, 2)))
        streams.setpoints = True; time.sleep(1.5)
        command(gcs, mav.MAV_CMD_DO_SET_MODE, mav.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 6, 0, log=log)  # OFFBOARD
        command(gcs, mav.MAV_CMD_COMPONENT_ARM_DISARM, 1, log=log); log(dict(kind="event", name="arm"))
        # record loop until injection time, observe, optional restore
        t_launch = time.monotonic(); injected = restored = False; takeoff_logged = False
        while time.monotonic() - t_launch < a.observe + a.inject_at:
            m = gcs.recv_match(blocking=True, timeout=1)
            if m is None: continue
            tp = m.get_type()
            if tp in ("HEARTBEAT", "STATUSTEXT", "SYS_STATUS", "EXTENDED_SYS_STATE", "GLOBAL_POSITION_INT", "LOCAL_POSITION_NED", "BATTERY_STATUS", "COMMAND_ACK"):
                d = m.to_dict(); d["kind"] = "msg"; d["src"] = m.get_srcSystem()
                if tp == "HEARTBEAT" and m.get_srcSystem() == 1: d["nav_state"] = decode_custom_mode(m.custom_mode)
                if tp == "LOCAL_POSITION_NED" and not takeoff_logged and m.z < -9.0 and abs(m.vz) < 0.2:
                    takeoff_logged = True; log(dict(kind="event", name="takeoff_complete"))
                log(d)
            now = time.monotonic() - t_launch
            if not injected and now >= a.inject_at:
                injected = True
                if a.event == "offboard_loss": streams.setpoints = False; log(dict(kind="event", name="last_valid_setpoint", t=streams.last_setpoint_t - t_start))
                elif a.event == "datalink_loss": streams.heartbeat = False; log(dict(kind="event", name="last_heartbeat_sent", t=streams.last_heartbeat_t - t_start))
                elif a.event == "rc_loss": streams.manual = False
                elif a.event == "gps_loss": command(gcs, mav.MAV_CMD_INJECT_FAILURE, FAILURE_UNIT["gps"], FAILURE_TYPE["off"], 0, log=log)
                elif a.event.startswith("battery"): command(gcs, mav.MAV_CMD_INJECT_FAILURE, FAILURE_UNIT["battery"], FAILURE_TYPE["wrong"], 0, log=log)
                elif a.event == "geofence_breach": streams.target = [40.0, 0.0, -10.0]
                log(dict(kind="event", name="injection", event=a.event))
            if injected and not restored and a.restore_at > 0 and now >= a.inject_at + a.restore_at:
                restored = True
                if a.event == "offboard_loss": streams.setpoints = True
                elif a.event == "datalink_loss": streams.heartbeat = True
                elif a.event == "rc_loss": streams.manual = True
                elif a.event == "gps_loss": command(gcs, mav.MAV_CMD_INJECT_FAILURE, FAILURE_UNIT["gps"], FAILURE_TYPE["ok"], 0, log=log)
                elif a.event.startswith("battery"): command(gcs, mav.MAV_CMD_INJECT_FAILURE, FAILURE_UNIT["battery"], FAILURE_TYPE["ok"], 0, log=log)
                log(dict(kind="event", name="reconnect_event", event=a.event))
    finally:
        streams.stop(); raw.close()
        px4.send_signal(signal.SIGINT)
        try: px4.wait(timeout=15)
        except subprocess.TimeoutExpired: px4.kill()
        logs = sorted((work / "log").rglob("*.ulg"))
        if logs: shutil.copy(logs[-1], out / "flight.ulg")
    trace = build_trace(out, row, a, MATRIX)
    (out / "trace.json").write_text(json.dumps(trace, indent=1) + "\n")
    print(json.dumps(dict(run=out.name, event=a.event, config=a.config, valid=trace["validity"], mode_sequence=[e["detail"] for e in trace["events"] if e["name"] == "native_transition"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
