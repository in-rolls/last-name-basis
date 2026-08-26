# 03 — Much of what looks like a surname isn't one

Surname frequencies from [instate](https://github.com/appeler/instate)'s 2017
electoral rolls: 1.9M distinct tokens over 700M people.

**Finding.** The commonest "surname" in India is `devi`, an honorific. Thirteen
such tokens — devi, kumari, kaur, bai, rani, begam, khatun, bibi and the
ambiguous singh and kumar — sit in the surname slot for **19% of the country**.
Counting them makes Indian names look far more concentrated than they are: 18
tokens cover a quarter of India, but it takes 103 real family names. And these
are precisely the tokens analysis 01 finds carry no caste signal.

Read [`note.md`](note.md). Run with `make a03`.

| file | what |
|---|---|
| `titles.py` | the published title list, split into clear and ambiguous |
| `data.py` | instate frequencies; the Kerala initial share |
| `variants.py` | assign rare spellings to the common name they vary from |
| `figures.py` | concentration curves, title share, names-for-half, variant band |
| `pipeline.py` | entry point; writes `out/tab` and `out/fig` |
| `note.py` | renders `note.md` from the generated tables |

**The title list is a judgment**, so every figure reports three levels — as
written, minus honorifics, minus honorifics plus singh and kumar — and the list
is written to `out/tab/titles.csv` to be disagreed with.

**Limits.** Titles are not the only non-surname in the column; patronymics and
OCR debris are real and unquantified, so 19% is a floor. instate drops names
appearing fewer than three times and names shorter than three letters, and the
second removes most of Kerala and Tamil Nadu's initials.
