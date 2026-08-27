"""Analysis 07: where a surname works, and analysis 08's Karnataka null."""

from __future__ import annotations

import json
import pathlib

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
A07 = ROOT / "analyses/07_where_the_name_works/out/tab"
A08 = ROOT / "analyses/08_karnataka_initials/out/tab"


@pytest.fixture(scope="module")
def states():
    path = A07 / "by_state.csv"
    if not path.exists():
        pytest.skip("analysis 07 not built")
    return pd.read_csv(path).set_index("state")


def test_no_state_reports_a_result_without_its_coverage(states):
    """Every per-state number describes surnames past a disclosure floor.

    Reporting the result without the coverage beside it is how "Haryana has no
    Dalit surnames" gets read as a fact about Haryana rather than about the 36
    surnames that cleared the floor, covering 4% of the state.
    """
    assert states["covered_share"].notna().all()
    assert (states["covered_share"] > 0).all()
    # And the coverage really does vary enough to matter.
    assert states["covered_share"].max() / states["covered_share"].min() > 3


def test_the_spread_across_states_is_the_finding(states):
    assert states.loc["assam", "removed"] > 60
    assert states.loc["haryana", "removed"] < 1
    assert states["removed"].max() - states["removed"].min() > 50


def test_the_top25_control_preserves_the_ordering(states):
    """The objection a reader raises first.

    The floor keeps a state's commonest names and common names are the
    uninformative ones, so a state retaining few names could look uninformative
    by construction. If the ordering only held before this control, the result
    would be an artefact of the floor rather than a fact about the states.
    """
    for good in ("assam", "bihar"):
        for bad in ("punjab", "haryana", "kerala"):
            assert states.loc[good, "removed_top25"] > states.loc[bad, "removed_top25"]


def test_the_count_of_dalit_pointing_names_is_not_the_story(states):
    """Punjab has more of them than Assam and gets a twentieth of the benefit.

    Guarded because the first draft of this analysis reported that count as the
    explanatory variable, which is wrong: what matters is whether a decisive
    name is large.
    """
    path = A07 / "decisive_names.csv"
    if not path.exists():
        pytest.skip("analysis 07 not built")
    d = pd.read_csv(path)
    punjab = d[d.state == "punjab"]
    assam = d[d.state == "assam"]
    assert len(punjab) >= len(assam)
    assert states.loc["punjab", "removed"] < states.loc["assam", "removed"] / 10
    # Assam's single decisive name is far larger than any of Punjab's.
    assert assam["share_of_extract"].max() > 2 * punjab["share_of_extract"].max()


def test_karnataka_last_tokens_are_mostly_initials():
    path = A08 / "summary.json"
    if not path.exists():
        pytest.skip("analysis 08 not built")
    s = json.loads(path.read_text())
    assert s["naive_is_single_letter"] > 25
    tokens = pd.read_csv(A08 / "commonest_tokens.csv")
    # Every one of the top ten naive tokens should be a single letter.
    assert (tokens["naive"].head(10).str.len() == 1).all()
    assert (tokens["clean"].head(10).str.len() > 1).all()


def test_cleaning_karnataka_surnames_does_not_improve_prediction():
    """The null, kept explicitly so a future change cannot quietly invert it.

    Cleaning changes which names you get completely and moves the error by less
    than a mistake per hundred, in the wrong direction, because smaller cells
    resolve fewer people.
    """
    path = A08 / "summary.json"
    if not path.exists():
        pytest.skip("analysis 08 not built")
    s = json.loads(path.read_text())
    assert abs(s["cleaning_changes_prediction_by"]) < 1.5
    sc = pd.read_csv(A08 / "scores.csv").set_index("cue")
    assert (
        sc.loc["clean_surname", "share_resolved"]
        < sc.loc["naive_surname", "share_resolved"]
    )
    # Neither cue is close to useless *or* good: both sit between the blind
    # rate and a long way short of it.
    blind = sc.loc["naive_surname", "blind_per_100"]
    for cue in ("naive_surname", "clean_surname"):
        assert 0.8 * blind < sc.loc[cue, "mistakes_per_100"] < blind
