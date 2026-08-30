"""Figures for analysis 10."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from last_name_basis.style import ACCENT, INK, MUTED, style_axes  # noqa: E402

LABEL = {
    "last_token": "the last token\nwhat every method here reads",
    "written_surname": "a real written surname\nwhere the name has one",
    "given_name": "the given name\nwhich everyone has",
}


def cues(frame, shape: dict, out: Path) -> None:
    """What each part of a Kerala name gives away, and who has one.

    The bar is how well the cue separates Scheduled Caste candidates from the
    rest; the number beside it is the share of candidates the cue exists for.
    Drawn together because a cue that works for a quarter of people is not
    comparable to one that works for all of them.
    """
    d = frame.set_index("cue").loc[list(LABEL)]
    y = np.arange(len(d))[::-1]
    colours = [ACCENT if c == "last_token" else INK for c in d.index]

    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ax.axvline(0.5, color=MUTED, ls=":", lw=1.2)
    ax.text(0.502, -0.55, "a cue carrying nothing", fontsize=8.5, color=MUTED)
    ax.barh(y, d["ranks_sc_higher"], color=colours, height=0.52)
    for yi, row in zip(y, d.itertuples()):
        ax.text(
            row.ranks_sc_higher + 0.004,
            yi,
            f"{row.ranks_sc_higher:.2f}",
            va="center",
            fontsize=11,
            color=INK,
        )
        ax.text(
            row.ranks_sc_higher + 0.026,
            yi,
            f"{100 * row.share_of_all:.0f}% of candidates have one",
            va="center",
            fontsize=8.5,
            color=MUTED,
        )
    ax.set_yticks(y)
    ax.set_yticklabels(list(LABEL.values()), fontsize=9.5)
    ax.set_xlim(0.48, 0.83)
    ax.set_ylim(-0.85, len(d) - 0.35)
    ax.set_xlabel("how often a Scheduled Caste candidate's cue outranks another's")
    ax.set_title(
        "In Kerala the informative part of a name is not the surname\n"
        f"{100 * shape['last_token_is_a_single_letter']:.0f}% of last tokens are "
        "a single letter, so the cue every surname method\nreads is mostly an "
        "initial. The given name, which nobody looks at, carries more.",
        color=INK,
        loc="left",
        fontsize=11.5,
    )
    style_axes(ax)
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig(out, dpi=170)
    plt.close(fig)
