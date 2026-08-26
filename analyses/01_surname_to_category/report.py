"""Tables for the note. Every number here comes from the per-name frame."""

from __future__ import annotations

import pandas as pd
from data import PROB_COLS, load_cells, per_name
from metrics import add_metrics, headline

# Names a reader is likely to try, including two the table cannot answer.
LOOKUP = [
    "sood",
    "iyer",
    "kumar",
    "singh",
    "devi",
    "sharma",
    "gupta",
    "yadav",
    "das",
    "ram",
    "lal",
    "patel",
    "khan",
    "reddy",
    "jha",
    "paswan",
    "jatav",
    "valmiki",
    "manjhi",
]

DISPLAY = (
    ["last_name", "n", "share"]
    + PROB_COLS
    + [
        "guess",
        "err",
        "err_blind",
        "gain",
        "bits",
    ]
)


def lookup_table(named: pd.DataFrame, names: list[str] = LOOKUP) -> pd.DataFrame:
    """One row per requested name; absences are kept as rows, not dropped."""
    idx = named.set_index("last_name")
    rows = []
    for name in names:
        if name in idx.index:
            rows.append(idx.loc[name, [c for c in DISPLAY if c != "last_name"]])
        else:
            rows.append(pd.Series(dtype=float, name=name))
    out = pd.DataFrame(rows)
    out.index = pd.Index(names, name="last_name")
    return out


def floor_sensitivity(
    floors: tuple[int, ...] = (100, 200, 500, 1000),
    scheme: str = "secc",
) -> pd.DataFrame:
    """Does the >=100 suppression floor flatter or flatten the answer?

    The floor drops rare cells, and rare names are the informative ones, so the
    headline should get *less* informative as the floor rises. Confirm, don't
    assume.
    """
    rows = []
    for floor in floors:
        cells = load_cells(min_support=floor)
        named = per_name(cells, scheme=scheme)
        base = named[[f"n_{c}" for c in ("sc", "st", "other")]].sum()
        named = add_metrics(named, base)
        h = headline(named, base)
        rows.append(
            {
                "min_support": floor,
                "names": h["names"],
                "records_m": h["records"] / 1e6,
                "err_per_person": h["err_per_person"],
                "err_blind": h["err_blind_overall"],
                "mutual_info_bits": h["mutual_information_bits"],
                "share_guess_unchanged": h["share_people_guess_unchanged"],
            }
        )
    return pd.DataFrame(rows)


def pooling_shift(secc: pd.DataFrame, census: pd.DataFrame, top: int = 20):
    """Names whose caste split moves most when states are reweighted to Census.

    A large shift means the name is regionally concentrated and no single pooled
    number describes it honestly.
    """
    a = secc.set_index("last_name")
    b = census.set_index("last_name")
    common = a.index.intersection(b.index)
    shift = (b.loc[common, "p_sc"] - a.loc[common, "p_sc"]).rename("d_p_sc")
    out = pd.concat(
        [
            a.loc[common, ["n", "p_sc"]].rename(columns={"p_sc": "p_sc_secc"}),
            b.loc[common, ["p_sc"]].rename(columns={"p_sc": "p_sc_census"}),
            shift,
        ],
        axis=1,
    )
    out = out[out["n"] >= 50_000]
    return out.reindex(out["d_p_sc"].abs().sort_values(ascending=False).index).head(top)


def fmt(df: pd.DataFrame, decimals: int = 3) -> str:
    return df.round(decimals).to_string()
