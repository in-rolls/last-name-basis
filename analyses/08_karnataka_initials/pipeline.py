"""Karnataka: when the last token is an initial. Entry point: `make a08`."""

from __future__ import annotations

import json
from pathlib import Path

import data as source
import pandas as pd

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", HERE / "out/fig"


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    d = source.load()
    if d is None:
        print(f"skipped: {source.source_path()} not present")
        return

    counts = source.initial_share(d)
    scores = pd.DataFrame(
        [
            source.score(d, "naive_surname"),
            source.score(d, "clean_surname"),
            source.score(d, "pin"),
        ]
    )
    scores.to_csv(TAB / "scores.csv", index=False)

    naive = d["naive_surname"].value_counts().head(12)
    clean = d["clean_surname"].value_counts().head(12)
    tokens = pd.DataFrame(
        {
            "rank": range(1, 13),
            "naive": naive.index,
            "naive_n": naive.to_numpy(),
            "clean": clean.index,
            "clean_n": clean.to_numpy(),
        }
    )
    tokens.to_csv(TAB / "commonest_tokens.csv", index=False)

    summary = {
        **counts,
        "categories": d["category"].value_counts().to_dict(),
        "scores": scores.set_index("cue").to_dict("index"),
        # The result is a null and is meant to read as one: cleaning changes
        # which names you get and not what they predict.
        "cleaning_changes_prediction_by": float(
            scores.set_index("cue").loc["clean_surname", "mistakes_per_100"]
            - scores.set_index("cue").loc["naive_surname", "mistakes_per_100"]
        ),
    }
    (TAB / "summary.json").write_text(json.dumps(summary, indent=2))

    import figures

    figures.naive_vs_clean(tokens, scores, FIG / "naive_vs_clean.png")
    print(f"wrote {TAB} and {FIG}")


if __name__ == "__main__":
    main()
