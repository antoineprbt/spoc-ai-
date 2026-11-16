# Implemented method

## Scope

BLACKSITE is an offline educational decision-support simulation. The computation in `engine.py` is used by the application, not a mock label. It combines an unsupervised estimator with authored data, deterministic rules, and a graph. It does not use an LLM or computer vision at runtime.

## Data and model

`generate_data.py` uses Python's `random.Random(42)` to generate 200 reference rows per sensor bundle, 1,000 total. There are four numeric model features in fixed order: voltage (V), temperature (°C), particles (µg/m³), and vibration (mm/s). A shared latent random load adds weak dependence between voltage, temperature, and vibration. All five bundles use the same deliberately simplified normal regime.

Source IDs, zones, scenario names, event severity, and support/contradiction labels are **not model features**. The model trains only on `data/baseline.csv`. It does not fit on scenario events. Those events are authored demonstration fixtures, not a representative held-out evaluation dataset.

Parameters: `IsolationForest(n_estimators=200, max_samples=256, contamination=0.02, random_state=42, n_jobs=1)`. Isolation Forest partitions observations with random trees. Observations isolated with shorter paths tend to be more unusual. There is no feature scaling step; baseline means and standard deviations are used only for descriptive comparisons in the detail view.

For a sensor vector x:

```
raw_anomaly_score = -model.score_samples(x)
threshold = -model.offset_
decision = model.decision_function(x)
is_anomaly = decision < 0
strength = clamp(-decision / 0.15, 0, 1)
```

The 0.15 normalization scale is an explicit heuristic, not probability calibration. `contamination=0.02` sets a training-distribution threshold. It does not establish a 2% false-positive rate in use. The UI exposes the actual fitted threshold and score. Small rounding differences in displayed values do not change the underlying anomaly flag.

## Correlation

For each displayed prefix, keep observations whose age relative to its latest timestamp is at most 120 seconds. Connect a pair if its time gap is at most 120 seconds and either:

1. Both observations are in the **same zone**, and both types belong to `{power, visibility, equipment, environment}`; or
2. Their zones are explicitly **adjacent**, and their non-routine event types are identical.

Routine observations do not create these correlation edges. A pair involving a `contradict` input is marked as a contradiction association. This is an authored evidence relationship, not a machine-learned semantic judgment. Two contradictory reports can therefore be associated by the graph rule without meaning that they contradict each other logically.

An active anomaly creates one incident per zone. Its anchor is that zone's earliest active anomalous reading. Supporting evidence must link **directly** to at least one active anomaly; transitive chains do not absorb arbitrary observations. No incident is created solely by camera or field-report inputs in this version.

## Priority

Let A be the largest normalized anomaly strength among active anomalous readings in the incident zone. Let S be the largest authored severity among the incident's evidence. Let C be the number of distinct other source IDs whose **latest linked observation** has stance `support`. Let D be the corresponding number whose latest linked observation has stance `contradict`. The original anchor source does not count toward C or D. Repeated observations from the same source count once.

```
anomaly contribution       = 55 × A
corroboration contribution = 25 × min(C / 2, 1)
severity contribution      = 20 × S
contradiction contribution = -20 × min(D / 2, 1)
priority = clamp(round(sum(contributions)), 0, 100)
```

For consistency between backend and UI, individual contributions are rounded to two decimals before the final sum. Python's `round` uses ties-to-even rounding. Categories are high ≥70, elevated ≥40, review <40. These weights and cutoffs were chosen for an interpretable classroom demonstration. They have not been optimized or validated against real incidents.

Distinct IDs stand in for independent sources; real source independence is unverified. Repeated severe input can maintain severity even when it does not increase corroboration. An incident remains in review until its active anomaly anchors age out of the 120-second window; there is no operational “resolved” or “confirmed safe” action. Sensor status shows the latest received reading, which can outlive the active correlation window.

## Graph and playback

`networkx.DiGraph` stores facility, zone, source, and event nodes. Structural edges are `contains`, `hosts`, and `observed`; active observation links are `correlates` or `contradicts`. The frontend draws a readable SVG subgraph using actual nodes and edges returned by Python. It does not infer causality from edge direction. Layout positions are fixed presentation choices, not graph-embedding predictions.

Each run scores the events and computes a snapshot for each prefix independently. The browser progressively reveals the snapshots; the slider and export use only the selected prefix. Rewinding therefore does not expose later evidence. Sensor/model inference occurs on the server before animated playback, not in the animation itself.

## What is and is not evaluated

Automated tests check deterministic outputs, byte-identical data regeneration, absence of future-evidence leakage, evidence deduplication, contradictory evidence, correlation gating, graph provenance, local API behavior, and network-free engine computation. UI checks exercise the real browser flow. These demonstrate reproducibility and application behavior, **not** real-world accuracy or readiness.

The fixture was deliberately adjusted during development when a voltage-only synthetic drift did not exceed the learned threshold. The final alternative changes two channels of a fictional faulty bundle, making an anomaly visible before independent sources contradict it. This is scenario construction, not performance tuning on an independent test set. No precision, recall, F1, detection rate, or incident prediction claim is made.

## Limits and possible next work

The baseline has one stationary regime and little noise complexity. Stance, type, severity, and source independence are supplied by the scenario. It cannot establish smoke, identify people, attribute responsibility, predict attacks, or recommend tactical action. The app is a loopback demo without authentication or persistent state. Further academic work could compare robust statistical baselines on separate synthetic distributions and measure sensitivity to the correlation window; that work has not been implemented or evaluated here.
