#!/usr/bin/env python3
"""Apply an agent's estimator script to every dataset and save the results.

Usage:
  python run_all.py <estimator_script> <data_folder> <output_csv> [--limit N]

The estimator script must take a CSV path as its only argument and print
"estimate,se" on one line. Works with .py scripts (run with python) and
.R scripts (run with Rscript). Does NOT need or read any truth file.
"""
import sys, glob, os, subprocess, csv

def main():
    est, folder, out = sys.argv[1:4]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    runner = ["Rscript"] if est.lower().endswith(".r") else [sys.executable]
    files = sorted(glob.glob(os.path.join(folder, "*.csv")))[:limit]
    rows, failed = [], 0
    for i, f in enumerate(files, 1):
        fid = os.path.splitext(os.path.basename(f))[0]
        try:
            r = subprocess.run(runner + [est, f], capture_output=True, text=True, timeout=120)
            last = [l for l in r.stdout.strip().splitlines() if l.strip()][-1]
            e, s = [float(x) for x in last.split(",")[:2]]
            rows.append((fid, e, s))
        except Exception as ex:
            failed += 1
            rows.append((fid, "", ""))
            print(f"FAILED {fid}: {ex}", file=sys.stderr)
        if i % 50 == 0:
            print(f"{i}/{len(files)} done")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["id", "estimate", "se"]); w.writerows(rows)
    print(f"Wrote {out}: {len(rows)} rows, {failed} failed")

main()
