# Where a surname works, and where it does not

Analyses 01 and 05 give one national number and split it by caste. Neither says
*where* in India a name works, and the spread across states is much wider than
the national figure suggests. The same guess closes **67% of
the gap in Assam** and **0% in
Haryana**.

This is a description, not an explanation. An earlier version of this analysis
tried to explain the spread by how concentrated a state's names are. That does
not hold: concentration measured on the electoral roll correlates with the
result at +0.02, and measured inside the extract itself at -0.27. The spread is
real and worth showing; the reason for it is not established here.

## Read the coverage column first

Every number below describes the surnames that cleared outkast's 100-record
disclosure floor in that state, not the state. Those surnames cover between
**3% and 19%** of a state's Census 2011 population, a factor of
six: Kerala at 3% against
Odisha at 19%. Coverage does
not track the result -- Assam closes the largest gap on 4% of its people and
Odisha closes half of one on 19% -- so it is a caution about reading levels,
not a correction to apply.

| state | gap closed (%) | top 25 names only | covers | names |
|---|---|---|---|---|
| assam | 67 | 65 | 4% | 161 |
| bihar | 61 | 59 | 14% | 557 |
| gujarat | 53 | 51 | 4% | 390 |
| west bengal | 50 | 38 | 14% | 616 |
| odisha | 49 | 36 | 19% | 457 |
| chhattisgarh | 39 | 30 | 5% | 120 |
| rajasthan | 38 | 31 | 8% | 242 |
| madhya pradesh | 36 | 23 | 7% | 345 |
| maharashtra | 31 | 23 | 5% | 751 |
| uttarakhand | 28 | 28 | 8% | 43 |
| tamilnadu | 9 | 4 | 5% | 715 |
| punjab | 3 | 3 | 9% | 29 |
| uttar pradesh | 2 | 0 | 5% | 612 |
| kerala | 1 | 0 | 3% | 230 |
| haryana | 0 | 0 | 4% | 36 |

![How much of the gap a surname closes, by state](out/fig/where_it_works.png)

## The obvious objection, tested

The floor keeps a state's *commonest* names, and this repo's own finding is that
common names are the uninformative ones. So a state that retains few names might
look uninformative purely by construction, and Punjab retains 29 against Tamil
Nadu's 715.

Cutting every state to its 25 commonest names holds that constant. The ordering
survives (rank correlation
0.98): Assam and Bihar stay near the
top, Punjab, Haryana, Kerala and Uttar Pradesh at the bottom. That is the second
column above, and the open circles in the figure.

## What carries a state is one or two big names

Not a count of them. Punjab has five majority-Dalit surnames among its 25
commonest and closes 3% of the gap; Assam has two and
closes 67%.
The difference is that one of Assam's is `das`.

| state | its decisive surnames |
|---|---|
| Assam | `das` (10.4% of them, 65% Dalit), `mandal` (0.8% of them, 57% Dalit), `sarkar` (0.6% of them, 53% Dalit) |
| Bihar | `ram` (5.2% of them, 80% Dalit), `paswan` (4.1% of them, 89% Dalit), `manjhi` (1.9% of them, 89% Dalit) |
| Punjab | `ram` (3.6% of them, 62% Dalit), `lal` (2.5% of them, 52% Dalit), `pal` (0.6% of them, 59% Dalit) |
| Haryana | none |

![The surnames that carry a state](out/fig/decisive_names.png)

Punjab's two largest majority-Dalit names are `ram` at 62% and `lal` at 52%,
barely over the line and covering 6% of its retained surnames between them.
Bihar's are `paswan` and `manjhi` at 89%. Haryana has none at all: not one of
its 36 retained surnames is majority Dalit.

## Three things this cannot support

**A state's Scheduled Caste share.** The extract is not a census. It puts Punjab
at 38% Scheduled Caste,
which is higher than the Census figure for Punjab. Read the `covers` column
before reading anything into a base rate here.

**A comparison between states with very different base rates.** A surname
"points Dalit" when over half its bearers are, and that bar sits at
7.6% of the extract in Kerala against
38.1% in Punjab. The test is far more lenient in Punjab. Punjab still fails it, which is
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
