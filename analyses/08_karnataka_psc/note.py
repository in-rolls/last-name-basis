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

    split = pd.read_csv(TAB / "by_category.csv")
    rows = "\n".join(
        f"| {r.category} | {r.share_of_candidates:.0%} | "
        f"{r.blind_wrong_per_100:.0f} | **{r.wrong_per_100:.0f}** |"
        for r in split.sort_values("wrong_per_100").itertuples()
    )
    general = split.set_index("category").loc["General", "wrong_per_100"]
    sc = split.set_index("category").loc["Scheduled Caste", "wrong_per_100"]

    md = f"""# What a surname reveals about caste in Karnataka

Karnataka is absent from the census extract this repo runs on. outkast covers
nineteen states and Karnataka is not among them; in the south it holds only
Kerala and Tamil Nadu. The Public Service Commission select lists are therefore
the only caste-linked name data available for the state, and they can be asked
the repo's own question.

They come with two conditions that shape everything below. The candidates are
people who applied for and obtained state government jobs, so nothing here
describes Karnataka's population. And the category is one the candidate declared
in order to claim a quota, not caste as an observer would record it.

## Recovering the surname

The last token is a single letter **{s['naive_is_single_letter']:.0f}% of the time**.
The six commonest are

{top}

and dropping single letters gives a different list entirely:

{top_clean}

Two inventories of "Karnataka's commonest surnames" from the same {s['rows']:,}
names. Analysis 04 found Maharashtra failing the last-token
assumption by writing the surname first; this is the same assumption failing by
abbreviation. Everything below uses the cleaned surname, which is the last token
longer than one character.

![What a last-token rule calls a surname]({FIG}/naive_vs_clean.png)

## The surname works for one category and largely fails the rest

| category | share of candidates | wrong knowing nothing | wrong with the surname |
|---|---|---|---|
{rows}

The guess is wrong about {sc:.0f} of every 100 Scheduled Caste candidates and
{general:.0f} of every 100 General ones, an error **{sc / general:.1f} times
larger** for the group the quota exists for. Analysis 05 found the same direction
nationally, from SECC and the electoral rolls, sorting people into three census
categories. This is a different state, a different source and a different set of
labels, and it points the same way.

![What the guess gets wrong, by the candidate's own category]({FIG}/by_category.png)

Overall the surname takes the error from {blind:.1f} mistakes per 100 to
{clean['mistakes_per_100']:.1f}, closing **{s['gap_closed_share']:.0f}% of the
gap**. Among the states in analysis 07 that would sit between Tamil Nadu at 9%
and Uttarakhand at 28%, and far below Bihar at 61%. The comparison is
suggestive and not like-for-like: four quota categories are not three census
categories, and job applicants are not a population.

## Two smaller results

**Cleaning the initials out buys {-s['cleaning_changes_prediction_by']:.1f} mistakes
per hundred**, from {naive['mistakes_per_100']:.1f} to
{clean['mistakes_per_100']:.1f}. An earlier version of this note reported that
difference as slightly negative, on 14,854 candidates. At {s['rows']:,} the sign
is stable and the other way round, so the earlier reading was underpowered.

**The PIN code is worth almost nothing**, {pin['mistakes_per_100']:.1f} against
a blind {blind:.1f}. Geography does the opposite in Bihar, where a village takes
47 mistakes down to 17. Whether that is a fact about Karnataka or about a
recruitment list drawn from across the state, this data cannot say.

## How the numbers are computed

Every figure is leave-one-out: a candidate's own record is excluded from the
table used to score them. Most surnames here appear once or twice, so a plug-in
score would report memorisation. A cue is used when at least one *other*
candidate shares it, which is the rule analysis 09 uses; requiring two instead
moves the headline from {clean['mistakes_per_100']:.1f} to 43.9.

Karnataka's backward-class codes are collapsed into one OBC bucket, which folds
in 2B, a religion-defined category this repo does not report separately.

---

*Karnataka PSC select lists, collected in
[pranaam](https://github.com/appeler/pranaam).*
"""
    out = HERE / "note.md"
    out.write_text(md)
    print(f"wrote {out} ({len(md.splitlines())} lines)")


if __name__ == "__main__":
    main()
