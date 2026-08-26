"""Do neighbours rescue an uninformative surname? Entry point: `make a06`."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import neighbours as nb
import pandas as pd

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", HERE / "out/fig"

LADDERS = [
    ("land records", "records_ladder", "accounts", 3),
    ("Mahadalit census", "census_ladder", "households", 4),
]


def ladders():
    """analysis 02's loaders, imported without colliding on the name `data`."""
    folder = HERE.parent / "02_jati_by_geography"
    sys.path.insert(0, str(folder))
    saved = sys.modules.pop("data", None)
    try:
        spec = importlib.util.spec_from_file_location(
            "jati_data_06", folder / "data.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.modules.pop("data", None)
        if saved is not None:
            sys.modules["data"] = saved
        sys.path.remove(str(folder))


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    source = ladders()

    results, surname_tables = [], []
    for label, loader, weight, parts in LADDERS:
        ladder = getattr(source, loader)()
        if ladder is None:
            continue
        vsj = nb.village_surname_jati(ladder, "surname+village", weight, parts)
        scored = nb.fit_and_score(vsj, weight)
        scored["ladder"] = label
        results.append(scored)

        per = nb.per_surname(vsj, weight, scored["alpha"])
        per["ladder"] = label
        surname_tables.append(per)

    table = pd.DataFrame(results)
    table.to_csv(TAB / "held_out.csv", index=False)
    per_surname = pd.concat(surname_tables, ignore_index=True)
    per_surname.to_csv(TAB / "per_surname.csv", index=False)

    summary = {"held_out": table.set_index("ladder").to_dict("index")}
    (TAB / "summary.json").write_text(json.dumps(summary, indent=2))

    import figures

    figures.bracket(table, FIG / "bracket.png")
    figures.per_surname(
        per_surname[per_surname["ladder"] == "land records"],
        FIG / "per_surname.png",
    )

    print(json.dumps(summary, indent=2))
    print("\n=== the commonest surnames, held-out villages ===")
    print(per_surname.round(1).to_string(index=False))
    print(f"\nwrote {TAB} and {FIG}")


if __name__ == "__main__":
    main()
