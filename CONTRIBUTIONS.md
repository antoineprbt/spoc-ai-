# Group contributions — review before submission

**Course:** ESSEC SPOC AI for Business / Advanced AI Algorithms (AAA)  
**Project:** BLACKSITE  
**Group number:** 2  
**Contribution record last updated:** 16 November 2026  
**Submission date:** Pending final Moodle upload

This records only contributions currently established. Each group member should review and complete their own row. AI assistance is disclosed in `AI_PROMPTS.md`; the application was built with Codex assistance, not as unaided human coding.

| Member name | Actual work performed | Concrete evidence | What they can explain or reproduce |
|---|---|---|---|
| Antoine Préaubert | Led the BLACKSITE product build with Codex: conceived the product and crisis-simulation use case, defined the scope and requirements, directed the AI-assisted implementation, and arranged the hosted demo. | Product brief: `docs/prompts/01_build_request.txt`; implementation and documentation in this repository; hosted demo: https://spoc-ai-blacksite.vercel.app | Product concept, scope, user flow, and simulation boundaries. Review `METHODOLOGY.md` and rehearse the demo before claiming detailed understanding of the model and scoring. |
| Srinith Patibandla | Recorded scenes 6–8 of the demo video (Sensor drift test, why it matters / reproducibility, close); planned the on-screen actions and narration timing for those scenes. | Video segment (scenes 6–8). | How the Sensor drift scenario differs from Nightfall (conflicting evidence → priority 14 vs 96), that the score is a review priority not a confidence, and the project's reproducibility (pinned packages, fixed seed, data generator, user guide, AI prompts). 
| Yassine SAIDI | Produced scenes 4–5 of the demo video ("Connect the dots": the NetworkX event-link graph; "The priority score": the explainable four-factor score with human review) and assembled the complete final video. For scenes 4–5: wrote the shot list and narration, prepared the app state so the segment continues seamlessly from scene 3, checked every on-screen value against the app (E06–E07 link: zone A, 18 s apart; score 96 = 55 + 25 + 16 + 0), and synchronised the on-screen actions with the narration. For the full video: merged scenes 1–3, 4–5 and 6–8 into a single edit within the 5-minute limit (cuts, captions, zooms, audio levelling) and anonymised it (no names, accounts or browser interface on screen). | Video segment (scenes 4–5); final assembled demo video; shot list and narration script for scenes 4–5; editing brief for the final video. | How the event-link graph is built: facility, zone, source and event nodes; two events are linked only within 120 s, in the same or a neighbouring zone; each link is explained in plain words; a link shows association, not cause. How Nightfall's score of 96 breaks down: anomaly strength +55, corroboration +25 (independent sources count once), authored severity +16, contradiction 0. Why it is a review priority and not a confidence percentage, and why the alert stays "not verified" and requires analyst review. How the final video was cut and timed to stay within 5 minutes. |
| Other group members | To be completed and confirmed by each member. | Add the specific files, review, corrections, or video segment. | State what the member can personally explain or reproduce. |

## Group verification

- [ ] Members have completed and reviewed their own contribution statements.
- [ ] Names and student identifiers, if required by the course, are accurate.
- [ ] The group has rehearsed the app and can explain the model, rules, score, and uncertainty.
- [ ] Another member has tried the hosted demo or local setup; record the actual result below.
- [ ] `AI_PROMPTS.md` includes any later prompts used for video or editing.
- [ ] The final video shows the real app and avoids fabricated performance or deployment claims.
- [ ] The ZIP/source code, data, user guide, and final video have been uploaded to Moodle.

**Independent setup / rehearsal outcome:** Pending; record who tested, when, environment, and result.

**Video owner and actual contribution:** Pending group confirmation.

**Final upload owner and confirmation:** Pending Moodle submission.
