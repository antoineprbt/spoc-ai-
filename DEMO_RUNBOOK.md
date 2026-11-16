# Five-minute real-app demonstration

Target: **5:00**, acceptable brief range **4:30–5:30**. This is a recording plan, not a record of a video already made. The group owns filming, narration, editing, and submission.

## Before recording

Start the app using `README.md`. Maximize a desktop browser, close unrelated tabs, select Nightfall, set speed to 1×, and reset. Keep the simulation banner in frame. Rehearse once. For smooth narration, pause the stream instead of pretending a prerecorded or static result is live. Use the slider to return to any required event.

## Recording sequence

| Time | Real on-screen action | Points to explain in your own words |
|---|---|---|
| **0:00–0:35** | Show BLACKSITE's initial screen, scenario menu, and station map | The problem is fragmented observations during a fictional facility incident. BLACKSITE brings them into one review workspace. All data and camera illustrations are synthetic; this is an educational simulation. |
| **0:35–1:10** | Click **Run simulation**. Watch E06–E10 arrive. Pause if useful. | Isolation Forest is actually scoring four numeric sensor features. A detected anomaly is an unusual pattern, not a confirmed emergency. Camera and field labels are authored inputs, not computer vision or LLM outputs. |
| **1:10–1:55** | Open **Sensor data**, then click **E06 / PQ-A1** | Show voltage, temperature, particles, vibration, the raw model score, threshold, and negative decision value. The model uses 200 trees, 1,000 baseline rows, and seed 42. The descriptive feature deviation is not a causal explanation or feature-attribution method. |
| **1:55–2:45** | Finish playback if paused. Click the alert, then **Event links**. Click E07 or E08; show link explanations below the graph. | NetworkX stores the facility/source/event graph. Correlation uses time, zone, and type. E06 and E07 share zone A and are 18 seconds apart. Repeated messages from the same source do not count as independent corroboration. Association does not prove cause. |
| **2:45–3:25** | Return to the incident panel and inspect its four factors | Nightfall ends at 96 = 55 anomaly + 25 corroboration + 16 authored severity. Contradiction contributes zero here. This is a transparent review priority, not “96% confidence.” Point to **UNCERTAINTY / NOT VERIFIED** and **ANALYST REVIEW REQUIRED**. |
| **3:25–4:15** | Select **Sensor drift**, run at 2×, let it finish, inspect the alert | Now camera, field, and independent sensor observations contradict the original bundle. The output visibly changes to two anomalous readings and a priority of 14. A sensor issue is a hypothesis; the app does not establish the cause. If time allows, run Routine operations to show the nominal control. |
| **4:15–4:45** | Show **How it works**, then the project folder or README | Explain the mix of actual ML, explicit rules, graph structure, and replay. Show saved CSV/JSON, pinned packages, generator, guide, citations, and AI prompt disclosure. The app runs locally after installation. Do not describe the synthetic fixture as an accuracy benchmark. |
| **4:45–5:00** | Return to the app; optionally export evidence | State the limit: real-world validation would require representative data and verified sources. The contribution is an explainable, reproducible simulation. Close on the visible working product. |

## Accurate claims to keep

- “We use a real Isolation Forest implementation from scikit-learn.”
- “The three scenarios are constructed synthetic examples, not a measured performance benchmark.”
- “The camera is a procedural illustration with authored labels.”
- “Correlation and incident scoring are explicit rules, not an LLM deciding what happened.”
- “The model and data use fixed seeds, and all runtime assets are local.”
- “Codex assisted with building the application and documents; our actual review, revisions, and recording contributions are disclosed.”

Do not claim attack prediction, real cameras, person identification, confirmed smoke, validated accuracy, production deployment, or human-only authorship. Check the course syllabus before naming which components go beyond the taught material.

## Finish the submission

Complete real contributions, append actual later prompts, rebuild the source archive, and upload it alongside the video according to the assignment portal. Verify the final video duration and that the recording shows the score changing between scenarios. The supplied deadline is **17 November 2026 at 23:59**; confirm the portal's timezone.
