# BLACKSITE — User guide

## 1. Open the application

Follow `README.md` to install the requirements and start the local server. Open [http://127.0.0.1:8501](http://127.0.0.1:8501) in a desktop browser. You should see **BLACKSITE**, **LOCAL ENGINE READY**, the Northstar Station schematic, and **SIMULATION — SYNTHETIC DATA ONLY**.

The initial screen is idle: zero processed events, no sensor readings, no alerts. The camera panel is an illustrated placeholder. All positions use a fictional local drawing grid. The exercise date, 17 February 2030, is fictional and unrelated to the recording date.

## 2. Run Nightfall

1. Leave **Nightfall** selected in the **SCENARIO** menu.
2. Click **Run simulation**. The local model scores the stream, then playback reveals 14 observations in order.
3. The first five readings establish nominal conditions. **E06** reports a power disturbance. **E07** adds an authored haze observation. **E08** adds a fictional equipment-fault report. **E10** brings a second sensor bundle's unusual readings.
4. Watch zone A highlight, the alert queue populate, and the priority factors change. The final run has three sensor anomalies, one incident, and a 96/100 review score with the pinned environment.

The clock shows fictional event time. Playback is accelerated: 1× advances one observation every 1.4 seconds. The three detected anomalies are three readings, not three incidents or three independent sources.

## 3. Control playback

| Control | Effect |
|---|---|
| **Pause / Resume** | Stop or continue revealing observations |
| **Next event** (▸\|) | Pause and reveal exactly one more event |
| **Displayed event count** slider | Pause and inspect a prefix of the stream; 0 restores the initial snapshot |
| **Speed** | 0.5×, 1×, or 2× replay speed |
| **Reset simulation** (↺) | Clear the displayed stream and selections |
| **Run simulation** | Compute and replay the selected scenario from the start |
| **SCENARIO** menu | Select a new input stream; clears the previous output |
| **Reduce motion** | Disable nonessential transitions and event entrances; does not stop playback |

Only evidence up to the displayed event count appears in that snapshot. Later observations do not change the score shown for an earlier time. After the final event, use the slider to revisit the stream or **Run simulation** to restart it.

## 4. Inspect an incident and a reading

Click **Power annex** in the alert queue, or select zone A on the map. The right panel shows the incident's priority, its contributing factors, and uncertainty. Selecting another zone shows its local state; it does not change the data.

Click **E06: Voltage disturbance** in the timeline (scroll the timeline upward if needed). The panel shows the exact four readings, raw anomaly score, threshold, and decision value. A **negative decision value** indicates an anomaly under this fitted model.

The descriptive deviation compares a feature to its baseline mean and standard deviation. It is **not** an Isolation Forest feature attribution. Use **Back to incident** to return to the score breakdown.

Click a camera or field event to read its authored observation and the explicit notice that no vision or language model interpreted it. The camera illustration shows the latest CAM-A1 observation received so far; selecting a timeline item does not rewind that illustration. Use the slider to rewind the entire snapshot.

## 5. Read the priority and uncertainty

Priority is a 0–100 **review-order heuristic**. It is not confidence, probability of harm, or a confirmed diagnosis.

| Factor | Contribution |
|---|---:|
| Maximum current sensor anomaly strength in the zone | 0 to +55 |
| Other source IDs that support the incident, capped at two | 0 to +25 |
| Highest authored severity among linked events | 0 to +20 |
| Other source IDs contradicting the signal, capped at two | 0 to −20 |

The four contributions are added, rounded, and bounded to 0–100. High priority means at least 70, elevated means 40–69, and review means below 40. These thresholds are design choices, not validated safety limits.

**Corroborated signals** means multiple distinct sources in the scenario agree. **Limited evidence** means further observations are needed. **Conflicting evidence** means other sources challenge the original signal. All three states remain **ANALYST REVIEW REQUIRED**. No alert becomes a confirmed fact automatically.

## 6. Follow event links

Select **Event links** above the map, or **Inspect the evidence links** in the incident panel. The graph shows Northstar Station, the incident zone, reporting sources, and event nodes. Click an event node or scroll down and click an event ID in the explanations.

Gray edges show containment and observation provenance. Orange edges indicate rule-based association. Dashed edges involve contradictory observations. The text list gives the time gap, zone relation, event types, and linked event IDs. Links express association; they do not establish cause.

All correlation edges use observations in the current 120-second window. An incident's evidence must link directly to at least one active anomalous sensor reading. The displayed graph is the incident subgraph; the full graph is included in the export.

## 7. Inspect sensor data

Select **Sensor data**. The table shows only sensor readings received so far, their features and model score. Orange rows are detected anomalies. Click an event/source entry to inspect it. The **Sensor status** panel always shows each bundle's latest received status, while the summary anomaly count counts all anomalous readings received so far.

## 8. Compare the alternatives

Select **Sensor drift** and click **Run simulation**. The first unusual sensor bundle is later challenged by a clear authored camera observation, a nominal independent bundle, and a fictional local report. Final output: two anomalous readings, one incident, **14/100**, **Conflicting evidence**. “Sensor drift” names the constructed scenario; the system does not prove that a sensor fault caused the discrepancy.

Select **Routine operations** and run it. Final output: 14 processed events, five reporting bundles, zero anomalies and no active alert. This is a nominal control fixture, not evidence of a measured false-positive rate.

## 9. Export evidence

Click **Export evidence ↓** after at least one event. Your browser downloads a JSON file named, for example, `blacksite-nightfall-event-14.json`. It contains the displayed snapshot, exact observations, model settings, dataset hashes, score factors, and complete graph. If playback is paused partway, the export contains that prefix only. No upload occurs.

Refreshing the browser resets the interface. Keep exported JSON if you need an audit artifact. The application does not maintain a database or save your review actions.

## 10. Record the demo

Use `DEMO_RUNBOOK.md` for a five-minute sequence. Explain that the anomaly detector is machine learning, correlation and scoring are explicit rules, NetworkX stores the graph, and all camera/report inputs are synthetic. Keep the simulation label visible. The group records and edits the actual video separately.
