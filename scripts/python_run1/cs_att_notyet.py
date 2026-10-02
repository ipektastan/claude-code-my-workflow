"""Callaway-Sant'Anna ATT with not-yet-treated controls, staggered state-year panel.

Usage: python cs_att_notyet.py path/to/panel.csv
Input columns: state, year, y, treated (absorbing 0/1, balanced panel).
Prints: estimate,se

Method: ATT(g,t) = mean change in y for cohort g minus mean change for states
that are never treated or not yet treated by max(t, base). Post-periods use base
year g-1; pre-periods use t-1. States treated in the first sample year have no
pre-period and are dropped. Overall ATT averages post-period ATT(g,t) weighted by
cohort size. SE is the standard deviation over 999 bootstrap draws that resample
whole states (seed 1); draws containing no never-treated state are skipped.
"""
import sys

import numpy as np
import pandas as pd


def att(Y, G, years):
    y0 = years.min()
    rows = []
    for gg in sorted(G[G > y0].unique()):
        tr = np.where(G.values == gg)[0]
        for t in years:
            base = gg - 1 if t >= gg else t - 1
            if base < y0:
                continue
            c = np.where((G.values == 0) | (G.values > max(t, base)))[0]
            if len(c) == 0:
                continue
            Yt = Y[t].values
            Yb = Y[base].values
            a = (Yt[tr] - Yb[tr]).mean() - (Yt[c] - Yb[c]).mean()
            rows.append((t - gg, a, len(tr)))
    r = pd.DataFrame(rows, columns=["e", "att", "n"])
    post = r[r.e >= 0]
    return np.average(post.att, weights=post.n)


def main(path, B=999, seed=1):
    d = pd.read_csv(path)
    first = d[d.treated == 1].groupby("state").year.min()
    d["g"] = d.state.map(first).fillna(0).astype(int)
    Y = d.pivot(index="state", columns="year", values="y")
    G = d.groupby("state").g.first()
    years = Y.columns.values

    est = att(Y, G, years)

    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(B):
        s = rng.choice(len(Y), len(Y))
        Yb = Y.iloc[s].reset_index(drop=True)
        Gb = G.iloc[s].reset_index(drop=True)
        if (Gb == 0).sum() == 0:
            continue
        draws.append(att(Yb, Gb, years))
    print(f"{est},{np.std(draws)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python cs_att_notyet.py path/to/panel.csv")
    main(sys.argv[1])
