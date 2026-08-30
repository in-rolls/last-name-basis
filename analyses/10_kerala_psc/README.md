# 10 — Kerala, where the question often has no object

Everything else here asks what a last name gives away about caste. In Kerala
that question frequently has nothing to land on.

**Finding.** 78% of last tokens are a single letter, and only 27% of candidates
have a written surname at all. A name is a given name plus initials standing for
a father and a house: `KALPANA A`, `SHYLAJA E T`. Scoring the parts that exist:

| cue | who has one | ranks a Dalit's higher |
|---|---|---|
| the last token, what every method reads | 100% | **0.59** |
| a written surname | 27% | **0.70** |
| the given name | 100% | **0.69** |

The informative part of a Kerala name is the part no surname-based method looks
at. That is a stronger version of analyses 04 and 08: in Maharashtra and
Karnataka a last-token rule reads the wrong token, and here it reads a letter,
because there is no other token to read.

**Scope.** Community is a reservation category the candidate declared, not
observed caste. Scored on Scheduled Caste against the other caste categories,
866,812 candidates at 19% Scheduled Caste. The Muslim (16%) and Christian (7%)
buckets are set aside, since Kerala reserves for both and scoring them would
make religion a predictor. The 17% with no community are treated as missing at
random, though the label pattern says otherwise: forward castes have no
reservation to claim, so dropping blanks removes the most distinctive non-Dalit
names and pushes every figure down. Read them as a floor.

Run with `make a10`. Read [the note](note.md).
