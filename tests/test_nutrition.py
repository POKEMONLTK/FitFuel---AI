"""Unit tests for FitFuel AI pure nutrition and biomechanical calculations."""

import unittest
from modules.nutrition.bmi import calculate_bmi, get_bmi_category, get_healthy_weight_range
from modules.nutrition.energy import calculate_bmr, calculate_tdee, adjust_calories_for_goal
from modules.nutrition.protein import calculate_protein_target
from modules.nutrition.targets import calculate_nutrition_targets


class TestNutritionCalculations(unittest.TestCase):
    """Test suite for deterministic metabolic formulas."""

    def test_bmi_calculation(self):
        # 175 cm, 70 kg -> 70 / (1.75^2) = 22.857... -> 22.9
        bmi = calculate_bmi(175.0, 70.0)
        self.assertEqual(bmi, 22.9)

        category, color, desc = get_bmi_category(bmi)
        self.assertEqual(category, "Normal weight")

    def test_bmi_invalid_input(self):
        with self.assertRaises(ValueError):
            calculate_bmi(-170, 70)
        with self.assertRaises(ValueError):
            calculate_bmi(170, 0)

    def test_bmr_calculation_male(self):
        # Men: 10 * 78 + 6.25 * 175 - 5 * 20 + 5 = 780 + 1093.75 - 100 + 5 = 1778.75 -> 1779
        bmr = calculate_bmr(weight_kg=78.0, height_cm=175.0, age=20, sex="male")
        self.assertEqual(bmr, 1779.0)

    def test_bmr_calculation_female(self):
        # Women: 10 * 60 + 6.25 * 165 - 5 * 25 - 161 = 600 + 1031.25 - 125 - 161 = 1345.25 -> 1345
        bmr = calculate_bmr(weight_kg=60.0, height_cm=165.0, age=25, sex="female")
        self.assertEqual(bmr, 1345.0)

    def test_tdee_calculation(self):
        bmr = 1779.0
        # moderately active multiplier = 1.55 -> 1779 * 1.55 = 2757.45 -> 2757
        tdee = calculate_tdee(bmr, activity_level="moderately_active")
        self.assertEqual(tdee, 2757.0)

    def test_protein_targets(self):
        # 78 kg muscle gain -> (1.8 to 2.2) -> 140.4g to 171.6g, optimal ~156g
        min_p, opt_p, max_p = calculate_protein_target(weight_kg=78.0, goal="muscle_gain")
        self.assertGreaterEqual(opt_p, min_p)
        self.assertLessEqual(opt_p, max_p)
        self.assertAlmostEqual(opt_p, 156.0, delta=1.0)

    def test_exercise_adaptation(self):
        profile = {
            "height_cm": 175.0,
            "weight_kg": 78.0,
            "age": 20,
            "sex": "male",
            "goal": "muscle_gain",
            "activity_level": "moderately_active",
        }
        # Without exercise session
        targets_base = calculate_nutrition_targets(profile)
        
        # With high volume 20s test (17 reps)
        ex_session = {
            "exercise": "pushup",
            "valid_repetitions": 16,
            "form_consistency_score": 0.85,
            "intensity_tier": "high",
        }
        targets_adapted = calculate_nutrition_targets(profile, ex_session)

        self.assertTrue(targets_adapted["exercise_bonus_applied"])
        self.assertGreater(targets_adapted["target_calories"], targets_base["target_calories"])

    def test_fuzzy_food_lookup(self):
        from modules.food.nutrition_lookup import NutritionLookup
        lookup = NutritionLookup()
        
        # Test alias resolution
        roti_item = lookup.find_food("chappati")
        self.assertIsNotNone(roti_item)
        self.assertEqual(roti_item["name"], "Roti (Whole Wheat Chapati)")

        dal_item = lookup.find_food("dhal")
        self.assertIsNotNone(dal_item)
        self.assertEqual(dal_item["name"], "Dal Tadka")

        egg_item = lookup.find_food("boiled eggs")
        self.assertIsNotNone(egg_item)
        self.assertEqual(egg_item["name"], "Boiled Egg")

        # Test nutrition scaling (85 kcal per standard serving of 2 chapatis)
        scaled = lookup.calculate_item_nutrition("chappati", portion_category="2 pieces")
        self.assertEqual(scaled["calories"], 85.0)
        self.assertGreater(scaled["carbs_g"], 15.0)


if __name__ == "__main__":
    unittest.main()
