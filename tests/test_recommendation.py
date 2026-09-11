"""Unit tests for FitFuel AI recommendation constraints, filters, and rankings."""

import unittest
from modules.recommendation.personalization import (
    is_diet_compatible,
    has_allergen_conflict,
    has_disliked_ingredients,
    filter_safe_recipes,
)
from modules.recommendation.ranking import rank_recipes


class TestRecommendationEngine(unittest.TestCase):
    """Test suite for recommendation constraints and scoring."""

    def test_diet_compatibility(self):
        self.assertTrue(is_diet_compatible("vegetarian", "vegan"))
        self.assertTrue(is_diet_compatible("vegetarian", "vegetarian"))
        self.assertFalse(is_diet_compatible("vegetarian", "non-vegetarian"))
        self.assertFalse(is_diet_compatible("vegan", "vegetarian"))
        self.assertTrue(is_diet_compatible("non-vegetarian", "vegan"))

    def test_allergen_filtering(self):
        self.assertTrue(has_allergen_conflict("dairy, gluten", "dairy"))
        self.assertTrue(has_allergen_conflict("peanuts", "tree nuts|peanuts"))
        self.assertFalse(has_allergen_conflict("none", "dairy"))
        self.assertFalse(has_allergen_conflict("gluten", "dairy"))

    def test_disliked_food_filtering(self):
        recipe = {
            "title": "Mushroom Stir Fry",
            "description": "Button mushrooms in garlic sauce",
            "items_json": '["mushrooms", "rice"]',
        }
        self.assertTrue(has_disliked_ingredients(recipe, "mushroom"))
        self.assertFalse(has_disliked_ingredients(recipe, "eggplant"))

    def test_safe_recipes_filtering(self):
        recipes = [
            {"id": "1", "title": "Chicken Curry", "diet_type": "non-vegetarian", "allergens": "none"},
            {"id": "2", "title": "Paneer Tikka", "diet_type": "vegetarian", "allergens": "dairy"},
            {"id": "3", "title": "Dal Tadka", "diet_type": "vegan", "allergens": "none"},
        ]
        # User is vegetarian, allergic to dairy
        profile = {
            "diet_type": "vegetarian",
            "allergens": "dairy",
            "disliked_foods": "",
        }
        safe = filter_safe_recipes(recipes, profile)
        self.assertEqual(len(safe), 1)
        self.assertEqual(safe[0]["title"], "Dal Tadka")

    def test_vector_cosine_similarity(self):
        from modules.recommendation.ranking import calculate_vector_cosine_similarity
        # Exact matching proportions
        vec_a = (500.0, 30.0, 50.0, 15.0)
        vec_b = (500.0, 30.0, 50.0, 15.0)
        sim = calculate_vector_cosine_similarity(vec_a, vec_b)
        self.assertAlmostEqual(sim, 1.0, places=2)

        # Proportional vector (scaled by 2)
        vec_c = (1000.0, 60.0, 100.0, 30.0)
        sim_prop = calculate_vector_cosine_similarity(vec_a, vec_c)
        self.assertAlmostEqual(sim_prop, 1.0, places=2)

    def test_suggest_meal_swaps_structured(self):
        from modules.recommendation.recommender import RecommendationEngine
        engine = RecommendationEngine()
        meal_items = [
            {"name": "White Rice (Cooked)", "portion_category": "medium"},
            {"name": "Dal Tadka", "portion_category": "medium"},
        ]
        swaps = engine.suggest_meal_swaps(meal_items, goal="muscle_gain")
        self.assertTrue(len(swaps["suggestions"]) >= 1)
        first_swap = swaps["suggestions"][0]
        self.assertIn("delta_nutrients", first_swap)
        self.assertIn("glycemic_impact", first_swap)
        self.assertIn("fiber_g", first_swap["delta_nutrients"])


if __name__ == "__main__":
    unittest.main()
