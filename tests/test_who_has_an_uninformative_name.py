"""The differential-error result, and the null beside it."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

TAB = Path(__file__).resolve().parent.parent / (
    "analyses/05_who_has_an_uninformative_name/out/tab"
)


@pytest.fixture(scope="module")
def caste():
    path = TAB / "by_caste.csv"
    if not path.exists():
        pytest.skip("analysis 05 not built")
    return pd.read_csv(path).set_index("caste")


def test_the_name_does_nothing_for_dalits(caste):
    """29.3 against a blind 29.6. The headline of this analysis."""
    import json

    blind = json.loads((TAB / "summary.json").read_text())["blind_per_100"]
    sc = caste.loc["Scheduled Caste", "mistakes_per_100"]
    assert abs(sc - blind) < 1.5


def test_it_does_a_lot_for_everyone_else(caste):
    assert caste.loc["neither", "mistakes_per_100"] < 20
    assert (
        caste.loc["Scheduled Caste", "mistakes_per_100"]
        - caste.loc["neither", "mistakes_per_100"]
        > 8
    )


def test_recall_is_wildly_unequal(caste):
    assert caste.loc["Scheduled Caste", "found_by_the_guess"] < 0.45
    assert caste.loc["neither", "found_by_the_guess"] > 0.9


def test_the_sex_gap_does_not_run_one_way():
    """Reported as a null: women fare worse in Bihar and better in UP. An
    earlier draft's figure asserted the opposite before the numbers came in."""
    path = TAB / "sex_gap.csv"
    if not path.exists():
        pytest.skip("sex table not built")
    g = pd.read_csv(path)
    assert (g["gap"] > 0).any() and (g["gap"] < 0).any()
