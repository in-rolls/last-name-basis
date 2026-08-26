"""Last names that record the bearer's sex rather than their family.

An earlier draft called these "not real surnames", which is wrong. Devi is a
last name: it is on the Aadhaar card, on the roll, on the school record, and it
is what the woman is called. Nobody appends it as a title any more.

What makes it different from Sharma is who carries it. On the Bihar rolls, 81%
of women have a last name from this list against 10% of men, and the family
names in the same state read as 84-89% male because those families' women are
recorded as Devi. So for most women in the Hindi belt the last-name slot encodes
sex, and the family name their brothers carry is simply absent.

That is why these names carry no caste signal. A name assigned by sex cannot
track a lineage, and analysis 01 finds exactly that: devi costs 24 mistakes per
hundred against 30 for knowing nothing at all.

`CLEAR` are unambiguously sex-marking: no man is called Devi or Kumari.

`AMBIGUOUS` is `singh` and `kumar`, and analysis 04 has since measured both by
asking how often each is shared with the bearer's father or husband. **Singh
transmits 78% of the time and Kumar 8%.** So Singh is mostly a real inherited
surname and grouping it here was wrong; Kumar mostly is not. Both stay in this
set so the three reporting levels remain comparable with earlier versions of the
note, but the `measured` level in the pipeline is the one to trust.

Not covered by this list, and found by analysis 04's measurement instead: given
names sitting in the last-name slot, which is a larger category than anything
here -- sanjay, ashok, suresh, ramesh, sunita and anita all transmit under 2% of
the time. Some of that is real naming practice and some is that instate takes
the last token, which is a given name in surname-first states.
"""

from __future__ import annotations

import pandas as pd

CLEAR = {
    "devi": "carried by women only",
    "kumari": "carried by unmarried women",
    "kaur": "given to every Sikh woman",
    "bai": "carried by women, western and central India",
    "rani": "carried by women",
    "begam": "carried by Muslim women",
    "begum": "carried by Muslim women",
    "khatun": "carried by Muslim women",
    "bibi": "carried by Muslim women",
    "banu": "carried by Muslim women",
    "beevi": "carried by Muslim women, Kerala",
    "sri": "honorific for a man, rarely a family name",
    "smt": "abbreviation of Srimati, for a married woman",
}

AMBIGUOUS = {
    "singh": "every Sikh man, and a filler; also a real surname",
    "kumar": "male counterpart to kumari; also a real surname",
}

LEVELS = {
    "as_written": set(),
    "minus_clear": set(CLEAR),
    "minus_all": set(CLEAR) | set(AMBIGUOUS),
}

LEVEL_LABEL = {
    "as_written": "names as written on the roll",
    "minus_clear": "minus sex-marking names",
    "minus_all": "minus sex-marking names, singh and kumar",
}


def table() -> pd.DataFrame:
    """The list itself, so it can be disagreed with."""
    rows = [
        {"token": t, "kind": kind, "why": why}
        for kind, d in (("clear", CLEAR), ("ambiguous", AMBIGUOUS))
        for t, why in d.items()
    ]
    return pd.DataFrame(rows)
