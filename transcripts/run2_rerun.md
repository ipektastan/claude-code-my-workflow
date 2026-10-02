# Transcript: run2_rerun.jsonl

## USER  2026-10-02T06:09:10.627Z

There is a state-year panel in runs/run2/d_e4fd.csv. y is a state suicide-rate index, treated is whether the state currently has a law change (it starts at different dates in different states), state and year are identifiers. Estimate the effect of treated on y. Tell me what you estimated, how you did it, and how much I should trust it.

**TOOL CALL**
```json
{
  "tool": "Bash",
  "input": {
    "command": "cd \"C:/Users/ipekt/Documents/econ_workshop/claude-code-my-workflow\"; ls runs runs/run2; head -5 runs/run2/d_e4fd.csv; wc -l runs/run2/d_e4fd.csv; which Rscript python python3; ls runs/run2/..",
    "description": "Inspect data file and available tools"
  }
}
```

**TOOL RESULT**
```
runs:
run2

runs/run2:
d_e4fd.csv
state,year,y,treated
1,1964,0.249539,1
1,1965,0.793481,1
1,1966,0.571233,1
1,1967,0.317805,1
1684 runs/run2/d_e4fd.csv
which: no Rscript in (/c/Users/ipekt/bin:/mingw64/bin:/usr/local/bin:/usr/bin:/bin:/mingw64/bin:/usr/bin:/c/Users/ipekt/bin:/c/Windows/system32:/c/Windows:/c/Windows/System32/Wbem:/c/Windows/System32/WindowsPowerShell/v1.0:/c/Windows/System32/OpenSSH:/c/Program Files/dotnet:/cmd:/c/Users/ipekt/anaconda3:/c/Users/ipekt/anaconda3/Library/mingw-w64/bin:/c/Users/ipekt/anaconda3/Library/usr/bin:/c/Users/ipekt/anaconda3/Library/bin:/c/Users/ipekt/anaconda3/Scripts:/c/Users/ipekt/AppData/Local/Microsoft/WindowsApps:/c/Users/ipekt/AppData/Local/Programs/Microsoft VS Code/bin:/mingw64/bin:/usr/bin/vendor_perl:/usr/bin/core_perl)
/c/Users/ipekt/anaconda3/python
/c/Users/ipekt/AppData/Local/Microsoft/WindowsApps/python3
run2
```

**TOOL CALL**
```json
{
  "tool": "Bash",
  "input": {
    "command": "cd \"C:/Users/ipekt/Documents/econ_workshop/claude-code-my-workflow\"; python -c \"\nimport pandas as pd\nd=pd.read_csv('runs/run2/d_e4fd.csv')\nprint(d.describe()); print(d.isna().sum())\nprint(d.state.nunique(), d.year.min(), d.year.max(), d.groupby('state').size().value_counts())\nprint(d.duplicated(['state','year']).sum())\nd=d.sort_values(['state','year'])\nsw=d.groupby('state').treated.apply(lambda s:(s.diff().fillna(0)!=0).sum())\nprint('switches per state', sw.value_counts())\nprint('off-switches', (d.groupby('state').treated.diff()==-1).sum())\nfirst=d[d.treated==1].groupby('state').year.min()\nprint('cohorts'); print(first.value_counts().sort_index())\nprint('never treated', d.state.nunique()-len(first))\n\"; python -c \"import linearmodels, statsmodels; print('ok')\"; pip list 2>/dev/null | grep -i -E \"differences|csdid|pyfixest|linearmodels|statsmodels\"",
    "description": "Describe panel structure and treatment timing"
  }
}
```

**TOOL RESULT**
```
             state         year            y      treated
count  1683.000000  1683.000000  1683.000000  1683.000000
mean     26.000000  1980.000000     0.857703     0.691622
std      14.723976     9.524735     0.383153     0.461961
min       1.000000  1964.000000    -0.413902     0.000000
25%      13.000000  1972.000000     0.609513     0.000000
50%      26.000000  1980.000000     0.872888     1.000000
75%      39.000000  1988.000000     1.128592     1.000000
max      51.000000  1996.000000     2.013493     1.000000
state      0
year       0
y          0
treated    0
dtype: int64
51 1964 1996 33    51
Name: count, dtype: int64
0
switches per state treated
1    37
0    14
Name: count, dtype: int64
off-switches 0
cohorts
year
1964     9
1969     2
1970     2
1971     7
1972     3
1973    11
1974     3
1975     2
1976     1
1977     3
1980     1
1984     1
1985     1
Name: count, dtype: int64
never treated 5
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import linearmodels, statsmodels; print('ok')
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'linearmodels'
pyfixest                          0.60.0
statsmodels                       0.14.5
```

