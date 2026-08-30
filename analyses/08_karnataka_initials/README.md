# 08 — Karnataka, where the last token is an initial

Analysis 04 found Maharashtra writes the surname first, so a last-token rule
picks up a given name there. Karnataka breaks the same assumption differently.

**Finding.** **34% of last tokens in Karnataka are a single letter.** The six
commonest are `S`, `R`, `K`, `N`, `B`, `G` — eleven initials before the first
real surname. Drop single letters and the list becomes `Kumar`, `Patil`, `Naik`,
`Manjunatha`, `Biradar`, `Nagaraja`: two completely different inventories of
"Karnataka's commonest surnames" from the same 14,854 names.

**Cleaning buys a little.** 45.3 mistakes per 100 naive against 43.9 cleaned,
versus 52.5 knowing nothing, so dropping the initials recovers about a sixth of
what a name is worth here. Neither cue is strong. The cleaned surname still
resolves fewer candidates than the naive one, 86% against 88%, because splitting
the initial-buckets leaves more of them alone in a cell: the naive rule was never
using surnames to predict, it was pooling people into a few enormous
initial-buckets.

An earlier version of this reported the difference as a null and slightly
negative, on 14,854 candidates. At 48,395 the sign is stable and the other way
round. That earlier reading was underpowered.

**Scope.** These are Public Service Commission select lists — educated
applicants for government jobs — and the category is self-declared for a quota,
not observed caste. Nothing here estimates a population quantity. Karnataka's
backward-class codes are collapsed into one OBC bucket.

Run with `make a08`. Read [the note](note.md).
