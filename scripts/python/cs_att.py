"""Callaway-Sant'Anna overall ATT for a staggered, absorbing binary treatment.

Usage: python cs_att.py path/to/panel.csv

Input columns: state, year, y, treated (0/1, never switches off).
Prints one line: estimate,se

Method (unchanged from the run2 analysis):
  - group g = first treated year; never-treated states are the control group
  - states treated in the first sample year have no pre-period and are not estimated
  - ATT(g,t) = mean change in y for cohort g minus mean change for never-treated,
    with base period g-1 for t >= g and t-1 for t < g (varying base)
  - overall ATT = cohort-size-weighted average of post-period ATT(g,t)
  - SE = std of 499 state-level (cluster) bootstrap draws, seed 1
"""
import sys

import numpy as np
import pandas as pd


def att_gt(W, G, years, first_year):
    out = []
    for g in sorted(G[(G > 0) & (G > first_year)].unique()):
        for t in years:
            base = g - 1 if t >= g else t - 1
            if base < first_year:
                continue
            tr = G.index[G == g]
            c = G.index[G == 0]
            c = c[c.isin(G.index[G != g])]
            if len(c) == 0:
                continue
            dy = W[t] - W[base]
            out.append((g, t, dy[tr].mean() - dy[c].mean(), len(tr)))
    return pd.DataFrame(out, columns=["g", "t", "att", "n"])


def overall(a):
    post = a[a.t >= a.g]
    return np.average(post.att, weights=post.n)


def main(path):
    d = pd.read_csv(path).sort_values(["state", "year"])
    first = d[d.treated == 1].groupby("state").year.min()
    d["g"] = d.state.map(first).fillna(0).astype(int)  # 0 = never treated
    first_year = d.year.min()
    years = sorted(d.year.unique())
    W = d.pivot(index="state", columns="year", values="y")
    G = d.groupby("state").g.first()

    est = overall(att_gt(W, G, years, first_year))

    rng = np.random.default_rng(1)
    states = W.index.values
    draws = []
    for _ in range(499):
        sm = rng.choice(states, len(states), replace=True)
        Wb = W.loc[sm].reset_index(drop=True)
        Gb = G.loc[sm].reset_index(drop=True)
        try:
            draws.append(overall(att_gt(Wb, Gb, years, first_year)))
        except Exception:
            pass
    se = np.std(draws)

    print(f"{est},{se}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python cs_att.py path/to/panel.csv")
    main(sys.argv[1])
