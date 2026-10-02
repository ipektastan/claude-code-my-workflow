"""Simulate female suicide-rate panels (elasticity scale) copying design_sheet.md.

Scenario X: constant treatment effect.
Scenario Y: effect ~0 at adoption, growing with years since adoption to a long-run value.

Secrecy: the seed, effect sizes and every truth value go only to truth.json.
This script prints nothing derived from them.
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data"
N_SIMS = 300

# ---- Design (design_sheet.md sections 2-4) ----
YEARS = np.arange(1964, 1997)                 # 33 years
N_STATES = 51
N_ALWAYS, N_NEVER = 9, 5
ADOPT_COUNTS = {1969: 2, 1970: 2, 1971: 7, 1972: 3, 1973: 11, 1974: 3,
                1975: 2, 1976: 1, 1977: 3, 1980: 1, 1984: 1, 1985: 1}
SD_STATE = 0.27        # between-state SD of state means
SD_RESID = 0.195       # residual SD after state and year FE (stationary AR(1) SD)
RHO = 0.35             # within-state AR(1) correlation
# Year-effect SD is not given directly; back it out from total SD 0.35:
# 0.35^2 - 0.27^2 - 0.195^2 ~= 0.0116 -> about 0.10.
SD_YEAR = 0.10

# Effect path for Scenario Y (shape of Table I col 1f): ~0 for years 0-2 after
# adoption, then a linear ramp reaching the long-run value 19 years after adoption.
RAMP_START, RAMP_END = 2, 19


def ramp(k):
    """Share of the long-run effect reached k years after adoption (k >= 0)."""
    return np.clip((k - RAMP_START) / (RAMP_END - RAMP_START), 0.0, 1.0)


# ---- Seeding (secret) ----
seed_text = (ROOT / "secret_seed.txt").read_text(encoding="utf-8").strip()
master = int.from_bytes(hashlib.sha256(seed_text.encode("utf-8")).digest()[:8], "big")
ss_truth, ss_design, ss_ids, ss_sims = np.random.SeedSequence(master).spawn(4)

# ---- Adoption schedule: assign cohorts to state ids 1..51 (fixed for all datasets) ----
adopt = np.array([1900] * N_ALWAYS + [2100] * N_NEVER
                 + [y for y, n in ADOPT_COUNTS.items() for _ in range(n)])
assert len(adopt) == N_STATES
adopt = np.random.default_rng(ss_design).permutation(adopt)   # adopt[s-1] = year for state s

S, T = np.meshgrid(np.arange(1, N_STATES + 1), YEARS, indexing="ij")   # (51, 33)
A = adopt[S - 1]
treated = (T >= A).astype(int)
k = np.where(A == 1900, 10**6, T - A)          # always-treated -> at long-run effect
share_y = np.where(treated == 1, ramp(k), 0.0)

# ---- True effects (drawn, never printed) ----
rng_truth = np.random.default_rng(ss_truth)
ratio = share_y[treated == 1].mean()           # ATT_Y / long-run, fixed by the schedule
while True:
    lr_y = rng_truth.uniform(-0.30, -0.10)
    att_y = lr_y * ratio
    # Scenario X's constant effect must equal ATT_Y and lie in its stated range U(-0.20,-0.05).
    if -0.20 <= att_y <= -0.05:
        break
tau_x = att_y

eff = {"X": np.where(treated == 1, tau_x, 0.0), "Y": share_y * lr_y}
att = {sc: float(eff[sc][treated == 1].mean()) for sc in eff}   # computed from the DGP

# ---- File IDs (random-looking, unique, scenarios interleaved) ----
rng_ids = np.random.default_rng(ss_ids)
ids = set()
while len(ids) < 2 * N_SIMS:
    ids.add("d_" + "".join(rng_ids.choice(list("0123456789abcdef"), 4)))
ids = list(rng_ids.permutation(sorted(ids)))
id_map = {"X": ids[:N_SIMS], "Y": ids[N_SIMS:]}

# ---- Simulate ----
OUT.mkdir(exist_ok=True)
for old in OUT.glob("d_*.csv"):
    old.unlink()

sim_seeds = ss_sims.spawn(2 * N_SIMS)
innov_sd = SD_RESID * np.sqrt(1 - RHO**2)
datasets = {"X": [], "Y": []}
j = 0
for sc in ("X", "Y"):
    for i in range(N_SIMS):
        r = np.random.default_rng(sim_seeds[j])
        alpha = 1.0 + r.normal(0, SD_STATE, N_STATES)
        gamma = r.normal(0, SD_YEAR, len(YEARS))
        gamma -= gamma.mean()
        e = np.empty((N_STATES, len(YEARS)))
        e[:, 0] = r.normal(0, SD_RESID, N_STATES)           # stationary start
        for t in range(1, len(YEARS)):
            e[:, t] = RHO * e[:, t - 1] + r.normal(0, innov_sd, N_STATES)
        y = alpha[:, None] + gamma[None, :] + eff[sc] + e
        fid = id_map[sc][i]
        pd.DataFrame({"state": S.ravel(), "year": T.ravel(),
                      "y": np.round(y.ravel(), 6), "treated": treated.ravel()}
                     ).to_csv(OUT / f"{fid}.csv", index=False)
        datasets[sc].append({"id": fid, "seed_index": j})
        j += 1

truth = {
    "note": "Truth for the simulation exercise. Do not open until estimates are scored.",
    "scenarios": {
        "X": {"description": "constant effect", "tau": tau_x, "true_att": att["X"],
              "files": datasets["X"]},
        "Y": {"description": "effect grows with years since adoption",
              "long_run_effect": lr_y, "true_att": att["Y"],
              "effect_path": f"long_run * clip((k-{RAMP_START})/{RAMP_END - RAMP_START},0,1), "
                             "k = year - adoption year; always-treated at long_run",
              "event_time_effects": {str(kk): float(lr_y * ramp(kk)) for kk in range(0, 28)},
              "files": datasets["Y"]},
    },
    "adoption_year_by_state": {str(s): int(adopt[s - 1]) for s in range(1, N_STATES + 1)},
    "dgp": {"sd_state": SD_STATE, "sd_year": SD_YEAR, "sd_resid": SD_RESID, "rho": RHO,
            "state_mean": 1.0, "seeding": "sha256(secret_seed.txt) -> SeedSequence; "
            "spawn(4)=[truth, design, ids, sims]; sims spawned 600, X first then Y"},
}
(ROOT / "truth.json").write_text(json.dumps(truth, indent=2), encoding="utf-8")
print(f"Wrote {2 * N_SIMS} CSV files and truth.json.")
