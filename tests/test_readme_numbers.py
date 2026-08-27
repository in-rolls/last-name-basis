"""Every headline number on the front page must match the output it came from.

The failure this guards against has happened four times: an analysis is re-run,
its note is regenerated automatically, and the README -- which is written by
hand -- keeps the old number. Nobody notices, because nothing compares the two.

Each claim below pairs a regex against README.md with the output that should
supply the captured number. A claim that no longer matches is either a stale
number or a rewritten sentence; both need a human to look.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
A01 = ROOT / "analyses/01_surname_to_category/out/tab"
A02 = ROOT / "analyses/02_jati_by_geography/out/tab"
A03 = ROOT / "analyses/03_how_few_names/out/tab"
A05 = ROOT / "analyses/05_who_has_an_uninformative_name/out/tab"
A06 = ROOT / "analyses/06_neighbours/out/tab"


def _json(path: Path) -> dict:
    if not path.exists():
        pytest.skip(f"{path} not built")
    return json.loads(path.read_text())


def _ladder(target: str, rung: str) -> float:
    path = A02 / "ladders.csv"
    if not path.exists():
        pytest.skip("analysis 02 not built")
    d = pd.read_csv(path)
    row = d[(d["target"] == target) & (d["level"] == rung) & (d["ladder"] == "records")]
    return float(row["mistakes_per_100_loo"].to_numpy()[0])


def _surname_pair(surname: str) -> tuple[float, float]:
    path = A06 / "per_surname.csv"
    if not path.exists():
        pytest.skip("analysis 06 not built")
    d = pd.read_csv(path)
    row = d[d["surname"] == surname]
    return float(row["alone"].to_numpy()[0]), float(
        row["with_neighbours"].to_numpy()[0]
    )


def _sex_gap(state: str) -> float:
    """Women's mistakes per 100 minus men's. Positive means women fare worse."""
    path = A05 / "by_sex.csv"
    if not path.exists():
        pytest.skip("analysis 05 not built")
    d = pd.read_csv(path)
    d = d[d["state"] == state].set_index("who")["mistakes_per_100"]
    return float(d["women"] - d["men"])


def _analytic_share(state: str) -> float:
    """Share of the state's roll the sex estimate actually rests on.

    Not `gendered_share`: that is measured before `by_sex` inner-joins onto the
    caste table, and a surname can be gendered and then dropped for having no
    caste row. Maharashtra reads 66% before the merge and 36% after.
    """
    path = A05 / "surname_resolution.csv"
    if not path.exists():
        pytest.skip("analysis 05 not built")
    d = pd.read_csv(path).set_index("state")
    return float(d.loc[state, "analytic_share"]) * 100


def _roll(key: str):
    return lambda: _json(A01 / "headline.json")["weighted"]["roll"][key]


def _a03(*path):
    def get():
        v = _json(A03 / "summary.json")
        for k in path:
            v = v[k]
        return v

    return get


def _mah(key: str):
    return lambda: _json(A06 / "summary.json")["held_out"]["Mahadalit census"][key]


def _ceil(key: str):
    return lambda: _json(A06 / "summary.json")["ceiling"][key]


def _caste(group: str):
    return lambda: _json(A05 / "summary.json")["by_caste"][group]["mistakes_per_100"]


def claims():
    """(label, regex with one capture group, callable giving the value).

    Nothing here may touch the filesystem: this list is built at collection
    time, when a clean checkout has no out/tab at all.
    """

    return [
        # Section 01 is roll-weighted throughout. The SECC-weighted blind rate
        # is 29.6, and quoting the two on one page without saying which is
        # which is how the front page ended up self-contradictory.
        (
            "01 roll Dalit share",
            r"about (\d+) are Dalit",
            lambda: _roll("base_rates")()["sc"] * 100,
        ),
        (
            "01 roll Adivasi share",
            r"(\d+) Adivasi",
            lambda: _roll("base_rates")()["st"] * 100,
        ),
        (
            "01 roll blind",
            r"you get \*\*(\d+) of 100 wrong\*\*",
            lambda: _roll("err_blind")() * 100,
        ),
        (
            "01 roll with name",
            r"You get \*\*(\d+) wrong\*\*",
            lambda: _roll("err_per_person")() * 100,
        ),
        (
            "01 share unchanged",
            r"for \*\*(\d+)% of people the name does\s+not change",
            lambda: _roll("share_guess_unchanged")() * 100,
        ),
        (
            "01 share made worse",
            r"for \*\*(\d+)% it makes the guess harder\*\*",
            lambda: _roll("share_less_sure")() * 100,
        ),
        # The rung with median cell size 1, so the one where plug-in bias is
        # worst and leave-one-out is not optional.
        (
            "02 surname+village",
            r"leaves you wrong \*\*(\d+) times in 100\*\*",
            lambda: _ladder("jati", "surname+village"),
        ),
        (
            "02 surname alone",
            r"drop the village, and it is \*\*(\d+)\*\*",
            lambda: _ladder("jati", "surname"),
        ),
        (
            "03 commonest name share",
            r"at (\d+\.\d)% of the electoral roll",
            lambda: _a03("levels", "as_written", "top_name_share")() * 100,
        ),
        (
            "03 sex-marking coverage",
            r"cover \*\*(\d+(?:\.\d)?)% of the\s+country\*\*",
            lambda: _a03("levels", "minus_clear", "people_dropped_share")() * 100,
        ),
        (
            "03 names for a quarter",
            r"\*\*(\d+)\*\* if\s+you count only names a brother",
            _a03("levels", "minus_all", "names_for_25"),
        ),
        (
            "05 Dalit error",
            r"Dalit is guessed wrong (\d+) times in 100",
            _caste("Scheduled Caste"),
        ),
        (
            "05 other error",
            r"outside the schedules\s+gets \*\*(\d+)\*\*",
            _caste("neither"),
        ),
        (
            "05 Bihar sex gap",
            r"\*\*(\d+\.\d) more mistakes per hundred than men's in Bihar\*\*",
            lambda: _sex_gap("bihar"),
        ),
        (
            "05 Rajasthan sex gap",
            r"but (\d+\.\d) \*fewer\*",
            lambda: -_sex_gap("rajasthan"),
        ),
        (
            "05 Maharashtra sex gap",
            r"and (\d+\.\d) fewer in Maharashtra",
            lambda: -_sex_gap("maharashtra"),
        ),
        # Coverage measured AFTER the merge onto the caste table, which is what
        # the estimate actually rests on. The pre-merge gendered share reads
        # 66% for Maharashtra where the analytic share is 36%.
        (
            "05 Rajasthan coverage",
            r"(\d+)% of the Rajasthan roll",
            lambda: _analytic_share("rajasthan"),
        ),
        (
            "05 Bihar coverage",
            r"(\d+)% of the Bihar roll",
            lambda: _analytic_share("bihar"),
        ),
        (
            "05 Maharashtra coverage",
            r"(\d+)% of the Maharashtra roll",
            lambda: _analytic_share("maharashtra"),
        ),
        (
            "06 chaudhary alone",
            r"Chaudhary goes from (\d+) mistakes",
            lambda: _surname_pair("\u091a\u094c\u0927\u0930\u0940")[0],
        ),
        (
            "06 chaudhary rescued",
            r"Chaudhary goes from \d+ mistakes to (\d+)",
            lambda: _surname_pair("\u091a\u094c\u0927\u0930\u0940")[1],
        ),
        (
            "06 prasad alone",
            r"Prasad from (\d+) to \d+",
            lambda: _surname_pair("\u092a\u094d\u0930\u0938\u093e\u0926")[0],
        ),
        (
            "06 prasad rescued",
            r"Prasad from \d+ to (\d+)",
            lambda: _surname_pair("\u092a\u094d\u0930\u0938\u093e\u0926")[1],
        ),
        (
            "06 surname alone",
            r"the surname alone leaves \*\*(\d+)\*\*",
            _mah("surname_only"),
        ),
        (
            "06 with neighbours",
            r"neighbours bring\s+that to \*\*(\d+)\*\*",
            _mah("surname_plus_neighbours"),
        ),
        # Not "the roll page": caste is on no roll. The 9 comes from matching
        # the roll's cues against a caste register of the same population.
        (
            "06 ceiling",
            r"caste register leave \*\*(\d+)\*\*",
            _ceil("mistakes_per_100"),
        ),
        (
            "06 households",
            r"([\d,]+) Scheduled Caste\s+households",
            _ceil("households"),
        ),
        ("06 villages", r"([\d,]+) held-out villages", _ceil("villages_held_out")),
    ]


@pytest.mark.parametrize(
    "label,pattern,expected", claims(), ids=lambda v: v if isinstance(v, str) else ""
)
def test_readme_number_matches_its_output(label, pattern, expected) -> None:
    text = README.read_text()
    value = expected() if callable(expected) else expected
    match = re.search(pattern, text)
    assert match, f"{label}: README no longer contains a sentence matching {pattern!r}"
    printed = float(match.group(1).replace(",", ""))
    # Half of the last printed digit: 30 covers [29.5, 30.5), 10.5 covers
    # [10.45, 10.55). A number rounded correctly passes; a stale one does not.
    decimals = len(match.group(1).split(".")[1]) if "." in match.group(1) else 0
    tol = 0.5 * 10**-decimals
    assert (
        abs(printed - value) < tol
    ), f"{label}: README says {match.group(1)}, output says {value:.4f}"
