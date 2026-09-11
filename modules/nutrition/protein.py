"""FitFuel AI Protein Target Calculations.

Estimates evidence-based protein ranges based on body mass, goals,
and exercise performance.
Does NOT claim to measure protein absorption from exercise.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

# Dietary protein benchmarks (grams per kg body weight)
PROTEIN_GOAL_RANGES = {
    "weight_loss": (1.6, 2.0),       # Preserves lean mass in deficit
    "maintenance": (1.2, 1.6),       # General tissue maintenance
    "muscle_gain": (1.8, 2.2),       # Stimulates myofibrillar protein synthesis
    "general_wellness": (1.0, 1.4),  # Standard health RDA guideline
}


def calculate_protein_target(
    weight_kg: float,
    goal: str = "maintenance",
    exercise_session: Optional[Dict] = None,
) -> Tuple[float, float, float]:
    """Calculate recommended protein intake range (g/day).

    Args:
        weight_kg: Body weight in kilograms.
        goal: Primary goal key.
        exercise_session: Optional recent exercise metrics dict.

    Returns:
        Tuple of (min_protein_g, optimal_protein_g, max_protein_g).
    """
    min_rate, max_rate = PROTEIN_GOAL_RANGES.get(goal, (1.2, 1.6))

    # Adaptive nudge based on observed exercise volume
    if exercise_session:
        valid_reps = exercise_session.get("valid_repetitions", 0)
        form_score = exercise_session.get("form_consistency_score", 0.8)

        # Higher muscular demand warrants the higher end of the range
        if valid_reps >= 15 and form_score >= 0.75:
            min_rate = min(min_rate + 0.1, max_rate)
        elif valid_reps < 8:
            pass

    optimal_rate = round((min_rate + max_rate) / 2.0, 2)

    min_protein = round(weight_kg * min_rate, 1)
    optimal_protein = round(weight_kg * optimal_rate, 1)
    max_protein = round(weight_kg * max_rate, 1)

    return (min_protein, optimal_protein, max_protein)
