"""Does the village premium travel outside Bihar?

Bihar's land records give this repo its strongest single result: across 141
jatis a surname alone leaves 47 mistakes per 100 and a surname plus a village
leaves 17. Nothing established whether that 30-point collapse is a fact about
surnames and villages or a fact about Bihar.

The Odisha Record of Rights carries a jati and a village for every tenant, so it
can answer the same question with the same protocol. Two limits govern how far
the answer travels, and both are printed beside every number rather than left to
a footnote:

**This is one district, not a state.** The scrape has reached district 24,
Gajapati, and no further. Gajapati is small, heavily Adivasi and on the Andhra
border; its castes are not Odisha's. Nothing here may be labelled "Odisha".

**Each village is a sample.** The fetch caps khatiyans per village, and the cap
has changed between runs, so villages accumulate rather than being censused. The
realised distribution is measured from the data rather than assumed from a
command line, because a constant written here goes stale the moment the scrape
is restarted with a different flag. Village cells are small either way, so
leave-one-out is not optional.

The surname is the **last** token, which is measured rather than assumed. A
token appearing in both a tenant's name and their father's or husband's is an
inherited one, and in Gajapati that token is last 80% of the time, first 11%.
Maharashtra fails the same test in the other direction (analysis 04), so the
test is run per state and never carried over.
"""

from __future__ import annotations

import gzip
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TENANTS = HERE / "out/tab/tenants.parquet"
DISTRICT = "Gajapati"

_SPACE = re.compile(r"\s+")


def normalise(value: str) -> str:
    """Strip, collapse whitespace, drop a parenthesised gloss.

    The parser keeps glosses like `କୈବର୍ତ୍ତ (ମାଛଧରା)`, which are the same jati
    written two ways. Merging them is the Odia equivalent of the sud/sood
    problem, and the merge list is published beside the results.
    """
    if not isinstance(value, str):
        return ""
    value = re.sub(r"\([^)]*\)", " ", value)
    return _SPACE.sub(" ", value).strip()


def _github() -> Path:
    return Path(os.environ.get("GITHUB_DIR", Path.home() / "Documents/GitHub"))


def checkpoints() -> Path:
    """Where the Odisha scraper and its checkpoints live.

    The scraper moved to its own repository, but a fetch was running in
    pranaam at the time and could not be interrupted, so both locations exist
    during the cutover. The first that holds a parser wins, and the fallback
    can be deleted once nothing is fetching from the old path.
    """
    root = _github()
    candidates = [
        root / "odisha-ror",
        root / "pranaam/scripts/data-acquisition/odisha_ror",
    ]
    for candidate in candidates:
        if (candidate / "parse_ror.py").exists() and (
            candidate / "raw" / "ror"
        ).exists():
            return candidate
    for candidate in candidates:
        if (candidate / "parse_ror.py").exists():
            return candidate
    return candidates[-1]


def materialise() -> bool:
    """Parse pranaam's fetched checkpoints into this repo's own table.

    The parser lives in pranaam and is imported rather than copied, so a fix
    there reaches here. Nothing is written back into that repository: a scrape
    runs in it, and its own `tenants.parquet` is a build artefact of a process
    this analysis does not own.
    """
    source = checkpoints() / "parse_ror.py"
    if not source.exists():
        return False
    spec = importlib.util.spec_from_file_location("parse_ror", source)
    if spec is None or spec.loader is None:
        return False
    module = importlib.util.module_from_spec(spec)
    sys.modules["parse_ror"] = module
    spec.loader.exec_module(module)
    # File discovery is done here rather than by `read_checkpoints`, which
    # globs `district_*/village_*.jsonl.gz`. The fetcher now writes a tahsil
    # level between the two, so that glob matches nothing and the upstream
    # parser silently returns zero records against a live scrape. Reported
    # upstream; this keeps working either way.
    root = checkpoints() / "raw" / "ror"
    records = []
    for path in sorted(root.glob("**/village_*.jsonl.gz")):
        try:
            with gzip.open(path, "rt", encoding="utf8") as handle:
                for line in handle:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # a partial final line from a live writer
        except (OSError, EOFError):
            continue  # a file being written right now
    if not records:
        return False
    TENANTS.parent.mkdir(parents=True, exist_ok=True)
    module.build(records).to_parquet(TENANTS, index=False)
    return True


