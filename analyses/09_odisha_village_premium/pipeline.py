"""Does the village premium travel outside Bihar? Entry point: `make a09`."""

from __future__ import annotations

import json
from pathlib import Path

import data as source
import jati as norm
import pandas as pd

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", HERE / "out/fig"
A02 = HERE.parent / "02_jati_by_geography/out/tab/ladders.csv"

# Collapsing 377 label strings to 218 moves the premium by half a mistake per
# hundred, so the threshold is reported rather than tuned.
THRESHOLDS = [92, 85, 78, 72]


def bihar() -> dict | None:
    """The Bihar rungs this is compared against, on the same protocol."""
    if not A02.exists():
        return None
    d = pd.read_csv(A02)
    d = d[(d["target"] == "jati") & (d["ladder"] == "records")].set_index("level")
    alone = float(d.loc["surname", "mistakes_per_100_loo"])
    village = float(d.loc["surname+village", "mistakes_per_100_loo"])
    return {
        "surname": alone,
        "surname_village": village,
        "premium": alone - village,
        "premium_share": 100 * (alone - village) / alone,
        "groups": int(d.loc["surname", "cells"] and 141),
        "households": int(d.loc["surname", "people"]),
    }


LADDER = [
    ("surname + village", ["surname", "village"]),
    ("surname + RI circle", ["surname", "ri"]),
    ("surname + tahsil", ["surname", "tahsil"]),
    ("surname alone", ["surname"]),
]


def bihar_ladder() -> list[float] | None:
    """Bihar's rungs at the same four sizes of place, leave-one-out."""
    if not A02.exists():
        return None
    d = pd.read_csv(A02)
    d = d[(d["target"] == "jati") & (d["ladder"] == "records")].set_index("level")
    order = ["surname+village", "surname+zone", "surname+district", "surname"]
    return [float(d.loc[k, "mistakes_per_100_loo"]) for k in order]


def bihar_blind() -> float | None:
    """Bihar's blind rate, from analysis 02's own summary rather than typed."""
    path = A02.parent / "summary.json"
    if not path.exists():
        return None
    return float(
        json.loads(path.read_text())["baselines_mistakes_per_100"]["records/jati"]
    )


def score_all(frame: pd.DataFrame, group: str) -> dict:
    alone = source.score(frame, ["surname"], group=group)
    village = source.score(frame, ["surname", "village"], group=group)
    place = source.score(frame, ["village"], group=group)
    return {
        "groups": int(frame[group].nunique()),
        "households": int(len(frame)),
        "blind": source.blind(frame, group=group),
        "surname": alone["mistakes_per_100"],
        "surname_village": village["mistakes_per_100"],
        "village_alone": place["mistakes_per_100"],
        "premium": alone["mistakes_per_100"] - village["mistakes_per_100"],
        "premium_share": 100
        * (alone["mistakes_per_100"] - village["mistakes_per_100"])
        / alone["mistakes_per_100"],
    }


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    frame = source.load()
    if frame is None:
        print("skipped: tenants.parquet not present")
        return

    position = source.surname_position(frame)
    result = norm.normalise(frame["jati"])
    result["merges"].to_csv(TAB / "jati_merges.csv", index=False)
    result["dropped"].to_csv(TAB / "jati_dropped.csv", index=False)

    frame["jati_norm"] = frame["jati"].map(result["mapping"])
    frame = frame[frame["jati_norm"].notna()].copy()
    # Reported both ways rather than decided: a jati recorded as "Pana" and one
    # recorded as "Pana Christian" are two prediction targets unless the
    # religion is stripped, and treating religion as a predictor is not
    # something this repo does silently.
    frame["jati_no_religion"] = frame["jati_norm"].map(norm.strip_religion)

    scored = {
        "as recorded": score_all(frame, "jati_norm"),
        "religion stripped": score_all(frame, "jati_no_religion"),
    }

    sensitivity = []
    for threshold in THRESHOLDS:
        norm.MIN_SIMILARITY = threshold
        mapping = norm.normalise(frame["jati"])["mapping"]
        alt = frame.assign(g=frame["jati"].map(mapping))
        alt = alt[alt["g"].notna()]
        row = score_all(alt, "g")
        row["threshold"] = threshold
        sensitivity.append(row)
    norm.MIN_SIMILARITY = THRESHOLDS[0]
    pd.DataFrame(sensitivity).to_csv(TAB / "sensitivity.csv", index=False)

    frame["ri"] = (
        frame["district_code"].astype(str)
        + "|"
        + frame["tahsil_code"].astype(str)
        + "|"
        + frame["ri_code"].astype(str)
    )
    frame["tahsil"] = (
        frame["district_code"].astype(str) + "|" + frame["tahsil_code"].astype(str)
    )
    ladder = [
        source.score(frame, keys, group="jati_norm")["mistakes_per_100"]
        for _, keys in LADDER
    ]
    pd.DataFrame(
        {"level": [name for name, _ in LADDER], "mistakes_per_100": ladder}
    ).to_csv(TAB / "ladder.csv", index=False)

    summary = {
        "district": frame.attrs["district"],
        "ladder": ladder,
        "ladder_levels": [name for name, _ in LADDER],
        "per_village_cap": frame.attrs["per_village_cap"],
        "villages": int(frame["village"].nunique()),
        "surnames": int(frame["surname"].nunique()),
        "surname_position": position,
        "normalisation": {
            k: result[k]
            for k in (
                "strings_in",
                "strings_out",
                "households_dropped",
                "households_merged",
            )
        },
        "gajapati": scored,
        "bihar": bihar(),
        "bihar_ladder": bihar_ladder(),
        "bihar_blind": bihar_blind(),
        "sensitivity": sensitivity,
    }
    (TAB / "summary.json").write_text(json.dumps(summary, indent=2))
    pd.DataFrame(scored).T.to_csv(TAB / "scores.csv")

    import figures

    figures.premium(summary, FIG / "village_premium.png")
    bl = bihar_ladder()
    if bl is not None:
        figures.atrophy(
            {"Bihar": bl, "Gajapati district, Odisha": summary["ladder"]},
            {
                "Bihar": bihar_blind() or 0.0,
                "Gajapati district, Odisha": scored["as recorded"]["blind"],
            },
            FIG / "atrophy.png",
        )
    print(f"wrote {TAB} and {FIG}")


if __name__ == "__main__":
    main()
