# 02 — How fast caste information dies as the place gets bigger

Bihar ladders from the `naampata` package in
`jati`, which is not public: the same surname scored against
successively coarser geographies, for 141 jatis and for the reservation
categories. The Muslim split uses the caste dictionary in
[land](https://github.com/in-rolls/land).

**Finding.** Surname plus village leaves you wrong 16 times in 100 about which
of 141 jatis someone belongs to. Drop the village and it is 47. Neither the name
nor the place is worth much alone; the pair is worth a great deal.

Also scores the **hamlet**, one rung below anything naampata ships: across
2.98M Scheduled Caste households, surname plus hamlet leaves you wrong 7 times in
100 against 12 at the village. Bihar's hamlets are often caste-named — `chamar
tola`, `mushar tola` — so the place alone (18) beats the surname alone (30).

Read [`note.md`](note.md). Run with `make a02`.

| file | what |
|---|---|
| `data.py` | locate the ladders; build the category-with-religion target |
| `mahadalit.py` | the raw Bihar census, scored one rung below the village |
| `figures.py` | atrophy curve, name-versus-place, the Singh waffles |
| `pipeline.py` | entry point; writes `out/tab` and `out/fig` |
| `note.py` | renders `note.md` from the generated tables |

Scoring lives in `src/last_name_basis/scoring.py`, shared with analysis 01.

**Limits.** Bihar only. The records ladder counts land-owning accounts, so it
under-represents the landless, who are disproportionately Dalit and EBC. The
census ladder covers Scheduled Caste households only. Surnames in these tables
are in Devanagari.

Inputs are read from sibling checkouts of `jati` and `land` if the packages are
not installed; the pipeline exits with a message rather than failing obscurely.
