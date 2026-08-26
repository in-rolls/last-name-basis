# On a last-name basis

**How much does an Indian surname tell you about caste?**

Take a hundred adults at random: about 19 are Dalit, 6 Adivasi, 75 neither.
Guess "neither" every time and you get **25 of 100 wrong**. Now let yourself
hear their last name. You get **20 wrong**.

Five mistakes saved — and that average describes nobody. A few names settle the
question outright (Jha and Yadav cost you 0 and 1). But for **91% of people the
name does not change your answer at all**, and for **32% it makes the guess
harder** than it was for a stranger. Meanwhile the names that would help are
carried by almost no one: Devi, Singh and Kumar are the three commonest surnames
in India, and all three leave you no better off than a stranger would.

![A hundred people picked at random](out/fig/random_hundred.png)

Read [**`note/note.md`**](note/note.md) for the write-up. Every number in it
is generated; nothing is typed by hand.

![The commonest names in India tell you almost nothing](out/fig/common_and_empty.png)

## What is actually being measured

`P(caste | last name)` from [outkast](https://github.com/appeler/outkast)'s
disclosure-limited extract of the **Socio-Economic and Caste Census 2011** —
3,930 surnames, 19 states, 77M household-head records, pooled over states and
over adults.

Pooling over states is the "mixed city" assumption: you do not know where the
person is from. It is checked rather than asserted — knowing the state on its
own leaves you making 30 mistakes per hundred, exactly as many as knowing
nothing, while the name alone takes you to 20. The signal is caste, not
geography in disguise.

How *common* a name is comes from [instate](https://github.com/appeler/instate)'s
2017 electoral-roll counts, not from SECC. SECC records heads of household, who
are mostly men, so it undercounts women's surnames badly — Devi is 2.3M there
and Kumari 52k, when on the rolls Devi is the commonest surname in the country.

**Caste here means SC / ST / Other.** SECC has no OBC category, so the line
between backward and forward castes is invisible. This is the legibility of
Dalit and Adivasi status, nothing wider.

## Run it

```
uv venv .venv && uv pip install --python .venv/bin/python -e '.[dev]'
make all      # tables + figures into out/
make note     # renders note/note.md from out/tab
make test     # reconciliation checks
make lint
```

`outkast` is the only required data dependency. Roll frequencies and coverage
additionally use `instate`; without it the build still runs and reports those as
unavailable.

## Layout

| path | what |
|---|---|
| `src/last_name_basis/data.py` | load outkast cells, pool to one row per surname |
| `src/last_name_basis/metrics.py` | error, gain, bits, recall, signal decomposition |
| `src/last_name_basis/coverage.py` | roll frequencies; what share of a city is covered |
| `src/last_name_basis/report.py` | lookup, floor sensitivity, pooling comparison |
| `src/last_name_basis/figures.py` | the six figures |
| `scripts/build.py` | single entry point; writes `out/tab` and `out/fig` |
| `scripts/note.py` | renders the note from the generated tables |

## What is deliberately not here

No table ranked by how well a name identifies caste. Everything published is
ranked by name frequency or looked up by name. The finding is that surnames are
a weak signal; a ranked diagnosticity list would be a screening tool.

## Known limits

- Coverage is thin. Sood, Iyer, Balmiki and Agarwal are absent; Himachal,
  Karnataka, Andhra/Telangana, Jharkhand and Delhi are not in SECC at all.
  Against Delhi's 2017 roll the table speaks to 56% of surnames, and 27% of
  Delhi electors are listed with no surname at all.
- SECC records heads of household, so the reference population skews male and
  older.
- The 100-record suppression floor drops rare cells, which are the sharp ones.
  Raising the floor lowers measured informativeness, so these figures are
  conservative.
- This is a perfect guesser with one cue. A real person also has your first
  name, your father's or husband's name, your neighbourhood. A floor, not a
  ceiling.
