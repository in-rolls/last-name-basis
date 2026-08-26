# 04 — Which token is actually the surname?

Analysis 03 rests on a list of names I wrote by hand. The electoral rolls can
measure it instead: every record carries the elector's **father or husband**, and
**a token appearing in both names is one that passed between two family
members** — which is what a family name is.

Read [`investigate.ipynb`](investigate.ipynb). Run with `make a04`.

## What it found

| | transmitted |
|---|---|
| devi, kumari, kaur, rani, bai, begam, khatun, bibi | **0.001 – 0.006** |
| singh | **0.78** |
| kumar | **0.08** |
| yadav, sharma, mandal, paswan, thakur | 0.85 – 0.96 |
| sanjay, ashok, suresh, ramesh, sunita, anita | under 0.02 |

The hand list was right about the ten sex-marking names and wrong about the two
it called ambiguous: **Singh mostly is inherited and Kumar mostly is not.** And
it missed a whole category — given names sitting in the last-name slot, which is
larger than everything on the list.

**It also caught a defect in analysis 03.** Maharashtra writes the surname first
(`patil ashwini`, father `patil ashok`), so instate's last-token `last_name`
holds a *given* name there. Analysis 03's Maharashtra and Gujarat figures have
been withdrawn rather than corrected in place.

## Where the method does not run

The relative's name is a bare given name in **Gujarat 100%**, **Tamil Nadu 96%**
and **Kerala 93%** of rows, so there is nothing to match against. A low score
there is a fact about the roll, not about naming — an earlier draft of this
analysis read Tamil Nadu's near-zero as evidence that Tamil naming has no family
names, which it is not. `method_applies` marks this, and the roll-up is
restricted to the seven states that pass.

## Other limits

It measures **patrilineal** transmission, so a title given to every man of a
community (Punjab's *singh*) is indistinguishable from a family name. Married
women match against a husband, so the score mixes inheritance with marriage.
Delhi has no relative name at all. OCR breaks matches that really existed.

A full scan reads ~1.5GB of gzipped rolls and takes about eight minutes, so
`out/tab/*.csv` is cached — delete it to recompute.

| file | what |
|---|---|
| `transmission.py` | the scorer; searches every position, credits every shared token |
| `investigate.ipynb` | the write-up, including both wrong turns |