**TOOL CALL**
```json
{
  "tool": "Bash",
  "input": {
    "command": "mkdir -p \"C:/Users/ipekt/AppData/Local/Temp/claude/C--Users-ipekt-Documents-econ-workshop-claude-code-my-workflow/d9bb33ac-14f2-4d7d-8e8d-c1e0dc059266/scratchpad\"; cd \"$_\"; cat > did.py <<'EOF'\nimport pandas as pd, numpy as np, pyfixest as pf, warnings\nwarnings.filterwarnings('ignore')\nd=pd.read_csv(r'C:/Users/ipekt/Documents/econ_workshop/claude-code-my-workflow/runs/run2/d_e4fd.csv').sort_values(['state','year'])\nfirst=d[d.treated==1].groupby('state').year.min()\nd['g']=d.state.map(first).fillna(0).astype(int)   # 0 = never treated\nY0=d.year.min()\n# 1. TWFE\nm=pf.feols('y ~ treated | state + year', d, vcov={'CRV1':'state'})\nprint('TWFE all states:', m.coef().values, m.se().values)\ndn=d[d.g!=Y0]\nm2=pf.feols('y ~ treated | state + year', dn, vcov={'CRV1':'state'})\nprint('TWFE drop always-treated:', m2.coef().values, m2.se().values)\n\n# 2. Callaway-Sant'Anna (no covariates), long differences vs base g-1\nW=d.pivot(index='state',columns='year',values='y'); G=d.groupby('state').g.first()\nyears=sorted(d.year.unique())\ndef attgt(W,G,ctrl):\n    out=[]\n    for g in sorted(G[(G>0)&(G>Y0)].unique()):\n        for t in years:\n            base=g-1 if t>=g else t-1   # varying base pre-period (CS default)\n            if base<Y0: continue\n            tr=G.index[G==g]\n            if ctrl=='never': c=G.index[G==0]\n            else: c=G.index[(G==0)|(G>max(t,base))]\n            c=c[c.isin(G.index[G!=g])]\n            if len(c)==0: continue\n            dy=W[t]-W[base]\n            out.append((g,t,dy[tr].mean()-dy[c].mean(),len(tr)))\n    return pd.DataFrame(out,columns=['g','t','att','n'])\ndef agg(a):\n    post=a[a.t>=a.g]; simple=np.average(post.att,weights=post.n)\n    a=a.assign(e=a.t-a.g)\n    es=a.groupby('e').apply(lambda x: np.average(x.att,weights=x.n))\n    return simple, es\nrng=np.random.default_rng(1)\nfor ctrl in ['never','notyet']:\n    a=attgt(W,G,ctrl); s,es=agg(a)\n    bs=[];bes=[]\n    states=W.index.values\n    for b in range(499):\n        sm=rng.choice(states,len(states),replace=True)\n        Wb=W.loc[sm].reset_index(drop=True); Gb=G.loc[sm].reset_index(drop=True)\n        try:\n            ab=attgt(Wb,Gb,ctrl); sb,esb=agg(ab); bs.append(sb); bes.append(esb)\n        except Exception: pass\n    bes=pd.DataFrame(bes)\n    print(f'\\nCS ({ctrl}-treated controls): overall ATT={s:.4f}  bootSE={np.std(bs):.4f}  95%CI=({np.percentile(bs,2.5):.4f},{np.percentile(bs,97.5):.4f})')\n    tab=pd.DataFrame({'att':es,'se':bes.std()}).loc[-10:20]\n    print(tab.round(3).to_string())\n    pre=a[a.t<a.g]; print('pre-period placebo avg:',round(np.average(pre.att,weights=pre.n),4))\nEOF\npython did.py",
    "description": "Run TWFE and Callaway-Sant'Anna estimators",
    "timeout": 600000
  }
}
```

