"""Invariants for the Bihar ladders."""

from __future__ import annotations

import pytest
from conftest import load

source = load("02_jati_by_geography", "data")

from last_name_basis import leave_one_out_ladder, score_ladder  # noqa: E402

RUNGS = ["surname+village", "surname+zone", "surname+district", "surname"]


@pytest.fixture(scope="module")
def records():
    d = source.records_ladder()
    if d is None:
        pytest.skip("naampata ladders unavailable")
    return d


@pytest.fixture(scope="module")
def scored(records):
    return score_ladder(source.with_group(records, "jati"), group="group").set_index(
        "level"
    )


def test_shares_sum_to_one_within_every_cell(records):
    totals = records.groupby(["level", "cell"], observed=True)["share"].sum()
    assert totals.min() == pytest.approx(1.0, abs=1e-6)
    assert totals.max() == pytest.approx(1.0, abs=1e-6)


def test_mistakes_rise_as_geography_coarsens(scored):
    """If a rung inverts, the cell keys are wrong."""
    values = [scored.loc[r, "mistakes_per_100"] for r in RUNGS]
    assert values == sorted(values)


def test_place_alone_is_worse_than_name_plus_place(scored):
    assert (
        scored.loc["village", "mistakes_per_100"]
        > scored.loc["surname+village", "mistakes_per_100"]
    )


def test_no_single_person_cells(scored):
    """A cell holding one person is 'predicted' perfectly by construction. If
    any appear, the sharp village figure stops being trustworthy."""
    assert scored["smallest_cell"].min() >= 2


def test_leave_one_out_barely_moves_any_rung(records):
    """The only thing standing between "surname + village is nearly perfect"
    and a sparsity artifact."""
    d = source.with_group(records, "jati")
    plug = score_ladder(d, group="group").set_index("level")["mistakes_per_100"]
    loo = leave_one_out_ladder(d, group="group").set_index("level")[
        "mistakes_per_100_loo"
    ]
    gap = (loo - plug).abs()
    assert gap.max() < 2.0, f"leave-one-out moved a rung by {gap.max():.2f}"


def test_surnames_are_devanagari(records):
    """An earlier draft matched the Latin string "singh" and hit two stray
    cells out of the 9,849 the Devanagari form actually has."""
    village = records[records["level"] == "surname+village"]
    last = village["cell"].str.rsplit("|", n=1).str[-1]
    assert (last.str.contains(r"[ऀ-ॿ]")).mean() > 0.95
    assert (last == "सिंह").sum() > 1000


def test_muslim_split_is_a_refinement_not_a_relabel(records):
    """Splitting Muslims out may only ever subdivide a category, so the six-way
    target can never be easier to guess than the five-way one."""
    five = score_ladder(source.with_group(records, "category"), group="group")
    six = score_ladder(source.with_group(records, "category_religion"), group="group")
    merged = five.merge(six, on="level", suffixes=("_5", "_6"))
    assert (merged["mistakes_per_100_6"] >= merged["mistakes_per_100_5"] - 1e-9).all()
