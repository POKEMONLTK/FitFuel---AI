"""FitFuel AI Energy & Caloric Requirement Calculations.

Uses transparent, validated clinical equations (Mifflin-St Jeor) for Basal Metabolic
Rate (BMR) and Total Daily Energy Expenditure (TDEE).
"""

from __future__ import annotations

from typing import Dict, Optional

# Standard Physical Activity Level (PAL) Multipliers
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,  # Little to no exercise, desk work
    "lightly_active": 1.375,  # Light exercise 1-3 days/week
    "moderately_active": 1.55,  # Moderate exercise 3-5 days/week
    "very_active": 1.725,  # Hard exercise 6-7 days/week
    "extra_active": 1.9,  # Very hard training or physical job
}

# Caloric adjustment based on primary fitness goal
GOAL_CALORIE_DELTAS = {
    "weight_loss": -450,  # Sustainable caloric deficit
    "maintenance": 0,  # Caloric equilibrium
    "muscle_gain": 350,  # Mild hypercaloric surplus for lean hypertrophy
    "general_wellness": 0,  # Metabolic baseline
}


def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str = "male",
) -> float:
    """Calculate Basal Metabolic Rate using the Mifflin-St Jeor equation.

    Men: BMR = (10 * weight) + (6.25 * height) - (5 * age) + 5
    Women: BMR = (10 * weight) + (6.25 * height) - (5 * age) - 161

    Args:
        weight_kg: Weight in kilograms.
        height_cm: Height in centimeters.
        age: Age in years.
        sex: 'male' or 'female'.

    Returns:
        Rounded BMR in kcal/day.
    """
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    if str(sex).lower() == "female":
        bmr = base - 161.0
    else:
        # Default to male / standard baseline
        bmr = base + 5.0
    return round(bmr, 0)


def calculate_tdee(bmr: float, activity_level: str = "moderately_active") -> float:
    """Calculate Total Daily Energy Expenditure (TDEE).

    Args:
        bmr: Basal metabolic rate in kcal.
        activity_level: Activity category key.

    Returns:
        Estimated daily maintenance calories.
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 0)


def calculate_exercise_metabolic_bonus(exercise_session: Optional[Dict]) -> Dict[str, Any]:
    """Calculate explicit work-factor and EPOC (Excess Post-Exercise Oxygen Consumption) allowance.

    Biomechanical basis:
    - Push-ups / Squats / Sit-ups recruit skeletal muscle motor units and elevate post-exercise
      oxygen consumption (EPOC) proportional to volume and cadence.
    """
    if not exercise_session:
        return {
            "exercise_bonus_kcal": 0.0,
            "direct_work_kcal": 0.0,
            "epoc_kcal": 0.0,
            "description": "Baseline calculation without acute exercise stimulus.",
        }

    ex_type = str(exercise_session.get("exercise", "pushup")).lower()
    valid_reps = int(exercise_session.get("valid_repetitions", 0))
    intensity = str(exercise_session.get("intensity_tier", "moderate")).lower()
    form_consistency = float(exercise_session.get("form_consistency_score", 0.8))

    # Repetition work cost benchmark
    cost_per_rep = {"squat": 0.65, "pushup": 0.45, "situp": 0.35}.get(ex_type, 0.45)
    direct_kcal = round(valid_reps * cost_per_rep * form_consistency, 1)

    # EPOC elevation buffer for post-workout recovery
    if intensity == "high" or valid_reps >= 15:
        epoc_kcal = 85.0
    elif intensity == "moderate" or valid_reps >= 8:
        epoc_kcal = 45.0
    elif valid_reps > 0:
        epoc_kcal = 20.0
    else:
        epoc_kcal = 0.0

    total_bonus = round(direct_kcal + epoc_kcal, 0)
    desc = (
        f"{valid_reps} valid {ex_type}s performed ({intensity} tier). "
        f"Direct exertion: ~{direct_kcal:.1f} kcal, EPOC replenishment: +{epoc_kcal:.0f} kcal."
    )

    return {
        "exercise_bonus_kcal": total_bonus,
        "direct_work_kcal": direct_kcal,
        "epoc_kcal": epoc_kcal,
        "description": desc,
    }


def adjust_calories_for_goal(
    tdee: float,
    goal: str = "maintenance",
    exercise_session: Optional[Dict] = None,
) -> float:
    """Adjust daily calories for fitness goal and recent exercise intensity.

    Args:
        tdee: Total Daily Energy Expenditure.
        goal: User's primary fitness goal.
        exercise_session: Optional structured metrics from recent exercise test.

    Returns:
        Adjusted target calories (enforcing a minimum healthy floor of 1200 kcal).
    """
    delta = GOAL_CALORIE_DELTAS.get(goal, 0)
    target = tdee + delta

    # Adaptive EPOC & work-factor replenishment bonus
    bonus_data = calculate_exercise_metabolic_bonus(exercise_session)
    target += bonus_data["exercise_bonus_kcal"]

    # Ensure safe physiological minimum
    return max(round(target, 0), 1200.0)