**TOOL RESULT**
```
TWFE all states: [0.00660369] [0.02340833]
TWFE drop always-treated: [0.04061678] [0.03176167]

CS (never-treated controls): overall ATT=-0.1724  bootSE=0.0391  95%CI=(-0.2480,-0.0977)
       att     se
e                
-10 -0.023  0.061
-9  -0.014  0.083
-8   0.084  0.075
-7  -0.105  0.071
-6  -0.070  0.048
-5  -0.002  0.053
-4   0.030  0.044
-3   0.031  0.047
-2  -0.009  0.042
-1   0.099  0.046
 0   0.008  0.050
 1   0.056  0.048
 2  -0.038  0.059
 3   0.019  0.057
 4  -0.043  0.068
 5  -0.032  0.067
 6  -0.032  0.070
 7  -0.026  0.077
 8  -0.091  0.059
 9  -0.123  0.049
 10 -0.112  0.058
 11 -0.213  0.058
 12 -0.231  0.068
 13 -0.208  0.059
 14 -0.159  0.052
 15 -0.231  0.063
 16 -0.253  0.048
 17 -0.326  0.061
 18 -0.367  0.086
 19 -0.374  0.077
 20 -0.411  0.079
pre-period placebo avg: 0.0042

CS (notyet-treated controls): overall ATT=-0.1730  bootSE=0.0384  95%CI=(-0.2519,-0.0987)
       att     se
e                
-10 -0.019  0.055
-9  -0.000  0.103
-8   0.120  0.050
-7  -0.072  0.067
-6  -0.098  0.041
-5  -0.010  0.051
-4   0.016  0.046
-3   0.008  0.041
-2  -0.010  0.045
-1   0.089  0.047
 0  -0.005  0.037
 1   0.039  0.050
 2  -0.021  0.045
 3   0.005  0.050
 4  -0.045  0.055
 5  -0.029  0.062
 6  -0.047  0.067
 7  -0.055  0.071
 8  -0.093  0.059
 9  -0.115  0.052
 10 -0.098  0.057
 11 -0.200  0.055
 12 -0.219  0.071
 13 -0.206  0.062
 14 -0.153  0.064
 15 -0.229  0.066
 16 -0.253  0.051
 17 -0.3
... [shortened, 1598 characters in total]
```

**TOOL CALL**
```json
{
  "tool": "Bash",
  "input": {
    "command": "cd \"C:/Users/ipekt/AppData/Local/Temp/claude/C--Users-ipekt-Documents-econ-workshop-claude-code-my-workflow/d9bb33ac-14f2-4d7d-8e8d-c1e0dc059266/scratchpad\"; cat > extra.py <<'EOF'\nexec(open('did.py').read().split('# 2.')[0])\nexec('# 2.'+open('did.py').read().split('# 2.')[1].split('rng=')[0])\na=attgt(W,G,'never').assign(e=lambda x:x.t-x.g)\n# balanced: cohorts observed for e in 0..12\ngs=a[a.e==12].g.unique(); b=a[a.g.isin(gs)&(a.e.between(0,12))]\nprint('balanced cohorts',gs, 'n states',G[G.isin(gs)].size)\nprint('balanced e0-12 avg ATT', b.groupby('e').apply(lambda x:np.average(x.att,weights=x.n)).mean().round(4))\npost=a[a.e>=0]; print('dynamic (equal weight e=0..20):', post[post.e<=20].groupby('e').apply(lambda x:np.average(x.att,weights=x.n)).mean().round(4))\n# Sun-Abraham style via interaction-weighted: saturated cohort x rel-time with never-treated as control\ndn=d[d.g!=Y0].copy()\nfit=pf.event_study(data=dn,yname='y',idname='state',tname='year',gname='g',estimator='twfe') if False else None\n# simple dynamic TWFE (binned) to show contrast\ndn['e']=np.where(dn.g>0,(dn.year-dn.g).clip(-10,20),-1000)\nr=pf.feols('y ~ i(e, ref=-1) | state + year', dn[dn.e!=-1000].pipe(lambda x:x) if False else dn.assign(e=dn.e.replace(-1000,-1)), vcov={'CRV1':'state'})\nprint(r.tidy().iloc[[10,15,20,25,29]][['Estimate','Std. Error']].round(3))\n# Did2s (Gardner) via pyfixest\ntry:\n    from pyfixest.did.estimation import did2s\n    g2=did2s(dn.assign(treat=dn.treated.astype(bool)),yname='y',first_stage='~0|state+year',second_stage='~treat',treatment='treat',cluster='state')\n    print('did2s:',g2.coef().values,g2.se().values)\nexcept Exception as ex: print('did2s err',ex)\nEOF\npython extra.py",
    "description": "Robustness: balanced cohorts, dynamic TWFE, did2s",
    "timeout": 300000
  }
}
```

