"""Which position holds the surname, for every state.

Analysis 04 found Maharashtra writes the surname first by matching against the
father's name. That test cannot run where the roll records the relative as a
bare given name -- Gujarat, Tamil Nadu, Kerala -- which is exactly where the
question also matters.

This is a second detector that needs no relative name at all. A surname column
repeats: a few thousand families supply millions of people. A given-name column
does not repeat nearly as hard. So compare how concentrated the first token is
against the last, and the more concentrated one is the surname.

Where both detectors run they agree, which is the reason to trust this one where
only it can.
"""

from __future__ import annotations

import csv
import gzip
from collections import Counter

import pandas as pd
from transmission import roll_path

TOP = 20


def _share_in_top(counter: Counter, top: int = TOP) -> float:
    total = sum(counter.values())
    if not total:
        return 0.0
    return sum(v for _, v in counter.most_common(top)) / total


def detect(state: str, limit: int = 500_000) -> dict | None:
    """Concentration of the first token against the last, for one state."""
    path = roll_path(state)
    if not path.exists():
        return None
    first: Counter = Counter()
    last: Counter = Counter()
    rows = 0
    with gzip.open(path, "rt") as fh:
        for i, row in enumerate(csv.DictReader(fh)):
            if i >= limit:
                break
            parts = row["english_name"].split()
            if len(parts) < 2:
                continue
            n = int(row["n_times"])
            rows += n
            if len(parts[0]) > 1:
                first[parts[0]] += n
            if len(parts[-1]) > 1:
                last[parts[-1]] += n

    if not rows:
        return None
    f, la = _share_in_top(first), _share_in_top(last)
    return {
        "state": state,
        "people": rows,
        "top20_first": f,
        "top20_last": la,
        "surname_position": "first" if f > la else "last",
        # How lopsided the call is. Near 1.0 means the two positions look alike
        # and the call should not be leaned on.
        "ratio": (min(f, la) / max(f, la)) if max(f, la) else 1.0,
    }


def detect_all(states: list[str], limit: int = 500_000) -> pd.DataFrame:
    rows = [detect(s, limit) for s in states]
    return pd.DataFrame([r for r in rows if r]).sort_values("top20_first")
