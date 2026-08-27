"""The differential-error result, and the null beside it."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from conftest import load

source = load("05_who_has_an_uninformative_name", "data")

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
    maharashtra = g.loc[g["state"] == "maharashtra", "gap"]
    if not maharashtra.empty:
        assert abs(maharashtra.iloc[0]) < 0.5


def test_sex_weights_use_upnaam_surname_order(tmp_path, monkeypatch):
    artifact = tmp_path / "upnaam/data/derived/resolved/maharashtra.parquet"
    artifact.parent.mkdir(parents=True)
    pd.DataFrame(
        {
            "source_row": [0, 1, 2],
            "state": ["maharashtra"] * 3,
            "name_raw": ["patil ashwini", "jadhav suresh", "sattar"],
            "weight": [10, 5, 20],
            "surname": ["patil", "jadhav", None],
            "surname_position": ["first", "first", None],
            "abstained": [False, False, True],
            "resolver_revision": ["resolver-v1"] * 3,
        }
    ).to_parquet(artifact, index=False)
    monkeypatch.setenv("GITHUB_DIR", str(tmp_path))
    result = source.surname_by_sex(
        "maharashtra", {"ashwini": 0.8, "suresh": 0.1, "patil": 0.0}
    ).set_index("last_name")
    assert result.loc["patil", "female"] == pytest.approx(8)
    assert result.loc["patil", "male"] == pytest.approx(2)
    assert result.loc["jadhav", "female"] == pytest.approx(0.5)
