"""Assign rare spellings to the common name they are probably a variant of.

Assignment, not clustering. Edit-distance components chain -- `a` links to `b`
links to `c` while `a` and `c` are unrelated -- so any partition of them would
be arbitrary. Each tail name gets mapped to its nearest head name or to nothing,
which is well defined and is what the question needs.

All-pairs at 1.9M names is 1.8e12 comparisons. Blocking by first letter and
length band cuts that to something that runs in seconds.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from rapidfuzz.distance import Levenshtein
from rapidfuzz.process import cdist

HEAD = 2000
MAX_EDITS = 1
VOWELS = set("aeiou")
# A head name must be this many times commoner than the tail name it absorbs,
# so two genuinely distinct names of similar size are never merged.
FREQ_RATIO = 20


def assign(
    counts: pd.DataFrame,
    column: str = "national",
    head: int = HEAD,
    max_edits: int = MAX_EDITS,
    freq_ratio: int = FREQ_RATIO,
) -> pd.DataFrame:
    """Map tail names to head names. Returns the accepted merges only."""
    d = counts[["last_name", column]].rename(columns={column: "n"})
    d = d[d["n"] > 0].sort_values("n", ascending=False).reset_index(drop=True)
    heads = d.head(head)
    tail = d.iloc[head:]

    head_by_key: dict[tuple[str, int], pd.DataFrame] = {}
    for (ch, ln), g in heads.groupby(
        [heads["last_name"].str[0], heads["last_name"].str.len()]
    ):
        head_by_key[(ch, ln)] = g

    rows = []
    for (ch, ln), g in tail.groupby(
        [tail["last_name"].str[0], tail["last_name"].str.len()]
    ):
        # An edit of 1 can change length by at most 1, so only three bands match.
        cands = pd.concat(
            [head_by_key.get((ch, ln + d_), pd.DataFrame()) for d_ in (-1, 0, 1)]
        )
        if cands.empty:
            continue
        dist = cdist(
            g["last_name"].tolist(),
            cands["last_name"].tolist(),
            scorer=Levenshtein.distance,
            score_cutoff=max_edits,
            workers=-1,
        )
        best = np.argmin(dist, axis=1)
        best_d = dist[np.arange(len(g)), best]
        ok = best_d <= max_edits
        if not ok.any():
            continue
        rows.append(
            pd.DataFrame(
                {
                    "last_name": g["last_name"].to_numpy()[ok],
                    "n": g["n"].to_numpy()[ok],
                    "target": cands["last_name"].to_numpy()[best[ok]],
                    "target_n": cands["n"].to_numpy()[best[ok]],
                    "edits": best_d[ok],
                }
            )
        )
    if not rows:
        return pd.DataFrame(columns=["last_name", "n", "target", "target_n", "edits"])
    out = pd.concat(rows, ignore_index=True)
    out = out[out["target_n"] >= freq_ratio * out["n"]]
    out = out[
        [transliteration_variant(a, b) for a, b in zip(out["last_name"], out["target"])]
    ]
    return out.sort_values("n", ascending=False).reset_index(drop=True)


def transliteration_variant(a: str, b: str) -> bool:
    """Is the single edit between `a` and `b` a plausible spelling of one name?

    Distance alone is far too permissive on short names: it happily merges
    `raul` into `raut`, `ari` into `ali` and `ajam` into `alam`, which are
    different names. Romanised Indian surnames vary in three narrow ways, and
    restricting to those keeps `kamar -> kumar` while dropping the rest:

    a vowel written as a different vowel (kumar/komar, devi/davi);
    a doubled consonant written single (hassan/hasan);
    an aspirating `h` present or absent (sahu/shahu).
    """
    ops = Levenshtein.editops(a, b)
    if len(ops) != 1:
        return False
    op = ops[0]
    if op.tag == "replace":
        return a[op.src_pos] in VOWELS and b[op.dest_pos] in VOWELS
    ch = a[op.src_pos] if op.tag == "delete" else b[op.dest_pos]
    if ch == "h":
        return True
    # A doubled letter written single, or the reverse.
    longer, pos = (a, op.src_pos) if op.tag == "delete" else (b, op.dest_pos)
    return longer[pos - 1 : pos] == ch or longer[pos + 1 : pos + 2] == ch


def merged_counts(counts: pd.DataFrame, merges: pd.DataFrame, column: str) -> pd.Series:
    """Counts after folding each variant into its target."""
    s = counts.set_index("last_name")[column]
    s = s[s > 0]
    if merges.empty:
        return s
    m = merges[merges["last_name"].isin(s.index) & merges["target"].isin(s.index)]
    moved = m.groupby("target")["n"].sum()
    out = s.drop(index=m["last_name"], errors="ignore").copy()
    out = out.add(moved.reindex(out.index).fillna(0), fill_value=0)
    return out
