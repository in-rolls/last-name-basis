"""Where a surname works, state by state.

Analyses 01 and 05 report one national number and its split by caste. Neither
says *where* the name works, and the range across states is far wider than the
national figure suggests.

Everything comes from the same source as analysis 01 -- outkast's SECC extract,
`state x birth_year x surname -> n_sc, n_st, n_other`, adults only, cells with
at least 100 records -- pooled to one row per (state, surname).

Two things about that extract govern how these numbers may be read, so they are
computed here rather than left to the note:

`covered_share`  what fraction of the state's Census 2011 population the
                 retained surnames account for. It runs from 3% to 19%, so
                 every per-state result describes surnames that cleared a
                 disclosure floor, not a state.

`removed_top25`  the same score with every state cut to its 25 commonest
                 names. The floor keeps common names, and this repo's own
                 finding is that common names are the uninformative ones, so a
                 state retaining few names could look uninformative by
                 construction. This holds that constant.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
A01 = HERE.parent / "01_surname_to_category"
TOP_N = 25


def _secc():
    """Analysis 01's loader, imported without colliding with this data.py."""
    spec = importlib.util.spec_from_file_location("a01_data", A01 / "data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load() -> pd.DataFrame:
    """One row per (state, surname), birth-year cells pooled."""
    secc = _secc()
    cells = secc.load_cells()
    per = cells.groupby(["state", "last_name"], as_index=False)[secc.COUNT_COLS].sum()
    per.attrs["count_cols"] = secc.COUNT_COLS
    per.attrs["categories"] = secc.CATEGORIES
    return per


def census_population() -> pd.Series:
    return _secc().census_population()


def score(counts: np.ndarray) -> dict:
    """Blind and with-name error for one state, and the share of the gap closed.

    The guess is each surname's argmax category. Leave-one-out is deliberately
    absent: every cell here holds at least 100 records, so removing one person
    cannot flip an argmax, and a LOO column would be identical to this one.
    """
    total = counts.sum()
    if total <= 0:
        return {"blind": 0.0, "with_name": 0.0, "removed": 0.0}
    prior = counts.sum(axis=0)
    blind = 100 * (1 - prior.max() / total)
    with_name = 100 * (1 - counts.max(axis=1).sum() / total)
    return {
        "blind": float(blind),
        "with_name": float(with_name),
        "removed": float(100 * (blind - with_name) / blind) if blind > 0 else 0.0,
    }


def state_table(per: pd.DataFrame, min_names: int = TOP_N) -> pd.DataFrame:
    """Per-state scores, with the coverage and the top-25 control beside them."""
    cols = per.attrs["count_cols"]
    pop = census_population()
    rows = []
    for state, d in per.groupby("state"):
        n = d[cols].to_numpy(float)
        if len(d) < min_names:
            continue
        totals = n.sum(axis=1)
        top = d.assign(_t=totals).nlargest(min_names, "_t")[cols].to_numpy(float)
        row = {"state": state, "names": len(d), "people": float(n.sum())}
        row.update(score(n))
        row["removed_top25"] = score(top)["removed"]
        row["sc_share_of_extract"] = float(100 * n[:, 0].sum() / n.sum())
        census = pop.get(state, np.nan)
        row["census_population"] = float(census)
        row["covered_share"] = float(100 * n.sum() / census) if census else np.nan
        rows.append(row)
    return pd.DataFrame(rows).sort_values("removed", ascending=False)


def decisive_names(per: pd.DataFrame, state: str, k: int = 3) -> pd.DataFrame:
    """The surnames that actually carry a state's signal.

    Not a count of Dalit-pointing names -- that misleads. Punjab has five in its
    top 25 and closes 3% of the gap; Assam has two and closes 65%, because one
    of them is `das`. What matters is how many people a decisive name covers.
    """
    cols = per.attrs["count_cols"]
    d = per[per["state"] == state].copy()
    n = d[cols].to_numpy(float)
    d["people"] = n.sum(axis=1)
    d["p_sc"] = n[:, 0] / d["people"]
    d["points_sc"] = n.argmax(axis=1) == 0
    d["share_of_extract"] = 100 * d["people"] / d["people"].sum()
    out = d[d["points_sc"]].nlargest(k, "people")
    return out[["last_name", "people", "p_sc", "share_of_extract"]].reset_index(
        drop=True
    )


def github_dir() -> Path:
    return Path(os.environ.get("GITHUB_DIR", Path.home() / "Documents/GitHub"))
