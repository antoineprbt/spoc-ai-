# Sources and attribution

Prepared 16 November 2026. The package versions below match `requirements.txt`; documentation links may display a newer maintained version. The application does not fetch these sources at runtime.

## Dataset

**Northstar Station / Nightfall synthetic observations**, version 1 (2026), generated specifically for this assignment by `generate_data.py` with seed 42, with AI assistance disclosed in `AI_PROMPTS.md`.

Files: `data/baseline.csv`, `data/scenarios.json`, `data/facility.json`. Provenance and schema: `data/README.md`. No third-party dataset, real camera footage, personal data, operational feed, geographic coordinate, or institutional dataset was used. The fictional facility, text observations, and scenarios were authored for this build. They are not empirical evidence about a real crisis.

Suggested dataset citation: “BLACKSITE project. (2026). *Northstar Station / Nightfall synthetic observations* (v1). Assignment-generated synthetic dataset and generator, included with the submitted code.” Add the group's actual names only after contributions are completed.

## Runtime packages

| Package / version | Source | Actual purpose in this app |
|---|---|---|
| **scikit-learn 1.8.0** | [Project](https://scikit-learn.org/), [IsolationForest API](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) | Fits and executes the local Isolation Forest model; BSD-3-Clause project |
| **NumPy 2.4.6** | [NumPy 2.4 documentation](https://numpy.org/doc/2.4/) | Numeric feature arrays, baseline mean/deviation, clipping, and sorting; BSD-3-Clause project |
| **NetworkX 3.6.1** | [DiGraph documentation](https://networkx.org/documentation/stable/reference/classes/digraph.html) | Stores facility/source/event nodes, provenance edges, and correlation edges; BSD-3-Clause project |
| **SciPy 1.17.1** | [SciPy documentation](https://docs.scipy.org/doc/scipy/) | Required numerical dependency of scikit-learn; not presented as a separate algorithm in the UI; BSD-3-Clause project |
| **joblib 1.5.3** | [Official documentation](https://joblib.readthedocs.io/en/stable/) | Required scikit-learn execution dependency; model uses one job, with no custom disk cache; BSD-3-Clause project |
| **threadpoolctl 3.6.0** | [Official source repository](https://github.com/joblib/threadpoolctl) | Required scikit-learn dependency for native thread-pool management; BSD-3-Clause project |

Installed numerical wheels can include additional native-library license notices. Those are supplied by the original package distributions; this submission lists dependencies rather than redistributing their binaries.

## Language, server, and browser

- **Python standard library**, tested with CPython 3.14.3. [Python documentation](https://docs.python.org/3/). `http.server` serves the local app; `json`/`csv` read inputs; `random` generates the baseline; `pathlib` locates project files; `datetime` formats fictional times; `hashlib` records input hashes; `argparse` handles the port option; `unittest` verifies behavior; `zipfile` packages the handoff. These are part of Python, not separately installed packages. The [HTTP server documentation](https://docs.python.org/3/library/http.server.html) describes its development-oriented limitations.
- **Browser-native HTML, CSS, SVG, and JavaScript.** No React, Streamlit, Flask, D3, charting library, icon package, web font, CDN asset, or frontend build dependency is used. Flask happened to exist on the development machine but was not used or imported by this project.
- **System fonts** are requested through CSS and supplied by the viewer's device; no font files are bundled or downloaded.

## Algorithm attribution

Isolation Forest originates with Fei Tony Liu, Kai Ming Ting, and Zhi-Hua Zhou, “Isolation Forest,” *2008 Eighth IEEE International Conference on Data Mining*, pp. 413–422. [DOI: 10.1109/ICDM.2008.17](https://doi.org/10.1109/ICDM.2008.17). BLACKSITE uses scikit-learn's implementation; it does not claim to implement the original research code or reproduce the paper's evaluation.

The time/zone/type correlation rules, priority weights, independent-source heuristic, scenario labels, and interface are project-specific choices documented in `METHODOLOGY.md`. They are not attributed to a validated crisis-management standard.

## Code, visuals, and development assistance

- Application code, tests, synthetic data generator, documentation drafts, SVG logo, station schematic, and camera illustration were created in this Codex-assisted build. No external code template or copied application component was used.
- The camera panel is a procedural SVG drawing. There is no photographic source, real surveillance frame, pretrained vision model, or image-generation API.
- The installed **frontend-skill** design guidance informed layout restraint, hierarchy, and interaction choices. It is development guidance, not a runtime package or an imported code component.
- **OpenAI Codex** assisted with coding, documentation, data construction, terminal checks, official-source lookup, and local-browser verification. See `AI_PROMPTS.md` for the actual brief and disclosure. No separate subagents or external AI image/video generators were invoked for this build.
- The original assignment brief supplied by the user is preserved in `docs/prompts/01_build_request.txt`. The full course syllabus and grading rubric were not supplied, so no claim is made about unseen course materials.
