"""Invariants for the surname-transmission scorer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from conftest import load

tr = load("04_which_token_is_the_surname", "transmission")

TAB = Path(__file__).resolve().parent.parent / (
    "analyses/04_which_token_is_the_surname/out/tab"
)


def test_scorer_is_position_agnostic():
    """The same fact with the shared token first or last must score the same.

    The last-token version passed every aggregate check I ran and was still
    reading a given name for the whole of Maharashtra.
    """
    first = tr.shared_tokens("patil ashwini", "patil ashok")
    last = tr.shared_tokens("ashwini patil", "ashok patil")
    assert [t for _, t in first] == [t for _, t in last] == ["patil"]


def test_initials_are_not_names():
    assert tr.shared_tokens("k sunita", "k raman") == []


@pytest.fixture(scope="module")
def tokens():
    path = TAB / "transmission_by_token.csv"
    if not path.exists():
        pytest.skip("scan not built")
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def states():
    path = TAB / "by_state.csv"
    if not path.exists():
        pytest.skip("scan not built")
    return pd.read_csv(path).set_index("state")


def score(tokens, state, token):
    row = tokens[(tokens.state == state) & (tokens.token == token)]
    if row.empty:
        pytest.skip(f"{token} not scored in {state}")
    return float(row.transmitted.iloc[0])


def test_sex_marking_names_do_not_transmit(tokens):
    for token in ("devi", "kumari"):
        assert score(tokens, "bihar", token) < 0.01


def test_family_names_do_transmit(tokens):
    """0.8, not 0.99. Early probes over the head of each file read sharma at
    0.99, but those rows are the commonest name combinations; across the whole
    file the tail carries single-token relative names and OCR noise, and the
    honest figure is 0.85."""
    for token in ("singh", "yadav", "sharma"):
        assert score(tokens, "bihar", token) > 0.8


def test_kumar_is_neither(tokens):
    """The case analysis 03 had to guess at. Most Kumars did not inherit it,
    a real minority did, and the measurement says so without being asked."""
    assert 0.02 < score(tokens, "bihar", "kumar") < 0.25


def test_maharashtra_writes_the_surname_first(states):
    """The defect this analysis exists to catch."""
    assert states.loc["maharashtra", "position_first"] > 0.9
    assert states.loc["bihar", "position_last"] > 0.8


def test_method_is_marked_inapplicable_where_the_relative_has_no_surname(states):
    """Gujarat records the relative as a bare given name in every row, and
    Tamil Nadu in 96% of them. A low score there is a fact about the roll, not
    about how those places name people -- an earlier draft read it as the
    latter."""
    for state in ("gujarat", "tamil_nadu", "kerala"):
        if state in states.index:
            assert not states.loc[state, "method_applies"]
    for state in ("bihar", "maharashtra", "odisha"):
        assert states.loc[state, "method_applies"]


def test_singh_and_kumar_disagree_with_the_hand_list(tokens, states):
    """The measurement's whole point: it corrects the list I wrote by hand."""
    usable = set(states[states.method_applies].index)
    s = tokens[tokens.state.isin(usable)]
    agg = s.groupby("token").apply(
        lambda g: (g.transmitted * g.bearers).sum() / g.bearers.sum(),
        include_groups=False,
    )
    assert agg["singh"] > 0.5, "singh is mostly inherited; dropping it was wrong"
    assert agg["kumar"] < 0.25, "kumar is mostly not inherited"
