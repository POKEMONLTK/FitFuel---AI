"""Unit tests for FitFuel AI K-Nearest Neighbors (KNN) Nutrient-Space Meal Swap Clustering (PID 09)."""

import unittest
from modules.food.nutrition_lookup import NutritionLookup
from modules.recommendation.knn_swaps import KNNSwapEngine, SKLEARN_AVAILABLE


class TestKNNSwapEngine(unittest.TestCase):
    """Test suite for 6D nutrient space vectorization, cosine indexing, and multi-objective swaps."""

    @classmethod
    def setUpClass(cls):
        cls.lookup = NutritionLookup()
        cls.engine = KNNSwapEngine(lookup=cls.lookup)

    def test_engine_initialization(self):
        """Verify KNN engine builds 6D index across catalog items."""
        self.assertTrue(len(self.engine.catalog_items) > 10)
        if SKLEARN_AVAILABLE:
            self.assertIsNotNone(self.engine.knn_model)
            self.assertIsNotNone(self.engine.vectors)
            # Ensure vectors have 6 dimensions: [cals, prot, carbs, fat, fiber, gi]
            self.assertEqual(self.engine.vectors.shape[1], 6)

    def test_glycemic_index_estimation(self):
        """Verify taxonomic GI assignment and fiber-protein blunting heuristics."""
        high_gi_item = {"name": "White Rice (Cooked)", "carbs_g": 28.0, "fiber_g": 0.4, "protein_g": 2.7, "fat_g": 0.3}
        low_gi_item = {"name": "Dal Tadka", "carbs_g": 18.0, "fiber_g": 4.5, "protein_g": 7.0, "fat_g": 3.0}
        pure_protein_item = {"name": "Boiled Egg White", "carbs_g": 0.2, "fiber_g": 0.0, "protein_g": 11.0, "fat_g": 0.2}

        gi_high = self.engine._estimate_glycemic_index(high_gi_item)
        gi_low = self.engine._estimate_glycemic_index(low_gi_item)
        gi_protein = self.engine._estimate_glycemic_index(pure_protein_item)

        self.assertGreaterEqual(gi_high, 65.0)
        self.assertLessEqual(gi_low, 55.0)
        self.assertLessEqual(gi_protein, 30.0)

    def test_find_substitutes_muscle_gain(self):
        """Verify muscle gain swaps prioritize protein enhancement and return structured deltas."""
        swaps = self.engine.find_substitutes(
            source_item_name="White Rice (Cooked)",
            goal="muscle_gain",
            user_profile={"diet_type": "vegetarian", "allergens": "none"},
            top_k=3,
        )
        self.assertTrue(len(swaps) >= 1)
        for swap in swaps:
            self.assertEqual(swap["from_item"], "White Rice (Cooked)")
            self.assertIn("to_item", swap)
            self.assertIn("delta_nutrients", swap)
            self.assertTrue(swap.get("knn_optimized"))
            self.assertGreaterEqual(swap.get("knn_similarity", 0.0), 0.0)
            self.assertLessEqual(swap.get("knn_similarity", 0.0), 1.0)
            # Delta calories within allowable bounds (+/- 190 kcal)
            cal_delta = swap["delta_nutrients"]["calories"]
            self.assertLessEqual(abs(cal_delta), 190.0)

    def test_find_substitutes_diet_constraints(self):
        """Verify strict dietary boundaries: vegan users never receive dairy or poultry."""
        vegan_profile = {"diet_type": "vegan", "allergens": "none", "disliked_foods": ""}
        swaps = self.engine.find_substitutes(
            source_item_name="Chapati / Roti (Whole Wheat)",
            goal="muscle_gain",
            user_profile=vegan_profile,
            top_k=5,
        )
        for swap in swaps:
            target_food = self.lookup.find_food(swap["to_item"])
            if target_food:
                self.assertIn(
                    target_food.get("diet_type", "").lower(),
                    ["vegan"],
                    f"Candidate {swap['to_item']} has diet {target_food.get('diet_type')} which violates vegan rule",
                )

    def test_find_substitutes_allergen_exclusion(self):
        """Verify allergen safety: dairy-allergic users never receive dairy-containing swaps."""
        dairy_allergic_profile = {"diet_type": "vegetarian", "allergens": "dairy", "disliked_foods": ""}
        swaps = self.engine.find_substitutes(
            source_item_name="White Rice (Cooked)",
            goal="muscle_gain",
            user_profile=dairy_allergic_profile,
            top_k=5,
        )
        for swap in swaps:
            target_food = self.lookup.find_food(swap["to_item"])
            if target_food:
                allergens = str(target_food.get("allergens", "")).lower()
                self.assertNotIn("dairy", allergens)

    def test_find_substitutes_weight_loss(self):
        """Verify weight loss goal penalizes high calories and rewards fiber / lower glycemic impact."""
        swaps = self.engine.find_substitutes(
            source_item_name="White Rice (Cooked)",
            goal="weight_loss",
            user_profile={"diet_type": "vegetarian", "allergens": "none"},
            top_k=2,
        )
        self.assertTrue(len(swaps) >= 1)
        for swap in swaps:
            self.assertIn("glycemic_impact", swap)
            self.assertIn("delta_nutrients", swap)


if __name__ == "__main__":
    unittest.main()