**TOOL RESULT**
```
TWFE all states: [0.00660369] [0.02340833]
TWFE drop always-treated: [0.04061678] [0.03176167]
balanced cohorts [1969 1970 1971 1972 1973 1974 1975 1976 1977 1980 1984] n states 36
balanced e0-12 avg ATT -0.0696
dynamic (equal weight e=0..20): -0.1518
             Estimate  Std. Error
Coefficient                      
e::1            0.045       0.043
e::6           -0.027       0.050
e::11          -0.199       0.051
e::16          -0.207       0.051
e::20          -0.281       0.050
did2s: [-0.07160538] [0.02489125]
```

## ASSISTANT  2026-10-02T06:13:06.915Z

The law change lowers y. My headline estimate is an average effect of about **−0.17 (SE 0.04, 95% CI −0.25 to −0.10)**, and it grows over time. The simple regression most people would run first says **+0.01 (SE 0.02)**, and that number is wrong for this design.

## The data
- 51 states observed every year from 1964 to 1996, with no missing values.
- Once a state turns `treated` on, it never turns it off.
- 37 states adopt in 13 different years between 1969 and 1985.
- 9 states are already treated in 1964, the first year. With no before-period, they can't tell us anything about the effect, so they drop out of the modern estimators.
- 5 states are never treated.

## What I estimated

| Method | Estimate | SE |
|---|---|---|
| Standard regression with state and year fixed effects (TWFE), all states | +0.007 | 0.023 |
| Same, dropping the 9 always-treated states | +0.041 | 0.032 |
| **Callaway–Sant'Anna, never-treated states as controls** | **−0.172** | 0.039 |
| Callaway–Sant'Anna, not-yet-treated states as controls | −0.173 | 0.038 |
| Gardner two-stage method (each state-year weighted equally) | −0.072 | 0.025 |
| Average of years 0–12 after adoption, only for states observed that long | −0.070 | — |

- **Why the standard regression fails here:** states adopt at different times and the effect grows after adoption. The regression then uses early adopters, whose y is still falling, as the comparison group for late adopters. That pushes the estimate toward zero, and here it even makes it slightly positive.
- **Callaway–Sant'Anna:** it compares each adopting group with clean controls only, then averages those comparisons. Standard errors come from a 499-draw bootstrap that resamples whole states. I coded it by hand in Python because R isn't installed here.
- **Year by year:** the effect is about zero for roughly 7 years after adoption. It then becomes clearly negative: about −0.11 at year 10, −0.25 at year 16 and −0.41 at year 20. The dynamic regression gives the same pattern.

## How much to trust it
1. **The direction (negative, delayed, growing): fairly confident.** Every method that handles staggered timing gives a negative number. Both choices of control group agree, and the year-by-year pattern is consistent.
2. **The exact size: much less confident.** Depending on how the year-by-year effects are averaged, you get anything from −0.07 to −0.17. The −0.17 leans on the long-run years, so it depends on which question you are asking:
   - Average effect over 12 years: about −0.07.
   - Long-run effect: −0.2 to −0.4.
3. **The long-run years rest on a small comparison group.** Effects 15 or more years out come mainly from the 1969–1973 adopters compared against only the 5 never-treated states. Something unusual in those 5 states would carry straight into the long-run numbers.
4. **Before adoption, the treated and control states mostly move together.** The pre-adoption estimates average 0.004 and are individually noisy. The exception is the year right before adoption: +0.10 (SE 0.05). That could be states adopting after an unusual year, or it could be noise. It slightly weakens the assumption that the two groups would have kept moving together without the law. I haven't run a formal sensitivity test for this.
5. **The 9 always-treated states are left out entirely**, so the result describes states that adopted between 1969 and 1985.
6. **Not done:**
   - There are no covariates, so the estimates assume the trends would have matched without any adjustment.
   - There's no adjustment for multiple testing across the year-by-year estimates.
   - I don't know what units y is in; it takes negative values, so it isn't a raw suicide rate.

The setup looks like the classic unilateral-divorce and suicide panel. If so, don't compare these magnitudes to published ones until you know how y was built.

The scripts are in my scratchpad, not the repo (`did.py` and `extra.py`). If you want this kept, I can save them as a numbered script under `scripts/` that writes its tables to `output/`.

## USER  2026-10-02T06:13:50.508Z

