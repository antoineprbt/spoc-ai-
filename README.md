# BLACKSITE

**See the signal. Understand the incident.**

A local browser application for ESSEC's **SPOC AI for Business — Advanced AI Algorithms (AAA)** group assignment. BLACKSITE combines multivariate anomaly detection, explicit event-correlation rules, and a facility graph to help an analyst review a **fictional** incident at **Northstar Station**.

**SIMULATION — SYNTHETIC DATA ONLY.** No cameras, external feeds, real facilities, identities, or operational systems are connected.

## Run it

Prerequisites: **CPython 3.11–3.14 (excluding 3.14.1, which NetworkX does not support)**, `pip`, and a modern desktop browser. Development and verification used **Python 3.14.3 on macOS**. Other operating systems have not been manually verified. Internet access is needed once to install the pinned Python packages. After installation, the application runs locally without API keys, cloud services, external fonts, model downloads, or an internet connection.

Open a terminal **inside the project folder** (the folder containing this README and `app.py`). On macOS / Linux:

```sh
python3 -m venv .venv
```
*Français : crée un environnement Python isolé dans le dossier du projet.*

```sh
.venv/bin/python -m pip install -r requirements.txt
```
*Français : installe les six dépendances aux versions indiquées.*

```sh
.venv/bin/python app.py
```
*Français : entraîne le modèle sur les données locales et lance le serveur de démonstration.*

