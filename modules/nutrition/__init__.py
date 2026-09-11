"""FitFuel AI Nutrition Engine Package."""
from .bmi import calculate_bmi, get_bmi_category, get_healthy_weight_range
from .energy import calculate_bmr, calculate_tdee, adjust_calories_for_goal
from .protein import calculate_protein_target
from .targets import calculate_nutrition_targets

__all__ = [
    "calculate_bmi",
    "get_bmi_category",
    "get_healthy_weight_range",
    "calculate_bmr",
    "calculate_tdee",
    "adjust_calories_for_goal",
    "calculate_protein_target",
    "calculate_nutrition_targets",
]
