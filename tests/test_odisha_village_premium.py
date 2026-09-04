"""Analysis 09: the village premium in Bihar against a partial Odisha."""

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
    odisha = summary["odisha"]["as recorded"]
    assert bihar["premium"] > odisha["premium"]
    # Both are large; the finding is the difference between them, not that one
    # of them is zero.
    assert odisha["premium"] > 10
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
    both = summary["odisha"]
    assert set(both) == {"as recorded", "religion stripped"}
    for scored in both.values():
        assert scored["premium"] < summary["bihar"]["premium"]


def test_a_partial_scrape_is_never_reported_as_a_finished_one(summary):
    """The scope claim moved but did not disappear.

    This analysis once covered one district and said so. It now covers many,
    which retires that caveat and creates the opposite risk: a scrape that has
    reached a fraction of the state's khatiyans being written up as Odisha
    entire. The note has to keep saying the crawl is unfinished and that its
    districts were not entered at random.
    """
    assert len(summary["districts"]) > 1
    note = (ROOT / "analyses/09_odisha_village_premium/note.md").read_text()
    assert "not finished" in note or "unfinished" in note
    assert "random" in note


def test_the_pooled_premium_is_reported_beside_its_spread(summary):
    """Pooling states hides that districts disagree, and here it inverts.

    The pooled premium exceeds every district's, because a village in the
    pooled problem also names a district and a region. Reporting the pooled
    number alone would overstate what a village is worth to someone who
    already knows where they are, so the per-district scores must be present
    and the note must account for the gap.
    """
    per = pd.DataFrame(summary["by_district"])
    assert len(per) > 5
    pooled = summary["odisha"]["as recorded"]["premium"]
    assert per["premium"].min() < per["premium"].max()
    note = (ROOT / "analyses/09_odisha_village_premium/note.md").read_text()
    if pooled > per["premium"].max():
        assert "larger than every district" in note


def test_the_sampling_limit_is_recorded(summary):
    """The sampling depth biases the premium downward, so it is measured.

    Not read off the --per-village flag: that is a per-run cap, it has changed
    between runs and is now effectively off, and villages accumulate across
    runs. A finished village is censused; one the crawl is still working
    through is not, and only the realised distribution separates them.
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
    odisha = summary["ladder"]
    assert abs(bihar[-1] - odisha[-1]) < 2, "surname-alone rungs should agree"
    assert odisha[0] - bihar[0] > 4, "village rungs should differ"
