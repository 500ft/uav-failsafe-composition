"""Trace conversion preserves the raw observations, and silent failures are caught (section 12 items 6 and 7).

Every test builds its own tiny raw capture; none launches a simulator or touches the network.
"""
import json, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.trace import build_trace  # noqa: E402
from harness.cases import MATRIX, resolve  # noqa: E402
from harness import verify as verifier  # noqa: E402

CASE = resolve("px4-v1.17.0-sih-quadx-rtl", "datalink_loss", 1)
PARAMS = {k: float(v) for k, v in CASE["parameters"].items()}


def heartbeat(t, custom_mode, armed=True):
    return dict(kind="msg", src=1, mavpackettype="HEARTBEAT", t_host_s=t, custom_mode=custom_mode,
                base_mode=128 if armed else 0, time_boot_ms=int(t * 1000))


OFFBOARD = 6 << 16
LOITER = (4 << 16) | (3 << 24)
RTL = (4 << 16) | (5 << 24)


def write_run(tmp: Path, rows, case=CASE):
    run = tmp / case["case_id"]
    run.mkdir(parents=True)
    (run / "case.json").write_text(json.dumps(case))
    (run / "raw.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return run


def baseline_rows():
    """A 1 Hz heartbeat stream (the real rate) plus the harness records. Modes follow timeline T1:
    Offboard until the injection at 40 s, Hold at +10 s, RTL at +15 s."""
    rows = [
        dict(kind="case_resolved", t_host_s=0.0, case_id=CASE["case_id"]),
        dict(kind="param_export", t_host_s=1.0, values=PARAMS),
        dict(kind="event", name="arm", t_host_s=9.0),
        dict(kind="event", name="takeoff_complete", t_host_s=15.0),
        dict(kind="event", name="injection", t_host_s=40.0, t_vehicle_s=40.0, event="datalink_loss",
             streams=dict(gcs_heartbeat=False, offboard_setpoints=True)),
        dict(kind="event", name="horizon_reached", t_host_s=85.0),
        dict(kind="stages", t_host_s=85.1, stages=[dict(stage="launch", status="ok", evidence="px4.log", detail={})]),
    ]
    for whole_second in range(10, 86):
        mode = OFFBOARD if whole_second < 50 else (LOITER if whole_second < 55 else RTL)
        rows.append(heartbeat(float(whole_second), mode))
    rows.sort(key=lambda r: r["t_host_s"])
    return rows


class ConversionPreservationTests(unittest.TestCase):
    def test_counts_and_labels_survive_conversion_and_reload(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            rows = baseline_rows()
            run = write_run(tmp, rows)
            trace = build_trace(run, CASE, MATRIX)
            (run / "trace.json").write_text(json.dumps(trace, indent=1))
            reloaded = json.loads((run / "trace.json").read_text())

            self.assertEqual(reloaded, trace, "a saved trace must reload identically")
            conv = reloaded["conversion"]
            self.assertEqual(conv["raw_lines"], len(rows))
            self.assertEqual(conv["raw_vehicle_messages"], sum(1 for r in rows if r.get("kind") == "msg"))
            self.assertEqual(conv["samples_written"], len(reloaded["samples"]))
            self.assertEqual(conv["events_written"], len(reloaded["events"]))
            self.assertTrue(conv["raw_retained_at"].endswith("raw.jsonl"))

            # every mode change present in the raw capture appears as a transition, in order, with raw labels
            self.assertEqual([e["detail"]["to"] for e in reloaded["events"] if e["name"] == "native_transition"],
                             ["AUTO_LOITER", "AUTO_RTL"])
            self.assertEqual(reloaded["manifest"]["run_id"], CASE["case_id"])
            times = [e["t_vehicle_s"] for e in reloaded["events"]]
            self.assertEqual(times, sorted(times), "events must be emitted in time order")

    def test_an_unmapped_event_name_is_recorded_not_dropped_silently(self):
        with tempfile.TemporaryDirectory() as d:
            rows = baseline_rows() + [dict(kind="event", name="some_future_event", t_host_s=86.0)]
            run = write_run(Path(d), rows)
            trace = build_trace(run, CASE, MATRIX)
            self.assertIn("some_future_event", trace["conversion"]["unmapped_event_names"])
            self.assertIn("some_future_event", (run / "raw.jsonl").read_text())


class SilentFailureTests(unittest.TestCase):
    def verify_rows(self, rows, case=CASE):
        with tempfile.TemporaryDirectory() as d:
            run = write_run(Path(d), rows, case)
            trace = build_trace(run, case, MATRIX)
            # the hazard flag normally comes from the autopilot log; these fixtures have none, so inject it here
            for extra in [r for r in rows if r.get("kind") == "hazard_fixture"]:
                trace["events"].append(dict(name="hazard_flag", t_vehicle_s=extra["t_vehicle_s"],
                                            t_host_s=extra["t_vehicle_s"], detail={"flag": extra["flag"]}))
            trace["events"].sort(key=lambda e: e["t_vehicle_s"])
            (run / "trace.json").write_text(json.dumps(trace, indent=1))
            return verifier.verify(run)

    def test_ineffective_injection_is_refuted_not_passed(self):
        """The stimulus was sent but no monitor ever activated: execution succeeded, behaviour did not."""
        result = self.verify_rows(baseline_rows())
        self.assertEqual(result["status"], "refuted")
        self.assertTrue(any("never rose" in r for r in result["reasons"]))

    def test_a_run_matching_the_hand_derivation_verifies(self):
        rows = baseline_rows() + [dict(kind="hazard_fixture", t_vehicle_s=50.0, flag="gcs_connection_lost")]
        result = self.verify_rows(rows)
        self.assertEqual(result["status"], "verified", result["reasons"])
        self.assertEqual(result["timeline_id"], "T1")

    def test_a_stale_result_from_another_case_is_not_accepted(self):
        other = resolve("px4-v1.17.0-sih-quadx-hold", "datalink_loss", 2)
        with tempfile.TemporaryDirectory() as d:
            run = write_run(Path(d), baseline_rows(), CASE)
            trace = build_trace(run, other, MATRIX)          # a trace built for a different case
            (run / "trace.json").write_text(json.dumps(trace, indent=1))
            result = verifier.verify(run)
            self.assertNotEqual(result["status"], "verified")
            self.assertTrue(any("is not case" in r for r in result["reasons"]), result["reasons"])

    def test_missing_oracle_is_unverified_never_verified(self):
        case = resolve("px4-v1.17.0-sih-quadx-land", "geofence_breach", 1)   # no hand-derived timeline
        result = self.verify_rows(baseline_rows(), case)
        self.assertEqual(result["status"], "unverified")
        self.assertTrue(any("no hand-derived timeline" in r for r in result["reasons"]))


if __name__ == "__main__":
    unittest.main()
