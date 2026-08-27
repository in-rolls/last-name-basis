# 08 — Karnataka, where the last token is an initial

Analysis 04 found Maharashtra writes the surname first, so a last-token rule
picks up a given name there. Karnataka breaks the same assumption differently.

**Finding.** **34% of last tokens in Karnataka are a single letter.** The six
commonest are `S`, `R`, `K`, `N`, `B`, `G` — eleven initials before the first
real surname. Drop single letters and the list becomes `Kumar`, `Patil`, `Naik`,
`Manjunatha`, `Biradar`, `Nagaraja`: two completely different inventories of
"Karnataka's commonest surnames" from the same 14,854 names.

**And a null.** Cleaning changes the names and not the prediction: 49.2 mistakes
per 100 naive against 49.6 cleaned, versus 54.5 knowing nothing. It is slightly
*worse*, because splitting the initial-buckets into real surnames leaves fewer
people sharing a cell with anyone (74% resolved down to 69%). The naive rule was
never using surnames to predict; it was pooling people into a few enormous
initial-buckets.

**Scope.** These are Public Service Commission select lists — educated
applicants for government jobs — and the category is self-declared for a quota,
not observed caste. Nothing here estimates a population quantity. Karnataka's
backward-class codes are collapsed into one OBC bucket.

Run with `make a08`. Read [the note](note.md).
