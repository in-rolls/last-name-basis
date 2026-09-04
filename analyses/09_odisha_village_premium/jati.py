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
                 space, are one prediction target. `ଖଣ୍ଡାୟତ` and `ଖଣ୍ଡାଏତ`
                 are the clearest case. Nearness of spelling proposes a merge;
                 it never decides one, because `ଚମାର`/`କମାର`,
                 `ଗଣ୍ଡ`/`ଗଣ୍ଡା` and `ଭୂମିଆ`/`ଭୂମିଜ` are each one edit apart
                 and each two different jatis. A candidate is confirmed by a
                 second signal sharing no input with the first: two spellings
                 of one jati are carried by the same surnames. Merging runs
                 only into a strictly commoner form, so the direction of every
                 merge is determined, and every candidate -- accepted or
                 rejected -- is published with both of its scores.

`strip_religion` A jati may carry a religion as a suffix: `ପାଣ` and
                 `ପାଣ ଖ୍ରୀଷ୍ଟିୟାନ` are recorded separately. Treating those as
                 two targets makes religion a predictor, which this repo does
                 not do. Stripping is therefore available but NOT applied by
                 default: analysis 09 scores both ways and reports the pair, so
                 the effect of the choice is visible rather than assumed.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd
from rapidfuzz.distance import Levenshtein

# A caste value longer than this is a runaway capture, not a caste. The parser
# in pranaam uses 40; the empirical break here is at 20, above which values are
# plainly administrative text.
MAX_LEN = 20

# Religion words that appear as a modifier on a jati rather than as one.
RELIGION = ("ଖ୍ରୀଷ୍ଟିୟାନ", "ମୁସଲମାନ", "ଖ୍ରୀଷ୍ଟିଆନ")

# Spelling nearness proposes a candidate. Odia jati labels are short, so one
# substitution in a four-character string is a large proportional change:
# `fuzz.ratio` scores ସଉରା/ସୌରା at 75 and ଖଣ୍ଡାୟତ/ଖଣ୍ଡାଏତ at 86. A ratio
# threshold high enough to be safe on long strings therefore merged nothing.
# Edit distance scaled to length is used instead.
MAX_EDITS = 2
EDIT_RATE = 0.15

# A candidate is confirmed by the surname profiles of its two labels. Measured
# against pairs known from the caste names to be the same jati and pairs known
# to be different, the two separate cleanly: same-jati pairs score 0.31 to 0.99,
# different-jati pairs 0.00 to 0.10, and 2,000 random label pairs have a median
# of 0.003.
MIN_PROFILE = 0.25

# Below this many households the profile stops discriminating: subsampling a
# known-same pair down to ten rows gives cosines as low as 0.16, and a
# known-different pair reaches 0.21. Rarer labels are left as recorded rather
# than merged on spelling alone.
MIN_HOUSEHOLDS = 25

_SPACE = re.compile(r"\s+")


def _key(value: str) -> str:
    return _SPACE.sub("", value)


def drop_runaway(counts: pd.Series) -> tuple[pd.Series, pd.DataFrame]:
    bad = counts.index.to_series().str.len() > MAX_LEN
    dropped = pd.DataFrame(
        {"jati": counts.index[bad], "households": counts.to_numpy()[bad]}
    )
    return counts[~bad.to_numpy()], dropped


def surname_profiles(frame: pd.DataFrame) -> dict[str, pd.Series]:
    """Return each jati's surname distribution.

    Args:
        frame: Rows carrying a `jati` and a `surname`.

    Returns:
        One surname-count series per jati.
    """
    tally = frame.groupby(["jati", "surname"], observed=True).size().rename("n")
    return {j: g.droplevel(0) for j, g in tally.groupby(level=0)}


def profile_similarity(profiles: dict[str, pd.Series], left: str, right: str) -> float:
    """Return the cosine between two jatis' surname distributions.

    Args:
        profiles: Surname counts per jati.
        left: One jati label.
        right: The other jati label.

    Returns:
        Cosine similarity in [0, 1]; 0 when either label has no surnames.
    """
    if left not in profiles or right not in profiles:
        return 0.0
    a, b = profiles[left], profiles[right]
    index = a.index.union(b.index)
    x = a.reindex(index, fill_value=0).to_numpy(dtype=float)
    y = b.reindex(index, fill_value=0).to_numpy(dtype=float)
    scale = float(np.linalg.norm(x) * np.linalg.norm(y))
    return float(x @ y / scale) if scale else 0.0


def _budget(key: str) -> int:
    """Return how many edits still count as one spelling of one label."""
    return max(1, min(MAX_EDITS, round(EDIT_RATE * len(key))))


