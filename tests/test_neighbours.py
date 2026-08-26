"""Invariants for the held-out neighbours test."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from conftest import load

nb = load("06_neighbours", "neighbours")


def test_the_split_is_by_village_and_disjoint():
    """Leakage here would manufacture the finding."""
    villages = pd.Index([f"v{i}" for i in range(1000)])
    train, test = nb.split_villages(villages)
    assert not (train & test)
    assert len(train) + len(test) == 1000
    assert 0.25 < len(test) / 1000 < 0.35


def test_the_split_is_stable():
    a = nb.split_villages(pd.Index([f"v{i}" for i in range(500)]))
    b = nb.split_villages(pd.Index([f"v{i}" for i in range(500)]))
    assert a == b


@pytest.fixture(scope="module")
def held_out():
    path = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "analyses/06_neighbours/out/tab/held_out.csv"
    )
    if not path.exists():
        pytest.skip("analysis 06 not built")
    return pd.read_csv(path).set_index("ladder")


def test_neighbours_help_but_do_not_rescue(held_out):
    for ladder in held_out.index:
        row = held_out.loc[ladder]
        assert row["surname_plus_neighbours"] < row["surname_only"]
        # Nowhere near closing the gap to knowing the village itself.
        assert row["surname_only"] - row["surname_plus_neighbours"] < 15


def test_neighbours_alone_are_useless(held_out):
    """The check that caught a broken first design. Averaging P(jati|surname)
    over neighbours scored worse than blind, and the combined model still
    'improved' the headline by 0.1 -- noise dressed as a result. Co-occurrence
    cannot identify you, only tilt you, so this must stay bad."""
    for ladder in held_out.index:
        row = held_out.loc[ladder]
        assert row["neighbours_only"] > row["surname_only"]


def test_alpha_did_not_stop_at_the_grid_edge(held_out):
    """The first grid topped out at 1.2 and the optimum was past it, which
    understated the gain by half."""
    assert not held_out["alpha_at_grid_edge"].any()


def test_uninformative_names_are_the_ones_rescued():
    """The question was about specific names, not the mean. The mean moves by
    four; the worst-off common names move by twenty."""
    path = (
        __import__("pathlib").Path(__file__).resolve().parent.parent
        / "analyses/06_neighbours/out/tab/per_surname.csv"
    )
    if not path.exists():
        pytest.skip("analysis 06 not built")
    d = pd.read_csv(path)
    # Across both ladders, how much a name gains should rise with how badly it
    # does alone.
    r = np.corrcoef(d["alone"], d["saved"])[0, 1]
    assert r > 0.4, f"expected uninformative names to gain most, got r={r:.2f}"
    assert d["saved"].max() > 10
