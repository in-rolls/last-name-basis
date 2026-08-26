"""Whose name tells you nothing. Entry point: `make a05`."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import data as source
import pandas as pd

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", HERE / "out/fig"
SEX_STATES = ["bihar", "uttar_pradesh", "west_bengal", "rajasthan", "maharashtra"]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def analysis_01():
    """Analysis 01's scored per-name table, loaded without the name collision.

    Its `metrics` does `from data import ...`, which resolves to *this*
    analysis's data.py once that is in sys.modules. Import it under a namespaced
    key with analysis 01's folder first on the path.
    """
    import sys

    folder = HERE.parent / "01_surname_to_category"
    sys.path.insert(0, str(folder))
    saved = sys.modules.pop("data", None)
    try:
        secc = _load("secc_data_05", folder / "data.py")
        sys.modules["data"] = secc
        metrics = _load("secc_metrics_05", folder / "metrics.py")
        table = secc.per_name(secc.load_cells())
        base = secc.base_rates(table)
        return secc, metrics.add_metrics(table, base)
    finally:
        sys.modules.pop("data", None)
        if saved is not None:
            sys.modules["data"] = saved
        sys.path.remove(str(folder))


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    secc, named = analysis_01()
    caste = source.by_caste(named, secc.PROB_COLS, secc.CATEGORIES)
    caste.to_csv(TAB / "by_caste.csv", index=False)

    summary = {
        "blind_per_100": caste.attrs["blind"],
        "by_caste": caste.set_index("caste").to_dict("index"),
        "spread": source.spread(named),
    }

    sex_path = TAB / "by_sex.csv"
    if sex_path.exists():
        sex = pd.read_csv(sex_path)
    else:
        gender = source.first_name_gender()
        rows = []
        if gender is not None:
            for state in SEX_STATES:
                sexed = source.surname_by_sex(state, gender)
                if sexed is None:
                    continue
                r = source.by_sex(named, sexed, secc.PROB_COLS)
                r["state"] = state
                rows.append(r)
        sex = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
        if not sex.empty:
            sex.to_csv(sex_path, index=False)

    if not sex.empty:
        wide = sex.pivot(index="state", columns="who", values="mistakes_per_100")
        wide["gap"] = wide["women"] - wide["men"]
        wide.to_csv(TAB / "sex_gap.csv")
        summary["by_sex"] = wide.to_dict("index")

    (TAB / "summary.json").write_text(json.dumps(summary, indent=2))

    import figures

    figures.by_caste(caste, FIG / "by_caste.png")
    if not sex.empty:
        figures.by_sex(wide, caste.attrs["blind"], FIG / "by_sex.png")

    print(json.dumps(summary, indent=2))
    print("\n=== mistakes made on you, by your own caste ===")
    print(caste.round(3).to_string(index=False))
    if not sex.empty:
        print("\n=== mistakes made on you, by sex ===")
        print(wide.round(2).to_string())
    print(f"\nwrote {TAB} and {FIG}")


if __name__ == "__main__":
    main()
