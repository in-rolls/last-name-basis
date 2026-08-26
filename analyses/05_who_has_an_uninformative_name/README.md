# 05 — Whose name tells you nothing

The other analyses report an average. This asks *who*, because if the
uninformative names are not spread evenly then every name-based caste method has
differential error in a knowable direction.

**Finding.** A Dalit is guessed wrong **29 times in 100 against a blind rate of
30** — the name buys essentially nothing — while someone outside the schedules
gets **17**. Recall is 34% against 96%. Any method that infers caste from an
Indian surname is roughly as good as chance for Scheduled Caste individuals and
substantially better than chance for everyone else.

**And a null.** The obvious companion prediction — that women fare worse, since
a woman in the Hindi belt is often recorded under a sex-marking name — does not
hold. Women are worse off in Bihar by 3 mistakes per 100 and *better* off in
Uttar Pradesh by 2. Devi sits at the base rate; Ram, Das and Lal, which men
carry, are well above it.

Read [`note.md`](note.md). Run with `make a05`.

| file | what |
|---|---|
| `data.py` | caste- and sex-weighted error; roll sexing via naampy |
| `figures.py` | the two exhibits |
| `pipeline.py` | entry point |
| `note.py` | renders `note.md` |

**Limits.** SC/ST/Other only. The caste split decomposes the same table it
evaluates, so it is the ceiling a perfect user of that table would hit, not a
fitted model's performance. Nothing per-name is published.
