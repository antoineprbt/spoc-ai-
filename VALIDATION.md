# Verification record

Date: **16 November 2026**. This records observed development checks, not independent certification or a model benchmark.

## Environment

- Empty initial project directory; no existing application was overwritten.
- CPython **3.14.3** on macOS; a dedicated local virtual environment.
- Six runtime packages installed at the exact versions in `requirements.txt`.
- Python's local server, browser-native frontend, no Node dependency for running the app.
- In-app Chromium browser used to exercise the actual interface. Desktop viewport: 1440 × 1000; the document scrolls vertically and dense panels have their own scrolling.

## Automated behavioral checks

**14 tests passed** with the project test command. Coverage:

1. Browser assets served locally.
2. Bootstrap and all three scenario endpoints.
3. Invalid requests and non-allowlisted file paths rejected.
4. Alerts expire after their anomaly anchors leave the active time window.
5. Contradiction lowers priority without asserting safety.
6. Correlation requires the specified time, zone, and type conditions.
7. Fresh model fits with the fixed seed reproduce the same outputs.
8. Graph nodes and edges preserve observation provenance.
9. Earlier snapshots contain no future evidence.
10. Engine initialization and every scenario run complete while socket connection attempts are forbidden by a test patch.
11. Priorities equal the bounded sum of their exposed factors and remain unverified.
12. Repeated source reports do not inflate corroboration.
13. Regenerated input files match the saved dataset byte for byte.
14. Scenario fixtures yield distinct expected outputs.

Additional checks: Python package dependency compatibility; JavaScript syntax; original prompt copy matches the supplied attachment byte for byte.

These tests do not measure classification accuracy or the quality of the chosen scoring weights. Network-free engine testing and local browser assets do not constitute a test of every operating system's network behavior.

## Observed fixture outcomes

| Scenario | Processed observations | Anomalous readings | Active incidents | Final priority |
|---|---:|---:|---:|---:|
| Nightfall | 14 | 3 | 1 | 96 |
| Sensor drift | 14 | 2 | 1 | 14 |
| Routine operations | 14 | 0 | 0 | None |

Model threshold observed in the pinned environment: **0.573102** for `-score_samples`. Nightfall E06: raw score **0.711758**, decision **−0.138656**. These are fixture outputs, not a validated diagnostic threshold.

## Manual browser checks

- Initial idle state and the persistent synthetic-data label.
- Nightfall run from the button through all 14 events.
- Changed scenario to Sensor drift; observed two detections, priority 14, and conflicting evidence.
- Routine operations run through 14 events: zero anomalies, zero active alerts, no priority score.
- Pause, rewind to event 0, next event to event 1, jump to the final frame, and resume from a rewind.
- Facility-map zone selection and returning to the active incident.
- Event-links graph and linked authored-camera observation detail.
- Sensor-data table and E06's actual readings and model output.
- Methodology dialog open/close.
- Reduced-motion control and changed replay speed.
- Narrow viewport check at 390 × 844: stacked panels and no page-level horizontal overflow (body width 390 pixels).
- No browser warning/error entries were returned during the inspected session.
- Browser download of a partial JSON export. The downloaded file was parsed: it contained exactly one displayed event, no future events or alerts, and three input-data hashes.

A real replay bug was found during manual testing: the pause update replaced the slider's chosen value before it was read. The handler now captures the value first; browser retesting confirmed a rewind to zero and a single step to one. Interactive SVG groups were also made accessible as button-containing groups. Inspector spacing was reduced so its uncertainty explanation is visible at the desktop test width.

Screenshots in `docs/screenshots/` are captures of the running application, not design mockups.

## Portable archive check

The source archive was extracted into a separate temporary directory. A **fresh virtual environment** was created inside that extracted copy, the pinned requirements were installed, dependency compatibility passed, all 14 tests passed again, and the README's `app.py` entry point started. This check used the same Mac, not another person's computer. The temporary copy and environment were removed afterward.

An additional launch from an unrelated working directory confirmed that the application resolves its assets and data relative to its own files. The final entry point was checked through the local health endpoint on an OS-selected port. Only the displayed startup port was corrected after the extracted-copy test; that correction received this targeted launch/health check. Final documentation updates do not change the validated engine or frontend.

## Scope limits

Initial local verification included no deployment or external-camera integration; no real-world validation, independent user study, or submitted video was performed. No claim is made that a different person's machine has been tested. Windows instructions are supplied but were not manually exercised. The group must complete its own names, contributions, rehearsal, video, and final upload.

## Hosted verification — 16 November 2026

Production: https://spoc-ai-blacksite.vercel.app . Anonymous HTTPS requests returned 200 for the page, CSS, JavaScript, health, and bootstrap. Actual POST requests for all three scenarios returned 14 frames with final anomaly counts 3 / 2 / 0 and priorities 96 / 14 / none. The GitHub repository is linked to the Vercel project for subsequent pushes. Hosted requests require internet; the original offline local mode remains available.
