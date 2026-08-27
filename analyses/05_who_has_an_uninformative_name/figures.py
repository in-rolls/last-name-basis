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
    blind = table.attrs["blind"]
    d = table.sort_values("mistakes_per_100", ascending=False)
    y = np.arange(len(d))[::-1]
    colours = [ACCENT if "Scheduled Caste" in c else INK for c in d["caste"]]

    fig, ax = plt.subplots(figsize=(8.6, 3.9))
    ax.barh(y, d["mistakes_per_100"], color=colours, height=0.58)
    ax.axvline(blind, color=MUTED, ls="--", lw=1.4)
    ax.text(
        blind + 0.4,
        len(d) - 0.55,
        f"knowing nothing at all — {blind:.0f}",
        fontsize=9,
        color=MUTED,
    )
    for yi, (c, v, s) in zip(
        y, zip(d["caste"], d["mistakes_per_100"], d["share_of_people"])
    ):
        ax.text(v + 0.4, yi, f"{v:.0f}", va="center", fontsize=9.5, color=INK)
        ax.text(0.4, yi, f"{s:.0%} of India", va="center", fontsize=8.5, color="white")
    ax.set_yticks(y)
    ax.set_yticklabels(d["caste"], fontsize=10)
    ax.set_xlim(0, 33)
    ax.set_ylim(-0.9, len(d) - 0.3)
    ax.set_xlabel("of 100 people like you, how many the guess gets wrong")
    ax.set_title(
        "A name-based guess does nothing for Dalits\n"
        "It is as wrong about them as knowing nothing, and much better "
        "about everyone else.",
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
