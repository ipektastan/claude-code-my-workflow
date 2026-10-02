#!/usr/bin/env python3
"""Score estimator results against the revealed truth.

  python score.py inspect truth.json
  python score.py where truth.json d_b51e d_e4fd          # which scenario are these files in?
  python score.py subset truth.json <data_dir> <out_dir> N  # copy N files per scenario for the bootstrap/coverage run
  python score.py score truth.json results.csv [label]     # bias, RMSE, coverage per scenario
"""
import sys, json, csv, shutil, math, os

def load(tp):
    t = json.load(open(tp))
    sc = t["scenarios"]
    ids = {}
    truth = {}
    for name, s in sc.items():
        for f in s["files"]:
            ids[f["id"]] = name
            truth[f["id"]] = f.get("true_att", s["true_att"])
    return t, sc, ids, truth

YEARS = range(1964, 1997)
RAMP_START, RAMP_END = 2, 19

def _ramp(k):
    return min(1.0, max(0.0, (k - RAMP_START) / (RAMP_END - RAMP_START)))

def estimands(t):
    """Per scenario: (true_att over all treated state-years, true effect averaged over adopters only).
    Recomputed from adoption_year_by_state, tau and the ramp used in gen_data.py."""
    out = {}
    for name, s in t["scenarios"].items():
        tau = s.get("tau", s.get("long_run_effect"))
        allv, adv = [], []
        for st, a in t["adoption_year_by_state"].items():
            if a == 2100:
                continue
            for yr in YEARS:
                if yr < a:
                    continue
                if a == 1900 or name == "X":
                    e = tau                      # always treated: at long-run level
                else:
                    e = tau * _ramp(yr - a)
                allv.append(e)
                if a != 1900:
                    adv.append(e)
        out[name] = (sum(allv) / len(allv), sum(adv) / len(adv))
    return out

def inspect(tp):
    t, sc, ids, truth = load(tp)
    est = estimands(t)
    for name, s in sc.items():
        print(name, {k: (v if k != "files" else f"{len(v)} files, first={v[0]}") for k, v in s.items()})
        print(f"   recomputed all-treated truth {est[name][0]:.4f} (file says {s['true_att']:.4f}); "
              f"adopters-only truth (what CS targets) {est[name][1]:.4f}")

def where(tp, *fids):
    t, sc, ids, truth = load(tp)
    for f in fids:
        print(f, "->", ids.get(f, "NOT FOUND"), "true_att", truth.get(f))

def subset(tp, data_dir, out_dir, n):
    t, sc, ids, truth = load(tp)
    os.makedirs(out_dir, exist_ok=True)
    cnt = {k: 0 for k in sc}
    for fid in sorted(ids):
        s = ids[fid]
        if cnt[s] < int(n):
            shutil.copy(os.path.join(data_dir, fid + ".csv"), out_dir)
            cnt[s] += 1
    print("copied", cnt, "to", out_dir)

def score(tp, rp, label=""):
    t, sc, ids, truth = load(tp)
    est_ad = estimands(t)
    by = {k: [] for k in sc}
    for r in csv.DictReader(open(rp)):
        if r["id"] not in ids or r["estimate"] == "":
            continue
        by[ids[r["id"]]].append((float(r["estimate"]), float(r["se"]) if r["se"] not in ("", "nan") else float("nan"), truth[r["id"]]))
    print(f"== {label or rp}")
    for name, rows in by.items():
        if not rows:
            continue
        n = len(rows)
        err = [e - tr for e, s, tr in rows]
        bias = sum(err) / n
        rmse = math.sqrt(sum(x * x for x in err) / n)
        sd = math.sqrt(sum((x - bias) ** 2 for x in err) / (n - 1)) if n > 1 else float("nan")
        mean_est = sum(e for e, s, tr in rows) / n
        tru = sum(tr for e, s, tr in rows) / n
        cov = [(abs(e - tr) <= 1.96 * s) for e, s, tr in rows if s == s]
        covs = f"{sum(cov)}/{len(cov)} = {sum(cov)/len(cov):.2f}" if cov else "n/a (no SEs)"
        tad = est_ad[name][1]
        bias_ad = mean_est - tad
        print(f"scenario {name} ({sc[name]['description']}): adopters-only truth={tad:.4f}  bias vs that={bias_ad:+.4f} ({100*bias_ad/abs(tad):+.0f}%)")
        print(f"   vs the file's true_att: n={n}  true={tru:.4f}  mean est={mean_est:.4f}  "
              f"bias={bias:+.4f} ({100*bias/abs(tru):+.0f}% of truth)  sd={sd:.4f}  RMSE={rmse:.4f}  coverage={covs}")

if __name__ == "__main__":
    cmd, args = sys.argv[1], sys.argv[2:]
    {"inspect": inspect, "where": where, "subset": subset, "score": score}[cmd](*args)
