"""FitFuel AI Portion Estimator.

Translates human-friendly portion categories and counts into mathematical
scaling multipliers for accurate macronutrient calculation.
"""

from __future__ import annotations

from typing import Dict, List

# Standard portion category multipliers relative to default serving size (1.0)
PORTION_MULTIPLIERS: Dict[str, float] = {
    "small": 0.70,          # ~70% of standard serving
    "medium": 1.0,          # 100% standard baseline serving
    "large": 1.45,         # ~145% of standard serving
    "extra_large": 2.0,    # Double serving
    "half_portion": 0.50,
    "1 piece": 0.50,
    "2 pieces": 1.0,
    "3 pieces": 1.50,
    "4 pieces": 2.0,
}


class PortionEstimator:
    """Provides portion scaling multipliers and user options."""

    @staticmethod
    def get_portion_options() -> List[str]:
        """Return list of selectable portion categories."""
        return [
            "small",
            "medium",
            "large",
            "extra_large",
            "half_portion",
            "1 piece",
            "2 pieces",
            "3 pieces",
            "4 pieces",
        ]

    @staticmethod
    def get_multiplier(portion_category: str) -> float:
        """Resolve multiplier for category string."""
        return PORTION_MULTIPLIERS.get(portion_category.lower().strip(), 1.0)

    @staticmethod
    def format_portion_label(portion_category: str, multiplier: float) -> str:
        """Render readable label with percentage scaling."""
        pct = int(multiplier * 100)
        return f"{portion_category.capitalize()} ({pct}% standard)"