def load() -> pd.DataFrame | None:
    """Tenant rows with a jati, a village and a surname."""
    if not TENANTS.exists() and not materialise():
        return None
    d = pd.read_parquet(TENANTS)
    d["jati"] = d["caste_or"].map(normalise)
    d["name"] = d["name_or"].map(normalise)
    d["village"] = (
        d["district_code"].astype(str)
        + "|"
        + d["tahsil_code"].astype(str)
        + "|"
        + d["village_code"].astype(str)
    )
    tokens = d["name"].str.split()
    d["surname"] = tokens.map(lambda t: t[-1] if isinstance(t, list) and t else "")
    keep = d["jati"].ne("") & d["surname"].ne("")
    out = d.loc[keep].reset_index(drop=True)
    out.attrs["district"] = DISTRICT
    out.attrs["sampling"] = village_sampling(out)
    return out


def village_sampling(d: pd.DataFrame) -> dict:
    """How many khatiyans each village actually contributed.

    Not the `--per-village` flag: that is a per-run cap, villages accumulate
    across runs, and the flag has already changed from 40 to 10 mid-collection.
    """
    per = d.groupby(["district_code", "tahsil_code", "village_code"])[
        "khatiyan"
    ].nunique()
    return {
        "villages": int(len(per)),
        "khatiyans_per_village_median": float(per.median()),
        "khatiyans_per_village_mean": float(per.mean()),
        "khatiyans_per_village_max": int(per.max()),
    }


def surname_position(d: pd.DataFrame) -> dict:
    """Where the inherited token sits, measured from the relative's name.

    Run before any scoring. A last-token rule is an assumption, and analysis 04
    showed it is false in Maharashtra; carrying it into a new state unchecked is
    how that defect happened the first time.
    """
    frame = d[d["relative_name_or"].fillna("").str.strip().ne("")]
    counts = {"first": 0, "middle": 0, "last": 0}
    shared = 0
    for name, relative in zip(frame["name"], frame["relative_name_or"]):
        tokens = name.split()
        relatives = set(normalise(relative).split())
        if len(tokens) < 2:
            continue
        hits = [i for i, t in enumerate(tokens) if t in relatives]
        if not hits:
            continue
        shared += 1
        for i in hits:
            where = "first" if i == 0 else "last" if i == len(tokens) - 1 else "middle"
            counts[where] += 1
    total = sum(counts.values()) or 1
    return {
        "rows_with_a_relative": int(len(frame)),
        "rows_sharing_a_token": shared,
        "share_sharing_a_token": float(shared / max(len(frame), 1)),
        "positions": {k: v / total for k, v in counts.items()},
        "surname_is": max(counts, key=lambda k: counts[k]),
    }


def score(d: pd.DataFrame, keys: list[str], group: str = "jati") -> dict:
    """Leave-one-out mistakes per 100 guessing `group` from `keys`.

    Identical in form to the Bihar ladder, so the two are comparable: a
    household never votes for its own cell, and one whose cell is then empty
    falls back to the commonest group overall rather than being excused.
    """
    groups = sorted(d[group].unique())
    index = {g: i for i, g in enumerate(groups)}
    truth = d[group].map(index).to_numpy()
    cell = d[keys].astype(str).agg("|".join, axis=1) if len(keys) > 1 else d[keys[0]]

    counts = (
        pd.crosstab(cell, d[group]).reindex(columns=groups, fill_value=0).astype(float)
    )
    rows = counts.loc[cell].to_numpy()
    own = np.zeros_like(rows)
    own[np.arange(len(d)), truth] = 1
    left = rows - own

    prior = counts.to_numpy().sum(axis=0)
    fallback = int(prior.argmax())
    resolved = left.sum(axis=1) > 0
    guess = np.where(resolved, left.argmax(axis=1), fallback)

    return {
        "cue": " + ".join(keys),
        "households": int(len(d)),
        "groups": len(groups),
        "cells": int(counts.shape[0]),
        "mistakes_per_100": float(100 * (guess != truth).mean()),
        "share_resolved": float(100 * resolved.mean()),
    }


def blind(d: pd.DataFrame, group: str = "jati") -> float:
    counts = d[group].value_counts()
    return float(100 * (1 - counts.max() / counts.sum()))
