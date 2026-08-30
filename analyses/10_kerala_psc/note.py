"""Render analysis 10's note from its outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", "out/fig"


def main() -> None:
    path = TAB / "summary.json"
    if not path.exists():
        print("skipped: analysis 10 not built")
        return
    s = json.loads(path.read_text())
    shape, scored = s["name_shape"], s["scored"]
    cues = pd.read_csv(TAB / "cues.csv").set_index("cue")
    last, written, given = (
        cues.loc[k] for k in ("last_token", "written_surname", "given_name")
    )
    dropped = scored["dropped"]

    md = f"""# Kerala, where the question often has no object

Everything else in this repo asks what a last name gives away about caste. In
Kerala that question frequently has nothing to land on.

**{100 * shape['last_token_is_a_single_letter']:.0f}% of last tokens are a single
letter.** None of the first tokens are. A name here is a given name followed by
initials standing for a father and a house: `KALPANA A`, `SHYLAJA E T`,
`SHAHUL HAMEED C K`. Only
{100 * shape['has_a_written_surname']:.0f}% of candidates have a written surname
at all, meaning a word after the given name that is not an initial.

So the honest thing is to measure the parts of a name that exist, and compare
them against the part every method in this repo reads.

| cue | who has one | distinct values | ranks a Dalit's higher |
|---|---|---|---|
| the last token | {100 * last['share_of_all']:.0f}% | {int(last['distinct_values']):,} | **{last['ranks_sc_higher']:.2f}** |
| a written surname | {100 * written['share_of_all']:.0f}% | {int(written['distinct_values']):,} | **{written['ranks_sc_higher']:.2f}** |
| the given name | {100 * given['share_of_all']:.0f}% | {int(given['distinct_values']):,} | **{given['ranks_sc_higher']:.2f}** |

Take one Scheduled Caste candidate and one other at random and rank the pair by
a cue; the last column is how often the Scheduled Caste candidate ranks higher.
A cue carrying nothing gives 0.50.

![What each part of a Kerala name gives away]({FIG}/cues.png)

**The last token, which is what a surname method reads, gives
{last['ranks_sc_higher']:.2f}.** A written surname gives
{written['ranks_sc_higher']:.2f}, and only a quarter of people have one. The
given name gives {given['ranks_sc_higher']:.2f} and everybody has one.

In Kerala the informative part of a name is the part no surname-based method
looks at. That is a stronger version of what analyses 04 and 08 found in
Maharashtra and Karnataka. There the last-token rule read the wrong token. Here
it often reads a letter, because there is no other token to read.

## What is being predicted, and what was set aside

Community in these lists is a **reservation category the candidate declared**,
not caste as an observer would record it. The scored comparison is Scheduled
Caste against everyone else inside the caste categories: Scheduled Caste,
Scheduled Tribe, other backward classes, and forward. That is
{scored['candidates']:,} candidates, {100 * scored['share_of_all']:.0f}% of the
file, of whom {100 * scored['sc_share']:.0f}% are Scheduled Caste.

Set aside: the Muslim bucket at {100 * dropped['Muslim']:.0f}% and the Christian
bucket at {100 * dropped['Christian']:.0f}%, because Kerala reserves for both and
scoring them would make religion a predictor, which this repo does not do.

Also set aside are the {100 * dropped['no community given']:.0f}% with no
community, treated here as missing at random. **The label pattern says they are
not.** `MENON` and `NAMBOOTHIRI` appear zero times in the community column and
`NAIR` 794 times, because a forward caste has no reservation to claim, so the
blanks are disproportionately forward caste. Dropping them removes the most
distinctive non-Dalit names from the comparison, which pushes every figure above
*down*. Read them as a floor.

## Limits

- These are people who applied for and obtained state government jobs. Nothing
  here describes Kerala.
- The given name carries religion as well as caste even inside the Hindu
  categories, and this cannot separate the two. The given-name figure is not a
  clean caste signal.
- Analysis 07 puts Kerala at 0.85 from the census extract and the electoral
  rolls. That is a different population, a different target and a different set
  of names, and the two should not be read as one number moving.

---

*Kerala PSC select lists, collected in
[pranaam](https://github.com/appeler/pranaam).*
"""
    out = HERE / "note.md"
    out.write_text(md)
    print(f"wrote {out} ({len(md.splitlines())} lines)")


if __name__ == "__main__":
    main()
