"""Reconciliation and regression checks on the per-name table."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from conftest import load

from last_name_basis import entropy_bits

data = load("01_surname_to_category", "data")
metrics = load("01_surname_to_category", "metrics")
coverage = load("01_surname_to_category", "coverage")

PROB_COLS = data.PROB_COLS
base_rates, load_cells, per_name = data.base_rates, data.load_cells, data.per_name
add_metrics, signal_decomposition = metrics.add_metrics, metrics.signal_decomposition
weighted_summary = metrics.weighted_summary
with_roll_frequency = coverage.with_roll_frequency


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

    from last_name_basis.style import allocate, band_of, mistake_bands

    table = per_name(load_cells())
    table = with_roll_frequency(add_metrics(table, base_rates(table)))
    if table["share_roll"].isna().all():
        pytest.skip("instate roll counts unavailable")

    baseline = weighted_summary(table, "share_roll")["err_blind"] * 100
    bands = mistake_bands(baseline)
    band = (table["err"] * 100).map(lambda m: band_of(m, bands))
    shares = np.array(
        [
            table.loc[band == i, "share_roll"].sum() / table["share_roll"].sum()
            for i in range(len(bands))
        ]
    )
    assert shares.sum() == pytest.approx(1.0)
    counts = allocate(shares)
    assert counts.sum() == 100
    # The last band is "harder than a stranger" -- it must not be empty, since
    # that group is the note's sharpest claim.
    assert counts[-1] > 0


def test_cut_averages_to_the_mutual_information_under_its_own_prior():
    """`cut` is measured against a prior, so it is only interpretable alongside
    the weighting that prior came from. Averaging a roll-weighted table against
    a SECC-weighted prior silently breaks the identity -- it is how one draft
    reported 0.32 and 0.44 for the same quantity, and 9 squares against 16%."""

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
    assert float(w[table["cut"] < 0].sum()) == pytest.approx(
        summary["share_whose_name_is_more_mixed_than_the_population"]
    )


def test_cut_never_exceeds_total_uncertainty(named):
    """Unlike KL, `cut` is bounded above by H(caste) -- a name cannot appear to
    tell you more than the answer itself. That bound is why it is the headline."""

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


def test_no_surname_can_make_the_guess_wronger_than_blind(named):
    """The fact that made "for 16% it makes the guess harder" impossible.

    The blind guess names the population's largest category; the name-based
    guess names the surname's. Since max(p) >= p[blind] for every row, using
    the name can never raise the error rate. The 16% was an entropy comparison
    -- the surname's caste mix is more evenly spread than the population's --
    written up as if it were an error rate, and in error terms it points the
    other way: those people average 42.8 mistakes per 100 against 45.9 blind.
    """
    d = with_roll_frequency(named)
    w = d["share_roll"].fillna(0).to_numpy(float)
    if w.sum() <= 0:
        pytest.skip("roll frequencies unavailable")
    p = d[PROB_COLS].to_numpy()
    prior = (p * (w / w.sum())[:, None]).sum(axis=0)
    err_name = 1 - p.max(axis=1)
    err_blind = 1 - p[:, int(prior.argmax())]
    assert (err_name > err_blind + 1e-12).sum() == 0

    # And the group the old sentence was about is better off, not worse.
    mixed = entropy_bits(p) > entropy_bits(prior)
    wm = w[mixed]
    assert (wm * err_name[mixed]).sum() / wm.sum() < (
        wm * err_blind[mixed]
    ).sum() / wm.sum()


def test_a_score_carrying_nothing_gives_exactly_a_half():
    """Calibration. Without this the statistic could be silently mis-scaled."""
    from last_name_basis.scoring import ranks_above

    flat = np.array([0.3, 0.3, 0.3])
    assert (
        ranks_above(flat, np.array([5.0, 3.0, 2.0]), np.array([4.0, 1.0, 6.0])) == 0.5
    )
    assert (
        ranks_above(np.array([0.0, 1.0]), np.array([0.0, 9.0]), np.array([9.0, 0.0]))
        == 1.0
    )
    assert (
        ranks_above(np.array([0.0, 1.0]), np.array([9.0, 0.0]), np.array([0.0, 9.0]))
        == 0.0
    )


def test_two_implementations_of_the_rank_statistic_agree(named):
    """The headline claim now rests on this number, so it gets two routes.

    One sorts individuals and splits ties in a single pass; the other groups by
    distinct score first. They share nothing beyond their inputs.
    """
    table = with_roll_frequency(named)
    for weight in (None, "share_roll"):
        if weight == "share_roll" and table["share_roll"].fillna(0).sum() <= 0:
            continue
        a = metrics.discrimination(table, weight)
        b = metrics.discrimination_by_levels(table, weight)
        for category in a:
            assert abs(a[category] - b[category]) < 1e-3, (category, weight, a, b)


def test_the_surname_discriminates_far_better_than_it_decides(named):
    """The point the accuracy figures conceal.

    Accuracy against the largest category is mostly a statement about the base
    rate: a rule naming the majority is right 70 times in 100 in a population
    that is 70% one group, whatever surnames reveal. Ranking is not inflatable
    that way, and it says a surname separates Dalit from non-Dalit well while
    changing the decision for almost nobody.
    """
    table = with_roll_frequency(named)
    ranked = metrics.discrimination(table)
    assert ranked["sc"] > 0.75, ranked
    assert ranked["st"] > 0.75, ranked
    # And the decision rule still leaves most people where the base rate put them.
    summary = weighted_summary(table, "share")
    assert summary["share_guess_unchanged"] > 0.8
