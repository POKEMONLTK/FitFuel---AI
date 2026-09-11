"""Unit tests for FitFuel AI Machine Learning Recommendation Ranker (IEEE PID 09)."""

import unittest
from modules.recommendation.ml_ranker import MLRecipeRanker
from modules.recommendation.recommender import RecommendationEngine


class TestMLRecipeRanker(unittest.TestCase):
    """Test suite for ML-based recommendation scoring, feature extraction, and adaptation."""

    def setUp(self):
        self.ranker = MLRecipeRanker()
        self.sample_recipe = {
            "id": "R101",
            "title": "High-Protein Paneer Power Bowl",
            "meal_type": "lunch",
            "diet_type": "vegetarian",
            "cuisine": "indian",
            "calories": 520,
            "protein_g": 32.0,
            "carbs_g": 48.0,
            "fat_g": 22.0,
            "fiber_g": 8.5,
            "goal_suitability": "muscle_gain",
        }
        self.sample_profile = {
            "name": "Athlete",
            "goal": "muscle_gain",
            "preferred_cuisine": "indian",
            "diet_type": "vegetarian",
            "weight_kg": 75.0,
            "height_cm": 178.0,
        }
        self.sample_targets = {
            "target_calories": 2400.0,
            "target_protein_g": 140.0,
            "target_carbs_g": 280.0,
            "target_fat_g": 65.0,
        }
        self.sample_consumed = {
            "calories": 600.0,
            "protein_g": 30.0,
            "carbs_g": 70.0,
            "fat_g": 15.0,
        }

    def test_feature_extraction_dimensions_and_bounds(self):
        """Verify feature extraction extracts all defined features within [0, 1] range."""
        feats = self.ranker.extract_features(
            recipe=self.sample_recipe,
            user_profile=self.sample_profile,
            nutrition_targets=self.sample_targets,
            consumed_today=self.sample_consumed,
            exercise_session={"valid_repetitions": 22, "intensity_tier": "vigorous"},
            feedback_history=[],
        )

        self.assertEqual(len(feats), len(MLRecipeRanker.FEATURE_NAMES))
        for feat_name, val in feats.items():
            self.assertIn(feat_name, MLRecipeRanker.FEATURE_NAMES)
            self.assertGreaterEqual(val, 0.0, f"{feat_name} below 0.0: {val}")
            self.assertLessEqual(val, 1.05, f"{feat_name} exceeds 1.0: {val}")

    def test_predict_score_and_attribution(self):
        """Verify ML model produces valid bounded scores and 100% normalized feature attributions."""
        feats = self.ranker.extract_features(
            recipe=self.sample_recipe,
            user_profile=self.sample_profile,
            nutrition_targets=self.sample_targets,
            consumed_today=self.sample_consumed,
            exercise_session={"valid_repetitions": 18, "intensity_tier": "moderate"},
            feedback_history=[],
        )

        score, attributions = self.ranker.predict_score_and_attribution(feats)
        self.assertGreaterEqual(score, 0.05)
        self.assertLessEqual(score, 0.99)
        self.assertEqual(len(attributions), len(MLRecipeRanker.FEATURE_NAMES))

        # Attribution percentage sum should be ~100%
        total_pct = sum(attributions.values())
        self.assertAlmostEqual(total_pct, 100.0, delta=1.5)

    def test_rank_candidates_sorting(self):
        """Verify candidates are sorted descending by ML recommendation score."""
        candidate_recipes = [
            {
                "id": "R1",
                "title": "Low Fit Item",
                "calories": 900,
                "protein_g": 5.0,
                "carbs_g": 140.0,
                "fat_g": 35.0,
                "fiber_g": 1.0,
                "goal_suitability": "general_wellness",
                "cuisine": "global",
            },
            self.sample_recipe,
        ]

        ranked = self.ranker.rank_candidates(
            safe_recipes=candidate_recipes,
            user_profile=self.sample_profile,
            nutrition_targets=self.sample_targets,
            consumed_today=self.sample_consumed,
            exercise_session={"valid_repetitions": 25, "intensity_tier": "vigorous"},
            feedback_history=[],
        )

        self.assertEqual(len(ranked), 2)
        self.assertGreaterEqual(ranked[0]["recommendation_score"], ranked[1]["recommendation_score"])
        # Sample recipe has high protein + muscle gain alignment, so it should rank first
        self.assertEqual(ranked[0]["id"], "R101")
        self.assertTrue(ranked[0]["ml_ranked"])
        self.assertIn("feature_attribution", ranked[0])

    def test_recommender_engine_integration(self):
        """Verify RecommendationEngine successfully uses ML ranker and attaches XAI explanation."""
        engine = RecommendationEngine()
        recs = engine.recommend(
            user_profile=self.sample_profile,
            exercise_session={"valid_repetitions": 20, "intensity_tier": "vigorous", "exercise": "pushup"},
            consumed_today=self.sample_consumed,
            feedback_history=[],
            top_k=2,
        )

        self.assertTrue(len(recs) >= 1)
        first_rec = recs[0]
        self.assertIn("recommendation_score", first_rec)
        self.assertTrue(first_rec.get("ml_ranked", False))
        self.assertIn("why_points", first_rec)
        self.assertTrue(len(first_rec["why_points"]) >= 2)

    def test_online_feedback_adaptation(self):
        """Verify adapt_with_feedback accepts user rating without raising exceptions."""
        feedback_entry = {
            "recipe_id": "R101",
            "recipe_title": "High-Protein Paneer Power Bowl",
            "taste_rating": 5,
            "satiety_rating": 5,
            "would_eat_again": 1,
        }
        # Should execute smoothly
        self.ranker.adapt_with_feedback(
            feedback_entry=feedback_entry,
            recipe=self.sample_recipe,
            user_profile=self.sample_profile,
            nutrition_targets=self.sample_targets,
        )


if __name__ == "__main__":
    unittest.main()
