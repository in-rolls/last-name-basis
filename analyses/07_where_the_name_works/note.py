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
        f"| {r.state} | {r.removed:.0f} | {r.ranks_dalit_higher:.2f} | "
        f"{r.removed_top25:.0f} | {r.covered_share:.0f}% | {r.names:,} |"
        for r in t.itertuples()
    )
    by_rank = t.set_index("state")["ranks_dalit_higher"]
    kerala_rank = f"{by_rank.get('kerala', float('nan')):.2f}"
    maharashtra_rank = f"{by_rank.get('maharashtra', float('nan')):.2f}"
    punjab_rank = f"{by_rank.get('punjab', float('nan')):.2f}"
    haryana_rank = f"{by_rank.get('haryana', float('nan')):.2f}"
    kerala_share = f"{t.set_index('state').loc['kerala', 'sc_share_of_extract']:.0f}"

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

| state | gap closed (%) | ranks Dalit higher | top 25 names only | covers | names |
|---|---|---|---|---|---|
{rows}

![How much of the gap a surname closes, by state]({FIG}/where_it_works.png)

## Two measures, and where they disagree

The gap-closed column is accuracy against the largest category, so a state's
composition moves it as much as its surnames do. The next column is not: take
one Dalit and one non-Dalit from the state at random, rank the pair by what
their surnames say, and it is how often the Dalit ranks higher. A surname
carrying nothing gives 0.50.

The two agree on the ordering broadly and part company at the bottom, which is
where the conclusion lived. Kerala closes under 1% of the gap and ranks at
{kerala_rank}, about level with Maharashtra at {maharashtra_rank}. Kerala's
surnames separate Dalit from non-Dalit perfectly respectably; they seldom change
the answer because only {kerala_share}% of its extract is Scheduled Caste, so
raising the odds still rarely crosses a half.

Punjab and Haryana are different. At {punjab_rank} and {haryana_rank} against a
floor of 0.50, those are states whose surnames genuinely carry little about
caste. Grouping them with
Kerala, as the gap-closed column alone does, puts two unlike things together.

![Deciding badly is not the same as carrying nothing]({FIG}/discriminates.png)

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

## What the extract will not tell you

**A state's Scheduled Caste share.** The extract is not a census. It puts Punjab
at {punjab['sc_share_of_extract']:.0f}% Scheduled Caste,
which is higher than the Census figure for Punjab. Read the `covers` column
before reading anything into a base rate here.

**A comparison of gap-closed between states with different base rates.** A
surname "points Dalit" when over half its bearers are, and that bar sits at
{kerala['sc_share_of_extract']:.1f}% of the extract in Kerala against
{punjab['sc_share_of_extract']:.1f}% in Punjab, so the test is far more lenient
there. Compare the ranking column across states instead, which is what it is
for; the gap-closed column is comparable only among states of similar
composition.

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
