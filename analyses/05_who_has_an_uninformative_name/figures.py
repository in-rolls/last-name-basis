"""Figures for the differential-error analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from last_name_basis.style import ACCENT, INK, MUTED, style_axes  # noqa: E402


def by_caste(table: pd.DataFrame, out: Path) -> None:
    """Blind against with-name, per group, under one estimator.

    The earlier version plotted `name_vagueness_per_100` under an axis reading
    "how many the guess gets wrong", which is a different quantity, and drew the
    population-wide blind rate across groups whose own blind rates are 0 and
    100. Both are fixed here: the bars are recall error and each group gets its
    own blind bar.
    """
    d = table.sort_values("wrong_per_100", ascending=False)
    y = np.arange(len(d), dtype=float)[::-1]
    h = 0.36

    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    ax.barh(y + h / 2, d["blind_wrong_per_100"], color=MUTED, height=h)
    colours = [ACCENT if "Scheduled Caste" in c else INK for c in d["caste"]]
    ax.barh(y - h / 2, d["wrong_per_100"], color=colours, height=h)

    for yi, row in zip(y, d.itertuples()):
        ax.text(
            row.blind_wrong_per_100 + 1.2,
            yi + h / 2,
            f"{row.blind_wrong_per_100:.0f}",
            va="center",
            fontsize=9,
            color=MUTED,
        )
        ax.text(
            row.wrong_per_100 + 1.2,
            yi - h / 2,
            f"{row.wrong_per_100:.0f}",
            va="center",
            fontsize=9.5,
            color=INK,
        )
        # Only on the widest row: on a 0-wide or 4-wide bar the label spills
        # out of the bar and collides with its own value.
        if yi == y[0]:
            ax.text(
                1.2,
                yi + h / 2,
                "knowing nothing",
                va="center",
                fontsize=8,
                color="white",
            )
            ax.text(
                1.2,
                yi - h / 2,
                "with the name",
                va="center",
                fontsize=8,
                color="white",
            )

    ax.set_yticks(y)
    ax.set_yticklabels(
        [f"{r.caste}\n{r.share_of_people:.0%} of India" for r in d.itertuples()],
        fontsize=9.5,
    )
    ax.set_xlim(0, 112)
    ax.set_ylim(-0.8, len(d) - 0.2)
    ax.set_xlabel("of 100 people in this group, how many the guess gets wrong")
    ax.set_title(
        "The name helps Dalits most, and still leaves them worst off\n"
        "It misses two thirds of Dalits and four percent of everyone else.",
        color=INK,
        loc="left",
        fontsize=12,
    )
    style_axes(ax)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(out, dpi=170)
    plt.close(fig)


def by_sex(wide: pd.DataFrame, blind: float, out: Path) -> None:
    d = wide.sort_values("gap", ascending=False)
    y = np.arange(len(d))[::-1]
    h = 0.34
    fig, ax = plt.subplots(figsize=(8.2, 0.72 * len(d) + 2.0))
    ax.barh(y + h / 2, d["women"], height=h, color=ACCENT, label="women")
    ax.barh(y - h / 2, d["men"], height=h, color=INK, label="men")
    ax.axvline(blind, color=MUTED, ls="--", lw=1.2)
    for yi, (w, m) in zip(y, zip(d["women"], d["men"])):
        ax.text(
            w + 0.4, yi + h / 2, f"{w:.0f}", va="center", fontsize=8.5, color=ACCENT
        )
        ax.text(m + 0.4, yi - h / 2, f"{m:.0f}", va="center", fontsize=8.5, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([s.replace("_", " ").title() for s in d.index], fontsize=9.5)
    ax.set_xlim(0, 36)
    ax.set_xlabel("of 100 people, how many the guess gets wrong")
    ax.set_title(
        "The sex gap changes direction across states\n"
        "Resolved surnames do not support one women-versus-men pattern.",
        color=INK,
        loc="left",
        fontsize=12,
    )
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    style_axes(ax)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(out, dpi=170)
    plt.close(fig)
