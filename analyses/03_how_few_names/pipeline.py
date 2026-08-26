"""How concentrated are Indian surnames, and what counts as one?

Entry point: `make a03`.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import data as source
import figures
import pandas as pd
import titles
import variants

HERE = Path(__file__).resolve().parent
TAB, FIG = HERE / "out/tab", HERE / "out/fig"
BIG_STATE = 500_000


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def analysis_01_scores() -> pd.DataFrame | None:
    """Per-surname mistakes per 100, from analysis 01's data, to join the two.

    Deliberately does not import analysis 01's `metrics`: that module does
    `from data import ...`, which resolves to *this* analysis's `data.py` once
    it is in `sys.modules`, and the resulting ImportError was being swallowed.
    The one number needed here is one line to compute.
    """
    folder = HERE.parent / "01_surname_to_category"
    if not (folder / "data.py").exists():
        return None
    try:
        secc = _load("secc_for_03", folder / "data.py")
        table = secc.per_name(secc.load_cells())
    except (FileNotFoundError, ImportError):
        return None

    probs = table[secc.PROB_COLS]
    table = table.assign(err=1 - probs.max(axis=1))
    counts = table[[f"n_{c}" for c in secc.CATEGORIES]].sum()
    prior = (counts / counts.sum()).to_numpy()
    table.attrs["blind"] = float((1 - prior.max()) * 100)
    return table.set_index("last_name")


# Analysis 04 found that these states write the surname FIRST, so instate's
# last-token `last_name` holds a given name for them and any count of "how many
# surnames cover half the state" is about the wrong word. Withdrawn rather than
# reported: see analyses/04_which_token_is_the_surname.
SURNAME_FIRST = {"Maharashtra", "Gujarat"}


def state_table(counts: pd.DataFrame) -> pd.DataFrame:
    drop_clear = titles.LEVELS["minus_clear"]
    drop_all = titles.LEVELS["minus_all"]
    is_clear = counts["last_name"].isin(drop_clear)
    is_any = counts["last_name"].isin(drop_all)

    rows = []
    for state in counts.columns:
        if state in ("last_name", "national"):
            continue
        s = counts[state]
        people = float(s.sum())
        if people < BIG_STATE or state in SURNAME_FIRST:
            continue
        rows.append(
            {
                "state": state,
                "people": people,
                "clear_share": float(s[is_clear].sum() / people),
                "title_share": float(s[is_any].sum() / people),
                "names_for_half": source.names_for(s),
                "names_for_half_real": source.names_for(s[~is_any]),
                "top10_share": float(source.curve(s)[9]),
            }
        )
    return pd.DataFrame(rows).sort_values("title_share", ascending=False)


def main() -> None:
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)

    counts = source.surnames()
    if counts is None:
        raise SystemExit("instate not found; see analyses/03_how_few_names/README.md")

    titles.table().to_csv(TAB / "titles.csv", index=False)
    national = counts["national"]
    total = float(national.sum())

    curves, summary_levels, marks = {}, {}, {}
    for level, drop in titles.LEVELS.items():
        kept = national[~counts["last_name"].isin(drop)]
        curves[level] = source.curve(kept)
        marks[level] = source.names_for(kept, 0.25)
        summary_levels[level] = {
            "label": titles.LEVEL_LABEL[level],
            "people_dropped_share": float(
                national[counts["last_name"].isin(drop)].sum() / total
            ),
            "top_name_share": float(curves[level][0]),
            "names_for_25": marks[level],
            "names_for_50": source.names_for(kept, 0.5),
            "names_for_90": source.names_for(kept, 0.9),
        }

    per_state = state_table(counts)
    per_state.to_csv(TAB / "by_state.csv", index=False)

    merges = variants.assign(counts)
    merged = variants.merged_counts(counts, merges, "national")
    moved = float(merges["n"].sum() / total)
    merges.head(200).to_csv(TAB / "variant_merges.csv", index=False)

    summary = {
        "names": int(len(counts)),
        "tokens": total,
        "commonest": str(counts.nlargest(1, "national")["last_name"].iloc[0]),
        "levels": summary_levels,
        "variants": {
            "merges": int(len(merges)),
            "people_moved": float(merges["n"].sum()),
            "share_of_tokens_moved": moved,
        },
    }

    scored = analysis_01_scores()
    if scored is not None:
        rows = []
        for token in list(titles.CLEAR) + list(titles.AMBIGUOUS):
            n = float(national[counts["last_name"] == token].sum())
            if n <= 0 or token not in scored.index:
                continue
            rows.append(
                {
                    "token": token,
                    "kind": "clear" if token in titles.CLEAR else "ambiguous",
                    "people": n,
                    "share_of_roll": n / total,
                    "mistakes_per_100": float(scored.loc[token, "err"] * 100),
                }
            )
        cost = pd.DataFrame(rows).sort_values("people", ascending=False)
        cost.to_csv(TAB / "title_signal.csv", index=False)
        summary["blind_mistakes_per_100"] = scored.attrs["blind"]

    # Who carries these names. This reads the raw per-state rolls -- hundreds
    # of megabytes each -- so it takes minutes and the result is cached. Delete
    # out/tab/sex_marked.csv to recompute.
    sex_path = TAB / "sex_marked.csv"
    if sex_path.exists():
        sex = pd.read_csv(sex_path)
    else:
        gender = source.first_name_gender()
        rows = (
            [
                source.sex_marked_share(st, gender)
                for st in (
                    "bihar",
                    "uttar_pradesh",
                    "west_bengal",
                    "maharashtra",
                    "kerala",
                    "tamil_nadu",
                )
            ]
            if gender is not None
            else []
        )
        sex = pd.DataFrame([r for r in rows if r is not None])
        if not sex.empty:
            sex.to_csv(sex_path, index=False)

    if not sex.empty:
        # Gender is looked up by first name, and naampy knows only some of them.
        # Tamil Nadu matches 4% of its roll, which is too thin a slice to
        # describe the state, so anything under a fifth is dropped rather than
        # quietly reported.
        shown = sex[sex["coverage"] >= 0.15]
        summary["sex_marked"] = shown.set_index("state").to_dict("index")
        summary["sex_marked_dropped_for_coverage"] = sorted(
            sex.loc[sex["coverage"] < 0.15, "state"]
        )
        if not shown.empty:
            figures.sex_marked(shown, FIG / "sex_marked.png")

    initials = source.kerala_initial_share()
    if initials is not None:
        summary["kerala_single_initial_share"] = initials
    (TAB / "summary.json").write_text(json.dumps(summary, indent=2))

    figures.concentration(curves, marks, FIG / "concentration.png")
    figures.title_share(per_state, FIG / "title_share.png")
    figures.names_for_half(per_state, FIG / "names_for_half.png")
    figures.variant_band(
        curves["as_written"], source.curve(merged), moved, FIG / "variant_band.png"
    )

    print(json.dumps(summary, indent=2))
    print("\n=== by state ===")
    print(
        per_state.assign(
            title_share=lambda d: (d.title_share * 100).round(1),
            clear_share=lambda d: (d.clear_share * 100).round(1),
        )[
            [
                "state",
                "clear_share",
                "title_share",
                "names_for_half",
                "names_for_half_real",
            ]
        ].to_string(
            index=False
        )
    )
    if scored is not None:
        print(
            "\n=== what the titles cost you (blind = %.1f) ==="
            % summary["blind_mistakes_per_100"]
        )
        print(cost.round(3).to_string(index=False))
    print(f"\nwrote {TAB} and {FIG}")


if __name__ == "__main__":
    main()