def merge_variants(
    counts: pd.Series, profiles: dict[str, pd.Series]
) -> tuple[dict[str, str], pd.DataFrame, pd.DataFrame]:
    """Map each rare spelling onto the commonest form it is a variant of.

    Ordered by frequency so a merge always runs from rarer to commoner, which
    makes the result independent of iteration order. A candidate is accepted
    only when the surname profiles agree as well as the spelling.

    Args:
        counts: Households per jati label.
        profiles: Surname counts per jati label.

    Returns:
        The label mapping, the accepted merges, and the rejected candidates.
    """
    ordered = counts.sort_values(ascending=False)
    canonical: list[str] = []
    mapping: dict[str, str] = {}
    merged, refused = [], []
    for name in ordered.index:
        key = _key(name)
        budget = _budget(key)
        best = None
        for candidate in canonical:
            distance = Levenshtein.distance(key, _key(candidate))
            if distance > budget:
                continue
            agreement = profile_similarity(profiles, name, candidate)
            row = {
                "variant": name,
                "candidate": candidate,
                "households": int(ordered[name]),
                "edits": int(distance),
                "profile_cosine": round(agreement, 4),
            }
            if int(ordered[name]) < MIN_HOUSEHOLDS:
                row["verdict"] = "too rare to check"
            elif agreement < MIN_PROFILE:
                row["verdict"] = "different surnames"
            else:
                best = candidate
                merged.append({**row, "merged_into": candidate})
                break
            refused.append(row)
        if best is None:
            canonical.append(name)
            mapping[name] = name
        else:
            mapping[name] = best
    return mapping, pd.DataFrame(merged), pd.DataFrame(refused)


def carry_across_religion(
    mapping: dict[str, str], counts: pd.Series
) -> tuple[dict[str, str], pd.DataFrame]:
    """Apply a base label's merge to its religion-suffixed forms.

    `ଉରାମ` merges into `ଓରାମ` on the evidence, but
    `ଉରାମ ଖ୍ରୀଷ୍ଟିଆନ` is a smaller group whose surname profile scores just
    under the threshold, so it was left separate. Splitting one jati in two
    according to whether the clerk wrote the religion is not a distinction the
    record makes. Where the bases have been judged the same, the suffixed forms
    follow, and each such merge is recorded as carried rather than measured.

    Args:
        mapping: The mapping produced from the evidence.
        counts: Households per jati label.

    Returns:
        The extended mapping and the merges it added.
    """
    rows = []
    for label, target in list(mapping.items()):
        if label != target:
            continue
        tokens = label.split()
        suffix = [t for t in tokens if t in RELIGION]
        if not suffix or len(tokens) == len(suffix):
            continue
        base = " ".join(t for t in tokens if t not in RELIGION)
        canonical_base = mapping.get(base)
        if canonical_base is None or canonical_base == base:
            continue
        rebuilt = " ".join([canonical_base, *suffix])
        if mapping.get(rebuilt) != rebuilt:
            continue
        mapping[label] = rebuilt
        rows.append(
            {
                "variant": label,
                "merged_into": rebuilt,
                "candidate": rebuilt,
                "households": int(counts.get(label, 0)),
                "edits": -1,
                "profile_cosine": float("nan"),
                "verdict": "carried from the base label",
            }
        )
    return mapping, pd.DataFrame(rows)


def strip_religion(value: str) -> str:
    """Return the jati without a religion modifier, or the value unchanged."""
    tokens = [t for t in value.split() if t not in RELIGION]
    return " ".join(tokens) if tokens else value


def normalise(frame: pd.DataFrame) -> dict:
    """Apply the layer and return the mapping alongside its full audit trail.

    Args:
        frame: Rows carrying a `jati` and a `surname`.

    Returns:
        The mapping, the merges and refusals that produced it, and counts.
    """
    counts = frame["jati"].value_counts()
    kept, dropped = drop_runaway(counts)
    profiles = surname_profiles(frame[frame["jati"].isin(kept.index)])
    mapping, merges, refused = merge_variants(kept, profiles)
    mapping, carried = carry_across_religion(mapping, kept)
    if len(carried):
        merges = pd.concat([merges, carried], ignore_index=True)
    resolved = counts[counts.index.isin(mapping)].groupby(mapping).sum()
    covering = resolved.sort_values(ascending=False).cumsum() / resolved.sum()
    return {
        "mapping": mapping,
        "dropped": dropped,
        "merges": merges,
        "refused": refused,
        "strings_in": int(len(counts)),
        "strings_out": int(len(set(mapping.values()))),
        # The raw count is dominated by a tail carrying almost no one, which
        # makes the target look far harder than it is against Bihar's 141
        # curated jatis. How many labels it takes to cover the households is
        # the comparable number.
        "labels_covering_99pct": int((covering < 0.99).sum() + 1),
        "households_dropped": int(dropped["households"].sum()) if len(dropped) else 0,
        "households_merged": int(merges["households"].sum()) if len(merges) else 0,
        "candidates_refused": int(len(refused)),
    }