Open **[http://127.0.0.1:8501](http://127.0.0.1:8501)**, choose **Nightfall**, and click **Run simulation**. Keep the terminal open. Stop the server with **Ctrl+C**. Do not open `static/index.html` directly.

Windows / PowerShell alternative, from the project folder:

```powershell
py -3 -m venv .venv
```
*Français : crée l'environnement avec la version de Python 3 installée ; elle doit être comprise entre 3.11 et 3.14.*

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```
*Français : installe les dépendances sans modifier la politique d'exécution de PowerShell.*

```powershell
.venv\Scripts\python.exe app.py
```
*Français : lance l'application ; ouvre ensuite la même adresse locale dans le navigateur.*

## What works

- **Three deterministic scenarios:** Nightfall, Sensor drift, Routine operations. Each contains 14 observations spanning 2 minutes 40 seconds of fictional time.
- **Actual local machine learning:** scikit-learn Isolation Forest scores voltage, temperature, particles, and vibration against 1,000 generated baseline rows.
- **Explainable correlation:** links require a time gap of at most 120 seconds plus explicit zone/type conditions. Each incident lists the observations and the reason for each link.
- **NetworkX graph:** facility → zones → sources → observations, with additional correlation and contradiction edges.
- **Transparent priority:** separate anomaly, corroboration, severity, and contradiction factors; all alerts remain unverified.
- **Working controls:** replay, pause/resume, next event, time scrubber, speed, reset, zone selection, observation inspection, three workspace tabs, reduced motion, and JSON evidence export.
- **Fully local visuals:** original SVG facility plan and clearly labeled procedural camera illustration.

The model trains when the server starts. Each **Run simulation** request scores the selected stream and computes a snapshot for every event prefix. The browser then reveals those snapshots sequentially. This is accelerated replay, not a live feed or a stream-processing deployment. At 1×, the display advances every 1.4 seconds; it does not wait the full fictional time gap.

## Deliverables

| File / folder | Purpose |
|---|---|
| `app.py` | Local HTTP server and API; binds only to `127.0.0.1` |
| `engine.py` | Isolation Forest, correlation rules, priority score, NetworkX graph |
| `static/` | HTML, CSS, JavaScript, favicon; no frontend build required |
| `generate_data.py` | Recreates every synthetic input file with seed 42 |
| `data/baseline.csv` | 1,000 multivariate normal-reference observations |
| `data/scenarios.json` | Three scripted scenario streams, 42 observations in total |
| `data/facility.json` | Four zones, five sensor bundles, two camera sources, one report source |
| `data/README.md` | Data schemas, generation method, and provenance |
| `requirements.txt` | Exact versions for every installed runtime dependency |
| `USER_GUIDE.md` | User flow, controls, reading the scores, uncertainty |
| `METHODOLOGY.md` | Implemented formulas, graph rules, and limitations |
| `SOURCES.md` | Package, algorithm, dataset, and asset citations |
| `AI_PROMPTS.md`, `docs/prompts/` | Actual build prompt and truthful tool-use disclosure |
| `CONTRIBUTIONS.md` | Unfilled group attribution template |
| `DEMO_RUNBOOK.md` | Five-minute walkthrough for recording the real app |
| `VALIDATION.md` | Checks actually performed and their scope |
| `tests/test_engine.py` | Determinism, data, calculation, and API checks |
| `prepare_submission.py` | Creates a portable source/data/documentation ZIP |

## Reproduce and verify

Regeneration replaces only the three generated input files in `data/`. It leaves the data README untouched. Restart the server after changing data or Python code.

```sh
.venv/bin/python generate_data.py
```
*Français : régénère les données synthétiques à l'identique à partir de la graine 42.*

```sh
.venv/bin/python -m unittest discover -s tests -v
```
*Français : vérifie les calculs, les liens, la reproductibilité, l'absence de connexion réseau du moteur et les routes locales.*

```sh
.venv/bin/python -m pip check
```
*Français : vérifie la compatibilité des dépendances installées.*

Expected **fixture outcomes**, not model-accuracy measurements:

| End of scenario | Detected sensor anomalies | Active incident | Priority |
|---|---:|---:|---:|
| Nightfall | 3 | 1, corroborated signals | 96/100 |
| Sensor drift | 2 | 1, conflicting evidence | 14/100 |
| Routine operations | 0 | 0 | No score |

## Troubleshooting

- **Port already in use:** stop an earlier copy of the server or use another port:

```sh
.venv/bin/python app.py --port 8502
```
*Français : lance le serveur sur le port 8502 ; ouvre ensuite http://127.0.0.1:8502.*

- **Missing dependency:** use the `.venv` Python and install `requirements.txt`. The app stops with an explicit error rather than claiming an unavailable algorithm is running.
- **Installation fails:** check Python's version. Use a supported Python with available binary wheels; no large model is needed. There is no untested fallback disguised as Isolation Forest.
- **Missing data:** run `generate_data.py` and restart the app.
- **Changes not visible:** restart the server for Python/data changes, reload the browser for HTML/CSS/JavaScript changes. Nothing is persisted in browser storage.
- **Small laptop screen:** panels can scroll. For recording, maximize a desktop browser; use a 1440-pixel-wide or larger desktop view if available.

## Prepare the handoff

Fill the real names and actual work in `CONTRIBUTIONS.md`, append any further prompts to `AI_PROMPTS.md`, and record the video separately. Then rebuild the archive:

```sh
.venv/bin/python prepare_submission.py
```
*Français : crée `submission/BLACKSITE.zip` avec le code, les données et les documents, sans environnement Python ni fichiers personnels.*

The archive contains a top-level `BLACKSITE/` folder. The recipient extracts it and follows the setup commands above. Dependencies are not bundled. The video is not created or submitted by this project. Stated deadline: **17 November 2026, 23:59 (Europe/Paris)**; the group must verify the submission portal's timezone and upload rules.

## Known limits

This is an educational simulation, not a deployed operational system. The data is intentionally simple and constructed to make scenario differences visible. No held-out real-world evaluation, false-positive rate, calibrated risk estimate, or deployment claim is made. Camera/report labels, evidence stance, and severity are authored inputs; there is no computer vision or language-model inference. Distinct source identifiers are treated as independent for the scoring heuristic, although real source independence would require validation. Causes remain unconfirmed, and a clear camera image or a low score does not establish safety.

There is no authentication, incident persistence, or production hardening. Python's built-in HTTP server is used only for a local demo. Exact package versions and fixed seeds support reproduction; bit-for-bit numeric results across all platforms are not guaranteed. The full course syllabus was not supplied, so the group should verify that the demonstrated ML-plus-graph integration satisfies the instructor's “beyond the course” criterion.
