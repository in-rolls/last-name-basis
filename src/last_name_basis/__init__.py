"""Shared vocabulary for the analyses in this repo.

Each analysis in ``analyses/`` owns its own pipeline, data loading, figures and
note. What lives here is only what more than one of them needs: the scoring
measure and the drawing style.
"""

from .scoring import (
    entropy_bits,
    leave_one_out_ladder,
    score_ladder,
    weighted_summary,
)
from .style import (
    ACCENT,
    CATEGORY_FILL,
    INK,
    MUTED,
    allocate,
    band_of,
    mistake_bands,
    style_axes,
    waffle,
)

__all__ = [
    "entropy_bits",
    "weighted_summary",
    "score_ladder",
    "leave_one_out_ladder",
    "INK",
    "ACCENT",
    "MUTED",
    "CATEGORY_FILL",
    "style_axes",
    "allocate",
    "waffle",
    "mistake_bands",
    "band_of",
]
