# Karnataka, where the last token is an initial

Analysis 04 found that Maharashtra writes the surname first, so a last-token
rule picks up a *given* name there. Karnataka breaks the same assumption by a
different route: **34% of last tokens are a
single letter**, and the six commonest are

`S` (2,601), `R` (1,794), `K` (1,741), `N` (1,682), `B` (1,156), `C` (994)

before any real surname appears. Drop single letters and the same list reads

`Kumar` (1,079), `Patil` (607), `Naik` (523), `Manjunatha` (375), `Biradar` (230), `Rathod` (177)

Two completely different inventories of "Karnataka's commonest surnames",
from the same 48,395 names.

![What a last-token rule calls a surname](out/fig/naive_vs_clean.png)

## Cleaning the initials out buys a little, and not much

| cue | distinct values | mistakes per 100 | share resolved |
|---|---|---|---|
| knowing nothing | — | 52.5 | — |
| naive last token | 6,979 | 45.3 | 88% |
| cleaned surname | 8,529 | 43.9 | 86% |
| PIN code | 1,381 | 51.5 | 99% |

Dropping the initials improves the guess by
1.3 mistakes per hundred. Against a blind
rate of 52, the naive token is worth
7.2 and the cleaned surname
8.6, so cleaning recovers roughly a sixth of
what a name is worth here.

An earlier version of this note reported that difference as a null, and as
slightly negative. That reading came from 14,854 candidates; the collection has
since reached 48,395, and the sign is now stable and the other way round.
The earlier figure was underpowered, and the honest lesson is about the sample
rather than about surnames.

Two things did not change with the extra data. The naive column is still a third
initials, and the cleaned surname still resolves *fewer* people than the naive
one, 86% against 88%,
because splitting the initial-buckets leaves more candidates alone in a cell.
The naive rule was never predicting from surnames. It was pooling candidates
into a handful of very large buckets keyed on a letter, which beats guessing
blind by a little.

**Neither cue is strong.** The better of the two still leaves
44 mistakes per
hundred. The PIN code is worth almost nothing, which is the opposite of what
geography does in Bihar, where a village takes 47 mistakes down to 17.

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

With 48,395 rows across four categories, and most surnames appearing once
or twice, everything above is scored leave-one-out. A plug-in score would report
memorisation.

---

*Karnataka PSC select lists, collected in
[pranaam](https://github.com/appeler/pranaam).*
