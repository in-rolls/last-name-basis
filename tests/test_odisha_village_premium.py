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
    """The sampling depth biases the premium downward, so it is measured.

    Not read off the --per-village flag: that is a per-run cap, it has already
    changed from 40 to 10 mid-collection, and villages accumulate across runs.
    """
    sampling = summary["sampling"]
    assert sampling["khatiyans_per_village_median"] > 0
    assert (
        sampling["khatiyans_per_village_max"]
        >= sampling["khatiyans_per_village_median"]
    )
    assert summary["villages"] > 100


def test_the_ladder_rises_monotonically_with_the_size_of_the_place(summary):
    """Analysis 02's shape, reproduced in a second state.

    If a coarser place ever scored better than a finer one, the cue would be
    doing something other than locating the person, and the comparison with
    Bihar would not mean what it says.
    """
    ladder = summary["ladder"]
    assert ladder == sorted(ladder), ladder
    assert summary["ladder_levels"][0].endswith("village")
    assert summary["ladder_levels"][-1] == "surname alone"


def test_both_places_converge_once_the_place_is_discarded(summary):
    """The two lines meet at the surname alone and separate at the village.

    That is the whole comparison: equal without a place, unequal with one. If
    they stopped converging, the two datasets would no longer be measuring
    comparable surname signal and the premium difference would be confounded.
    """
    bihar = summary["bihar_ladder"]
    gajapati = summary["ladder"]
    assert abs(bihar[-1] - gajapati[-1]) < 2, "surname-alone rungs should agree"
    assert gajapati[0] - bihar[0] > 5, "village rungs should differ"
