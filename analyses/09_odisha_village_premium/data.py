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

**Each village is a sample.** The fetch runs at 40 khatiyans per village, so a
village cell holds at most 40 households rather than all of them. Village-level
cells are therefore small, and leave-one-out is not optional.

The surname is the **last** token, which is measured rather than assumed. A
token appearing in both a tenant's name and their father's or husband's is an
inherited one, and in Gajapati that token is last 80% of the time, first 11%.
Maharashtra fails the same test in the other direction (analysis 04), so the
test is run per state and never carried over.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TENANTS = HERE / "out/tab/tenants.parquet"
PER_VILLAGE_CAP = 40
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


def load() -> pd.DataFrame | None:
    """Tenant rows with a jati, a village and a surname."""
    if not TENANTS.exists():
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
    out.attrs["per_village_cap"] = PER_VILLAGE_CAP
    return out


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
