"""Behavioral checks for the calculation, data integrity, and local API."""
import copy
import json
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import make_handler
from engine import Engine, ROOT
from generate_data import generate


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine()
        cls.runs = {key: cls.engine.run(key) for key in cls.engine.scenarios}

    def test_fixed_seed_reproduces_model_outputs(self):
        second = Engine()
        self.assertEqual(self.runs["nightfall"], second.run("nightfall"))

    def test_saved_data_matches_generator_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            generate(Path(directory))
            for name in ("baseline.csv", "scenarios.json", "facility.json"):
                self.assertEqual((ROOT / "data" / name).read_bytes(), (Path(directory) / name).read_bytes())

    def test_offline_computation_does_not_open_network_connections(self):
        with patch("socket.socket.connect", side_effect=AssertionError("Network connection attempted")):
            engine = Engine()
            for scenario in engine.scenarios:
                self.assertEqual(len(engine.run(scenario)["frames"]), 14)

    def test_scenario_outcomes_are_distinct(self):
        night = self.runs["nightfall"]["frames"][-1]
        drift = self.runs["sensor_drift"]["frames"][-1]
        routine = self.runs["routine"]["frames"][-1]
        self.assertEqual(night["anomaly_count"], 3)
        self.assertEqual(drift["anomaly_count"], 2)
        self.assertEqual(routine["anomaly_count"], 0)
        self.assertGreater(night["alerts"][0]["score"], drift["alerts"][0]["score"])
        self.assertEqual(drift["alerts"][0]["uncertainty"], "Conflicting evidence")
        self.assertEqual(routine["alerts"], [])

    def test_no_future_evidence_in_earlier_frames(self):
        for result in self.runs.values():
            for n, frame in enumerate(result["frames"], start=1):
                known = {e["id"] for e in frame["events"]}
                self.assertEqual(len(known), n)
                for alert in frame["alerts"]:
                    self.assertTrue(set(alert["event_ids"]) <= known)
                    for link in alert["links"]:
                        self.assertIn(link["event_id"], known)
                        self.assertIn(link["anchor_id"], known)
        initial_alert = self.runs["nightfall"]["frames"][5]["alerts"][0]
        self.assertEqual(initial_alert["support_sources"], [])

    def test_repeated_source_does_not_inflate_corroboration(self):
        events = copy.deepcopy(self.runs["nightfall"]["frames"][7]["events"])
        before = self.engine.snapshot(events)["alerts"][0]
        duplicate = dict(events[-1], id="E99", seconds=77, time="22:15:17")
        after = self.engine.snapshot(events + [duplicate])["alerts"][0]
        self.assertEqual(before["support_sources"], after["support_sources"])
        self.assertEqual(before["factors"]["corroboration"], after["factors"]["corroboration"])

    def test_contradictions_reduce_priority_but_do_not_confirm_safety(self):
        events = copy.deepcopy(self.runs["sensor_drift"]["frames"][-1]["events"])
        contested = self.engine.snapshot(events)["alerts"][0]
        for event in events:
            if event["stance"] == "contradict":
                event["stance"] = "neutral"
        neutral = self.engine.snapshot(events)["alerts"][0]
        self.assertLess(contested["score"], neutral["score"])
        self.assertFalse(contested["verified"])

    def test_correlation_requires_time_zone_and_event_type(self):
        events = self.runs["nightfall"]["frames"][-1]["events"]
        left, right = events[5], events[6]
        self.assertIsNotNone(self.engine.correlation(left, right))
        self.assertIsNone(self.engine.correlation(left, dict(right, seconds=left["seconds"] + 121)))
        self.assertIsNone(self.engine.correlation(left, dict(right, zone="D")))
        self.assertIsNone(self.engine.correlation(left, dict(right, event_type="routine")))
        self.assertIsNone(self.engine.correlation(left, dict(right, zone="B")))
        self.assertIsNotNone(self.engine.correlation(left, dict(right, zone="B", event_type="power")))

    def test_priority_equals_bounded_sum_and_remains_unverified(self):
        for result in self.runs.values():
            for frame in result["frames"]:
                for alert in frame["alerts"]:
                    self.assertEqual(alert["score"], max(0, min(100, round(sum(alert["factors"].values())))))
                    self.assertFalse(alert["verified"])

    def test_graph_preserves_provenance_and_active_links(self):
        final = self.runs["nightfall"]["frames"][-1]
        graph = final["graph"]
        nodes = {n["id"] for n in graph["nodes"]}
        self.assertIn("station", nodes)
        for event in final["events"]:
            self.assertIn({"source": event["source_id"], "target": event["id"], "relation": "observed"}, graph["edges"])
        for edge in graph["edges"]:
            self.assertIn(edge["source"], nodes)
            self.assertIn(edge["target"], nodes)
            if edge["relation"] in ("correlates", "contradicts"):
                self.assertLessEqual(edge["gap_seconds"], 120)

    def test_alerts_expire_without_new_evidence(self):
        events = copy.deepcopy(self.runs["nightfall"]["frames"][-1]["events"])
        events.append(dict(events[-1], id="E99", seconds=400, time="22:20:40"))
        self.assertEqual(self.engine.snapshot(events)["alerts"], [])


class APITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(Engine()))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_bootstrap_and_all_scenario_endpoints(self):
        with urlopen(self.base + "/api/bootstrap") as response:
            self.assertEqual(len(json.load(response)["scenarios"]), 3)
        for scenario in ("nightfall", "sensor_drift", "routine"):
            request = Request(self.base + "/api/run", data=json.dumps({"scenario": scenario}).encode(), headers={"Content-Type":"application/json"})
            with urlopen(request) as response:
                self.assertEqual(len(json.load(response)["frames"]), 14)

    def test_invalid_requests_and_private_paths_are_rejected(self):
        for data in (b'{"scenario":"unknown"}', b'not json', b'[]', b'{}'):
            with self.assertRaises(HTTPError) as failure:
                urlopen(Request(self.base + "/api/run", data=data))
            self.assertEqual(failure.exception.code, 400)
            failure.exception.close()
        for path in ("/engine.py", "/../requirements.txt", "/data/baseline.csv"):
            with self.assertRaises(HTTPError) as failure:
                urlopen(self.base + path)
            self.assertEqual(failure.exception.code, 404)
            failure.exception.close()

    def test_all_browser_assets_are_available_locally(self):
        for path in ("/", "/app.js", "/style.css", "/favicon.svg"):
            with urlopen(self.base + path) as response:
                self.assertEqual(response.status, 200)
                self.assertGreater(len(response.read()), 10)


if __name__ == "__main__":
    unittest.main()
