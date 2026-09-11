"""FitFuel AI BMI Calculator.

Calculates Body Mass Index (BMI) deterministically from measured height and weight.
Complies with scientific boundaries: no claims of photo-based BMI diagnosis.
"""

from __future__ import annotations

from typing import Tuple


def calculate_bmi(height_cm: float, weight_kg: float) -> float:
    """Calculate Body Mass Index (BMI).

    Formula: weight (kg) / (height (m) ** 2)

    Args:
        height_cm: Stature in centimeters.
        weight_kg: Body weight in kilograms.

    Returns:
        Rounded BMI value (1 decimal place).

    Raises:
        ValueError: If height or weight are non-positive.
    """
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("Height and weight must be positive numbers.")

    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m * height_m)
    return round(bmi, 1)


def get_bmi_category(bmi: float) -> Tuple[str, str, str]:
    """Return standard WHO classification and user-friendly explanation.

    Args:
        bmi: Calculated BMI value.

    Returns:
        Tuple of (category_label, badge_color_hex, descriptive_summary).
    """
    if bmi < 18.5:
        return (
            "Underweight",
            "#3B82F6",  # blue
            "Below the typical adult weight range. Focus on nutrient-dense calorie surplus.",
        )
    elif bmi < 25.0:
        return (
            "Normal weight",
            "#10B981",  # green
            "Within the healthy standard range. Focus on fitness maintenance and body composition.",
        )
    elif bmi < 30.0:
        return (
            "Overweight",
            "#F59E0B",  # amber
            "Slightly above standard range. Moderate calorie deficit with strength training recommended.",
        )
    else:
        return (
            "Obesity range",
            "#EF4444",  # red
            "Above standard health benchmark. Gradual sustainable deficit and active lifestyle encouraged.",
        )


def get_healthy_weight_range(height_cm: float) -> Tuple[float, float]:
    """Calculate healthy weight range corresponding to BMI 18.5 to 24.9.

    Args:
        height_cm: Stature in centimeters.

    Returns:
        Tuple of (min_weight_kg, max_weight_kg).
    """
    height_m = height_cm / 100.0
    min_w = 18.5 * (height_m**2)
    max_w = 24.9 * (height_m**2)
    return (round(min_w, 1), round(max_w, 1))
