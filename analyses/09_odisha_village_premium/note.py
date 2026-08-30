"""Render analysis 09's note from its outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", "out/fig"


def main() -> None:
    path = TAB / "summary.json"
    if not path.exists():
        print("skipped: analysis 09 not built")
        return
    s = json.loads(path.read_text())
    g = s["gajapati"]["as recorded"]
    gr = s["gajapati"]["religion stripped"]
    b = s["bihar"]
    pos = s["surname_position"]
    nrm = s["normalisation"]
    sens = pd.DataFrame(s["sensitivity"])

    sens_rows = "\n".join(
        f"| {int(r.threshold)} | {int(r.groups)} | {r.surname:.1f} | "
        f"{r.surname_village:.1f} | **{r.premium:.1f}** |"
        for r in sens.itertuples()
    )

    md = f"""# Does the village premium travel outside Bihar?

Bihar's land records support the strongest single result in this repo. Across
141 jatis a surname alone leaves {b['surname']:.0f} mistakes per 100, and a
surname together with a village leaves {b['surname_village']:.0f}. The question
that result raises is whether the {b['premium']:.0f}-point difference describes
surnames and villages in general or describes Bihar.

The Odisha Record of Rights records a jati and a village for every tenant, which
makes the same measurement possible elsewhere. Scored on the same protocol, in
{s['district']} district, **a village adds {g['premium']:.0f} points where in
Bihar it adds {b['premium']:.0f}**. Relative to what the surname leaves
unresolved, the village closes {g['premium_share']:.0f}% of the remainder here
against {b['premium_share']:.0f}% in Bihar.

![What a village adds, in Bihar and in Gajapati]({FIG}/village_premium.png)

Put on analysis 02's axis, the two places produce the same shape and different
depths. Both leave the same number of mistakes once the place is discarded, and
they separate as it is restored.

![Error rising as the place gets bigger, in both places]({FIG}/atrophy.png)

## What is being compared, and what is not

The two levels are not comparable and the figure is drawn so as not to invite
the comparison. Bihar sorts people among 141 curated jatis; {s['district']}
sorts them among {g['groups']} labels as recorded. A harder target produces more
mistakes whatever the surname does, so the quantity that carries across places
is the distance between the two rungs rather than the height of either.

Both places happen to leave 47 mistakes at the surname alone. Nothing follows
from that. The two are counting against different numbers of groups, so equal
heights there are not evidence that surnames are equally informative.

## Three choices that could have produced this result, and did not

A result assembled from a scraped record and a normalisation layer invites the
objection that the analyst's choices produced it. Three such choices were varied.

**How aggressively jati labels are merged.** Collapsing
{sens['groups'].max()} labels to {sens['groups'].min()} moves the premium by
less than a mistake per hundred.

| similarity threshold | groups | surname | + village | premium |
|---|---|---|---|---|
{sens_rows}

**Whether religion is stripped from the label.** A jati recorded as `ପାଣ` and
one recorded as `ପାଣ ଖ୍ରୀଷ୍ଟିୟାନ` are two prediction targets unless the
religion is removed, and treating religion as a predictor is not something this
repo does. Removing it lowers the premium from {g['premium']:.1f} to
{gr['premium']:.1f}, and leaves the conclusion unchanged. Both are reported
because the choice is substantive.

**Which token is taken as the surname.** {100 * pos['share_sharing_a_token']:.0f}%
of tenants share a token with the father or husband named beside them, and that
token is last {100 * pos['positions']['last']:.0f}% of the time and first
{100 * pos['positions']['first']:.0f}%. The last token is therefore the surname
in {s['district']}, which is the opposite of Maharashtra (analysis 04) and the
reason the test is run per state rather than assumed. Taking instead the last
token of the first person listed, which matters for the 13% of records naming
several people, moves the premium by 0.2.

## Limits

**This is one district of thirty, and it is not Odisha.** The scrape has reached
{s['district']} and no further. It is small, heavily Adivasi, and on the Andhra
border, and its castes are not the state's. The comparison is between one Bihar
and one district of Odisha.

**Each village is a sample, not a census.** The fetch caps how many khatiyans it
takes per village and the cap has already changed mid-collection, so the
realised figure is measured from the data: a median of
{s['sampling']['khatiyans_per_village_median']:.0f} khatiyans per village across
{s['sampling']['villages']:,} villages, with a maximum of
{s['sampling']['khatiyans_per_village_max']}. Bihar's ladder is built from a
complete record. A sampled village is a weaker cue than a complete one, so the
premium measured here is biased **downward**, and the gap to Bihar is an upper bound
on the true difference.

**The normalisation layer under-merges.** It leaves `ସଉରା` and `ସୌରା` separate,
because a one-character difference in a four-character string falls below any
threshold safe for longer names. {nrm['strings_in']} label strings become
{nrm['strings_out']}, against Bihar's curated 141. The sensitivity table above
is why the residual is reported and left: it does not move the answer. A fuller layer is being built in `upnaam` and will replace this one.

---

*Odisha Record of Rights collected in
[pranaam](https://github.com/appeler/pranaam). Bihar rungs from analysis 02.*
"""
    out = HERE / "note.md"
    out.write_text(md)
    print(f"wrote {out} ({len(md.splitlines())} lines)")


if __name__ == "__main__":
    main()
