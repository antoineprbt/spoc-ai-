# AI use and actual prompts

## Disclosure for this build

**Date:** 16 November 2026. **Tool:** OpenAI Codex, the coding assistant in the Codex desktop application. The exact deployed backend model identifier is not independently exposed in the project artifacts; no specific model version is claimed here.

The user supplied the BLACKSITE concept and implementation brief. Codex inspected an empty workspace, selected the local Python/browser approach, and generated the application, deterministic data generator, original SVG illustrations, tests, and draft documentation. Codex also ran terminal commands, consulted official package documentation, and exercised the local application in the integrated browser. Package installation used PyPI. The app itself does not call Codex or any AI provider.

**Actual build prompt:** [docs/prompts/01_build_request.txt](docs/prompts/01_build_request.txt). This is the verbatim attached request, beginning “We need to build our group's final assignment for ESSEC's SPOC AI for Business, Advanced AI Algorithms (AAA).” The preserved file retains the original spelling and punctuation. It contains the product concept, safety boundary, features, design brief, reproducibility requirements, and requested deliverables.

There was one task-specific user prompt for the initial build. The assistant's coding, debugging, and validation steps occurred within that conversation; they are not presented as invented follow-up prompts. General user coding preferences and system instructions are not a fabricated prompt history and are not reproduced here. The installed `frontend-skill` provided additional design guidance during the build.

No separate AI subagents, image-generation model, video-generation model, paid inference API, or runtime language model was used. Camera/report labels are authored synthetic inputs. Isolation Forest is the application's runtime machine-learning component, distinct from the AI coding assistant used during development.

## Development decisions and revisions (a log, not additional prompts)

| Observed action | Reason / outcome |
|---|---|
| Chose standard-library Python HTTP server + static browser UI | Minimal local setup with direct control over the requested dashboard layout |
| Installed exact scikit-learn, NetworkX, and numerical dependency versions | Actual local algorithms, reproducible installation |
| Generated 1,000 reference rows and three 14-event streams | Inspectable synthetic inputs with no personal or external data |
| First voltage-only drift fixture did not cross the fitted threshold | Revised the fictional faulty bundle to shift voltage and vibration; disclosed as fixture construction, not measured accuracy |
| Implemented prefix snapshots and source-ID deduplication | Avoid future-evidence leakage and inflated corroboration from repeated reports |
| Tested local computation and browser controls | Fix implementation issues and distinguish verified behavior from claims |

This file describes AI involvement honestly; it does **not** establish any group member's individual contribution. Complete `CONTRIBUTIONS.md` with the work each person actually performs. The group should read and be able to explain the code and limitations before recording or submitting it.

## Add real later prompts here

Do not fill this table with hypothetical prompts. Add only prompts that were actually sent, including prompts used to prepare the video, voiceover, editing, slides, or later code revisions. If no AI is used for the video, write that fact instead.

| Date | Group member | AI tool and model if known | Exact prompt or attached transcript path | Output used | Human checks / corrections |
|---|---|---|---|---|---|
| [Fill after use] | | | | | |

For a long prompt, save its verbatim text as a new numbered file in `docs/prompts/` and reference that file. Retain failed or revised prompts when they materially contributed to the deliverable; do not retroactively rewrite them as if they were the original instructions.

## Actual follow-up request — 16 November 2026

> ok , btwon bosse ds le rpeo github spoc-ai ( lui [https://github.com/antoineprbt/spoc-ai-](https://github.com/antoineprbt/spoc-ai-)) et btw je veux pas avoir à lanceru ne ocmmande pr relancer ! déploei sur vercel !

Codex added a Vercel Python adapter, pushed the project to that repository, and deployed the same engine as a hosted application. This supersedes the initial local-only delivery scope; offline reproduction remains supported.

## Suggested technical questions — not historical prompts

The following questions were drafted by Codex at the user's request as possible technical discussion topics. They were not asked during the original build and are not evidence of a group member's prior technical work. If actually used later, record that exchange and its outcome separately.

1. **Abstraction boundaries:** “How does separating the inference engine, HTTP adapter, and browser presentation let us reuse the same computation locally and on Vercel? Identify where transport concerns still leak into the application and explain whether another abstraction would justify its complexity.”
2. **API and deployment lifecycle:** “Trace a POST to /api/run from the Vercel rewrite through the Python handler to the returned snapshots. Which work happens during deployment, on a cold start, and on each request? What changes would avoid repeated model fitting without introducing stale model or dataset versions?”
3. **Temporal correctness:** “What invariants ensure that replaying an earlier snapshot cannot use future observations or count repeated reports as independent corroboration? Explain how the current tests exercise those invariants and describe a counterexample that would expose a flawed implementation.”
