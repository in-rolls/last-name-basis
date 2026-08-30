"""Figures for analysis 07."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from last_name_basis.style import ACCENT, INK, MUTED, style_axes  # noqa: E402


def where_it_works(table, out: Path) -> None:
    """How much of the gap a surname closes, state by state.

    The coverage column is printed inside the figure rather than left to the
    caption: every bar describes surnames that cleared a 100-record disclosure
    floor, and that floor keeps between 3% and 19% of a state's people.
    """
    d = table.sort_values("removed")
    y = np.arange(len(d), dtype=float)
    colours = [ACCENT if s in ("punjab", "haryana") else INK for s in d["state"]]

    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    ax.barh(y, d["removed"], color=colours, height=0.62)
    ax.scatter(
        d["removed_top25"], y, s=26, facecolor="white", edgecolor=MUTED, zorder=3
    )

    for yi, row in zip(y, d.itertuples()):
        ax.text(
            row.removed + 1.2,
            yi,
            f"{row.removed:.0f}",
            va="center",
            fontsize=9.5,
            color=INK,
        )
        ax.text(
            -2.0,
            yi,
            f"{row.covered_share:.0f}%",
            va="center",
            ha="right",
            fontsize=8,
            color=MUTED,
        )

    ax.set_yticks(y)
    ax.set_yticklabels(d["state"], fontsize=10)
    ax.set_xlim(-14, 78)
    ax.set_xlabel("how much of the gap the surname closes (%)")
    ax.set_title(
        "The same guess closes two thirds of the gap in Assam and none in "
        "Haryana\n"
        "Grey number: share of the state's people these surnames cover. "
        "Open circle: the\nsame score with every state cut to its 25 "
        "commonest names.",
        color=INK,
        loc="left",
        fontsize=11.5,
    )
    style_axes(ax)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(out, dpi=170)
    plt.close(fig)


def decisive(frames: dict, out: Path) -> None:
    """What carries a state's signal: one or two big names, or nothing."""
    states = list(frames)
    fig, axes = plt.subplots(1, len(states), figsize=(3.1 * len(states), 3.4))
    for ax, state in zip(np.atleast_1d(axes), states):
        d = frames[state]
        if len(d) == 0:
            ax.text(
                0.5,
                0.5,
                "no surname here\nis majority Dalit",
                ha="center",
                va="center",
                fontsize=10,
                color=MUTED,
                transform=ax.transAxes,
            )
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
        else:
            y = np.arange(len(d))[::-1]
            ax.barh(y, d["share_of_extract"], color=INK, height=0.55)
            for yi, row in zip(y, d.itertuples()):
                ax.text(
                    row.share_of_extract + 0.15,
                    yi,
                    f"{row.p_sc:.0%} Dalit",
                    va="center",
                    fontsize=8.5,
                    color=MUTED,
                )
            ax.set_yticks(y)
            ax.set_yticklabels(d["last_name"], fontsize=10)
            ax.set_xlim(0, 16)
            style_axes(ax)
            ax.grid(axis="y", visible=False)
        ax.set_title(state, fontsize=11, color=INK, loc="left")
    fig.supxlabel(
        "share of the surnames kept for this state, by people (%)", fontsize=9.5
    )
    fig.suptitle(
        "One or two big names carry a state, or nothing does",
        fontsize=12,
        color=INK,
        x=0.01,
        ha="left",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(out, dpi=170)
    plt.close(fig)


def decides_versus_discriminates(table, out: Path) -> None:
    """Where the two measures disagree, and why.

    The horizontal axis is accuracy against the largest category, which a
    state's composition inflates or suppresses. The vertical axis is how often a
    Dalit's surname outranks a non-Dalit's, which composition cannot touch.
    Kerala sits at the top left: surnames that separate as well as Maharashtra's
    and almost never change the answer, because so few Keralans in the extract
    are Scheduled Caste.
    """
    d = table.copy()
    fig, ax = plt.subplots(figsize=(8.6, 6.0))
    ax.axhline(0.5, color=MUTED, ls=":", lw=1.1)
    ax.text(1, 0.505, "a surname carrying nothing", fontsize=8.5, color=MUTED)

    flagged = {"kerala", "punjab", "haryana", "uttar pradesh", "bihar", "assam"}
    for row in d.itertuples():
        marked = row.state in flagged
        ax.scatter(
            row.removed,
            row.ranks_dalit_higher,
            s=64 if marked else 34,
            color=ACCENT if marked else INK,
            zorder=3,
        )
        if marked:
            ax.annotate(
                row.state,
                (row.removed, row.ranks_dalit_higher),
                textcoords="offset points",
                xytext=(8, -3),
                fontsize=9.5,
                color=ACCENT,
            )

    ax.set_xlim(-3, 72)
    ax.set_ylim(0.45, 1.0)
    ax.set_xlabel("share of the gap closed (%), which the base rate inflates")
    ax.set_ylabel("how often a Dalit's surname outranks a non-Dalit's")
    ax.set_title(
        "Deciding badly is not the same as carrying nothing\n"
        "Kerala's surnames separate about as well as Maharashtra's and change "
        "the answer\nfor almost nobody. Punjab's and Haryana's barely separate "
        "at all.",
        color=INK,
        loc="left",
        fontsize=11.5,
    )
    style_axes(ax)
    fig.tight_layout()
    fig.savefig(out, dpi=170)
    plt.close(fig)
