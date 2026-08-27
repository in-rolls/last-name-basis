"""How well could someone do with everything the electoral roll prints?

The rest of this repo measures a floor: what a surname alone gives away. This
measures the other end. Every cue used here -- the name, the father's or
husband's name, and the hamlet -- is printed on a public roll page.

The trap, and it cost two wrong answers before this was written: scoring only
the households a fine cell can resolve. At the finest rung just **36%** of
households share a cell with anyone else, and those are the easy ones -- people
with a same-named relative in the same hamlet. Leave-one-out silently drops the
rest and reports 1.2 mistakes per hundred, which describes a third of the
population and flatters it.

So every household is scored. Where the finest cell cannot resolve a person, the
guesser falls back to a coarser cue rather than being excused from guessing, and
where nothing resolves it falls back to the commonest jati overall.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def _cell(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    parts = [frame[c] for c in cols]
    return parts[0] if len(parts) == 1 else parts[0].str.cat(parts[1:], sep="|")


def _leave_one_out(cell: pd.Series, group: np.ndarray, n_groups: int):
    """Predict each row from its cell with that row removed.

    Returns the prediction and how many others were in the cell, so a caller can
    tell "resolved" from "nothing to go on".
    """
    table = pd.crosstab(cell, group).reindex(columns=range(n_groups), fill_value=0)
    pos = {c: i for i, c in enumerate(table.index)}
    counts = table.to_numpy()[[pos[c] for c in cell]]
    own = np.zeros_like(counts)
    own[np.arange(len(cell)), group] = 1
    held = counts - own
    others = held.sum(axis=1)
    return np.where(others > 0, held.argmax(axis=1), -1), others


def ceiling(
    frame: pd.DataFrame, chain: list[list[str]], group_col: str = "jati"
) -> dict:
    """Best achievable error using a fallback chain of cues, scoring everyone."""
    groups = sorted(frame[group_col].unique())
    gmap = {g: i for i, g in enumerate(groups)}
    truth = frame[group_col].map(gmap).to_numpy()
    fallback = int(np.bincount(truth, minlength=len(groups)).argmax())

    final = np.full(len(frame), -1)
    coverage = []
    for cols in chain:
        pred, others = _leave_one_out(_cell(frame, cols), truth, len(groups))
        coverage.append(
            {"cue": " + ".join(cols), "resolves": float((others > 0).mean())}
        )
        take = (final < 0) & (others > 0)
        final[take] = pred[take]
    unresolved = float((final < 0).mean())
    final[final < 0] = fallback

    return {
        "mistakes_per_100": float(100 * (final != truth).mean()),
        "households": int(len(frame)),
        "groups": len(groups),
        "coverage": coverage,
        "share_needing_the_global_fallback": unresolved,
    }
