"""Trace conversion preserves the raw observations, and silent failures are caught (section 12 items 6 and 7).

Every test builds its own tiny raw capture; none launches a simulator or touches the network.
"""
import json, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.trace import build_trace  # noqa: E402
from harness.cases import MATRIX, resolve  # noqa: E402
from harness import reproducibility, verify as verifier  # noqa: E402

CASE = dict(resolve("px4-v1.17.0-sih-quadx-rtl", "datalink_loss", 1), intended_mode="offboard")
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
                t = extra["t_vehicle_s"]
                trace["events"].append(dict(name="hazard_flag", t_vehicle_s=t, t_host_s=t,
                                            t_source="autopilot_log", t_vehicle_interval_s=[t, t],
                                            detail={"flag": extra["flag"], "edge": "rising", "value": True}))
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
        other = dict(resolve("px4-v1.17.0-sih-quadx-hold", "datalink_loss", 2), intended_mode="offboard")
        with tempfile.TemporaryDirectory() as d:
            run = write_run(Path(d), baseline_rows(), CASE)
            trace = build_trace(run, other, MATRIX)          # a trace built for a different case
            (run / "trace.json").write_text(json.dumps(trace, indent=1))
            result = verifier.verify(run)
            self.assertNotEqual(result["status"], "verified")
            self.assertTrue(any("is not case" in r for r in result["reasons"]), result["reasons"])

    def test_missing_oracle_is_unverified_never_verified(self):
        case = dict(resolve("px4-v1.17.0-sih-quadx-land", "geofence_breach", 1), intended_mode="offboard")
        result = self.verify_rows(baseline_rows(), case)
        self.assertEqual(result["status"], "unverified")
        self.assertTrue(any("no hand-derived timeline" in r for r in result["reasons"]))



