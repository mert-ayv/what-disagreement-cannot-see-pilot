# K4 test: pre-registration (2026-10-17, before any narrative is written or any model is asked)

Question: do current models, given the policy text and a user's free-text story, ask for exactly the facts that can
change the coverage outcome, and decide only when the outcome is determined? If yes, K4 (fact elicitation) is at
ceiling like K9 and K2, and the coverage-agent direction loses its core.

Ground truth: `relevance.py` over the expert port (`../src/expert.py`, certificate level). For each case
(`cases.py`), hidden facts are enumerated over fixed domains; the outcome is determined if all completions agree; a
hidden fact is relevant if changing it alone can change the outcome.

Cases (20): determined 10 (1, 2, 9, 10, 12, 15, 16, 18, 19, 20), of which 9 and 10 rest on recorded interpretive
choices (man without a female partner: expert denies, no table row; partner's vasectomy: expert checks the patient
only, text says "you or your partner"); open 10 (3, 4, 5, 6, 7, 8, 11, 13, 14, 17) with 1 or 2 relevant hidden facts
each (12 relevant facts in total); cases 6 and 17 also touch "timed" vs "frequent" intercourse.

Procedure: one Claude agent writes first-person stories from the case notes, mentioning only known facts; a second,
fresh Claude agent gets the policy text, the glossary and the stories, and for each answers covered / not covered /
need more information, with the questions it would ask (minimal set). Scored by the author against `cases.py`.

Metrics: (a) recall of relevant facts on open cases (12); (b) open cases decided without asking (confident errors);
(c) determined non-reading cases (8) decided correctly without questions; (d) extra questions per case; (e) whether
cases 9 and 10 are flagged as resting on a reading.

Kill rule: K4 as "models elicit the wrong facts" is **dead** if recall >= 90% (11 of 12), at most 1 open case is
decided without asking, and at least 7 of 8 determined non-reading cases are decided correctly. **Alive** if recall
< 75% (8 or fewer of 12) or at least 3 open cases are decided without asking. In between: weakened.

Limits: author-designed cases and domains; one judge, one run, same family as the writer; the expert's readings define
"relevant"; no API cost.
