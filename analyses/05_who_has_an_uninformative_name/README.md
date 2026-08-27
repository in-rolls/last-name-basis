# 05 — Whose name tells you nothing

The other analyses report an average. This asks *who*, because if the
uninformative names are not spread evenly then every name-based caste method has
differential error in a knowable direction.

**Finding.** The guess is wrong about **66 of every 100 Dalits** and **4 of
every 100 people outside the schedules**, a seventeen-fold gap that weights up
to the 20 mistakes per hundred it makes overall. Any method inferring caste from
an Indian surname misses most Scheduled Caste individuals while classifying
nearly everyone else correctly.

Note what that does *not* say. The name is not useless for Dalits: it is the
group it helps most, from wrong about all of them to wrong about 66 in a
hundred. It still leaves them far and away the worst served, which is the part
that matters downstream.

**And a null.** The obvious companion prediction — that women fare worse, since
a woman in the Hindi belt is often recorded under a sex-marking name — does not
hold consistently. With surnames resolved by Upnaam, women are worse off in
Bihar by 3.3 mistakes per 100, better off in Rajasthan by 1.4, and effectively
even in Maharashtra. Correcting Maharashtra from the final to the first token
changes its estimated gap from +0.85 to -0.19.

Read [`note.md`](note.md). Run with `make a05`.

| file | what |
|---|---|
| `data.py` | caste- and sex-weighted error; roll sexing via naampy |
| `figures.py` | the two exhibits |
| `pipeline.py` | entry point |
| `note.py` | renders `note.md` |

**Limits.** SC/ST/Other only. The caste split decomposes the same table it
evaluates, so it is the ceiling a perfect user of that table would hit, not a
fitted model's performance. The sex split covers only Bihar, Rajasthan, and
Maharashtra under Upnaam `resolver-v1`; its gendered-record coverage is 61%,
21%, and 66%, respectively. Nothing per-name is published.
