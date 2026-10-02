"""Design checks on the simulated CSVs only (never reads truth.json)."""
from pathlib import Path

import pandas as pd

files = sorted((Path(__file__).resolve().parent / "data").glob("d_*.csv"))
print("files:", len(files))
cols = {tuple(pd.read_csv(f, nrows=0).columns) for f in files}
print("column sets:", cols)

df = pd.concat((pd.read_csv(f) for f in files), keys=range(len(files)), names=["file"])
print("rows per file:", sorted(df.groupby(level="file").size().unique()),
      "| states:", df.state.nunique(), "| years:", df.year.min(), "-", df.year.max())

print("\ny pooled over all files:")
print(df.y.describe().round(3).to_string())
per = df.groupby(level="file")
print("\nper-file averages: mean %.3f, SD %.3f, SD of state means %.3f" % (
    per.y.mean().mean(), per.y.std().mean(),
    per.apply(lambda d: d.groupby("state").y.mean().std()).mean()))

share = df.groupby("year").treated.mean()
assert (df.groupby(["year", "state"]).treated.nunique() == 1).all()  # same schedule everywhere
print("\nshare of states treated by year:")
print(share.round(3).to_string())
