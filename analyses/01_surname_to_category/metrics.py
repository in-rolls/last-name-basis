"""Per-name informativeness measures.

Three questions get three columns, because they disagree and the disagreement
is the finding:

``err``       how often the name-based guess is wrong.
``gain``      how many of those errors the name actually saved you, versus
              ignoring it and always naming the commonest category.  Zero
              whenever the name does not flip the answer -- which is most names.
``cut``       how much of the uncertainty about caste the name removes.
              H(caste) - H(caste | this name).  This is the headline measure:
              it is bounded above by H(caste), so a name can never appear to
              tell you more than the answer itself, and it can go negative for
              a name that leaves you *less* sure than the population average.
``bits``      how far the name moves your belief away from the base rate.
              KL(p(caste|name) || p(caste)).  Kept because it is the standard
              quantity, but it is the wrong headline: it rewards surprise
              rather than certainty, and so ranks Paswan (which leaves you 89%
              sure) above Jha (which leaves you 99.7% sure).

Both average to the same thing -- the mutual information I(C;S) -- but only when
the prior they are measured against is the one implied by the weights being
averaged with.  ``weighted_summary`` enforces that; do not mix a roll-weighted
average with a SECC-weighted prior.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from data import CATEGORIES, PROB_COLS

from last_name_basis.scoring import entropy_bits
from last_name_basis.scoring import weighted_summary as _weighted_summary

LABELS = {"sc": "SC", "st": "ST", "other": "Other"}


def add_metrics(names: pd.DataFrame, base: pd.Series) -> pd.DataFrame:
    """Attach guess/error/gain/bits to a per-name frame. Order-independent."""
    out = names.copy()
    p = out[PROB_COLS].to_numpy()
    prior = np.array([base[f"n_{c}"] for c in CATEGORIES], dtype=float)
    prior = prior / prior.sum()

    blind = int(prior.argmax())
    out["guess"] = [LABELS[CATEGORIES[i]] for i in p.argmax(axis=1)]
    out["err"] = 1.0 - p.max(axis=1)
    out["err_blind"] = 1.0 - p[:, blind]
    out["gain"] = out["err_blind"] - out["err"]
    with np.errstate(divide="ignore", invalid="ignore"):
        out["bits"] = np.where(p > 0, p * np.log2(p / prior), 0.0).sum(axis=1)
        conditional = -np.where(p > 0, p * np.log2(p), 0.0).sum(axis=1)
    out["cut"] = entropy_bits(prior) - conditional
    return out


def headline(named: pd.DataFrame, base: pd.Series) -> dict:
    """The numbers the note leads with."""
    prior = (base / base.sum()).to_numpy()
    w = named["share"].to_numpy()
    return {
        "names": len(named),
        "records": float(named["n"].sum()),
        "base_rates": {c: float(prior[i]) for i, c in enumerate(CATEGORIES)},
        "caste_entropy_bits": entropy_bits(prior),
        "err_blind_overall": float(1.0 - prior.max()),
        "err_per_person": float((named["err"] * w).sum()),
        "err_per_name": float(named["err"].mean()),
        "mutual_information_bits": float((named["bits"] * w).sum()),
        "share_people_guess_unchanged": float(w[named["gain"].to_numpy() <= 0].sum()),
        "names_guess_unchanged": int((named["gain"] <= 0).sum()),
    }


def by_frequency_band(
    named: pd.DataFrame,
    bands: tuple[tuple[int, int], ...] = (
        (1, 10),
        (11, 25),
        (26, 50),
        (51, 100),
        (101, 250),
        (251, 500),
        (501, 1000),
        (1001, 10**9),
    ),
) -> pd.DataFrame:
    """Informativeness against how common the name is. The main exhibit."""
    ranked = named.sort_values("n", ascending=False).reset_index(drop=True)
    rows = []
    for lo, hi in bands:
        b = ranked.iloc[lo - 1 : min(hi, len(ranked))]
        if b.empty:
            continue
        rows.append(
            {
                "rank": f"{lo}-{min(hi, len(ranked))}",
                "names": len(b),
                "share_people": b["share"].sum(),
                "bits_p25": b["bits"].quantile(0.25),
                "bits_median": b["bits"].median(),
                "bits_p75": b["bits"].quantile(0.75),
                "err_mean": b["err"].mean(),
                "names_gain_gt0": int((b["gain"] > 0).sum()),
            }
        )
    return pd.DataFrame(rows)


def uninformative_cdf(
    named: pd.DataFrame,
    thresholds: tuple[float, ...] = (0.02, 0.05, 0.10, 0.25, 0.50, 1.00),
) -> pd.DataFrame:
    """How common are the names that tell you little -- weighted by people."""
    rows = []
    for t in thresholds:
        m = named["bits"] < t
        rows.append(
            {
                "bits_below": t,
                "share_people": float(named.loc[m, "share"].sum()),
                "names": int(m.sum()),
                "share_names": float(m.mean()),
            }
        )
    return pd.DataFrame(rows)


def confusion(named: pd.DataFrame) -> pd.DataFrame:
    """Where the guessing errors land: guessed category x true category."""
    counts = named.groupby("guess")[[f"n_{c}" for c in CATEGORIES]].sum()
    counts.columns = [LABELS[c] for c in CATEGORIES]
    return counts.div(counts.to_numpy().sum())


def recall_precision(named: pd.DataFrame, weight: str = "share") -> pd.DataFrame:
    """Who the guessing finds and who it misses, under a given people-weighting.

    Recall matters more than accuracy here: a rule that never says "Dalit" is
    80% accurate and finds nobody.  The weighting must match whatever the rest
    of the piece is using, or the population shares in this table will not agree
    with the ones quoted around it.
    """
    w = named[weight].fillna(0).to_numpy(float)
    w = w / w.sum()
    p = named[PROB_COLS].to_numpy()
    mass = pd.DataFrame(p * w[:, None], columns=[LABELS[c] for c in CATEGORIES])
    mass["guess"] = named["guess"].to_numpy()

    counts = mass.groupby("guess").sum()
    counts = counts.reindex(index=list(LABELS.values()), fill_value=0.0)
    truth = counts.sum(axis=0)
    guessed = counts.sum(axis=1)
    return pd.DataFrame(
        {
            "share_of_people": truth / truth.sum(),
            "share_guessed": guessed / truth.sum(),
            "recall": [
                counts.loc[c, c] / truth[c] if truth[c] else float("nan")
                for c in counts.columns
            ],
            "precision": [
                counts.loc[c, c] / guessed[c] if guessed[c] else float("nan")
                for c in counts.columns
            ],
        }
    )


def signal_decomposition(cells: pd.DataFrame) -> dict:
    """How much of the name's apparent caste signal is really geography?

    Pooling across states means a surname that merely marks a region inherits
    that region's caste mix.  In a mixed city that inference is legitimate --
    you genuinely do not know where someone is from -- but it is worth knowing
    how much of the signal it is.

    Uses the chain rule I(C; S, State) = I(C; State) + I(C; S | State).
    """
    counts = cells[[f"n_{c}" for c in CATEGORIES]].to_numpy(float)
    total = counts.sum()
    prior = counts.sum(axis=0) / total
    h_c = entropy_bits(prior)

    by_state = cells.groupby("state")[[f"n_{c}" for c in CATEGORIES]].sum().to_numpy()
    w_state = by_state.sum(axis=1) / total
    h_c_given_state = float(
        sum(w * entropy_bits(r / r.sum()) for w, r in zip(w_state, by_state))
    )

    by_cell = (
        cells.groupby(["state", "last_name"])[[f"n_{c}" for c in CATEGORIES]]
        .sum()
        .to_numpy()
    )
    w_cell = by_cell.sum(axis=1) / total
    h_c_given_both = float(
        sum(w * entropy_bits(r / r.sum()) for w, r in zip(w_cell, by_cell))
    )

    by_name = (
        cells.groupby("last_name")[[f"n_{c}" for c in CATEGORIES]].sum().to_numpy()
    )
    w_name = by_name.sum(axis=1) / total
    h_c_given_name = float(
        sum(w * entropy_bits(r / r.sum()) for w, r in zip(w_name, by_name))
    )

    def mistakes(groups) -> float:
        """Mistakes per hundred when you guess the commonest category in each
        group. Same unit as everything else, so the comparison needs no gloss."""
        w = groups.sum(axis=1) / total
        return float((w * (1 - groups.max(axis=1) / groups.sum(axis=1))).sum() * 100)

    return {
        "caste_entropy_bits": h_c,
        "name_alone_bits": h_c - h_c_given_name,
        "state_alone_bits": h_c - h_c_given_state,
        "name_given_state_bits": h_c_given_state - h_c_given_both,
        "name_and_state_bits": h_c - h_c_given_both,
        "mistakes_knowing_nothing": float((1 - prior.max()) * 100),
        "mistakes_knowing_state": mistakes(by_state),
        "mistakes_knowing_name": mistakes(by_name),
        "mistakes_knowing_both": mistakes(by_cell),
    }


def weighted_summary(named: pd.DataFrame, weight: str) -> dict:
    """This analysis's categories, scored by the shared routine."""
    return _weighted_summary(named, PROB_COLS, weight, CATEGORIES)
