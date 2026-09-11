"""FitFuel AI Comprehensive Nutrition Targets.

Synthesizes anthropometric data, energy expenditure formulas, protein benchmarks,
and exercise performance into a complete macronutrient profile with full mathematical transparency.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .bmi import calculate_bmi, get_bmi_category, get_healthy_weight_range
from .energy import adjust_calories_for_goal, calculate_bmr, calculate_tdee, calculate_exercise_metabolic_bonus
from .ml_energy_model import MLEnergyModel
from .protein import calculate_protein_target

_ML_ENERGY_MODEL: Optional[MLEnergyModel] = None


def get_ml_energy_model() -> MLEnergyModel:
    """Singleton getter for trained ML Energy Model."""
    global _ML_ENERGY_MODEL
    if _ML_ENERGY_MODEL is None:
        _ML_ENERGY_MODEL = MLEnergyModel()
    return _ML_ENERGY_MODEL


def calculate_nutrition_targets(
    profile: Dict[str, Any],
    exercise_session: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Calculate daily caloric and macronutrient targets with complete step-by-step transparency.

    Args:
        profile: Dictionary containing age, sex, height_cm, weight_kg, goal, activity_level.
        exercise_session: Optional structured metrics from the exercise test.

    Returns:
        Dictionary containing target values, ranges, and explanatory narrative.
    """
    height_cm = float(profile.get("height_cm", 175.0))
    weight_kg = float(profile.get("weight_kg", 70.0))
    age = int(profile.get("age", 25))
    sex = str(profile.get("sex", "male"))
    goal = str(profile.get("goal", "muscle_gain"))
    activity_level = str(profile.get("activity_level", "moderately_active"))

    # 1. Anthropometrics & BMI
    bmi = calculate_bmi(height_cm, weight_kg)
    bmi_category, bmi_badge_color, bmi_desc = get_bmi_category(bmi)
    min_w, max_w = get_healthy_weight_range(height_cm)

    # 2. BMR & TDEE (Mifflin-St Jeor Clinical Baseline)
    bmr = calculate_bmr(weight_kg, height_cm, age, sex)
    tdee = calculate_tdee(bmr, activity_level)

    # 3. Deterministic Baseline Calculation
    target_calories_deterministic = adjust_calories_for_goal(tdee, goal, exercise_session)
    min_prot, opt_prot, max_prot = calculate_protein_target(weight_kg, goal, exercise_session)

    # 4. ML Predictive Adaptation (IEEE PID 09)
    ml_model = get_ml_energy_model()
    ml_preds = ml_model.predict_adaptive_targets(profile, exercise_session)
    ml_adapted = ml_preds.get("ml_adapted", False)
    xai_attrib = ml_preds.get("xai_attribution", {})

    if exercise_session and ml_adapted:
        target_calories = max(target_calories_deterministic, ml_preds["target_calories"])
        opt_prot = max(opt_prot, ml_preds["target_protein_g"])
    else:
        target_calories = target_calories_deterministic

    protein_calories = opt_prot * 4.0

    # 5. Healthy Fats (22-25% of total caloric intake, 9 kcal/g)
    fat_pct = 0.22 if exercise_session and exercise_session.get("intensity_tier") == "high" else 0.25
    fat_calories = target_calories * fat_pct
    target_fat_g = round(fat_calories / 9.0, 1)

    # 6. Carbohydrates (Dynamic cycling: remainder goes to glycogen resynthesis, 4 kcal/g)
    remaining_calories = max(0.0, target_calories - protein_calories - fat_calories)
    target_carbs_g = round(remaining_calories / 4.0, 1)

    # 7. Dietary Fiber (14g per 1000 kcal benchmark)
    target_fiber_g = round((target_calories / 1000.0) * 14.0, 1)

    # 8. Hydration Benchmark (35ml per kg body weight)
    water_liters = round((weight_kg * 0.035), 1)

    # 9. Exercise-adaptive insight
    exercise_bonus_applied = False
    exercise_bonus_data = calculate_exercise_metabolic_bonus(exercise_session)
    exercise_note = exercise_bonus_data["description"]
    if exercise_session and exercise_bonus_data["exercise_bonus_kcal"] > 0:
        exercise_bonus_applied = True

    ml_summary_note = ""
    if exercise_session and ml_adapted:
        ml_summary_note = (
            f"🤖 ML Regressor (PID 09): Energy target {target_calories:.0f} kcal "
            f"(Baseline: {xai_attrib.get('metabolic_baseline_pct', 70)}%, "
            f"Kinematics: {xai_attrib.get('kinematic_movement_pct', 20)}%, "
            f"Goal: {xai_attrib.get('goal_calibration_pct', 10)}%)."
        )

    explanation = {
        "bmr_formula": f"Mifflin-St Jeor ({sex}): {bmr:.0f} kcal/day",
        "tdee_formula": f"TDEE ({activity_level}): {tdee:.0f} kcal/day",
        "goal_adjustment": f"Goal '{goal}': target adjusted to {target_calories:.0f} kcal/day",
        "exercise_adaptation": f"{exercise_note} {ml_summary_note}".strip(),
        "protein_ratio": f"{opt_prot:.1f}g ({round(opt_prot/weight_kg, 2)} g/kg)",
        "fat_ratio": f"{target_fat_g:.1f}g (~{int(fat_pct*100)}% total calories)",
        "carbs_ratio": f"{target_carbs_g:.1f}g (dynamic glycogen replenishment)",
        "ml_adapted": ml_adapted,
        "xai_attribution": xai_attrib,
        "disclaimer": "Wellness prototype estimate — not a clinical medical prescription.",
    }

    return {
        "bmi": bmi,
        "bmi_category": bmi_category,
        "bmi_badge_color": bmi_badge_color,
        "bmi_description": bmi_desc,
        "healthy_weight_range": (min_w, max_w),
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_calories,
        "target_protein_g": opt_prot,
        "protein_range": (min_prot, max_prot),
        "target_carbs_g": target_carbs_g,
        "target_fat_g": target_fat_g,
        "target_fiber_g": target_fiber_g,
        "target_water_liters": water_liters,
        "exercise_bonus_applied": exercise_bonus_applied,
        "ml_adapted": ml_adapted,
        "xai_attribution": xai_attrib,
        "explanation": explanation,
    }
