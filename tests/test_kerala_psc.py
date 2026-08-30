"""Analysis 10: Kerala, where a surname often does not exist."""

from __future__ import annotations

import json
import pathlib

import pandas as pd
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAB = ROOT / "analyses/10_kerala_psc/out/tab"


@pytest.fixture(scope="module")
def summary():
    path = TAB / "summary.json"
    if not path.exists():
        pytest.skip("analysis 10 not built")
    return json.loads(path.read_text())


def test_most_kerala_last_tokens_are_a_single_letter(summary):
    """The premise. Without it the analysis has no reason to exist."""
    shape = summary["name_shape"]
    assert shape["last_token_is_a_single_letter"] > 0.70
    assert shape["first_token_is_a_single_letter"] < 0.01
    assert shape["has_a_written_surname"] < 0.5


def test_the_given_name_beats_the_last_token(summary):
    """The finding: the informative part is the part nothing here reads.

    If this inverts, Kerala has become a state where a surname method works and
    the note is wrong.
    """
    cues = summary["cues"]
    assert cues["given_name"]["ranks_sc_higher"] > cues["last_token"]["ranks_sc_higher"]
    assert cues["last_token"]["ranks_sc_higher"] < 0.65
    assert cues["given_name"]["ranks_sc_higher"] > 0.6


def test_religion_buckets_are_excluded_and_the_loss_reported(summary):
    """Kerala reserves for Muslim and Christian communities.

    Scoring them would make religion a predictor. Excluding them silently would
    hide a third of the file, so the dropped share is carried in the output.
    """
    dropped = summary["scored"]["dropped"]
    assert set(dropped) == {"Muslim", "Christian", "no community given"}
    assert dropped["Muslim"] > 0.1
    assert summary["scored"]["share_of_all"] < 0.7
    # And nothing religious survived into the scored set.
    assert summary["scored"]["sc_share"] > 0.1


def test_the_cues_are_scored_by_the_shared_routine(summary):
    """Comparable with analyses 01 and 07 rather than merely similar."""
    from last_name_basis.scoring import ranks_above

    cues = pd.read_csv(TAB / "cues.csv")
    assert set(cues["cue"]) == {"last_token", "written_surname", "given_name"}
    # A degenerate cue must return exactly the no-information value.
    assert (
        ranks_above(
            pd.Series([0.2, 0.2]).to_numpy(),
            pd.Series([5.0, 5.0]).to_numpy(),
            pd.Series([5.0, 5.0]).to_numpy(),
        )
        == 0.5
    )
