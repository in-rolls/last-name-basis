"""Normalise Odia jati strings, and record every merge.

This is a placeholder for a layer being built in upnaam. It is deliberately
small and its whole output is published, so that replacing it later is a matter
of swapping one function and re-running, and so that any result here can be
checked against the merges that produced it.

Three things happen, in order, and each is reported separately because they are
different kinds of claim:

`drop_runaway`   The parser occasionally captures a mutation order rather than
                 a caste, when the caste marker is followed by an entire
                 administrative paragraph. These are identifiable by length and
                 amount to 15 households in 56,439.

`merge_variants` Two spellings of one jati, differing by a vowel sign or a
                 space, are one prediction target. `ସଉରା` and `ସୌରା` are the
                 clearest case. Merging is by edit distance on a
                 whitespace-stripped key, and only into a strictly commoner
                 form, so the direction of every merge is determined.

`strip_religion` A jati may carry a religion as a suffix: `ପାଣ` and
                 `ପାଣ ଖ୍ରୀଷ୍ଟିୟାନ` are recorded separately. Treating those as
                 two targets makes religion a predictor, which this repo does
                 not do. Stripping is therefore available but NOT applied by
                 default: analysis 09 scores both ways and reports the pair, so
                 the effect of the choice is visible rather than assumed.
"""

from __future__ import annotations

import re

import pandas as pd
from rapidfuzz import fuzz

# A caste value longer than this is a runaway capture, not a caste. The parser
# in pranaam uses 40; the empirical break here is at 20, above which values are
# plainly administrative text.
MAX_LEN = 20

# Religion words that appear as a modifier on a jati rather than as one.
RELIGION = ("ଖ୍ରୀଷ୍ଟିୟାନ", "ମୁସଲମାନ", "ଖ୍ରୀଷ୍ଟିଆନ")

MIN_SIMILARITY = 92
_SPACE = re.compile(r"\s+")


def _key(value: str) -> str:
    return _SPACE.sub("", value)


def drop_runaway(counts: pd.Series) -> tuple[pd.Series, pd.DataFrame]:
    bad = counts.index.to_series().str.len() > MAX_LEN
    dropped = pd.DataFrame(
        {"jati": counts.index[bad], "households": counts.to_numpy()[bad]}
    )
    return counts[~bad.to_numpy()], dropped


def merge_variants(counts: pd.Series) -> tuple[dict[str, str], pd.DataFrame]:
    """Map each rare spelling onto the commonest form it is a variant of.

    Ordered by frequency so a merge always runs from rarer to commoner, which
    makes the result independent of iteration order.
    """
    ordered = counts.sort_values(ascending=False)
    canonical: list[str] = []
    mapping: dict[str, str] = {}
    rows = []
    for name in ordered.index:
        key = _key(name)
        match = None
        for candidate in canonical:
            if fuzz.ratio(key, _key(candidate)) >= MIN_SIMILARITY:
                match = candidate
                break
        if match is None:
            canonical.append(name)
            mapping[name] = name
        else:
            mapping[name] = match
            rows.append(
                {
                    "variant": name,
                    "merged_into": match,
                    "households": int(ordered[name]),
                    "similarity": fuzz.ratio(key, _key(match)),
                }
            )
    return mapping, pd.DataFrame(rows)


def strip_religion(value: str) -> str:
    """Return the jati without a religion modifier, or the value unchanged."""
    tokens = [t for t in value.split() if t not in RELIGION]
    return " ".join(tokens) if tokens else value


def normalise(series: pd.Series) -> dict:
    """Apply the layer and return the mapping alongside its full audit trail."""
    counts = series.value_counts()
    kept, dropped = drop_runaway(counts)
    mapping, merges = merge_variants(kept)
    return {
        "mapping": mapping,
        "dropped": dropped,
        "merges": merges,
        "strings_in": int(len(counts)),
        "strings_out": int(len(set(mapping.values()))),
        "households_dropped": int(dropped["households"].sum()) if len(dropped) else 0,
        "households_merged": int(merges["households"].sum()) if len(merges) else 0,
    }
