"""Deterministic ML scoring, explicit correlation rules, and a NetworkX graph."""
from __future__ import annotations

import csv
import hashlib
import json
from itertools import combinations
from pathlib import Path

import networkx as nx
import numpy as np
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parent
FEATURES = ("voltage_v", "temperature_c", "particles_ug_m3", "vibration_mm_s")
FEATURE_LABELS = ("Voltage", "Temperature", "Particles", "Vibration")
WINDOW = 120
RELATED_TYPES = {"power", "visibility", "equipment", "environment"}


class Engine:
    def __init__(self, data_dir: Path = ROOT / "data"):
        self.facility = json.loads((data_dir / "facility.json").read_text(encoding="utf-8"))
        scenarios = json.loads((data_dir / "scenarios.json").read_text(encoding="utf-8"))
        self.scenarios = {s["id"]: s for s in scenarios}
        self.sources = {s["id"]: s for s in self.facility["sources"]}
        self.zones = {z["id"]: z for z in self.facility["zones"]}
        self.adjacent = {frozenset(pair) for pair in self.facility["adjacent_zones"]}
        with (data_dir / "baseline.csv").open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        values = np.array([[float(row[feature]) for feature in FEATURES] for row in rows])
        self.mean = values.mean(axis=0)
        self.std = values.std(axis=0)
        self.model = IsolationForest(n_estimators=200, max_samples=256,
                                     contamination=.02, random_state=42, n_jobs=1)
        self.model.fit(values)
        self.metadata = {
            "algorithm": "Isolation Forest", "library": "scikit-learn", "seed": 42,
            "trees": 200, "max_samples": 256, "contamination": .02,
            "baseline_rows": len(rows), "features": list(FEATURES),
            "threshold": round(float(-self.model.offset_), 6),
            "correlation_window_seconds": WINDOW,
            "normal_reference": {f: {"mean": round(float(self.mean[i]), 4),
                                      "std": round(float(self.std[i]), 4)} for i, f in enumerate(FEATURES)},
            "dataset_sha256": {name: hashlib.sha256((data_dir / name).read_bytes()).hexdigest()
                               for name in ("baseline.csv", "scenarios.json", "facility.json")},
        }

    def bootstrap(self):
        return {"facility": self.facility, "model": self.metadata,
                "scenarios": [{k: v for k, v in s.items() if k != "events"} |
                              {"event_count": len(s["events"])} for s in self.scenarios.values()],
                "initial": self.snapshot([])}

    def score_event(self, original):
        event = dict(original)
        event["analysis"] = None
        if event["kind"] == "sensor":
            vector = np.array([[event["readings"][feature] for feature in FEATURES]])
            decision = float(self.model.decision_function(vector)[0])
            raw = float(-self.model.score_samples(vector)[0])
            zscores = np.abs((vector[0] - self.mean) / self.std)
            event["analysis"] = {
                "is_anomaly": bool(decision < 0), "raw_score": round(raw, 6),
                "decision": round(decision, 6),
                "strength": round(float(np.clip(-decision / .15, 0, 1)), 6),
                # Descriptive deviations, NOT Isolation Forest feature attributions.
                "deviations": [{"feature": FEATURES[i], "label": FEATURE_LABELS[i],
                                "standard_deviations": round(float(zscores[i]), 1),
                                "value": float(vector[0][i]),
                                "reference_mean": round(float(self.mean[i]), 3)}
                               for i in np.argsort(zscores)[::-1]],
            }
        return event

    def correlation(self, left, right):
        gap = abs(left["seconds"] - right["seconds"])
        if gap > WINDOW:
            return None
        same_zone = left["zone"] == right["zone"]
        adjacent = frozenset([left["zone"], right["zone"]]) in self.adjacent
        same_type = left["event_type"] == right["event_type"] and left["event_type"] != "routine"
        related_type = {left["event_type"], right["event_type"]} <= RELATED_TYPES
        if not ((same_zone and related_type) or (adjacent and same_type)):
            return None
        geography = f"same zone {left['zone']}" if same_zone else "adjacent zones"
        types = f"{left['event_type']} / {right['event_type']}"
        relation = "contradicts" if "contradict" in (left["stance"], right["stance"]) else "correlates"
        return {"relation": relation, "gap_seconds": gap,
                "reason": f"{geography}; {gap}s apart (≤120s); related types: {types}."}

    def snapshot(self, events):
        now = events[-1]["seconds"] if events else 0
        active = [e for e in events if now - e["seconds"] <= WINDOW]
        anchors = [e for e in active if e["analysis"] and e["analysis"]["is_anomaly"]]
        alerts = []
        for zone in sorted({e["zone"] for e in anchors}):
            zone_anchors = [e for e in anchors if e["zone"] == zone]
            anchor = min(zone_anchors, key=lambda e: e["seconds"])
            # Every evidence item must link DIRECTLY to an active anchor. No chain drift.
            links = []
            for event in active:
                if event["id"] == anchor["id"]:
                    continue
                candidates = [(a, self.correlation(a, event)) for a in zone_anchors if a["id"] != event["id"]]
                candidates = [(a, c) for a, c in candidates if c]
                if candidates:
                    other, link = min(candidates, key=lambda pair: pair[1]["gap_seconds"])
                    links.append({"event_id": event["id"], "anchor_id": other["id"], **link})
            ids = {anchor["id"], *(a["id"] for a in zone_anchors), *(link["event_id"] for link in links)}
            evidence = [e for e in active if e["id"] in ids]
            # Latest report per source prevents repeated reports inflating corroboration.
            latest = {e["source_id"]: e for e in evidence}
            supports = {sid for sid, e in latest.items() if sid != anchor["source_id"] and e["stance"] == "support"}
            contradicts = {sid for sid, e in latest.items() if sid != anchor["source_id"] and e["stance"] == "contradict"}
            strength = max(a["analysis"]["strength"] for a in zone_anchors)
            severity = max(e["severity"] for e in evidence)
            factors = {
                "anomaly": round(55 * strength, 2),
                "corroboration": round(25 * min(len(supports) / 2, 1), 2),
                "severity": round(20 * severity, 2),
                "contradiction": round(-20 * min(len(contradicts) / 2, 1), 2),
            }
            score = int(np.clip(round(sum(factors.values())), 0, 100))
            level = "high" if score >= 70 else "elevated" if score >= 40 else "review"
            uncertainty = "Conflicting evidence" if contradicts else "Corroborated signals" if len(supports) >= 2 else "Limited evidence"
            explanation = (
                f"{len(contradicts)} independent source(s) challenge the original signal. A sensor issue is possible, not established."
                if contradicts else
                f"{len(supports)} other source(s) support review of the unusual readings. Agreement does not establish cause or confirm smoke."
                if supports else "One source has unusual readings. Independent observations are needed before drawing conclusions."
            )
            alerts.append({"id": f"INC-{zone}", "zone": zone, "title": f"Unusual conditions · {self.zones[zone]['name']}",
                           "score": score, "level": level, "factors": factors, "anomaly_strength": strength,
                           "severity": severity, "support_sources": sorted(supports),
                           "contradict_sources": sorted(contradicts), "event_ids": [e["id"] for e in evidence],
                           "anchor_id": anchor["id"], "links": links, "uncertainty": uncertainty,
                           "explanation": explanation, "verified": False})
        alerts.sort(key=lambda a: (-a["score"], a["id"]))

        graph = nx.DiGraph()
        graph.add_node("station", label="Northstar", kind="facility")
        for zone in self.zones.values():
            graph.add_node(zone["id"], label=zone["name"], kind="zone")
            graph.add_edge("station", zone["id"], relation="contains")
        for source in self.sources.values():
            graph.add_node(source["id"], label=source["id"], kind=source["kind"])
            graph.add_edge(source["zone"], source["id"], relation="hosts")
        for event in events:
            graph.add_node(event["id"], label=event["title"], kind="event", zone=event["zone"])
            graph.add_edge(event["source_id"], event["id"], relation="observed")
        for left, right in combinations(active, 2):
            link = self.correlation(left, right)
            if link:
                graph.add_edge(left["id"], right["id"], **link)
        sensor_status = []
        for source in self.sources.values():
            if source["kind"] != "sensor":
                continue
            latest = next((e for e in reversed(events) if e["source_id"] == source["id"]), None)
            sensor_status.append({**source, "latest": latest,
                                  "status": "awaiting" if not latest else "anomaly" if latest["analysis"]["is_anomaly"] else "nominal"})
        return {"seconds": now, "time": events[-1]["time"] if events else "22:14:00",
                "events": events, "alerts": alerts, "sensors": sensor_status,
                "anomaly_count": sum(bool(e["analysis"] and e["analysis"]["is_anomaly"]) for e in events),
                "graph": {"nodes": [{"id": n, **d} for n, d in graph.nodes(data=True)],
                          "edges": [{"source": u, "target": v, **d} for u, v, d in graph.edges(data=True)]}}

    def run(self, scenario_id):
        scenario = self.scenarios[scenario_id]
        events = [self.score_event(e) for e in scenario["events"]]
        # Prefixes are isolated: later evidence cannot affect earlier frames.
        frames = [self.snapshot(events[:n]) for n in range(1, len(events) + 1)]
        return {"scenario": {k: v for k, v in scenario.items() if k != "events"},
                "model": self.metadata, "frames": frames}
