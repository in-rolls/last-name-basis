# Karnataka, where the last token is an initial

Analysis 04 found that Maharashtra writes the surname first, so a last-token
rule picks up a *given* name there. Karnataka breaks the same assumption by a
different route: **34% of last tokens are a
single letter**, and the six commonest are

`S` (772), `R` (550), `K` (534), `N` (514), `B` (375), `G` (304)

before any real surname appears. Drop single letters and the same list reads

`Kumar` (315), `Patil` (165), `Naik` (149), `Manjunatha` (114), `Biradar` (69), `Nagaraja` (55)

Two completely different inventories of "Karnataka's commonest surnames",
from the same 14,854 names.

![What a last-token rule calls a surname](out/fig/naive_vs_clean.png)

## Cleaning changes the names and not the prediction

This is the part worth reporting carefully, because it is a null and it went
against what I expected.

| cue | distinct values | mistakes per 100 | share resolved |
|---|---|---|---|
| knowing nothing | — | 54.5 | — |
| naive last token | 4,021.0 | 49.2 | 74% |
| cleaned surname | 4,919.0 | 49.6 | 69% |
| PIN code | 1,177.0 | 54.0 | 97% |

Cleaning moves the error by
+0.4 mistakes per hundred, which is to
say it does not move it. It slightly *worsens* it, and the reason is visible in
the last column: dropping initials splits 4,021.0 cells into
4,919.0 smaller ones, so fewer people share a cell with anyone
else and more fall back to the blind guess.

So the naive rule was never predicting well by using real surnames. It was
pooling people into a handful of enormous initial-buckets, which beats guessing
blind by a little, exactly as the cleaned surnames do.

**Neither is worth much.** Against a blind rate of 55, the best of them
leaves 49. The PIN
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

With 14,854 rows across four categories, and most surnames appearing once
or twice, everything above is scored leave-one-out. A plug-in score would report
memorisation.

---

*Karnataka PSC select lists, collected in
[pranaam](https://github.com/appeler/pranaam).*
