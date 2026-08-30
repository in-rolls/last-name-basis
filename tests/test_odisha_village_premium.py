"""Analysis 09: the village premium in Bihar against one district of Odisha."""

from __future__ import annotations

import json
import pathlib

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAB = ROOT / "analyses/09_odisha_village_premium/out/tab"


@pytest.fixture(scope="module")
def summary():
    path = TAB / "summary.json"
    if not path.exists():
        pytest.skip("analysis 09 not built")
    return json.loads(path.read_text())


def test_the_surname_position_is_measured_before_it_is_used(summary):
    """Assuming the last token is the surname is what broke Maharashtra.

    Analysis 04 found Maharashtra writes the surname first, which invalidated
    two states' figures in analysis 03. The position is therefore measured per
    dataset from the relative's name, never carried over, and the result has to
    be present before any score is read.
    """
    position = summary["surname_position"]
    assert position["surname_is"] in {"first", "last"}
    assert position["share_sharing_a_token"] > 0.5
    assert sum(position["positions"].values()) == pytest.approx(1.0)


def test_the_village_adds_less_here_than_in_bihar(summary):
    bihar = summary["bihar"]
    gajapati = summary["gajapati"]["as recorded"]
    assert bihar["premium"] > gajapati["premium"]
    # Both are large; the finding is the difference between them, not that one
    # of them is zero.
    assert gajapati["premium"] > 10
    assert bihar["premium"] > 25


def test_the_result_survives_the_normalisation_choice(summary):
    """The objection this analysis is most exposed to.

    The jati labels are raw Odia strings merged by a layer written here rather
    than by a curated dictionary, so the merge threshold is an analyst's choice.
    If the premium moved with it, the result would be an artefact of that
    choice. Collapsing 377 labels to 218 moves it by less than one mistake.
    """
    sens = pd.DataFrame(summary["sensitivity"])
    assert len(sens) >= 3
    assert sens["groups"].max() / sens["groups"].min() > 1.5
    assert sens["premium"].max() - sens["premium"].min() < 1.5
    # And every variant stays well below Bihar's premium.
    assert sens["premium"].max() < summary["bihar"]["premium"] - 5


def test_religion_is_reported_both_ways_and_changes_nothing_qualitative(summary):
    """A jati label can carry a religion, which would make religion a predictor.

    Scoring only one way would either smuggle religion in or silently remove it.
    Both are reported, and the conclusion has to hold under each.
    """
    both = summary["gajapati"]
    assert set(both) == {"as recorded", "religion stripped"}
    for scored in both.values():
        assert scored["premium"] < summary["bihar"]["premium"]


def test_the_district_is_never_labelled_as_the_state(summary):
    """One district of thirty. Calling it Odisha would be the easy error."""
    assert summary["district"] == "Gajapati"
    note = (ROOT / "analyses/09_odisha_village_premium/note.md").read_text()
    assert "Gajapati" in note
    # The note must say what it is not.
    assert "not Odisha" in note or "not an Odisha result" in note


def test_the_sampling_limit_is_recorded(summary):
    """40 khatiyans per village biases the premium downward, so it is stated."""
    assert summary["per_village_cap"] == 40
    assert summary["villages"] > 100