Save your final estimator as a script that takes a CSV path as an argument and prints estimate,se for the treatment effect. Don't change the method.

**TOOL CALL**
```json
{
  "tool": "Bash",
  "input": {
    "command": "cd \"C:/Users/ipekt/Documents/econ_workshop/claude-code-my-workflow\"; ls scripts | head -50; ls scripts/python 2>/dev/null",
    "description": "List scripts folder layout"
  }
}
```

**TOOL RESULT**
```
Exit code 2
R
backtest.sh
check-derived-counts.py
check-ledger-coverage.py
check-links.py
check-model-versions.sh
check-palette-sync.py
check-palette-sync.sh
check-repo-hygiene.py
check-skill-integrity.py
check-spec-conformance.py
check-staleness.py
check-surface-sync.py
check-surface-sync.sh
check-tikz-prevention.py
file-issue.py
hook-battery.sh
install-hooks.sh
nightly-repro-check.sh
quality_score.py
run-skill-eval.sh
slide-qa.py
stamp-render.sh
sync_to_docs.sh
transcript_to_md.py
validate-findings.py
validate-setup.sh
```

**TOOL CALL**
```json
{
  "tool": "Write",
  "input": {
    "file_path": "C:\\Users\\ipekt\\Documents\\econ_workshop\\claude-code-my-workflow\\scripts\\python\\cs_att.py",
    "content": "\"\"\"Callaway-Sant'Anna overall ATT for a staggered, absorbing binary treatment.\n\nUsage: python cs_att.py path/to/panel.csv\n\nInput columns: state, year, y, treated (0/1, never switches off).\nPrints one line: estimate,se\n\nMethod (unchanged from the run2 analysis):\n  - group g = first treated year; never-treated states are the control group\n  - states treated in the first sample year have no pre-period and are not estimated\n  - ATT(g,t) = mean change in y for cohort g minus mean change for never-treated,\n    with base period g-1 for t >= g and t-1 for t < g (varying base)\n  - overall ATT = cohort-size-weighted average of post-period ATT(g,t)\n  - SE = std of 499 state-level (cluster) bootstrap draws, seed 1\n\"\"\"\nimport sys\n\nimport numpy as np\nimport pandas as pd\n\n\ndef att_gt(W, G, years, first_year):\n    out = []\n    for g in sorted(G[(G > 0) & (G > first_year)].unique()):\n        for t in years:\n            base = g - 1 if t >= g else t - 1\n            if base < first_year:\n                continue\n            tr = G.index[G == g]\n            c = G.index[G == 0]\n            c = c[c.isin(G.index[G != g])]\n            if len(c) == 0:\n                continue\n            dy = W[t] - W[base]\n            out.append((g, t, dy[tr].mean() - dy[c].mean(), len(tr)))\n    return pd.DataFrame(out, columns=[\"g\", \"t\", \"att\", \"n\"])\n\n\ndef overall(a):\n    post = a[a.t >= a.g]\n    return np.average(post.att, weights=post.n)\n\n\ndef main(path):\n    d = pd.read_csv(path).sort_values([\"state\", \"year\"])\n    first = d[d.treated == 1].groupby(\"state\").year.min()\n    d[\"g\"] = d.state.map(first).fillna(0).astype(int)  # 0 = never treated\n    first_year = d.year.min()\n    years = sorted(d.year.unique())\n    W = d.pivot(index=\"state\", columns=\"year\", values=\"y\")\n    G = d.groupby(\"state\").g.first()\n\n    est = overall(att_gt(W, G, years, first_year))\n\n    rng = np.random.default_rng(1)\n    states = W.index.values\n    draws = []\n    for _ in range(499):\n        sm = rng.choice(states, len(states), replace=True)\n        Wb = W.loc[sm].reset_index(drop=True)\n        Gb = G.loc[sm].reset_index(drop=True)\n        try:\n            draws.append(overall(att_gt(Wb, Gb, years, first_year)))\n        except Exception:\n            pass\n    se = np.std(draws)\n\n    print(f\"{est},{se}\")\n\n\nif __name__ == \"__main__\":\n    if len(sys.argv) != 2:\n        sys.exit(\"usage: python cs_att.py path/to/panel.csv\")\n    main(sys.argv[1])\n"
  }
}
```

**TOOL RESULT**
```
File created successfully at: C:\Users\ipekt\Documents\econ_workshop\claude-code-my-workflow\scripts\python\cs_att.py (file state is current in your context — no need to Read it back)
```

