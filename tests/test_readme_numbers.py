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


def _resolution(state: str) -> float:
    path = A05 / "surname_resolution.csv"
    if not path.exists():
        pytest.skip("analysis 05 not built")
    d = pd.read_csv(path).set_index("state")
    return float(d.loc[state, "gendered_share"]) * 100


def claims() -> list[tuple[str, str, float]]:
    """(label, regex with one capture group, expected value)."""
    h = _json(A01 / "headline.json")
    roll = h["weighted"]["roll"]
    a03 = _json(A03 / "summary.json")
    a05 = _json(A05 / "summary.json")
    a06 = _json(A06 / "summary.json")
    mah = a06["held_out"]["Mahadalit census"]
    ceil = a06["ceiling"]
    chaudhary = _surname_pair("चौधरी")
    prasad = _surname_pair("प्रसाद")

    return [
        # Section 01 is roll-weighted throughout. The SECC-weighted blind rate
        # is 29.6, and quoting the two on one page without saying which is
        # which is how the front page ended up self-contradictory.
        (
            "01 roll Dalit share",
            r"about (\d+) are Dalit",
            roll["base_rates"]["sc"] * 100,
        ),
        ("01 roll Adivasi share", r"(\d+) Adivasi", roll["base_rates"]["st"] * 100),
        (
            "01 roll blind",
            r"you get \*\*(\d+) of 100 wrong\*\*",
            roll["err_blind"] * 100,
        ),
        (
            "01 roll with name",
            r"You get \*\*(\d+) wrong\*\*",
            roll["err_per_person"] * 100,
        ),
        (
            "01 share unchanged",
            r"for \*\*(\d+)% of people the name does\s+not change",
            roll["share_guess_unchanged"] * 100,
        ),
        (
            "01 share made worse",
            r"for \*\*(\d+)% it makes the guess harder\*\*",
            roll["share_less_sure"] * 100,
        ),
        # The rung with median cell size 1, so the one where plug-in bias is
        # worst and leave-one-out is not optional.
        (
            "02 surname+village",
            r"leaves you wrong \*\*(\d+) times in 100\*\*",
            _ladder("jati", "surname+village"),
        ),
        (
            "02 surname alone",
            r"drop the village, and it is \*\*(\d+)\*\*",
            _ladder("jati", "surname"),
        ),
        (
            "03 commonest name share",
            r"at (\d+\.\d)% of the electoral roll",
            a03["levels"]["as_written"]["top_name_share"] * 100,
        ),
        (
            "03 sex-marking coverage",
            r"cover \*\*(\d+(?:\.\d)?)% of the\s+country\*\*",
            a03["levels"]["minus_clear"]["people_dropped_share"] * 100,
        ),
        (
            "03 names for a quarter",
            r"\*\*(\d+)\*\* if\s+you count only names a brother",
            a03["levels"]["minus_all"]["names_for_25"],
        ),
        (
            "05 Dalit error",
            r"Dalit is guessed wrong (\d+) times in 100",
            a05["by_caste"]["Scheduled Caste"]["mistakes_per_100"],
        ),
        (
            "05 other error",
            r"outside the schedules\s+gets \*\*(\d+)\*\*",
            a05["by_caste"]["neither"]["mistakes_per_100"],
        ),
        (
            "05 Bihar sex gap",
            r"\*\*(\d+\.\d) more mistakes per hundred than men's in Bihar\*\*",
            _sex_gap("bihar"),
        ),
        ("05 Rajasthan sex gap", r"but (\d+\.\d) \*fewer\*", -_sex_gap("rajasthan")),
        (
            "05 Maharashtra sex gap",
            r"and (\d+\.\d) fewer in Maharashtra",
            -_sex_gap("maharashtra"),
        ),
        (
            "05 Rajasthan coverage",
            r"\*\*(\d+)% of the Rajasthan roll",
            _resolution("rajasthan"),
        ),
        ("05 Bihar coverage", r"against (\d+)% in Bihar", _resolution("bihar")),
        (
            "05 Maharashtra coverage",
            r"(\d+)% in\s+Maharashtra\*\*",
            _resolution("maharashtra"),
        ),
        ("06 chaudhary alone", r"Chaudhary goes from (\d+) mistakes", chaudhary[0]),
        (
            "06 chaudhary rescued",
            r"Chaudhary goes from \d+ mistakes to (\d+)",
            chaudhary[1],
        ),
        ("06 prasad alone", r"Prasad from (\d+) to \d+", prasad[0]),
        ("06 prasad rescued", r"Prasad from \d+ to (\d+)", prasad[1]),
        (
            "06 surname alone",
            r"the surname alone leaves \*\*(\d+)\*\*",
            mah["surname_only"],
        ),
        (
            "06 with neighbours",
            r"neighbours bring\s+that to \*\*(\d+)\*\*",
            mah["surname_plus_neighbours"],
        ),
        # Not "the roll page": caste is on no roll. The 9 comes from matching
        # the roll's cues against a caste register of the same population.
        ("06 ceiling", r"caste register leave \*\*(\d+)\*\*", ceil["mistakes_per_100"]),
        ("06 households", r"([\d,]+) Scheduled Caste\s+households", ceil["households"]),
        ("06 villages", r"([\d,]+) held-out villages", ceil["villages_held_out"]),
    ]


@pytest.mark.parametrize(
    "label,pattern,expected", claims(), ids=lambda v: v if isinstance(v, str) else ""
)
def test_readme_number_matches_its_output(
    label: str, pattern: str, expected: float
) -> None:
    text = README.read_text()
    match = re.search(pattern, text)
    assert match, f"{label}: README no longer contains a sentence matching {pattern!r}"
    printed = float(match.group(1).replace(",", ""))
    # Half of the last printed digit: 30 covers [29.5, 30.5), 10.5 covers
    # [10.45, 10.55). A number rounded correctly passes; a stale one does not.
    decimals = len(match.group(1).split(".")[1]) if "." in match.group(1) else 0
    tol = 0.5 * 10**-decimals
    assert (
        abs(printed - expected) < tol
    ), f"{label}: README says {match.group(1)}, output says {expected:.4f}"
