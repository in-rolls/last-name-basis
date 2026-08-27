"""Where a surname works, state by state. Entry point: `make a07`."""

from __future__ import annotations

import json
from pathlib import Path

import data as source

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", HERE / "out/fig"
SPOTLIGHT = ["assam", "bihar", "punjab", "haryana"]


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    per = source.load()
    table = source.state_table(per)
    table.to_csv(TAB / "by_state.csv", index=False)

    spotlight = {s: source.decisive_names(per, s) for s in SPOTLIGHT}
    for state, d in spotlight.items():
        d.insert(0, "state", state)
    if spotlight:
        import pandas as pd

        pd.concat(spotlight.values(), ignore_index=True).to_csv(
            TAB / "decisive_names.csv", index=False
        )

    best, worst = table.iloc[0], table.iloc[-1]
    summary = {
        "states": int(len(table)),
        "names_total": int(table["names"].sum()),
        "coverage_share_range": [
            float(table["covered_share"].min()),
            float(table["covered_share"].max()),
        ],
        "best": {
            "state": best["state"],
            "removed": float(best["removed"]),
            "covered_share": float(best["covered_share"]),
        },
        "worst": {
            "state": worst["state"],
            "removed": float(worst["removed"]),
            "covered_share": float(worst["covered_share"]),
        },
        # The objection a reader raises first: the floor keeps common names,
        # and common names are the uninformative ones. If the ordering held
        # only before this control, the result would be an artefact of it.
        "top25_control": {
            "spearman_with_full": float(
                table["removed"].rank().corr(table["removed_top25"].rank())
            ),
            "by_state": {
                r["state"]: float(r["removed_top25"]) for _, r in table.iterrows()
            },
        },
        "by_state": {
            r["state"]: {
                k: float(r[k])
                for k in (
                    "removed",
                    "removed_top25",
                    "blind",
                    "with_name",
                    "covered_share",
                    "sc_share_of_extract",
                )
            }
            | {"names": int(r["names"])}
            for _, r in table.iterrows()
        },
    }
    (TAB / "summary.json").write_text(json.dumps(summary, indent=2))

    import figures

    figures.where_it_works(table, FIG / "where_it_works.png")
    figures.decisive(spotlight, FIG / "decisive_names.png")
    print(f"wrote {TAB} and {FIG}")


if __name__ == "__main__":
    main()