class MeasurementRepairTests(unittest.TestCase):
    """The 2026-09-24 critique: clock provenance, the response window, verdict precedence, flag history."""

    LOITER_CASE = dict(resolve("px4-v1.17.0-sih-quadx-rtl", "datalink_loss", 1), intended_mode="auto_loiter")

    def loiter_rows(self, recovery_mode=RTL, offset=0.0):
        """An Auto Loiter run: takeoff, loiter, injection at 40 s vehicle time, recovery at +15 s.

        `offset` shifts host time away from vehicle time, which is what a real launch latency does. Nothing the
        vehicle timed may move when it changes.
        """
        rows = [
            dict(kind="case_resolved", t_host_s=0.0, case_id=self.LOITER_CASE["case_id"]),
            dict(kind="param_export", t_host_s=1.0 + offset, values=PARAMS),
            dict(kind="command", cmd=176, params=[1, 4, 3, 0, 0, 0, 0], result=0, t_host_s=4.0 + offset),
            dict(kind="event", name="arm", t_host_s=9.0 + offset),
            dict(kind="event", name="takeoff_complete", t_host_s=18.0 + offset, t_vehicle_s=18.0),
            dict(kind="event", name="injection", t_host_s=40.0 + offset, t_vehicle_s=40.0, event="datalink_loss",
                 streams=dict(gcs_heartbeat=False, offboard_setpoints=True)),
            dict(kind="event", name="horizon_reached", t_host_s=85.0 + offset, t_vehicle_s=85.0),
            dict(kind="stages", t_host_s=85.1 + offset, stages=[]),
        ]
        for second in range(10, 86):
            mode = LOITER if second < 20 else (LOITER if second < 55 else recovery_mode)
            if second < 20:
                mode = (4 << 16) | (2 << 24)      # AUTO_TAKEOFF, before the injection
            rows.append(dict(heartbeat(float(second) + offset, mode), time_boot_ms=int(second * 1000)))
        rows.sort(key=lambda r: r["t_host_s"])
        return rows

    def trace_for(self, rows, case=None, hazard_at=50.0):
        case = case or self.LOITER_CASE
        tmp = Path(self._tmp.name)
        run = write_run(tmp / str(len(list(tmp.iterdir()))), rows, case)
        trace = build_trace(run, case, MATRIX)
        if hazard_at is not None:
            trace["events"].append(dict(name="hazard_flag", t_vehicle_s=hazard_at, t_host_s=hazard_at,
                                        t_source="autopilot_log", t_vehicle_interval_s=[hazard_at, hazard_at],
                                        detail={"flag": "gcs_connection_lost", "edge": "rising", "value": True}))
            trace["events"].sort(key=lambda e: e["t_vehicle_s"])
        (run / "trace.json").write_text(json.dumps(trace, indent=1))
        return run, trace

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_a_vehicle_timed_instant_does_not_move_when_the_host_offset_does(self):
        """The injector reads the vehicle clock; a launch latency must not rewrite that reading (F1)."""
        seen = []
        for offset in (0.0, 7.34, 41.0):
            _run, trace = self.trace_for(self.loiter_rows(offset=offset))
            injection = next(e for e in trace["events"] if e["name"] == "injection")
            self.assertEqual(injection["t_source"], "vehicle_observation")
            seen.append(injection["t_vehicle_s"])
        self.assertEqual(seen, [40.0, 40.0, 40.0])

    def test_a_host_only_instant_is_bounded_by_real_vehicle_readings(self):
        _run, trace = self.trace_for(self.loiter_rows(offset=7.34))
        reconstructed = [e for e in trace["events"] if e["t_source"] == "host_reconstructed"]
        self.assertTrue(reconstructed, "the heartbeat-derived events carry no vehicle timestamp")
        closed = 0
        for e in reconstructed:
            lo, hi = e["t_vehicle_interval_s"]
            if lo is not None:
                self.assertLessEqual(lo, e["t_vehicle_s"])
            if hi is not None:
                self.assertLessEqual(e["t_vehicle_s"], hi)
            closed += lo is not None and hi is not None
        self.assertTrue(closed, "instants inside the observation window must be bracketed")
        # `arm` precedes the first message carrying a vehicle timestamp, so it has no lower bound. An open bound
        # is the honest answer, not a defect: the verifier treats such an instant as inconclusive, never measured.
        arm = next(e for e in trace["events"] if e["name"] == "arm")
        self.assertIsNone(arm["t_vehicle_interval_s"][0])

    def test_takeoff_before_injection_does_not_refute_a_correct_recovery(self):
        """The whole point of F2: a normal setup transition must not count against the response."""
        run, _trace = self.trace_for(self.loiter_rows())
        result = verifier.verify(run)
        self.assertEqual(result["observed"]["setup_mode_sequence"], ["AUTO_LOITER"])
        self.assertEqual(result["observed"]["state_entering_window"], "AUTO_LOITER")
        self.assertEqual(result["observed"]["mode_sequence"], ["AUTO_RTL"])
        self.assertIn(result["status"], ("verified", "inconclusive"), result["reasons"])
        self.assertNotEqual(result["status"], "refuted")

    def test_the_wrong_recovery_is_still_refuted(self):
        run, _trace = self.trace_for(self.loiter_rows(recovery_mode=(4 << 16) | (6 << 24)))   # AUTO_LAND
        result = verifier.verify(run)
        self.assertEqual(result["status"], "refuted", result["reasons"])
        self.assertIn("AUTO_LAND", str(result["observed"]["mode_sequence"]))

    def test_a_broken_run_is_unverified_not_refuted(self):
        """An invalid capture or the wrong case is an experiment that could not be compared (F2)."""
        run, trace = self.trace_for(self.loiter_rows())
        trace["validity"] = dict(valid=False, reasons=["simulator_crash"])
        (run / "trace.json").write_text(json.dumps(trace, indent=1))
        result = verifier.verify(run)
        self.assertEqual(result["status"], "unverified")
        self.assertTrue(any("run is invalid" in r for r in result["reasons"]))

    def test_an_unknown_intended_mode_is_never_defaulted_to_offboard(self):
        """Re-normalising an Auto Loiter capture as the Offboard case compares the wrong timeline (TASK 2)."""
        case = {k: v for k, v in self.LOITER_CASE.items() if k != "intended_mode"}
        rows = [r for r in self.loiter_rows() if not (r.get("kind") == "command" and r.get("cmd") == 176)]
        run, trace = self.trace_for(rows, case=case)
        self.assertIsNone(trace["manifest"]["intended_mode"])
        self.assertEqual(trace["conversion"]["intended_mode_source"], "unavailable")
        result = verifier.verify(run)
        self.assertEqual(result["status"], "unverified")
        self.assertTrue(any("which mode was intended" in r for r in result["reasons"]))

    def test_the_intended_mode_is_recovered_from_the_raw_capture_not_a_summary(self):
        case = {k: v for k, v in self.LOITER_CASE.items() if k != "intended_mode"}
        _run, trace = self.trace_for(self.loiter_rows(), case=case)
        self.assertEqual(trace["manifest"]["intended_mode"], "auto_loiter")
        self.assertEqual(trace["conversion"]["intended_mode_source"], "raw_capture_do_set_mode")

    def test_an_estimate_straddling_the_deadline_is_inconclusive_not_a_pass(self):
        """A reconstructed instant bounded only to a wide window cannot confirm a 1.5 s tolerance (F1)."""
        run, trace = self.trace_for(self.loiter_rows())
        for e in trace["events"]:
            if e["name"] == "native_transition" and e["t_vehicle_s"] >= 40.0:
                e["t_source"] = "host_reconstructed"
                e["t_vehicle_interval_s"] = [e["t_vehicle_s"] - 4.0, e["t_vehicle_s"] + 4.0]
        (run / "trace.json").write_text(json.dumps(trace, indent=1))
        result = verifier.verify(run)
        self.assertEqual(result["status"], "inconclusive", result["reasons"])
        self.assertTrue(any("only bounded to" in r for r in result["reasons"]))

    def test_a_control_run_may_take_off_without_being_refuted(self):
        """Selecting a mode and taking off are setup; only a later change is the control run misbehaving (F2)."""
        case = dict(resolve("px4-v1.17.0-sih-quadx-rtl", "none", 1), intended_mode="auto_loiter")
        rows = [r for r in self.loiter_rows() if r.get("name") != "injection"]
        run, trace = self.trace_for(rows, case=case, hazard_at=None)
        # strip the post-injection recovery: a control run just keeps flying after takeoff
        trace["events"] = [e for e in trace["events"]
                           if not (e["name"] == "native_transition" and e["t_vehicle_s"] > 20.0)]
        (run / "trace.json").write_text(json.dumps(trace, indent=1))
        result = verifier.verify(run)
        self.assertEqual(result["status"], "verified", result["reasons"])
        self.assertEqual(result["observed"]["mode_sequence"], ["AUTO_LOITER"])   # T6: takeoff completes into loiter

    def test_a_control_run_that_really_changes_mode_is_refuted(self):
        case = dict(resolve("px4-v1.17.0-sih-quadx-rtl", "none", 1), intended_mode="auto_loiter")
        rows = [r for r in self.loiter_rows() if r.get("name") != "injection"]
        run, _trace = self.trace_for(rows, case=case, hazard_at=None)   # keeps the AUTO_RTL change at 55 s
        result = verifier.verify(run)
        self.assertEqual(result["status"], "refuted", result["reasons"])
        self.assertIn("AUTO_RTL", str(result["observed"]["mode_sequence"]))

    def test_no_sample_reports_a_null_selected_action(self):
        """JSON null read as PX4's Action::None is how an unobserved selector became a claim (F3)."""
        _run, trace = self.trace_for(self.loiter_rows())
        self.assertTrue(trace["samples"])
        for s in trace["samples"]:
            self.assertEqual(s["selected_action"], "unobserved")
            self.assertIn(s["t_source"], ("vehicle_observation", "autopilot_log", "host_reconstructed"))


