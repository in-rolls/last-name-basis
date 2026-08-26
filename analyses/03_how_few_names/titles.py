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

`AMBIGUOUS` is `singh` and `kumar`. Both are real inherited surnames for many
families *and* near-universal fillers -- Singh for every Sikh man and across the
Hindi belt, Kumar as a male counterpart to Kumari. Nothing in the rolls
separates the uses, so every figure is reported with and without them.

Not covered here: patronymics standing in the last-name slot, common in the
south, and OCR debris from scanned rolls. Both are real and neither is
quantified.
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
