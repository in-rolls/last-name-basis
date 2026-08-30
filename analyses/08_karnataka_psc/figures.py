"""Figures for analysis 08."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from last_name_basis.style import ACCENT, INK, MUTED, style_axes  # noqa: E402


def naive_vs_clean(tokens, scores, out: Path) -> None:
    """Cleaning changes the names completely and the prediction not at all.

    Left: what a last-token rule calls Karnataka's commonest surnames, against
    what survives dropping single letters. Right: what either is worth.
    """
    fig, (ax, bx) = plt.subplots(
        1, 2, figsize=(11.4, 5.2), gridspec_kw={"width_ratios": [1.55, 1]}
    )

    n = 10
    y = np.arange(n)[::-1]
    ax.barh(y + 0.2, tokens["naive_n"][:n], height=0.36, color=ACCENT)
    ax.barh(y - 0.2, tokens["clean_n"][:n], height=0.36, color=INK)
    for yi, row in zip(y, tokens.head(n).itertuples()):
        ax.text(
            row.naive_n + 12,
            yi + 0.2,
            f"{row.naive}",
            va="center",
            fontsize=9,
            color=ACCENT,
        )
        ax.text(
            row.clean_n + 12,
            yi - 0.2,
            f"{row.clean.title()}",
            va="center",
            fontsize=9,
            color=INK,
        )
    ax.set_yticks(y)
    ax.set_yticklabels([f"#{i}" for i in tokens["rank"][:n]], fontsize=9)
    ax.set_xlim(0, 1100)
    ax.set_xlabel("candidates carrying it")
    ax.set_title(
        "What a last-token rule calls a surname (red)\n"
        "against what is left after dropping single letters (black)",
        color=INK,
        loc="left",
        fontsize=11,
    )
    style_axes(ax)
    ax.grid(axis="y", visible=False)

    s = scores.set_index("cue")
    labels = ["knowing nothing", "naive last token", "cleaned surname", "PIN code"]
    values = [
        s.loc["naive_surname", "blind_per_100"],
        s.loc["naive_surname", "mistakes_per_100"],
        s.loc["clean_surname", "mistakes_per_100"],
        s.loc["pin", "mistakes_per_100"],
    ]
    yb = np.arange(len(values))[::-1]
    bx.barh(yb, values, height=0.55, color=[MUTED, ACCENT, INK, MUTED])
    for yi, v in zip(yb, values):
        bx.text(v + 0.7, yi, f"{v:.0f}", va="center", fontsize=10, color=INK)
    bx.set_yticks(yb)
    bx.set_yticklabels(labels, fontsize=9.5)
    bx.set_xlim(0, 66)
    bx.set_xlabel("of 100 candidates, how many you get wrong")
    gap = values[0] - min(values[1], values[2])
    bx.set_title(
        f"And either way it buys {gap:.0f} mistakes out of {values[0]:.0f}",
        color=INK,
        loc="left",
        fontsize=11,
    )
    style_axes(bx)
    bx.grid(axis="y", visible=False)

    fig.tight_layout()
    fig.savefig(out, dpi=170)
    plt.close(fig)


def by_category(split, out: Path) -> None:
    """Analysis 05's decomposition, on a different source and different labels.

    Same construction as `05/figures.by_caste`: the blind guess names the
    largest category, so each group's own blind rate is 0 or 100, and the bars
    are what the surname leaves.
    """
    d = split.sort_values("wrong_per_100", ascending=False)
    y = np.arange(len(d), dtype=float)[::-1]
    h = 0.36

    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    ax.barh(y + h / 2, d["blind_wrong_per_100"], color=MUTED, height=h)
    colours = ["#b8322f" if "Scheduled" in c else INK for c in d["category"]]
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
                "with the surname",
                va="center",
                fontsize=8,
                color="white",
            )

    ax.set_yticks(y)
    ax.set_yticklabels(
        [
            f"{r.category}\n{r.share_of_candidates:.0%} of candidates"
            for r in d.itertuples()
        ],
        fontsize=9.5,
    )
    ax.set_xlim(0, 112)
    ax.set_ylim(-0.8, len(d) - 0.2)
    ax.set_xlabel("of 100 candidates in this category, how many the guess gets wrong")
    ax.set_title(
        "The surname identifies a General candidate, and largely fails the rest\n"
        "Karnataka PSC select lists, where the quota category is self-declared.",
        color=INK,
        loc="left",
        fontsize=11.5,
    )
    style_axes(ax)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(out, dpi=170)
    plt.close(fig)
