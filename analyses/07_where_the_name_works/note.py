"""Render analysis 07's note from its outputs."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", "out/fig"


def main() -> None:
    s = json.loads((TAB / "summary.json").read_text())
    t = pd.read_csv(TAB / "by_state.csv")
    dec = pd.read_csv(TAB / "decisive_names.csv")
    lo, hi = s["coverage_share_range"]
    best, worst = s["best"], s["worst"]
    # By coverage, not by result: the two orderings are different, and using
    # the result's endpoints here produced "Haryana at 4% against Assam at 4%".
    thinnest = t.loc[t["covered_share"].idxmin()]
    thickest = t.loc[t["covered_share"].idxmax()]
    by_state = t.set_index("state")
    punjab, assam, kerala = (by_state.loc[k] for k in ("punjab", "assam", "kerala"))

    rows = "\n".join(
        f"| {r.state} | {r.removed:.0f} | {r.removed_top25:.0f} | "
        f"{r.covered_share:.0f}% | {r.names:,} |"
        for r in t.itertuples()
    )

    def names_for(state: str) -> str:
        d = dec[dec.state == state]
        if d.empty:
            return "none"
        return ", ".join(
            f"`{r.last_name}` ({r.share_of_extract:.1f}% of them, {r.p_sc:.0%} Dalit)"
            for r in d.itertuples()
        )

    md = f"""# Where a surname works, and where it does not

Analyses 01 and 05 give one national number and split it by caste. Neither says
*where* in India a name works, and the spread across states is much wider than
the national figure suggests. The same guess closes **{best['removed']:.0f}% of
the gap in {best['state'].title()}** and **{worst['removed']:.0f}% in
{worst['state'].title()}**.

This is a description, not an explanation. An earlier version of this analysis
tried to explain the spread by how concentrated a state's names are. That does
not hold: concentration measured on the electoral roll correlates with the
result at +0.02, and measured inside the extract itself at -0.27. The spread is
real and worth showing; the reason for it is not established here.

## Read the coverage column first

Every number below describes the surnames that cleared outkast's 100-record
disclosure floor in that state, not the state. Those surnames cover between
**{lo:.0f}% and {hi:.0f}%** of a state's Census 2011 population, a factor of
six: {thinnest['state'].title()} at {thinnest['covered_share']:.0f}% against
{thickest['state'].title()} at {thickest['covered_share']:.0f}%. Coverage does
not track the result -- Assam closes the largest gap on 4% of its people and
Odisha closes half of one on 19% -- so it is a caution about reading levels,
not a correction to apply.

| state | gap closed (%) | top 25 names only | covers | names |
|---|---|---|---|---|
{rows}

![How much of the gap a surname closes, by state]({FIG}/where_it_works.png)

## The obvious objection, tested

The floor keeps a state's *commonest* names, and this repo's own finding is that
common names are the uninformative ones. So a state that retains few names might
look uninformative purely by construction, and Punjab retains 29 against Tamil
Nadu's 715.

Cutting every state to its 25 commonest names holds that constant. The ordering
survives (rank correlation
{s['top25_control']['spearman_with_full']:.2f}): Assam and Bihar stay near the
top, Punjab, Haryana, Kerala and Uttar Pradesh at the bottom. That is the second
column above, and the open circles in the figure.

## What carries a state is one or two big names

Not a count of them. Punjab has five majority-Dalit surnames among its 25
commonest and closes {punjab['removed']:.0f}% of the gap; Assam has two and
closes {assam['removed']:.0f}%.
The difference is that one of Assam's is `das`.

| state | its decisive surnames |
|---|---|
| Assam | {names_for('assam')} |
| Bihar | {names_for('bihar')} |
| Punjab | {names_for('punjab')} |
| Haryana | {names_for('haryana')} |

![The surnames that carry a state]({FIG}/decisive_names.png)

Punjab's two largest majority-Dalit names are `ram` at 62% and `lal` at 52%,
barely over the line and covering 6% of its retained surnames between them.
Bihar's are `paswan` and `manjhi` at 89%. Haryana has none at all: not one of
its 36 retained surnames is majority Dalit.

## Three things this cannot support

**A state's Scheduled Caste share.** The extract is not a census. It puts Punjab
at {punjab['sc_share_of_extract']:.0f}% Scheduled Caste,
which is higher than the Census figure for Punjab. Read the `covers` column
before reading anything into a base rate here.

**A comparison between states with very different base rates.** A surname
"points Dalit" when over half its bearers are, and that bar sits at
{kerala['sc_share_of_extract']:.1f}% of the extract in Kerala against
{punjab['sc_share_of_extract']:.1f}% in Punjab. The test is far more lenient in Punjab. Punjab still fails it, which is
the one direction the asymmetry can be read safely; Kerala against Punjab is not.

**Any claim about people whose surnames were suppressed.** The floor removes
rare names, and analysis 01 shows rare names are the informative ones. These
figures are a floor on what surnames reveal, not a ceiling.

## Why there is no leave-one-out column

Every cell here holds at least 100 records, so removing one person cannot flip
which category a surname points to. Leave-one-out returns the plug-in number
exactly, in every state. Elsewhere in this repo the two differ a great deal, and
the reason they do not here is the disclosure floor.

---

*Caste composition from [outkast](https://github.com/appeler/outkast)'s SECC
2011 extract, the same source as analyses 01 and 05. State populations from
Census 2011.*
"""
    out = HERE / "note.md"
    out.write_text(md)
    print(f"wrote {out} ({len(md.splitlines())} lines)")


if __name__ == "__main__":
    main()
