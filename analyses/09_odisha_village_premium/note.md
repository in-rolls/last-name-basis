# Does the village premium travel outside Bihar?

Bihar's land records support the strongest single result in this repo. Across
141 jatis a surname alone leaves 47 mistakes per 100, and a
surname together with a village leaves 17. The question
that result raises is whether the 30-point difference describes
surnames and villages in general or describes Bihar.

The Odisha Record of Rights records a jati and a village for every tenant, which
makes the same measurement possible elsewhere. Scored on the same protocol
across **30 districts and 10,609 villages**, a village
adds 24 points where in Bihar it adds 30.
Relative to what the surname leaves unresolved, the village closes
52% of the remainder here against
64% in Bihar.

![What a village adds, in Bihar and in Odisha](out/fig/village_premium.png)

Put on analysis 02's axis, the two places produce the same shape at different
depths: they converge once the place is discarded and separate as it is
restored.

![Error rising as the place gets bigger, in both places](out/fig/atrophy.png)

## What is being compared, and what is not

The two levels are not comparable and the figure is drawn so as not to invite
the comparison. Bihar sorts people among 141 curated jatis; Odisha sorts them
among 5,389 labels as recorded. A harder target produces more mistakes
whatever the surname does, so the quantity that carries across places is the
distance between the two rungs rather than the height of either.

Both places happen to leave about 47 mistakes at the surname
alone -- 47.3 in Bihar against 46.8 here. Nothing
follows from that. They are counting against 141 groups and
5,389, so equal heights are not evidence that surnames are equally
informative.

## The premium is not one number

Pooling districts hides that they disagree. Scored separately, the premium runs
from 3 to 22 points across the
30 districts large enough to score, with a median of
11.

| district | tenants | labels | surname | + village | premium |
|---|---|---|---|---|---|
| ବୌଦ୍ଧ | 85,172 | 254 | 44.5 | 22.1 | **22.4** |
| ଗଂଜାମ | 72,953 | 197 | 37.2 | 17.7 | **19.5** |
| ସୁନ୍ଦରଗଡ଼ | 869,388 | 2208 | 41.9 | 24.5 | **17.4** |
| ଗଜପତି | 412,253 | 1089 | 49.7 | 33.8 | **15.9** |
| ନୟାଗଡ଼ | 34,938 | 166 | 33.5 | 18.2 | **15.3** |
| କୋରାପୁଟ | 76,636 | 453 | 24.3 | 18.7 | **5.6** |
| ନବରଂଗପୁର | 56,392 | 224 | 14.9 | 10.5 | **4.4** |
| ମୟୂରଭଞ୍ଜ | 44,952 | 254 | 15.9 | 12.1 | **3.7** |
| ପୁରୀ | 15,426 | 62 | 14.6 | 11.9 | **2.6** |
| ଦେବଗଡ଼ | 11,960 | 161 | 30.0 | 27.5 | **2.5** |

*The five districts with the largest premium and the five with the smallest.*

Gajapati, the single district this analysis first reported, gives 16 points scored on its own, against the 24 pooled across the state. The figure published from one district was 20.

**The pooled premium is larger than every district's.** Pooled it is
24; the largest single district is 22
and the median is 11. That is not a paradox and it
is not an error. Naming a village in the pooled problem also names a district
and a region, so the village is carrying geography the district-level scores
have already held fixed. Read the pooled number as what a village is worth to
someone guessing anywhere in Odisha, and the district numbers as what it is
worth to someone who already knows the district. Bihar's 30 is
a pooled figure too, so the pooled row is the like-for-like comparison.

## Three choices that could have produced this result, and did not

A result assembled from a scraped record and a normalisation layer invites the
objection that the analyst's choices produced it. Three such choices were varied.

**How aggressively jati labels are merged.** Collapsing
5,389 labels to 2,059 moves the premium by
less than a mistake per hundred.

| similarity threshold | groups | surname | + village | premium |
|---|---|---|---|---|
| 92 | 5389 | 46.8 | 22.4 | **24.4** |
| 85 | 4048 | 45.4 | 21.1 | **24.3** |
| 78 | 2978 | 44.7 | 20.4 | **24.3** |
| 72 | 2059 | 44.0 | 19.9 | **24.1** |

**Whether religion is stripped from the label.** A jati recorded as `ପାଣ` and
one recorded as `ପାଣ ଖ୍ରୀଷ୍ଟିୟାନ` are two prediction targets unless the
religion is removed, and treating religion as a predictor is not something this
repo does. Removing it moves the premium from 24.4 to
23.7. Both are reported because the choice is substantive.

**Which token is taken as the surname.**
90% of tenants share a token with the
father or husband named beside them, and that token is last
92% of the time and first
6%. The last token is therefore the surname
in Odisha, which is the opposite of Maharashtra (analysis 04) and the reason the
test is run per state rather than assumed.

## Limits

**The scrape is not finished.** It has reached 30 districts and
10,609 villages, a fraction of the state's estimated 25 million
khatiyans. Districts entered the crawl in a deliberate order rather than at
random, so what is scored here is not a random sample of Odisha, and the
per-district table is the honest way to read it.

**A finished village is a census; a village in progress is not.** The fetch no
longer caps khatiyans per village, so a completed village is enumerated rather
than sampled: a median of
98 khatiyans per village across
10,609 villages, against a median of 35 when this
analysis first ran, with a maximum of
4,424. Villages the crawl is still
working through remain partial, and a partial village is a weaker cue than a
complete one, so the premium is still biased **downward** and the gap to Bihar
remains an upper bound.

**The normalisation layer under-merges.** It leaves `ସଉରା` and `ସୌରା` separate,
because a one-character difference in a four-character string falls below any
threshold safe for longer names. 6,507 label strings become
5,389, against Bihar's curated 141. The sensitivity table above
is why the residual is reported and left: it does not move the answer. A fuller
layer is being built in `upnaam` and will replace this one.

---

*Odisha Record of Rights collected in
[odisha-ror](https://github.com/in-rolls/odisha-ror). Bihar rungs from analysis
02.*
