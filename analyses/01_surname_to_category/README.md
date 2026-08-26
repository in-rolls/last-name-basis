# 01 — What a surname alone says about caste, across India

`P(caste | last name)` from [outkast](https://github.com/appeler/outkast)'s
disclosure-limited extract of the Socio-Economic and Caste Census 2011, pooled
over 19 states and over adults. How common each name is comes from
[instate](https://github.com/appeler/instate)'s 2017 electoral-roll counts.

**Finding.** Guess a stranger's caste and you are wrong 25 times in 100. Hear
their surname and you are wrong 20. For 91% of people the name does not change
the answer at all, and for 32% it makes the guess harder.

Read [`note.md`](note.md). Run with `make a01`.

| file | what |
|---|---|
| `data.py` | load the outkast cells, pool to one row per surname |
| `metrics.py` | error, gain, recall, geography decomposition |
| `coverage.py` | roll frequencies; what share of a city the table can speak to |
| `report.py` | lookup, suppression-floor sensitivity, pooling comparison |
| `figures.py` | the six figures |
| `pipeline.py` | entry point; writes `out/tab` and `out/fig` |
| `note.py` | renders `note.md` from the generated tables |

**Caste here means SC / ST / Other.** SECC has no OBC category, so this is the
legibility of Dalit and Adivasi status and nothing wider. Analysis 02 has the
finer categories, for Bihar only.

`data.py` prefers the installed `outkast` package and falls back to a sibling
checkout only if it is missing.
