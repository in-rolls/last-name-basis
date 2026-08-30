"""Kerala, where the question often has no object. Entry point: `make a10`."""

from __future__ import annotations

import json
from pathlib import Path

import data as source
import pandas as pd

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", HERE / "out/fig"
CUES = ["last_token", "written_surname", "given_name"]


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    everyone = source.load()
    if everyone is None:
        print(f"skipped: {source.source_path()} not present")
        return

    shape = source.name_shape(everyone)
    buckets = everyone["bucket"].value_counts(normalize=True).to_dict()
    scored = source.scored_set(everyone)

    cues = pd.DataFrame([source.discrimination(scored, c) for c in CUES])
    cues.to_csv(TAB / "cues.csv", index=False)

    summary = {
        "name_shape": shape,
        "buckets": buckets,
        "scored": {
            "candidates": int(len(scored)),
            "share_of_all": float(len(scored) / len(everyone)),
            "sc_share": float((scored["bucket"] == "Scheduled Caste").mean()),
            # Dropped deliberately: in Kerala these are reservation categories
            # as much as religious ones, and scoring them would make religion a
            # predictor. Blanks are dropped too, treated as missing at random by
            # instruction, though the label pattern argues they are not.
            "dropped": {
                b: float(buckets.get(b, 0.0))
                for b in ("Muslim", "Christian", "no community given")
            },
        },
        "cues": cues.set_index("cue").to_dict("index"),
    }
    (TAB / "summary.json").write_text(json.dumps(summary, indent=2))

    import figures

    figures.cues(cues, shape, FIG / "cues.png")
    print(f"wrote {TAB} and {FIG}")


if __name__ == "__main__":
    main()