class ReproducibilityClockTests(unittest.TestCase):
    """A spread over reconstructed instants is not apparatus jitter (critique 2026-09-24, F1)."""

    def _runs(self, sources):
        with tempfile.TemporaryDirectory() as d:
            dirs = []
            for i, per_run in enumerate(sources):
                run = Path(d) / f"rep{i}"
                run.mkdir()
                events = [dict(name=name, t_vehicle_s=t, t_host_s=t, t_source=src)
                          for name, (t, src) in per_run.items()]
                (run / "trace.json").write_text(json.dumps(dict(
                    validity=dict(valid=True, reasons=[]),
                    manifest=dict(parameters_sha256="a" * 64, firmware_commit="b" * 40, intended_mode="offboard"),
                    events=events, samples=[])))
                dirs.append(run)
            return reproducibility.compare(dirs)

    def test_a_measured_spread_is_quotable_as_jitter(self):
        result = self._runs([{"takeoff_complete": (18.0, "vehicle_observation")},
                             {"takeoff_complete": (18.3, "vehicle_observation")}])
        self.assertEqual(result["timestamp_spread"]["takeoff_complete"]["quality"], "measured")
        self.assertTrue(result["jitter_quotable"])
        self.assertAlmostEqual(result["apparatus_jitter_s"]["takeoff_complete"], 0.3, places=3)

    def test_a_reconstructed_spread_is_not_quotable_as_jitter(self):
        result = self._runs([{"arm": (2.4, "host_reconstructed")}, {"arm": (3.1, "host_reconstructed")}])
        self.assertEqual(result["timestamp_spread"]["arm"]["quality"], "estimated")
        self.assertFalse(result["jitter_quotable"])
        self.assertIsNone(result["apparatus_jitter_s"])

    def test_mixing_clock_sources_is_named_not_averaged(self):
        result = self._runs([{"arm": (2.4, "host_reconstructed")}, {"arm": (2.5, "vehicle_observation")}])
        self.assertEqual(result["timestamp_spread"]["arm"]["quality"], "mixed_clock_sources")
        self.assertFalse(result["jitter_quotable"])

    def test_a_pre_repair_trace_has_unrecorded_provenance_not_assumed_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            dirs = []
            for i, t in enumerate((18.0, 18.3)):
                run = Path(d) / f"rep{i}"
                run.mkdir()
                (run / "trace.json").write_text(json.dumps(dict(
                    validity=dict(valid=True, reasons=[]),
                    manifest=dict(parameters_sha256="a" * 64, firmware_commit="b" * 40),
                    events=[dict(name="takeoff_complete", t_vehicle_s=t, t_host_s=t)], samples=[])))
                dirs.append(run)
            result = reproducibility.compare(dirs)
        self.assertEqual(result["timestamp_spread"]["takeoff_complete"]["quality"], "unrecorded_provenance")
        self.assertFalse(result["jitter_quotable"])

if __name__ == "__main__":
    unittest.main()
