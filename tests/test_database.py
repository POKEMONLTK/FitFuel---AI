"""Unit tests for FitFuel AI SQLite database schema, persistence, and seeding."""

import os
import tempfile
import unittest
from pathlib import Path

from database.database import DatabaseManager
from database.seed_db import audit_database, init_schema, seed_demo_data


class TestDatabaseManager(unittest.TestCase):
    """Test suite for SQLite relational database operations."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_fitfuel.db"
        self.db = DatabaseManager(db_file=self.db_path)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_schema_tables_exist(self):
        """Verify all 5 relational tables exist upon initialization."""
        stats = audit_database(self.db_path)
        expected_tables = {"users", "exercise_sessions", "meals", "meal_items", "feedback"}
        for tbl in expected_tables:
            self.assertIn(tbl, stats)
        # Default athlete row should be seeded automatically
        self.assertGreaterEqual(stats["users"], 1)

    def test_user_profile_save_and_retrieve(self):
        """Verify profile persistence and updating."""
        profile_data = {
            "name": "Sarah Connor",
            "age": 28,
            "sex": "female",
            "height_cm": 168.0,
            "weight_kg": 62.0,
            "goal": "weight_loss",
            "activity_level": "very_active",
            "diet_type": "vegan",
            "allergens": "peanuts",
            "disliked_foods": "mushroom",
            "preferred_cuisine": "mediterranean",
            "target_calories": 1850.0,
            "target_protein_g": 115.0,
            "target_carbs_g": 210.0,
            "target_fat_g": 50.0,
        }
        self.db.save_user_profile(profile_data, user_id=1)
        retrieved = self.db.get_user_profile(user_id=1)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["name"], "Sarah Connor")
        self.assertEqual(retrieved["goal"], "weight_loss")
        self.assertEqual(retrieved["diet_type"], "vegan")
        self.assertEqual(retrieved["allergens"], "peanuts")
        self.assertAlmostEqual(retrieved["target_calories"], 1850.0)

    def test_exercise_session_persistence(self):
        """Verify exercise kinematic sessions and JSON serialization."""
        session_data = {
            "exercise": "pushup",
            "duration_sec": 20.0,
            "repetitions": 18,
            "valid_repetitions": 16,
            "tempo_sec_per_rep": 1.15,
            "range_of_motion_score": 0.94,
            "form_consistency_score": 0.90,
            "intensity_tier": "high",
        }
        session_id = self.db.save_exercise_session(session_data, user_id=1)
        self.assertIsInstance(session_id, int)

        sessions = self.db.get_exercise_sessions(user_id=1, limit=5)
        self.assertGreaterEqual(len(sessions), 1)
        first = sessions[0]
        self.assertEqual(first["exercise_type"], "pushup")
        self.assertEqual(first["valid_repetitions"], 16)
        self.assertEqual(first["intensity_tier"], "high")

    def test_meal_and_item_persistence(self):
        """Verify meal transactions and cascade item links."""
        meal_info = {
            "meal_type": "breakfast",
            "total_calories": 380.0,
            "total_protein_g": 14.0,
            "total_carbs_g": 55.0,
            "total_fat_g": 8.0,
            "total_fiber_g": 6.0,
            "image_note": "Test breakfast photo",
        }
        items = [
            {
                "name": "Oatmeal",
                "portion_category": "medium",
                "portion_multiplier": 1.0,
                "calories": 250.0,
                "protein_g": 8.0,
                "carbs_g": 45.0,
                "fat_g": 4.0,
                "fiber_g": 4.5,
                "confidence": 0.95,
                "confirmed_by_user": 1,
            },
            {
                "name": "Almonds",
                "portion_category": "small",
                "portion_multiplier": 1.0,
                "calories": 130.0,
                "protein_g": 6.0,
                "carbs_g": 10.0,
                "fat_g": 4.0,
                "fiber_g": 1.5,
                "confidence": 0.90,
                "confirmed_by_user": 1,
            },
        ]
        meal_id = self.db.save_meal(meal_info, items, user_id=1)
        self.assertIsInstance(meal_id, int)

        today_meals = self.db.get_today_meals(user_id=1)
        self.assertGreaterEqual(len(today_meals), 1)
        m = today_meals[-1]
        self.assertEqual(m["meal_type"], "breakfast")
        self.assertEqual(len(m["items"]), 2)
        self.assertEqual(m["items"][0]["food_name"], "Oatmeal")

    def test_feedback_persistence(self):
        """Verify recommendation feedback logging."""
        feedback_data = {
            "recipe_id": "R01",
            "recipe_title": "Paneer Tikka Salad",
            "taste_rating": 5,
            "satiety_rating": 4,
            "portion_suitability": "just_right",
            "would_eat_again": 1,
            "comments": "Delicious and macro-friendly",
        }
        fb_id = self.db.save_feedback(feedback_data, user_id=1)
        self.assertIsInstance(fb_id, int)

        history = self.db.get_feedback_history(user_id=1)
        self.assertGreaterEqual(len(history), 1)
        self.assertEqual(history[0]["recipe_title"], "Paneer Tikka Salad")
        self.assertEqual(history[0]["taste_rating"], 5)

    def test_seed_demo_script(self):
        """Verify seed_demo_data loads records into clean database."""
        temp_db = Path(self.temp_dir.name) / "seed_test.db"
        init_schema(temp_db, reset=True)
        seed_demo_data(temp_db)
        stats = audit_database(temp_db)
        self.assertGreaterEqual(stats["users"], 1)
        self.assertGreaterEqual(stats["exercise_sessions"], 3)
        self.assertGreaterEqual(stats["meals"], 2)
        self.assertGreaterEqual(stats["meal_items"], 6)
        self.assertGreaterEqual(stats["feedback"], 3)


if __name__ == "__main__":
    unittest.main()
