"""Tokens that sit in the surname position without being family names.

The commonest "surname" in India is `devi`, at 6.5% of the electoral roll. It is
an honorific attached to women's names, not a family name, and neither are
`kumari`, `kaur`, `bai`, `rani`, `begam`, `khatun` or `bibi`. Counting them as
surnames makes India's names look far more concentrated than they are.

The list is a judgment, so it is published rather than buried, and it is split so
a reader can take the conservative half and leave the rest.

`CLEAR` are honorifics and gender markers. No family is called Devi the way a
family is called Sharma; the token marks that the bearer is a woman.

`AMBIGUOUS` is `singh` and `kumar`, and they are genuinely both things at once.
Singh is the surname of Rajput and other families *and* the name given to every
Sikh man *and* a common filler across the Hindi belt. Kumar is a family name in
some places and a placeholder in others. Nothing in the rolls separates the two
uses, so every figure is reported with and without them and the reader decides.

Not covered here, and worth naming: patronymics standing in the surname slot
(common in the south), and OCR debris from scanned rolls. Both are real and
neither is quantified in this analysis.
"""

from __future__ import annotations

import pandas as pd

CLEAR = {
    "devi": "honorific for a woman",
    "kumari": "honorific for an unmarried woman",
    "kaur": "given to every Sikh woman",
    "bai": "honorific for a woman, western and central India",
    "rani": "honorific, 'queen'",
    "begam": "honorific for a Muslim woman",
    "begum": "honorific for a Muslim woman",
    "khatun": "honorific for a Muslim woman",
    "bibi": "honorific for a Muslim woman",
    "banu": "honorific for a Muslim woman",
    "beevi": "honorific for a Muslim woman, Kerala",
    "sri": "honorific, 'mister'",
    "smt": "abbreviation of Srimati, 'missus'",
}

AMBIGUOUS = {
    "singh": "given to every Sikh man; also a real surname",
    "kumar": "common filler; also a real surname",
}

LEVELS = {
    "as_written": set(),
    "minus_clear": set(CLEAR),
    "minus_all": set(CLEAR) | set(AMBIGUOUS),
}

LEVEL_LABEL = {
    "as_written": "names as written on the roll",
    "minus_clear": "minus honorifics",
    "minus_all": "minus honorifics, singh and kumar",
}


def table() -> pd.DataFrame:
    """The list itself, so it can be disagreed with."""
    rows = [
        {"token": t, "kind": kind, "why": why}
        for kind, d in (("clear", CLEAR), ("ambiguous", AMBIGUOUS))
        for t, why in d.items()
    ]
    return pd.DataFrame(rows)
