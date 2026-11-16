"""Create the entire fictional dataset. No downloads, APIs, or personal files."""
from __future__ import annotations

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 42
FEATURES = ["voltage_v", "temperature_c", "particles_ug_m3", "vibration_mm_s"]
START = datetime(2030, 2, 17, 22, 14, 0)  # Fictional scenario clock, not today's date.


def generate(output: Path = ROOT / "data") -> None:
    output.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    facility = {
        "name": "Northstar Station", "fictional": True, "seed": SEED,
        "coordinate_system": "Fictional local drawing units; no geographic coordinates",
        "zones": [
            {"id": "A", "name": "Power annex", "x": 145, "y": 135, "width": 230, "height": 150},
            {"id": "B", "name": "Service corridor", "x": 405, "y": 135, "width": 255, "height": 95},
            {"id": "C", "name": "Cooling plant", "x": 145, "y": 325, "width": 230, "height": 150},
            {"id": "D", "name": "Operations", "x": 405, "y": 270, "width": 255, "height": 205},
        ],
        "adjacent_zones": [["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]],
        "sources": [
            {"id": "PQ-A1", "zone": "A", "kind": "sensor", "name": "Power-quality bundle"},
            {"id": "ENV-A2", "zone": "A", "kind": "sensor", "name": "Independent environment bundle"},
            {"id": "ENV-B1", "zone": "B", "kind": "sensor", "name": "Corridor sensor bundle"},
            {"id": "ENV-C1", "zone": "C", "kind": "sensor", "name": "Cooling sensor bundle"},
            {"id": "ENV-D1", "zone": "D", "kind": "sensor", "name": "Operations sensor bundle"},
            {"id": "CAM-A1", "zone": "A", "kind": "camera", "name": "Annex schematic camera"},
            {"id": "CAM-B1", "zone": "B", "kind": "camera", "name": "Corridor schematic camera"},
            {"id": "FIELD-A", "zone": "A", "kind": "field", "name": "Fictional maintenance log"},
        ],
    }
    (output / "facility.json").write_text(json.dumps(facility, indent=2) + "\n", encoding="utf-8")

    def normal():
        # All five synthetic bundles share one deliberately simplified normal regime.
        load = rng.gauss(0, 1)
        return [round(230 + rng.gauss(0, 1.25) - load * .35, 3),
                round(22 + rng.gauss(0, .55) + load * .25, 3),
                round(9 + rng.gauss(0, 1.25), 3),
                round(.08 + rng.gauss(0, .006) + load * .002, 4)]

    with (output / "baseline.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["sample_id", "source_id", "zone", *FEATURES])
        n = 0
        for source in facility["sources"]:
            if source["kind"] == "sensor":
                for _ in range(200):
                    n += 1
                    writer.writerow([f"BASE-{n:04d}", source["id"], source["zone"], *normal()])

    sources = {s["id"]: s for s in facility["sources"]}
    nominal = [230.2, 22.1, 9.2, .081]

    def event(number, seconds, source_id, event_type, title, message,
              readings=None, stance="neutral", severity=0, visual=None):
        source = sources[source_id]
        value = {"id": f"E{number:02d}", "seconds": seconds,
                 "time": (START + timedelta(seconds=seconds)).strftime("%H:%M:%S"),
                 "source_id": source_id, "zone": source["zone"], "kind": source["kind"],
                 "event_type": event_type, "title": title, "message": message,
                 "stance": stance, "severity": severity}
        if readings is not None:
            value["readings"] = dict(zip(FEATURES, readings))
        if visual:
            value["visual"] = visual
        return value

    common = [event(i + 1, i * 5, sid, "routine", "Baseline received",
                    "Synthetic readings are near the normal reference regime.", nominal)
              for i, sid in enumerate(["PQ-A1", "ENV-B1", "ENV-C1", "ENV-D1", "ENV-A2"])]

    scenarios = []
    for key, name, subtitle in [
        ("nightfall", "Nightfall", "Power disturbance with corroborating observations"),
        ("sensor_drift", "Sensor drift", "An isolated signal challenged by independent sources"),
        ("routine", "Routine operations", "Control stream with nominal observations"),
    ]:
        crisis, drift = key == "nightfall", key == "sensor_drift"
        events = list(common)
        events.append(event(6, 40, "PQ-A1", "power", "Voltage disturbance" if crisis or drift else "Stable power",
            "Voltage and vibration depart from the normal regime." if crisis else
            "The power bundle reports voltage and vibration shifts; temperature and particles remain nominal." if drift else
            "The power bundle reports nominal readings.",
            [198, 27, 10, .18] if crisis else [198, 22.1, 9.2, .16] if drift else nominal,
            "support" if crisis or drift else "neutral", .65 if crisis else .45 if drift else 0))
        events.append(event(7, 58, "CAM-A1", "visibility", "Smoke-like haze" if crisis else "Annex appears clear",
            "Authored camera observation: haze-like shapes near the equipment bay. Smoke is not verified." if crisis else
            "Authored camera observation: clear equipment bay; no visible haze. A clear view cannot rule out a fault.",
            stance="support" if crisis else "contradict" if drift else "neutral",
            severity=.6 if crisis else 0, visual="haze" if crisis else "clear"))
        events.append(event(8, 76, "FIELD-A", "equipment", "Equipment fault reported" if crisis else "Local check recorded",
            "Fictional technician reports a stopped fan and an unusual odor at cabinet A-3; cause unverified." if crisis else
            "Fictional technician reports a normal handheld voltage reading and no fault indicator." if drift else
            "Fictional maintenance check reports normal equipment operation.",
            stance="support" if crisis else "contradict" if drift else "neutral", severity=.75 if crisis else 0))
        events.append(event(9, 83, "CAM-B1", "routine", "Corridor remains clear",
            "Authored camera observation: service corridor unobstructed.", visual="corridor"))
        events.append(event(10, 95, "ENV-A2", "environment", "Environment shift" if crisis else "Independent reading nominal",
            "A second sensor bundle reports elevated temperature, particles, and vibration." if crisis else
            "The independent bundle remains near the normal reference regime.",
            [205, 37, 82, .24] if crisis else nominal,
            "support" if crisis else "contradict" if drift else "neutral", .8 if crisis else 0))
        events.append(event(11, 110, "ENV-C1", "routine", "Cooling plant nominal",
            "No unusual shift in the cooling plant bundle.", nominal))
        events.append(event(12, 125, "PQ-A1", "power", "Disturbance persists" if crisis or drift else "Power remains nominal",
            "The original power source repeats its unusual reading; repetition is not an independent source." if crisis or drift else
            "A second nominal reading arrives from the power bundle.",
            [201, 35, 67, .20] if crisis else [197, 22.2, 9.1, .17] if drift else nominal,
            "support" if crisis or drift else "neutral", .75 if crisis else .45 if drift else 0))
        events.append(event(13, 143, "FIELD-A", "equipment", "Fault indicator reported" if crisis else "Follow-up check recorded",
            "The same fictional technician reports a panel fault indicator. This is a follow-up, not another independent source." if crisis else
            "The same technician again reports normal local conditions; a sensor fault remains a hypothesis." if drift else
            "Routine inspection complete; no new issue reported.",
            stance="support" if crisis else "contradict" if drift else "neutral", severity=.8 if crisis else 0))
        events.append(event(14, 160, "ENV-D1", "routine", "Operations nominal",
            "Operations bundle remains near the normal reference regime.", nominal))
        scenarios.append({"id": key, "name": name, "description": subtitle,
                          "synthetic": True, "date": "2030-02-17", "events": events})
    (output / "scenarios.json").write_text(json.dumps(scenarios, indent=2) + "\n", encoding="utf-8")
    print(f"Generated 1,000 baseline samples and 3 × 14 scenario events in {output}")


if __name__ == "__main__":
    generate()
