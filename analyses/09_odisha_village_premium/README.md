# 09 — Does the village premium travel outside Bihar?

Bihar's land records support this repo's strongest single result: across 141
jatis a surname alone leaves 47 mistakes per 100 and a surname with a village
leaves 17. Whether that 30-point difference describes surnames and villages in
general, or describes Bihar, was untested.

**Finding.** Scored on the same protocol across **30 districts and 10,609
villages of Odisha**, 4.77M tenants, **a village adds 24 points where in Bihar
it adds 30**. Against what the surname leaves unresolved, the village closes
52% of the remainder here and 64% in Bihar. The premium travels; it is smaller.

**The premium is not one number.** Scored district by district it runs from 2.5
to 22.4 points, median 11.4 — and the pooled figure of 24.4 is larger than any
single district. Naming a village in the pooled problem also names a district
and a region, so the pooled village carries geography that a district-level
score has already held fixed. Bihar's 30 is pooled too, which is why the pooled
row is the like-for-like comparison and the district table is the honest way to
read the spread.

**The levels are not comparable and the figure does not invite it.** Bihar sorts
people among 141 curated jatis, Odisha among 5,389 labels as recorded. A harder
target costs mistakes whatever the surname does, so the quantity that carries
across is the distance between the rungs. Both happen to leave about 47 at the
surname alone; nothing follows from that.

**Three choices were varied and none produced the result.** Collapsing the
labels to little more than half as many moves the premium by less than a
mistake. Stripping the religion suffix from the jati label moves it from 24.4
to 23.7. The last token is the surname in 92% of tenants who share one with the
relative named beside them, so that rule is measured here rather than assumed.

**Scope.** The scrape is unfinished: 30 districts and 10,609 villages, but a
fraction of the state's estimated 25 million khatiyans, and districts entered
the crawl in a deliberate order rather than at random. A completed village is
now censused rather than sampled — a median of 98 khatiyans per village against
35 when this analysis first ran — but villages still in progress are partial,
so the premium remains biased downward and the gap to Bihar is an upper bound.

On analysis 02's axis, both places give the same shape at different depths, and
the lines cross: the village is worth more in Bihar, the larger units more in
Odisha.

![Error rising as the place gets bigger](out/fig/atrophy.png)

Run with `make a09`. Read [the note](note.md).
