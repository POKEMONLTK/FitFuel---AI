"""Unit tests for FitFuel AI Predictive ML Energy & Kinematic Adaptation Regressor (IEEE PID 09)."""

import unittest
from modules.nutrition.ml_energy_model import MLEnergyModel
from modules.nutrition.targets import calculate_nutrition_targets


class TestMLEnergyModel(unittest.TestCase):
    """Test suite for Gradient Boosting and Random Forest metabolic regression models."""

    def setUp(self):
        self.model = MLEnergyModel()
        self.sample_profile = {
            "name": "Athlete",
            "age": 24,
            "sex": "male",
            "height_cm": 178.0,
            "weight_kg": 75.0,
            "goal": "muscle_gain",
            "activity_level": "moderately_active",
        }

    def test_feature_extraction_completeness(self):
        """Verify feature extraction produces all defined features."""
        feats = self.model.extract_features(
            profile=self.sample_profile,
            exercise_session={"valid_repetitions": 20, "intensity_tier": "vigorous"},
        )
        self.assertEqual(len(feats), len(MLEnergyModel.FEATURE_NAMES))
        for name in MLEnergyModel.FEATURE_NAMES:
            self.assertIn(name, feats)
            self.assertIsInstance(feats[name], (int, float))

    def test_prediction_bounds_and_safety_floors(self):
        """Verify predicted target calories and protein satisfy physiological safety floors."""
        result = self.model.predict_adaptive_targets(
            profile=self.sample_profile,
            exercise_session={"valid_repetitions": 15, "intensity_tier": "moderate"},
        )
        self.assertGreaterEqual(result["target_calories"], 1200.0)
        self.assertGreaterEqual(result["target_protein_g"], 75.0 * 1.2)
        self.assertLessEqual(result["protein_g_per_kg"], 2.5)

    def test_kinematic_sensitivity(self):
        """Verify higher exercise volume/cadence increases predicted caloric expenditure and protein demand."""
        low_workout = {"valid_repetitions": 5, "tempo_sec_per_rep": 2.5, "intensity_tier": "low"}
        high_workout = {"valid_repetitions": 24, "tempo_sec_per_rep": 0.8, "intensity_tier": "vigorous"}

        res_low = self.model.predict_adaptive_targets(self.sample_profile, low_workout)
        res_high = self.model.predict_adaptive_targets(self.sample_profile, high_workout)

        # High workout output must yield higher or equal predicted energy burn and protein target
        self.assertGreaterEqual(res_high["target_calories"], res_low["target_calories"])
        self.assertGreaterEqual(res_high["target_protein_g"], res_low["target_protein_g"])

    def test_xai_feature_attribution(self):
        """Verify explainability attribution percentages sum to 100%."""
        result = self.model.predict_adaptive_targets(
            profile=self.sample_profile,
            exercise_session={"valid_repetitions": 18, "intensity_tier": "vigorous"},
        )
        xai = result.get("xai_attribution", {})
        self.assertIn("metabolic_baseline_pct", xai)
        self.assertIn("kinematic_movement_pct", xai)
        self.assertIn("goal_calibration_pct", xai)

        total_pct = xai["metabolic_baseline_pct"] + xai["kinematic_movement_pct"] + xai["goal_calibration_pct"]
        self.assertAlmostEqual(total_pct, 100.0, delta=1.0)

    def test_targets_integration(self):
        """Verify calculate_nutrition_targets successfully uses ML energy model."""
        targets = calculate_nutrition_targets(
            profile=self.sample_profile,
            exercise_session={"valid_repetitions": 18, "intensity_tier": "vigorous"},
        )
        self.assertTrue(targets["ml_adapted"])
        self.assertIn("xai_attribution", targets)
        self.assertIn("🤖 ML Regressor", targets["explanation"]["exercise_adaptation"])


if __name__ == "__main__":
    unittest.main()
