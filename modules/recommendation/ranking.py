"""FitFuel AI Recommendation Ranking Engine.

Scores safe candidate recipes using multi-objective nutritional alignment,
goal compatibility, cuisine preference, and historical feedback.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple


def calculate_vector_cosine_similarity(
    recipe_vec: Tuple[float, float, float, float],
    target_vec: Tuple[float, float, float, float],
) -> float:
    """Compute cosine similarity between normalized macronutrient vectors.

    Vectors represent: (calories, protein_g, carbs_g, fat_g).
    Components are scaled by reference units (500 kcal, 30g protein, 50g carbs, 15g fat)
    to balance geometric weight across units.
    """
    scales = [500.0, 30.0, 50.0, 15.0]
    r_scaled = [v / s for v, s in zip(recipe_vec, scales)]
    t_scaled = [v / s for v, s in zip(target_vec, scales)]

    dot = sum(a * b for a, b in zip(r_scaled, t_scaled))
    norm_r = math.sqrt(sum(a * a for a in r_scaled))
    norm_t = math.sqrt(sum(b * b for b in t_scaled))

    if norm_r == 0 or norm_t == 0:
        return 0.5

    sim = dot / (norm_r * norm_t)
    return round(max(0.0, min(1.0, sim)), 3)


def calculate_nutrition_match(
    recipe_cals: float,
    recipe_prot: float,
    remaining_cals: float,
    remaining_prot: float,
    recipe_carbs: float = 40.0,
    recipe_fat: float = 12.0,
    remaining_carbs: float = 120.0,
    remaining_fat: float = 40.0,
) -> float:
    """Evaluate how effectively a recipe fits remaining caloric and macronutrient budget.

    Synthesizes:
    1. Normalized 4D vector cosine similarity against remaining daily macro budget.
    2. Single-meal calorie envelope fit (preventing acute caloric spikes).
    3. Protein gap reduction.

    Returns:
        Score between 0.0 and 1.0.
    """
    # 1. Cosine vector similarity
    target_vec = (
        max(200.0, remaining_cals),
        max(10.0, remaining_prot),
        max(20.0, remaining_carbs),
        max(10.0, remaining_fat),
    )
    recipe_vec = (
        recipe_cals,
        recipe_prot,
        recipe_carbs,
        recipe_fat,
    )
    cos_sim = calculate_vector_cosine_similarity(recipe_vec, target_vec)

    # 2. Caloric envelope fit (ideal meal: ~35-45% of remaining budget)
    ideal_meal_cals = max(350.0, min(800.0, remaining_cals * 0.45))
    cal_diff = abs(recipe_cals - ideal_meal_cals)
    cal_score = max(0.0, 1.0 - (cal_diff / 500.0))

    # 3. Protein gap closure
    if remaining_prot > 0:
        prot_ratio = min(1.0, recipe_prot / max(15.0, remaining_prot * 0.45))
        prot_score = prot_ratio
    else:
        prot_score = 0.8  # Target already met

    # Composite nutrition score
    score = (0.45 * cos_sim) + (0.30 * cal_score) + (0.25 * prot_score)
    return round(score, 2)


def calculate_goal_match(recipe: Dict[str, Any], goal: str) -> float:
    """Score recipe alignment with fitness goal."""
    r_goal = str(recipe.get("goal_suitability", "")).lower()
    g = str(goal).lower()

    if r_goal == g:
        return 1.0

    # Hypertrophy / muscle gain prioritizes high protein (>25g)
    prot = float(recipe.get("protein_g", 0))
    cals = float(recipe.get("calories", 1))

    if g == "muscle_gain":
        return 1.0 if prot >= 28.0 else (0.8 if prot >= 20.0 else 0.5)
    elif g == "weight_loss":
        # Protein-to-calorie density
        density = prot / (cals / 100.0)  # g protein per 100 kcal
        return 1.0 if density >= 6.0 else (0.8 if density >= 4.5 else 0.5)
    elif g in ("maintenance", "general_wellness"):
        return 0.9  # Broadly suitable

    return 0.7


def calculate_cuisine_match(recipe_cuisine: str, preferred_cuisine: str) -> float:
    """Score cuisine preference alignment."""
    rc = str(recipe_cuisine).lower().strip()
    pc = str(preferred_cuisine).lower().strip()
    if not pc or pc == "all" or rc == "global" or pc == "global":
        return 0.9
    return 1.0 if rc == pc else 0.5


def calculate_feedback_score(recipe_id: str, recipe_title: str, feedback_history: List[Dict[str, Any]]) -> float:
    """Calculate preference score based on user's past ratings.

    Returns:
        Score between 0.0 and 1.0 (default 0.7 if unrated).
    """
    if not feedback_history:
        return 0.7  # Neutral prior

    matching_ratings = []
    for f in feedback_history:
        if (recipe_id and f.get("recipe_id") == recipe_id) or (
            recipe_title and f.get("recipe_title", "").lower() == recipe_title.lower()
        ):
            matching_ratings.append(f.get("taste_rating", 3))

    if matching_ratings:
        avg_rating = sum(matching_ratings) / len(matching_ratings)
        # Scale 1-5 to 0.2 - 1.0
        return round(avg_rating / 5.0, 2)

    return 0.7


def rank_recipes(
    safe_recipes: List[Dict[str, Any]],
    user_profile: Dict[str, Any],
    nutrition_targets: Dict[str, Any],
    consumed_today: Dict[str, float],
    feedback_history: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Rank safe recipes using weighted multi-criteria scoring function.

    Formula:
    Score = 0.30 * nutrition_match + 0.20 * goal_match + 0.15 * pref_match
            + 0.15 * allergy_safety + 0.10 * cuisine_match + 0.10 * feedback_score

    Returns:
        List of scored and ranked recipe dictionaries.
    """
    target_cals = float(nutrition_targets.get("target_calories", 2200))
    target_prot = float(nutrition_targets.get("target_protein_g", 130))
    target_carbs = float(nutrition_targets.get("target_carbs_g", 250))
    target_fat = float(nutrition_targets.get("target_fat_g", 60))

    consumed_cals = consumed_today.get("calories", 0.0)
    consumed_prot = consumed_today.get("protein_g", 0.0)
    consumed_carbs = consumed_today.get("carbs_g", 0.0)
    consumed_fat = consumed_today.get("fat_g", 0.0)

    remaining_cals = max(200.0, target_cals - consumed_cals)
    remaining_prot = max(0.0, target_prot - consumed_prot)
    remaining_carbs = max(0.0, target_carbs - consumed_carbs)
    remaining_fat = max(0.0, target_fat - consumed_fat)

    user_goal = user_profile.get("goal", "muscle_gain")
    user_cuisine = user_profile.get("preferred_cuisine", "indian")

    ranked = []
    for r in safe_recipes:
        recipe_cals = float(r.get("calories", 400))
        recipe_prot = float(r.get("protein_g", 20))
        recipe_carbs = float(r.get("carbs_g", 45))
        recipe_fat = float(r.get("fat_g", 12))

        # 1. Nutrition match (30%) - 4D vector cosine similarity + budget fit
        nutr_score = calculate_nutrition_match(
            recipe_cals=recipe_cals,
            recipe_prot=recipe_prot,
            remaining_cals=remaining_cals,
            remaining_prot=remaining_prot,
            recipe_carbs=recipe_carbs,
            recipe_fat=recipe_fat,
            remaining_carbs=remaining_carbs,
            remaining_fat=remaining_fat,
        )

        # 2. Goal match (20%)
        goal_score = calculate_goal_match(r, user_goal)

        # 3. Preference match (15%) - Diet match is guaranteed by filter
        pref_score = 1.0

        # 4. Allergy safety (15%) - Guaranteed 1.0 by hard filter
        allergy_score = 1.0

        # 5. Cuisine match (10%)
        cuisine_score = calculate_cuisine_match(r.get("cuisine", "global"), user_cuisine)

        # 6. Historical feedback (10%)
        fb_score = calculate_feedback_score(r.get("id", ""), r.get("title", ""), feedback_history)

        total_score = (
            (0.30 * nutr_score)
            + (0.20 * goal_score)
            + (0.15 * pref_score)
            + (0.15 * allergy_score)
            + (0.10 * cuisine_score)
            + (0.10 * fb_score)
        )

        r_scored = r.copy()
        r_scored["recommendation_score"] = round(total_score, 3)
        r_scored["score_breakdown"] = {
            "nutrition_match": nutr_score,
            "goal_match": goal_score,
            "preference_match": pref_score,
            "allergy_safety": allergy_score,
            "cuisine_match": cuisine_score,
            "feedback_score": fb_score,
        }
        r_scored["remaining_protein_gap_g"] = round(remaining_prot, 1)
        r_scored["remaining_calories_budget"] = round(remaining_cals, 0)
        ranked.append(r_scored)

    # Sort descending by composite recommendation score
    ranked.sort(key=lambda x: x["recommendation_score"], reverse=True)
    return ranked
