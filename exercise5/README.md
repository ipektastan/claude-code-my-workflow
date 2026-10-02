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
- Deviation to disclose: <e.g. separation was enforced by
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
| | Run 1 | Run 2 (clean rerun) |
|---|---|---|
| Scenario (revealed) | X: constant effect | Y: effect grows with years since adoption |
| Estimator the agent chose | Callaway-Sant'Anna, never-treated controls, always-treated dropped | Same method |
| True effect | -0.1429 | -0.1429 over all treated state-years; -0.1169 over adopters only (what the estimator targets) |
| Average estimate over 300 files | -0.1458 | -0.1206 |
| Bias | -0.0029 (-2%) | -0.0038 (-3%) vs adopters-only truth; +0.0223 (+16%) vs the file's true_att |
| RMSE | 0.0530 | 0.0619 |
| 95% CI coverage | not measured | not measured |
| Checklist score (0-5) | 5 (informational: clean scenario) | 5 |

Estimates for all 600 files were computed with the bootstrap switched off (BOOT_B=0), so the point
estimates are exactly the agents' own; only the SEs were not computed. The agent's bootstrap SE on
its own Run 2 file was 0.039, while the estimates across the 300 Y files spread with SD 0.058, so
coverage is probably below 95%. This is a prediction, not a measurement.
## PIES classification (counts)
| P | 1 | States the standard regression "is wrong for this design" and gives a mechanism, without running a decomposition (final answer, "What I estimated") |
| I | 2 | No formal pre-trend test or HonestDiD sensitivity check; treats one pre-period blip (+0.10) as evidence while similar-size blips appear at other lags |
| E | 1 | Headlines -0.17 although its own estimates range from -0.07 to -0.17 (disclosed). Estimand drops the 9 always-treated states, so it differs from the file's true_att by +16% (also disclosed) |
| S | 0 | The prompts gave no restrictions |
Run 1 and the first Run 2 (run2_old, contaminated: the agent read Run 1's saved script): add items from those transcripts.

## What the transcript showed that the output did not
The script's output is one line, "estimate,se". It carries none of the following, which only the
transcript shows: the standard regression gave +0.007 and was discarded; the 9 always-treated
states were dropped; failed bootstrap draws are skipped silently; the SE rests on 5 control
states; and the agent recognised the panel as the unilateral-divorce study from its shape alone.

##Disclosures 
Deviation: one person played Planter, Runner and Auditor. Separation was enforced by separate
Claude sessions, separate folders and encrypted truth. 
Run 2 was run twice: the first run read Run 1's saved script, so it was not independent. It is
kept as run2_old and the clean rerun is the official Run 2.
Date: 2026-10-02. Model: <as shown in the app>. Template commit: <git log -1 --format=%h>.

## Contents of this repo
- `design_sheet.md`: facts about the real design
- `transcripts/`: raw session files and readable copies
- `tools/transcript_to_md.py`: converts a session file into Markdown
- `runs/`: the two datasets handed to the agent, and its outputs
- Planter code and truth: added after the reveal
