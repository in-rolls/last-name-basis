# 06 — Does knowing your neighbours give you away?

Analysis 02's "surname + village" **memorises the village**. This holds out whole
villages, so the only thing available is the composition of the *other* surnames
there — the situation anyone inferring caste about a stranger is actually in.

**On average it helps a little.** In villages never seen during fitting, the
name alone costs 48 mistakes per 100 and the name plus neighbours costs 44.
About four saved, against the 48-to-17 gap that memorising the village closes.

**But the average hides the answer.** The claim was about particular names, and
those move far more: Chaudhary **80 → 56**, Prasad **72 → 54**, Devi and Singh
about nine each. Names that already identify you — Paswan at 6 — gain nothing.
It is a tendency rather than a law: Thakur gets three *worse*.

So the repo's headline needs qualifying, not retracting. A surname alone is weak.
A surname is not weak once you know where its bearer lives.

Read [`note.md`](note.md). Run with `make a06`.

| file | what |
|---|---|
| `neighbours.py` | held-out-village split, co-occurrence model, per-surname scoring |
| `figures.py` | the bracket, and which names get rescued |
| `pipeline.py` | entry point |
| `note.py` | renders `note.md` |

**One design failed first, and it is documented rather than deleted.** Averaging
`P(jati | surname)` over the neighbours yields a near-uniform smear and scores
*worse than blind*; it moved the headline 0.1 and would have licensed a false
null. Scoring the neighbour cue alone is what caught it and is now a permanent
test. A second correction: the mixing parameter's search range topped out below
the optimum, which understated the gain by half.

**Limits.** Bihar only; landowning households for one ladder. Village-level
composition, not true walk-order neighbours — rolls have house numbers but no
caste, so a finer cue could not be scored and is left unmeasured. Aggregate error
rates only; no model or per-person output is published.
