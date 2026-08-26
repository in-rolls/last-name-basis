"""Whose name tells you nothing, and whether that group is random.

The other analyses report a population average: a name saves about nine
mistakes per hundred, and for most people it changes nothing. This asks who the
"most people" are, because if the uninformative names are not evenly spread then
every name-based caste method has differential error in a knowable direction --
and that is the thing a downstream user of instate, outkast or a BISG-style
method needs to know before using one.

Two cuts, and both use data already in the repo:

by caste  weight each surname by the people of that caste who carry it, so the
          figure is "mistakes made on a Dalit" rather than "mistakes on average";
by sex    weight by female and male bearers, using naampy's first-name gender to
          sex the roll. Women disproportionately carry devi and kumari, which
          carry no caste signal at all.
"""

from __future__ import annotations

import csv
import gzip
import os
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

CATEGORY_LABEL = {"sc": "Scheduled Caste", "st": "Scheduled Tribe", "other": "neither"}


def _github() -> Path:
    return Path(os.environ.get("GITHUB_DIR", Path.home() / "Documents/GitHub"))


def by_caste(
    named: pd.DataFrame, prob_cols: list[str], categories: list[str]
) -> pd.DataFrame:
    """Mistakes made on a person, split by the person's own caste.

    The weighting is the whole point. Weighting names by all their bearers gives
    the population average; weighting by the bearers *of one caste* gives what a
    member of that caste actually experiences.
    """
    p = named[prob_cols].to_numpy()
    err = (1 - p.max(axis=1)) * 100
    guess = p.argmax(axis=1)

    counts = named[[f"n_{c}" for c in categories]].to_numpy()
    prior = counts.sum(axis=0) / counts.sum()

    rows = []
    for i, cat in enumerate(categories):
        w = counts[:, i]
        w = w / w.sum()
        rows.append(
            {
                "caste": CATEGORY_LABEL[cat],
                "share_of_people": float(prior[i]),
                "mistakes_per_100": float((w * err).sum()),
                "found_by_the_guess": float((w * (guess == i)).sum()),
            }
        )
    out = pd.DataFrame(rows)
    out.attrs["blind"] = float((1 - prior.max()) * 100)
    return out


def first_name_gender(min_bearers: int = 200) -> dict[str, float] | None:
    path = _github() / "naampy/in_rolls_state_year_fn_naampy.csv.gz"
    if not path.exists():
        return None
    d = pd.read_csv(path, usecols=["first_name", "n_female", "n_male"])
    g = d.groupby("first_name")[["n_female", "n_male"]].sum()
    n = g["n_female"] + g["n_male"]
    return (g["n_female"] / n)[n >= min_bearers].to_dict()


def surname_by_sex(state: str, gender: dict[str, float]) -> pd.DataFrame | None:
    """Female and male bearers of each surname, from one state's roll.

    Sex comes from the first name and the question is about the last name, so
    the two are independent.
    """
    path = _github() / f"instate/data/names_{state}.csv.gz"
    if not path.exists():
        return None
    female: Counter = Counter()
    male: Counter = Counter()
    with gzip.open(path, "rt") as fh:
        for row in csv.DictReader(fh):
            parts = row["english_name"].split()
            if len(parts) < 2:
                continue
            p_female = gender.get(parts[0])
            if p_female is None:
                continue
            n = int(row["n_times"])
            surname = parts[-1]
            if len(surname) < 2:
                continue
            female[surname] += n * p_female
            male[surname] += n * (1 - p_female)
    names = set(female) | set(male)
    return pd.DataFrame(
        {
            "last_name": sorted(names),
            "female": [female.get(x, 0.0) for x in sorted(names)],
            "male": [male.get(x, 0.0) for x in sorted(names)],
        }
    )


def by_sex(
    named: pd.DataFrame, sexed: pd.DataFrame, prob_cols: list[str]
) -> pd.DataFrame:
    """Mistakes made on a woman against a man, in one state."""
    d = named.merge(sexed, on="last_name", how="inner")
    err = (1 - d[prob_cols].to_numpy().max(axis=1)) * 100
    rows = []
    for label, col in (("women", "female"), ("men", "male")):
        w = d[col].to_numpy(float)
        w = w / w.sum()
        rows.append(
            {
                "who": label,
                "people": float(d[col].sum()),
                "mistakes_per_100": float((w * err).sum()),
            }
        )
    out = pd.DataFrame(rows)
    out.attrs["matched_names"] = len(d)
    return out


def spread(named: pd.DataFrame, weight: str = "share") -> dict:
    """How unevenly informativeness is distributed across people."""
    w = named[weight].fillna(0).to_numpy(float)
    w = w / w.sum()
    gain = named["gain"].to_numpy()
    return {
        "share_gain_zero": float(w[gain <= 1e-9].sum()),
        "share_of_gain_from_top_decile": float(
            np.sort(w * gain)[::-1][: max(1, len(gain) // 10)].sum()
            / max((w * gain).sum(), 1e-12)
        ),
    }
