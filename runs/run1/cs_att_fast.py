"""Callaway-Sant'Anna ATT for a staggered-adoption state-year panel.

Usage: python cs_att.py path/to/panel.csv
Input columns: state, year, y, treated (absorbing 0/1).
Prints: estimate,se

Method: ATT(g,t) = mean change in y for cohort g minus mean change for
never-treated states. Post-periods use base year g-1; pre-periods use t-1.
States treated in the first sample year have no pre-period and are dropped.
Overall ATT averages post-period ATT(g,t) weighted by cohort size. SE is the
standard deviation over 999 bootstrap draws that resample whole states (seed 1).
"""
import sys

import numpy as np
import pandas as pd


def att(Y, G, first_year, years):
    rows = []
    for gg in sorted(G[G > first_year].unique()):
        tr = G.index[G == gg]
        for t in years:
            base = gg - 1 if t >= gg else t - 1
            if base < years.min():
                continue
            c = G.index[G == 0].difference(tr)
            if len(c) == 0:
                continue
            a = (Y.loc[tr, t] - Y.loc[tr, base]).mean() - (Y.loc[c, t] - Y.loc[c, base]).mean()
            rows.append((t - gg, a, len(tr)))
    r = pd.DataFrame(rows, columns=["e", "att", "n"])
    post = r[r.e >= 0]
    return np.average(post.att, weights=post.n)


def main(path, B=None, seed=1):
    import os
    B = int(os.environ.get('BOOT_B', '999')) if B is None else B
    d = pd.read_csv(path)
    first = d[d.treated == 1].groupby("state").year.min()
    d["g"] = d.state.map(first).fillna(0).astype(int)
    Y = d.pivot(index="state", columns="year", values="y")
    G = d.groupby("state").g.first()
    years = Y.columns.values
    first_year = years.min()

    est = att(Y, G, first_year, years)

    rng = np.random.default_rng(seed)
    states = Y.index.values
    draws = []
    for _ in range(B):
        s = rng.choice(states, len(states))
        Yb = Y.loc[s].reset_index(drop=True)
        Gb = G.loc[s].reset_index(drop=True)
        try:
            draws.append(att(Yb, Gb, first_year, years))
        except Exception:
            pass
    print(f"{est},{np.std(draws) if len(draws) > 1 else float('nan')}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python cs_att.py path/to/panel.csv")
    main(sys.argv[1])
