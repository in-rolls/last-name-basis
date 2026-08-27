"""Render analysis 08's note from its outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", "out/fig"


def main() -> None:
    path = TAB / "summary.json"
    if not path.exists():
        print("skipped: analysis 08 not built")
        return
    s = json.loads(path.read_text())
    t = pd.read_csv(TAB / "commonest_tokens.csv")
    sc = pd.read_csv(TAB / "scores.csv").set_index("cue")
    naive, clean, pin = (sc.loc[k] for k in ("naive_surname", "clean_surname", "pin"))
    blind = naive["blind_per_100"]

    top = ", ".join(f"`{r.naive}` ({r.naive_n:,})" for r in t.head(6).itertuples())
    top_clean = ", ".join(
        f"`{r.clean.title()}` ({r.clean_n:,})" for r in t.head(6).itertuples()
    )

    md = f"""# Karnataka, where the last token is an initial

Analysis 04 found that Maharashtra writes the surname first, so a last-token
rule picks up a *given* name there. Karnataka breaks the same assumption by a
different route: **{s['naive_is_single_letter']:.0f}% of last tokens are a
single letter**, and the six commonest are

{top}

before any real surname appears. Drop single letters and the same list reads

{top_clean}

Two completely different inventories of "Karnataka's commonest surnames",
from the same {s['rows']:,} names.

![What a last-token rule calls a surname]({FIG}/naive_vs_clean.png)

## Cleaning changes the names and not the prediction

This is the part worth reporting carefully, because it is a null and it went
against what I expected.

| cue | distinct values | mistakes per 100 | share resolved |
|---|---|---|---|
| knowing nothing | — | {blind:.1f} | — |
| naive last token | {naive['distinct']:,} | {naive['mistakes_per_100']:.1f} | {naive['share_resolved']:.0f}% |
| cleaned surname | {clean['distinct']:,} | {clean['mistakes_per_100']:.1f} | {clean['share_resolved']:.0f}% |
| PIN code | {pin['distinct']:,} | {pin['mistakes_per_100']:.1f} | {pin['share_resolved']:.0f}% |

Cleaning moves the error by
{s['cleaning_changes_prediction_by']:+.1f} mistakes per hundred, which is to
say it does not move it. It slightly *worsens* it, and the reason is visible in
the last column: dropping initials splits {naive['distinct']:,} cells into
{clean['distinct']:,} smaller ones, so fewer people share a cell with anyone
else and more fall back to the blind guess.

So the naive rule was never predicting well by using real surnames. It was
pooling people into a handful of enormous initial-buckets, which beats guessing
blind by a little, exactly as the cleaned surnames do.

**Neither is worth much.** Against a blind rate of {blind:.0f}, the best of them
leaves {min(naive['mistakes_per_100'], clean['mistakes_per_100']):.0f}. The PIN
code is worth almost nothing at all, which is the opposite of what geography does
in Bihar, where a village takes 47 mistakes down to 17.

## What this does and does not establish

It establishes that **any count of Karnataka's commonest surnames built from
last tokens is counting initials**. That matters for analysis 03, which measures
how concentrated Indian naming is: a state like this one contributes a
concentration figure driven by how many people abbreviate, not by how many share
a family name.

It does not establish anything about caste in Karnataka. Two reasons, both
serious enough for the opening rather than a footnote:

- These are **Public Service Commission select lists**: educated applicants for
  government jobs, not a population sample.
- `reservation` is a **quota category the candidate declared**, not observed
  caste. Karnataka's backward-class codes are collapsed here into one OBC
  bucket, which also folds in 2B, a religion-defined category this repo does not
  report separately.

With {s['rows']:,} rows across four categories, and most surnames appearing once
or twice, everything above is scored leave-one-out. A plug-in score would report
memorisation.

---

*Karnataka PSC select lists, collected in
[pranaam](https://github.com/appeler/pranaam).*
"""
    out = HERE / "note.md"
    out.write_text(md)
    print(f"wrote {out} ({len(md.splitlines())} lines)")


if __name__ == "__main__":
    main()
