"""FitFuel AI Personalization & Hard Constraint Filter.

Enforces non-negotiable dietary boundaries (allergies, ethical diets, dislikes)
before any scoring or ranking takes place.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

# Diet hierarchy mapping allowed recipe diets for a user's selected lifestyle
DIET_HIERARCHY = {
    "vegan": ["vegan"],
    "vegetarian": ["vegan", "vegetarian"],
    "eggitarian": ["vegan", "vegetarian", "eggitarian"],
    "non-vegetarian": ["vegan", "vegetarian", "eggitarian", "non-vegetarian"],
}


def is_diet_compatible(user_diet: str, recipe_diet: str) -> bool:
    """Check if recipe diet is compatible with user diet choice."""
    u_diet = str(user_diet).lower().strip()
    r_diet = str(recipe_diet).lower().strip()
    allowed = DIET_HIERARCHY.get(u_diet, [u_diet])
    return r_diet in allowed


def has_allergen_conflict(user_allergens_str: str, recipe_allergens_str: str) -> bool:
    """Check if recipe contains any allergen declared by user.

    Args:
        user_allergens_str: Comma/pipe separated string (e.g., 'dairy, gluten').
        recipe_allergens_str: Recipe allergens string (e.g., 'dairy|gluten').

    Returns:
        True if an allergen conflict exists.
    """
    if not user_allergens_str or user_allergens_str.lower() in ("none", ""):
        return False
    if not recipe_allergens_str or recipe_allergens_str.lower() in ("none", ""):
        return False

    # Normalize user allergens
    delimiters = [",", "|", ";"]
    user_tokens = user_allergens_str.lower()
    for d in delimiters:
        user_tokens = user_tokens.replace(d, " ")
    user_set = {t.strip() for t in user_tokens.split() if t.strip()}

    # Normalize recipe allergens
    recipe_tokens = recipe_allergens_str.lower()
    for d in delimiters:
        recipe_tokens = recipe_tokens.replace(d, " ")
    recipe_set = {t.strip() for t in recipe_tokens.split() if t.strip()}

    return bool(user_set.intersection(recipe_set))


def has_disliked_ingredients(recipe: Dict[str, Any], disliked_str: str) -> bool:
    """Check if recipe contains user-disliked keywords in title, description, or ingredients."""
    if not disliked_str or disliked_str.lower().strip() in ("none", ""):
        return False

    disliked_tokens = [d.strip().lower() for d in disliked_str.split(",") if d.strip()]
    recipe_text = f"{recipe.get('title', '')} {recipe.get('description', '')} {recipe.get('items_json', '')}".lower()

    for token in disliked_tokens:
        if token in recipe_text:
            return True
    return False


def filter_safe_recipes(
    recipes: List[Dict[str, Any]],
    user_profile: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Filter out all recipes that violate hard dietary constraints.

    Args:
        recipes: Full candidate recipe list.
        user_profile: Profile dictionary with diet_type, allergens, disliked_foods.

    Returns:
        Filtered list of safe recipes.
    """
    user_diet = user_profile.get("diet_type", "vegetarian")
    user_allergens = user_profile.get("allergens", "none")
    user_dislikes = user_profile.get("disliked_foods", "")

    safe_recipes = []
    for r in recipes:
        # 1. Diet compliance
        if not is_diet_compatible(user_diet, r.get("diet_type", "vegetarian")):
            continue

        # 2. Allergen safety
        if has_allergen_conflict(user_allergens, str(r.get("allergens", "none"))):
            continue

        # 3. Disliked foods
        if has_disliked_ingredients(r, user_dislikes):
            continue

        safe_recipes.append(r)

    return safe_recipes
