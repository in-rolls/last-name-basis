# 03 — India's commonest last name tells you nothing

Surname frequencies from [instate](https://github.com/appeler/instate)'s 2017
electoral rolls (1.9M names over 700M people), plus first-name gender from
[naampy](https://github.com/appeler/naampy).

**Finding.** The commonest last name in India is `devi`, at 6.5% of the roll. It
is a real last name — but it records the bearer's sex, not her family. On the
Bihar rolls **81% of women carry a name from this group against 10% of men**, and
the family names in the same state read as 84–89% male because those families'
women are on the roll as Devi. A woman and her brother do not share a last name.

That is why these names carry no caste signal: a name assigned by sex cannot
track a lineage. Thirteen of them cover 19% of the country.

Counting them does not overstate how concentrated Indian naming is; it is that
concentrated, and Devi is genuinely what tens of millions of women are called on
a roll. What the count changes is what it is a count *of*. Eighteen names cover
a quarter of India, and 103 if you count only names a brother and sister share,
so the first figure describes names and the second describes lineages. The
spread of a name like Devi across castes is not noise obscuring a caste signal.
It is one of the ways the signal was removed.

Read [`note.md`](note.md). Run with `make a03`.

| file | what |
|---|---|
| `titles.py` | the published list, split into unambiguous and hard cases |
| `data.py` | instate frequencies; sex-marking shares; the Kerala initial share |
| `variants.py` | assign rare spellings to the common name they vary from |
| `figures.py` | sex-marking, concentration curves, names-for-half, variant band |
| `pipeline.py` | entry point; writes `out/tab` and `out/fig` |
| `note.py` | renders `note.md` from the generated tables |

**The list is a judgment**, so every figure reports three levels — as written,
minus sex-marking names, minus those plus singh and kumar — and the list lives in
[`titles.py`](titles.py) with a reason beside each name.

**Limits.** The sex split needs a first name naampy can gender, which covers 61%
of Bihar but only 4% of Tamil Nadu; anything under a fifth is dropped rather than
reported. The per-state sex pass reads the raw rolls and takes minutes, so its
result is cached in `out/tab/sex_marked.csv` — delete that to recompute. instate
drops names appearing fewer than three times and shorter than three letters,
which removes most of Kerala's and Tamil Nadu's initials.
