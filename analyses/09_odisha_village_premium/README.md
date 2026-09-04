# 09 — Does the village premium travel outside Bihar?

Bihar's land records support this repo's strongest single result: across 141
jatis a surname alone leaves 47 mistakes per 100 and a surname with a village
leaves 17. Whether that 30-point difference describes surnames and villages in
general, or describes Bihar, was untested.

**Finding.** Scored on the same protocol across **30 districts and 10,609
villages of Odisha**, 4.77M tenants, **a village adds 24 points where in Bihar
it adds 30**. Against what the surname leaves unresolved, the village closes
54% of the remainder here and 64% in Bihar. The premium travels; it is smaller.

**The premium is not one number.** Scored district by district it runs from 2.2
to 22.8 points, median 10.7 — and the pooled figure of 24.0 is larger than any
single district. Naming a village in the pooled problem also names a district
and a region, so the pooled village carries geography that a district-level
score has already held fixed. Bihar's 30 is pooled too, which is why the pooled
row is the like-for-like comparison and the district table is the honest way to
read the spread.

**The ladders cross.** Odisha is the easier target at every size of place
except the finest — 44 mistakes at the surname alone against Bihar's 47 — and
Bihar overtakes it exactly when the village arrives. The village does something
in Bihar that no larger unit does; Odisha's gain is spread across the scales.

**The levels are not comparable.** Bihar sorts people among 141 curated jatis,
Odisha among 5,756 label strings — but that count is misleading, and the honest
one is smaller: **485 labels carry 99% of tenants**. The rest is a tail of a few
households each, which costs almost nothing in the scoring and everything in how
hard the target looks.

**Merging spellings is evidence-gated, because spelling alone would be wrong.**
`ଚମାର`/`କମାର`, `ଗଣ୍ଡ`/`ଗଣ୍ଡା` and `ଭୂମିଆ`/`ଭୂମିଜ` are each one edit apart and
each two different jatis. Nearness proposes a merge; it is confirmed only when
the two labels' surname distributions agree, a signal sharing no input with the
string. Measured against pairs known from the caste names, same-jati pairs score
0.31 to 0.99 and different-jati pairs 0.00 to 0.10. 414,799 households were
merged and 4,654 candidates refused; both lists are published with their scores.
Moving the gate from 0.15 to 0.60 moves the premium by 0.13.

**Other choices were varied and none produced the result.** Stripping the
religion suffix from the jati label moves the premium from 24.0 to 23.3. The
last token is the surname for 92% of tenants who share one with the relative
named beside them, so that rule is measured here rather than assumed.

**Scope.** The scrape is unfinished: 30 districts and 10,609 villages, but a
fraction of the state's estimated 25 million khatiyans, and districts entered
the crawl in a deliberate order rather than at random. A completed village is
now censused rather than sampled — a median of 98 khatiyans per village against
35 when this analysis first ran — but villages still in progress are partial,
so the premium remains biased downward and the gap to Bihar is an upper bound.

![Error rising as the place gets bigger](out/fig/atrophy.png)

Run with `make a09`. Read [the note](note.md).
