"""Score the Bihar ladders: how fast caste information atrophies with distance.

Single entry point: `make a02`.
"""

from __future__ import annotations

import json
from pathlib import Path

import data as source
import mahadalit
import pandas as pd

from last_name_basis import leave_one_out_ladder, score_ladder

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", HERE / "out/fig"

TARGETS = ["jati", "category_religion", "category"]


def score(ladder: pd.DataFrame, weight: str, target: str) -> pd.DataFrame:
    d = source.with_group(ladder, target)
    out = score_ladder(d, group="group", weight=weight)
    loo = leave_one_out_ladder(d, group="group", weight=weight)
    out = out.merge(loo, on="level")
    out["target"] = target
    out["rung"] = out["level"].map(source.RUNG_LABEL).fillna(out["level"])
    out["place_only"] = out["level"].isin(source.PLACE_ONLY)
    return out


def baseline(ladder: pd.DataFrame, weight: str, target: str) -> float:
    """Mistakes per hundred knowing nothing at all -- no name, no place."""
    d = source.with_group(ladder[ladder["level"] == "surname"], target)
    totals = d.groupby("group", observed=True)[weight].sum()
    return float((1 - totals.max() / totals.sum()) * 100)


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    records = source.records_ladder()
    census = source.census_ladder()
    if records is None:
        raise SystemExit("naampata ladders not found; see analyses/02/README.md")

    scored, baselines = [], {}
    for target in TARGETS:
        try:
            s = score(records, "accounts", target)
        except FileNotFoundError:
            print(f"skipping {target}: caste dictionary unavailable")
            continue
        s["ladder"] = "records"
        scored.append(s)
        baselines[f"records/{target}"] = baseline(records, "accounts", target)

    if census is not None:
        s = score(census, "households", "jati")
        s["ladder"] = "census"
        scored.append(s)
        baselines["census/jati"] = baseline(census, "households", "jati")

    # The Mahadalit census, scored one rung finer than naampata's shipped
    # ladder: it carries the hamlet, which is the finest geography in any of
    # this data and has never been scored.
    mahadalit_summary = None
    raw = mahadalit.load()
    if raw is not None:
        lad = mahadalit.ladder(raw)
        hamlet = score_ladder(lad, group="jati", weight="households")
        hamlet = hamlet.merge(
            leave_one_out_ladder(lad, group="jati", weight="households"), on="level"
        )
        hamlet["ladder"] = "mahadalit_raw"
        hamlet["target"] = "jati"
        hamlet["rung"] = (
            hamlet["level"].map(mahadalit.RUNG_LABEL).fillna(hamlet["level"])
        )
        hamlet["place_only"] = hamlet["level"].isin(mahadalit.PLACE_ONLY)
        scored.append(hamlet)
        mahadalit_summary = {
            "households": int(len(raw)),
            "jatis": int(raw["jati"].nunique()),
            "districts": int(raw["district"].nunique()),
        }

    table = pd.concat(scored, ignore_index=True)
    table.to_csv(TAB / "ladders.csv", index=False)

    summary = {
        "baselines_mistakes_per_100": baselines,
        "groups": {
            "jati": int(records["jati"].nunique()),
            "category": int(records["category"].nunique()),
        },
        "records_accounts": int(
            records.loc[records["level"] == "surname", "accounts"].sum()
        ),
    }
    if mahadalit_summary:
        summary["mahadalit"] = mahadalit_summary
    (TAB / "summary.json").write_text(json.dumps(summary, indent=2))

    import figures

    figures.atrophy(table, baselines, FIG / "atrophy.png")
    if (table["ladder"] == "mahadalit_raw").any():
        figures.hamlet_ladder(table, FIG / "hamlet_ladder.png")
    figures.name_vs_place(table, baselines, FIG / "name_vs_place.png")
    # The rate for this specific surname, not the ladder average, so the
    # picture and its caption cannot disagree.
    devanagari_singh = "\u0938\u093f\u0902\u0939"
    v = records[records["level"] == "surname+village"].copy()
    v["last"] = v["cell"].str.rsplit("|", n=1).str[-1]
    v = v[v["last"] == devanagari_singh]
    by = v.groupby("cell", observed=True)["accounts"]
    size, top = by.sum(), by.max()
    singh_rate = float(((size / size.sum()) * (1 - top / size)).sum() * 100)

    figures.rung_waffles(
        records,
        source,
        FIG / "rung_waffles.png",
        surname=devanagari_singh,
        label="Singh",
        target_mistakes=singh_rate,
    )

    show = table[
        [
            "ladder",
            "target",
            "rung",
            "mistakes_per_100",
            "mistakes_per_100_loo",
            "median_groups_in_cell",
            "cells",
        ]
    ]
    print(json.dumps(summary, indent=2))
    for (lad, tgt), g in show.groupby(["ladder", "target"], observed=True):
        print(f"\n=== {lad} / {tgt} ===")
        print(g.drop(columns=["ladder", "target"]).to_string(index=False))
    print(f"\nwrote {TAB} and {FIG}")


if __name__ == "__main__":
    main()