**TOOL CALL**
```json
{
  "tool": "Bash",
  "input": {
    "command": "cd \"C:/Users/ipekt/Documents/econ_workshop/claude-code-my-workflow\"; python scripts/python/cs_att.py runs/run2/d_e4fd.csv; python scripts/python/cs_att.py; echo \"exit $?\"",
    "description": "Verify script reproduces earlier estimate",
    "timeout": 300000
  }
}
```

**TOOL RESULT**
```
-0.17242852525951557,0.03912622300447692
usage: python cs_att.py path/to/panel.csv
exit 1
```

## ASSISTANT  2026-10-02T06:15:28.150Z

I saved the estimator as [scripts/python/cs_att.py](scripts/python/cs_att.py). Run on your panel, it prints the same numbers as before: `-0.17242852525951557,0.03912622300447692` (estimate, SE).

```bash
python scripts/python/cs_att.py runs/run2/d_e4fd.csv
```

The method is the one behind my headline number: Callaway–Sant'Anna with never-treated states as controls, averaged over every post-adoption year (weighted by group size). The SE comes from 499 bootstrap draws that resample whole states, with seed 1. Run with no argument, it prints a usage line and exits with code 1.

- **Inputs it expects:** the CSV must have the columns `state`, `year`, `y` and `treated`, and treatment must never switch off once on. It needs at least one never-treated state.
- **Silently dropped draws:** a bootstrap draw that fails to compute is skipped without warning, as in the analysis, so on a panel with very few never-treated states the SE could rest on fewer than 499 draws.

I haven't committed it.

## USER  2026-10-02T06:15:36.724Z

What assumptions is your estimate relying on? List them.

## ASSISTANT  2026-10-02T06:15:54.267Z

The −0.17 rests on the assumptions below. Four of them can't be tested; the rest I either checked or took on faith.

## Identifying assumptions (none can be tested directly)
1. **Parallel trends against the never-treated states.** Had they never adopted, each adopting group's y would have moved like the average of the 5 never-treated states, in every year after adoption, out to 20+ years. This assumption carries the whole estimate.
   - It holds with no covariates. Nothing adjusts for differences between states, such as region or economic conditions.
   - It holds for y as measured. If parallel trends holds for the log of y or some other version, it generally fails for y itself.
   - The long-run effects rely on it over very long stretches, using only those 5 states as controls.
2. **No anticipation.** The law has no effect before it starts, in particular not in the year just before adoption, which every comparison uses as its baseline. The +0.10 (SE 0.05) estimate for that year is the one piece of evidence against this. If it reflects anticipation or adoption after an unusual year, the estimate is biased.
3. **No spillovers between states.** One state's law doesn't change y in other states, including the never-treated ones. Movement of people across state lines or regional effects would break this.
4. **Nothing else changes at adoption.** No other policy or shock starts in the same years as the law in adopting states. If one did, its effect gets attributed to the law.

## Assumptions about the data
5. **`treated` correctly marks when the law starts.** I take the first year with `treated = 1` as the adoption year. For the 9 states already treated in 1964, the true adoption year is unknown, which is why they are dropped.
6. **Treatment never switches off.** Checked: no state goes from treated back to untreated.
7. **Complete panel with consistent measurement.** Checked: every state appears in every year, with no gaps. I assume y is measured the same way across states and years.

## What the number means
8. **It's an average for 1969–1985 adopters only,** not for every state or every possible adoption year.
9. **The averaging leans on early adopters.** Each group counts once per post-adoption year, scaled by its number of states. Early adopters have the most post-adoption years, so they dominate, along with the long-run years where the effect is largest. A different average that is just as reasonable gives about −0.07. The −0.17 is not "the" effect, and it isn't constant over time.

## Assumptions behind the standard error
10. **States are independent of each other.** Within a state, years can be correlated in any way; the bootstrap resamples whole states, which allows for this.
11. **The bootstrap works with this few controls.** With only 5 never-treated states, it is shaky. Some resampled datasets will contain few or none of them, and any draw that fails to compute is dropped without warning. The true uncertainty is probably larger than SE 0.039 suggests.

The ones most likely to fail here are 1, 2 and 11. Assumption 1 is the whole identification, with no covariates and only 5 controls for the long-run years. Assumption 2 has the year-before-adoption blip against it. Assumption 11 bears directly on the SE.
