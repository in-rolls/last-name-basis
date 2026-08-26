"""How much does an Indian last name tell you about caste?"""

from .data import base_rates, load_cells, per_name
from .metrics import add_metrics, by_frequency_band, headline, uninformative_cdf

__all__ = [
    "load_cells",
    "per_name",
    "base_rates",
    "add_metrics",
    "headline",
    "by_frequency_band",
    "uninformative_cdf",
]
