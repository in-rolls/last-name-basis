"""Reconciliation and regression checks on the per-name table."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from last_name_basis.data import PROB_COLS, base_rates, load_cells, per_name
from last_name_basis.metrics import add_metrics, signal_decomposition


@pytest.fixture(scope="module")
def cells():
    return load_cells()


@pytest.fixture(scope="module")
def named(cells):
    table = per_name(cells)
    return add_metrics(table, base_rates(table))


def test_probabilities_sum_to_one(named):
    assert np.allclose(named[PROB_COLS].sum(axis=1), 1.0)


def test_records_reconcile_with_cells(cells, named):
    assert named["n"].sum() == pytest.approx(cells["total_support"].sum())
    assert named["share"].sum() == pytest.approx(1.0)


def test_one_row_per_surname(cells, named):
    assert len(named) == cells["last_name"].nunique()
    assert not named["last_name"].duplicated().any()


def test_probabilities_stay_attached_to_their_name(named):
    """Regression: probabilities are columns, so a re-sort cannot shear them off."""
    before = named.set_index("last_name")["p_sc"]
    after = named.sort_values("bits").set_index("last_name")["p_sc"]
    assert before.equals(after.reindex(before.index))


def test_gain_is_never_negative(named):
    """Knowing the name can never make the best guess worse."""
    assert (named["gain"] >= -1e-12).all()


def test_bits_are_never_negative(named):
    assert (named["bits"] >= -1e-12).all()


# The twelve walked through in the note, by regime. If any of these move the
# figures are telling the reader something false.
RULES_IN = ["paswan", "manjhi", "jatav", "chamar"]
RULES_OUT = ["sharma", "yadav", "jha", "tiwari"]
AT_BASE = ["singh", "prasad", "devi", "kumar"]


@pytest.mark.parametrize("name", RULES_IN)
def test_gazetted_jati_names_read_as_sc(named, name):
    row = named.set_index("last_name").loc[name]
    assert row["guess"] == "SC"
    assert row["p_sc"] > 0.85


@pytest.mark.parametrize("name", RULES_OUT)
def test_names_that_rule_out(named, name):
    assert named.set_index("last_name").loc[name, "p_sc"] < 0.02


@pytest.mark.parametrize("name", AT_BASE)
def test_common_names_sit_near_the_base_rate(named, name):
    base = base_rates(named)
    prior_sc = base["n_sc"] / base.sum()
    assert abs(named.set_index("last_name").loc[name, "p_sc"] - prior_sc) < 0.05


def test_waffle_caption_names_the_category_actually_guessed(named):
    """A caption reading 'not Dalit' beside the best guess's error rate is wrong
    wherever the best guess *is* Dalit -- jatav would read 13 when it is 87."""
    idx = named.set_index("last_name")
    for name in RULES_IN:
        row = idx.loc[name]
        assert row["guess"] == "SC"
        assert row["err"] == pytest.approx(1 - row["p_sc"])
    for name in AT_BASE + RULES_OUT:
        assert idx.loc[name, "guess"] == "Other"


def test_hundred_squares_are_representative():
    """Allocating squares across names hands them all to the commonest few and
    silently drops the long tail, which is 40% of people. Allocate across the
    bands instead, and check the picture still adds to a hundred."""
    from last_name_basis.coverage import with_roll_frequency
    from last_name_basis.figures import _allocate, _bucket, buckets
    from last_name_basis.metrics import weighted_summary

    table = per_name(load_cells())
    table = with_roll_frequency(add_metrics(table, base_rates(table)))
    if table["share_roll"].isna().all():
        pytest.skip("instate roll counts unavailable")

    baseline = weighted_summary(table, "share_roll")["err_blind"] * 100
    bands = buckets(baseline)
    band = (table["err"] * 100).map(lambda m: _bucket(m, bands))
    shares = np.array(
        [
            table.loc[band == i, "share_roll"].sum() / table["share_roll"].sum()
            for i in range(len(bands))
        ]
    )
    assert shares.sum() == pytest.approx(1.0)
    counts = _allocate(shares)
    assert counts.sum() == 100
    # The last band is "harder than a stranger" -- it must not be empty, since
    # that group is the note's sharpest claim.
    assert counts[-1] > 0


def test_cut_averages_to_the_mutual_information_under_its_own_prior():
    """`cut` is measured against a prior, so it is only interpretable alongside
    the weighting that prior came from. Averaging a roll-weighted table against
    a SECC-weighted prior silently breaks the identity -- it is how one draft
    reported 0.32 and 0.44 for the same quantity, and 9 squares against 16%."""
    from last_name_basis.coverage import with_roll_frequency
    from last_name_basis.metrics import weighted_summary

    table = per_name(load_cells())
    table = with_roll_frequency(add_metrics(table, base_rates(table)))
    if table["share_roll"].isna().all():
        pytest.skip("instate roll counts unavailable")

    summary = weighted_summary(table, "share_roll")
    table = add_metrics(
        table,
        pd.Series({f"n_{k}": v for k, v in summary["base_rates"].items()}),
    )
    w = table["share_roll"].fillna(0)
    w = w / w.sum()

    assert float((table["cut"] * w).sum()) == pytest.approx(
        summary["uncertainty_removed_bits"]
    )
    assert float(w[table["cut"] < 0].sum()) == pytest.approx(summary["share_less_sure"])


def test_cut_never_exceeds_total_uncertainty(named):
    """Unlike KL, `cut` is bounded above by H(caste) -- a name cannot appear to
    tell you more than the answer itself. That bound is why it is the headline."""
    from last_name_basis.metrics import entropy_bits

    base = base_rates(named)
    ceiling = entropy_bits((base / base.sum()).to_numpy())
    assert named["cut"].max() <= ceiling + 1e-9


def test_knowing_more_never_costs_you_mistakes(cells):
    """The note's geography check, as an invariant: adding the state on top of
    the name can only help, and the state alone must not beat the name."""
    d = signal_decomposition(cells)
    assert d["mistakes_knowing_both"] <= d["mistakes_knowing_name"] + 1e-9
    assert d["mistakes_knowing_both"] <= d["mistakes_knowing_state"] + 1e-9
    assert d["mistakes_knowing_name"] < d["mistakes_knowing_state"]
    assert d["mistakes_knowing_state"] <= d["mistakes_knowing_nothing"] + 1e-9


def test_chain_rule_holds(cells):
    d = signal_decomposition(cells)
    assert d["name_and_state_bits"] == pytest.approx(
        d["state_alone_bits"] + d["name_given_state_bits"]
    )
    assert d["name_and_state_bits"] >= d["name_alone_bits"] - 1e-12
