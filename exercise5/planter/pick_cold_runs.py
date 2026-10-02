"""Write cold_runs.txt: one file ID per scenario, random order, no labels. Prints nothing."""
import json
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent
truth = json.loads((ROOT / "truth.json").read_text(encoding="utf-8"))
rng = secrets.SystemRandom()
picks = [rng.choice(truth["scenarios"][sc]["files"])["id"] for sc in ("X", "Y")]
rng.shuffle(picks)
assert all((ROOT / "data" / f"{p}.csv").exists() for p in picks)
(ROOT / "cold_runs.txt").write_text("\n".join(picks) + "\n", encoding="utf-8")
