# Exercise 5: The estimator check

Paper: Stevenson & Wolfers (2006), "Bargaining in the Shadow of the Law: Divorce Laws and Family Distress", QJE.
Design copied: state-by-year panel, staggered adoption of unilateral divorce, female suicide rate,
two-way fixed effects. See `design_sheet.md`.

## Question
Does an AI agent recover a known planted effect on simulated data that copies this design?
When one identifying assumption is broken (effect grows over time under staggered adoption),
does anything in the agent's output warn us?

## Sealed truth (fixed before any agent run)
- Date sealed: 2026-10-01
- File: `sealed.enc` (kept outside this repo until the reveal)
- SHA-256: `<e419d21b90e4e9526bfe236d5a2c477a6cc06c486b91a6420d090d6fc9b27745>`
- At the reveal: decrypt, run `sha256sum sealed.enc` again, and check it matches this line.

## Roles and how they were kept apart
- Planter: <name>. Generated 600 datasets (300 per scenario), chose effect sizes by a
  random draw from a secret seed, never printed them, then encrypted code, seed and truth.
- Runner: <name>. Ran the agent cold on one dataset per scenario.
- Auditor: <name>. Reads the transcripts and scores the diagnostics.
- Deviation to disclose: <e.g. one person played all three roles; separation was enforced by
  separate Claude sessions, separate folders and encrypted truth>.

## Simulation (what the agent was NOT told)
- Panel: 51 states x 33 years (1964-1996), 1,683 rows per file, columns `state, year, y, treated`.
- Adoption schedule from the paper: 9 always treated, 5 never treated, 37 adopt 1969-1985.
- Scenario X: constant effect. Scenario Y: effect near zero at adoption, growing linearly
  to a long-run value by year 19 (same adoption dates). Files are unlabelled.
- Truth = true average effect on treated state-years, computed from the data-generating
  process, not from an estimator.
- Known limitations: noise is additive normal, so about 0.58% of y values are negative;
  year-effect SD (0.10) and the linear ramp are my assumptions.

## Conditions of the agent runs
- Model: <model shown in the app>
- Date: <date>
- Template: Sant'Anna workflow template, commit <hash>
- Permissions: template settings allow all Bash, Edit and Write without prompts
- Runs: `runs/run1` (file d_b51e), `runs/run2` (file d_e4fd), each a fresh session
- Prompt used: see `transcripts/`

## Diagnostic checklist (written BEFORE the runs, dated 2026-10-01)
For the run on the broken scenario, did the agent, without being asked:
1. Mention the parallel-trends assumption?
2. Run a pre-trend or event-study check?
3. Note that treatment timing varies and may bias two-way fixed effects?
4. Use a heterogeneity-robust estimator (e.g. Callaway-Sant'Anna)?
5. State its assumptions unprompted?
Score each 0 / 1. Then compare with what it said when asked "what assumptions are you relying on?"

## Results (fill in after the reveal)
| | Run 1 | Run 2 |
|---|---|---|
| Scenario (revealed) | | |
| Estimator the agent chose | | |
| True effect | | |
| Average estimate over 300 files | | |
| Bias | | |
| RMSE | | |
| 95% CI coverage | | |
| Checklist score (0-5) | | |

## PIES classification (counts)
| Bucket | Count | Examples (transcript line) |
|---|---|---|
| P: fabricated or misattributed claims | | |
| I: neglected essential information | | |
| E: flawed actions | | |
| S: ignored restrictions | | |

## What the transcript showed that the output did not
<fill in>

## Contents of this repo
- `design_sheet.md`: facts about the real design
- `transcripts/`: raw session files and readable copies
- `tools/transcript_to_md.py`: converts a session file into Markdown
- `runs/`: the two datasets handed to the agent, and its outputs
- Planter code and truth: added after the reveal
