#!/usr/bin/env python3
"""Make a copy of an agent's estimator whose bootstrap size B can be set by the
environment variable BOOT_B (default 999 = unchanged behaviour).
With BOOT_B=0 the copy prints the point estimate and 'nan' for the SE.
Only the number of bootstrap draws changes; the estimator is untouched.

Usage: python make_fast.py original.py fast_copy.py
"""
import sys, re

src = open(sys.argv[1], encoding="utf-8").read()
n = 0
src, k = re.subn(r"def main\(path, B=999, seed=1\):",
                 "def main(path, B=None, seed=1):\n    import os\n    B = int(os.environ.get('BOOT_B', '999')) if B is None else B", src)
n += k
src, k = re.subn(r'print\(f"\{est\},\{np\.std\(draws\)\}"\)',
                 'print(f"{est},{np.std(draws) if len(draws) > 1 else float(\'nan\')}")', src)
n += k
if n != 2:
    sys.exit(f"Did not find the expected lines (patched {n} of 2). Not writing {sys.argv[2]}; ask for help.")
open(sys.argv[2], "w", encoding="utf-8").write(src)
print("wrote", sys.argv[2])
