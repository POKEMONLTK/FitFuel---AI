"""FitFuel AI SQLite Database Manager.

Handles local persistence for user profiles, exercise sessions, meal logs,
and user feedback while respecting privacy by storing extracted metrics
rather than raw media files.
"""

from __future__ import annotations

import contextlib
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "fitfuel.db"


class DatabaseManager:
    """Manages SQLite database connections and transactions for FitFuel AI."""

    def __init__(self, db_file: Path | str = DB_PATH) -> None:
        self.db_file = str(db_file)
        self.init_db()

    @contextlib.contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_file, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initialize database tables with indexes and initial profile if empty."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT DEFAULT 'FitFuel Athlete',
                    age INTEGER DEFAULT 25,
                    sex TEXT DEFAULT 'male',
                    height_cm REAL DEFAULT 175.0,
                    weight_kg REAL DEFAULT 70.0,
                    goal TEXT DEFAULT 'muscle_gain',
                    activity_level TEXT DEFAULT 'moderately_active',
                    diet_type TEXT DEFAULT 'vegetarian',
                    allergens TEXT DEFAULT 'none',
                    disliked_foods TEXT DEFAULT '',
                    preferred_cuisine TEXT DEFAULT 'indian',
                    target_calories REAL DEFAULT 2200,
                    target_protein_g REAL DEFAULT 130,
                    target_carbs_g REAL DEFAULT 260,
                    target_fat_g REAL DEFAULT 65,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

            # 2. Exercise sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS exercise_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    exercise_type TEXT NOT NULL,
                    duration_sec REAL NOT NULL,
                    repetitions INTEGER NOT NULL,
                    valid_repetitions INTEGER NOT NULL,
                    tempo_sec_per_rep REAL,
                    range_of_motion_score REAL,
                    form_consistency_score REAL,
                    intensity_tier TEXT,
                    metrics_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """
            )

            # 3. Meals table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS meals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    meal_type TEXT NOT NULL,
                    total_calories REAL NOT NULL,
                    total_protein_g REAL NOT NULL,
                    total_carbs_g REAL NOT NULL,
                    total_fat_g REAL NOT NULL,
                    total_fiber_g REAL DEFAULT 0.0,
                    image_note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """
            )

            # 4. Meal items table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS meal_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meal_id INTEGER NOT NULL,
                    food_name TEXT NOT NULL,
                    portion_category TEXT NOT NULL,
                    portion_multiplier REAL DEFAULT 1.0,
                    calories REAL NOT NULL,
                    protein_g REAL NOT NULL,
                    carbs_g REAL NOT NULL,
                    fat_g REAL NOT NULL,
                    fiber_g REAL DEFAULT 0.0,
                    confidence REAL DEFAULT 1.0,
                    confirmed_by_user INTEGER DEFAULT 1,
                    FOREIGN KEY (meal_id) REFERENCES meals (id) ON DELETE CASCADE
                );
                """
            )

            # 5. Feedback table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    recipe_id TEXT,
                    recipe_title TEXT NOT NULL,
                    taste_rating INTEGER NOT NULL,
                    satiety_rating INTEGER NOT NULL,
                    portion_suitability TEXT,
                    would_eat_again INTEGER NOT NULL,
                    comments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                """
            )
            # Auto-seed baseline athlete profile if table is empty
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                    INSERT INTO users (
                        id, name, age, sex, height_cm, weight_kg, goal,
                        activity_level, diet_type, allergens, disliked_foods,
                        preferred_cuisine, target_calories, target_protein_g,
                        target_carbs_g, target_fat_g
                    ) VALUES (1, 'FitFuel Athlete', 25, 'male', 175.0, 70.0, 'muscle_gain',
                             'moderately_active', 'vegetarian', 'none', '', 'indian',
                             2200, 130, 260, 65)
                    """
                )
            conn.commit()

    def save_user_profile(self, profile: Dict[str, Any], user_id: int = 1) -> int:
        """Upsert user profile information."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            exists = cursor.fetchone()

            if exists:
                cursor.execute(
                    """
                    UPDATE users SET
                        name = ?, age = ?, sex = ?, height_cm = ?, weight_kg = ?,
                        goal = ?, activity_level = ?, diet_type = ?, allergens = ?,
                        disliked_foods = ?, preferred_cuisine = ?,
                        target_calories = ?, target_protein_g = ?,
                        target_carbs_g = ?, target_fat_g = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        profile.get("name", "FitFuel Athlete"),
                        int(profile.get("age", 25)),
                        profile.get("sex", "male"),
                        float(profile.get("height_cm", 175.0)),
                        float(profile.get("weight_kg", 70.0)),
                        profile.get("goal", "muscle_gain"),
                        profile.get("activity_level", "moderately_active"),
                        profile.get("diet_type", "vegetarian"),
                        profile.get("allergens", "none"),
                        profile.get("disliked_foods", ""),
                        profile.get("preferred_cuisine", "indian"),
                        float(profile.get("target_calories", 2200)),
                        float(profile.get("target_protein_g", 130)),
                        float(profile.get("target_carbs_g", 260)),
                        float(profile.get("target_fat_g", 65)),
                        user_id,
                    ),
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO users (
                        id, name, age, sex, height_cm, weight_kg, goal,
                        activity_level, diet_type, allergens, disliked_foods,
                        preferred_cuisine, target_calories, target_protein_g,
                        target_carbs_g, target_fat_g
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        profile.get("name", "FitFuel Athlete"),
                        int(profile.get("age", 25)),
                        profile.get("sex", "male"),
                        float(profile.get("height_cm", 175.0)),
                        float(profile.get("weight_kg", 70.0)),
                        profile.get("goal", "muscle_gain"),
                        profile.get("activity_level", "moderately_active"),
                        profile.get("diet_type", "vegetarian"),
                        profile.get("allergens", "none"),
                        profile.get("disliked_foods", ""),
                        profile.get("preferred_cuisine", "indian"),
                        float(profile.get("target_calories", 2200)),
                        float(profile.get("target_protein_g", 130)),
                        float(profile.get("target_carbs_g", 260)),
                        float(profile.get("target_fat_g", 65)),
                    ),
                )
            conn.commit()
            return user_id

    def get_user_profile(self, user_id: int = 1) -> Optional[Dict[str, Any]]:
        """Retrieve user profile by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def save_exercise_session(self, session_data: Dict[str, Any], user_id: int = 1) -> int:
        """Save exercise metrics to database."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Sanitize metrics dict to ensure clean JSON serialization
        clean_payload = {}
        for k, v in session_data.items():
            if k == "annotated_keyframes" or hasattr(v, "shape"):
                continue
            if hasattr(v, "item"):
                clean_payload[k] = v.item()
            elif isinstance(v, (int, float, str, bool, list, dict)) or v is None:
                clean_payload[k] = v

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO exercise_sessions (
                    user_id, exercise_type, duration_sec, repetitions,
                    valid_repetitions, tempo_sec_per_rep, range_of_motion_score,
                    form_consistency_score, intensity_tier, metrics_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    clean_payload.get("exercise", "pushup"),
                    float(clean_payload.get("duration_sec", 20)),
                    int(clean_payload.get("repetitions", 0)),
                    int(clean_payload.get("valid_repetitions", 0)),
                    float(clean_payload.get("tempo_sec_per_rep", 1.2)),
                    float(clean_payload.get("range_of_motion_score", 0.85)),
                    float(clean_payload.get("form_consistency_score", 0.85)),
                    clean_payload.get("intensity_tier", "moderate"),
                    json.dumps(clean_payload),
                    now_str,
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_exercise_sessions(self, user_id: int = 1, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch historical exercise sessions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM exercise_sessions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
            return [dict(r) for r in cursor.fetchall()]

    def save_meal(
        self,
        meal_info: Dict[str, Any],
        items: List[Dict[str, Any]],
        user_id: int = 1,
    ) -> int:
        """Save a complete meal along with itemized foods."""
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO meals (
                    user_id, meal_type, total_calories, total_protein_g,
                    total_carbs_g, total_fat_g, total_fiber_g, image_note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    meal_info.get("meal_type", "lunch"),
                    float(meal_info.get("total_calories", 0.0)),
                    float(meal_info.get("total_protein_g", 0.0)),
                    float(meal_info.get("total_carbs_g", 0.0)),
                    float(meal_info.get("total_fat_g", 0.0)),
                    float(meal_info.get("total_fiber_g", 0.0)),
                    meal_info.get("image_note", "User uploaded meal photo"),
                    now_str,
                ),
            )
            meal_id = cursor.lastrowid

            for item in items:
                cursor.execute(
                    """
                    INSERT INTO meal_items (
                        meal_id, food_name, portion_category, portion_multiplier,
                        calories, protein_g, carbs_g, fat_g, fiber_g,
                        confidence, confirmed_by_user
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        meal_id,
                        item.get("name", "Food Item"),
                        item.get("portion_category", "medium"),
                        float(item.get("portion_multiplier", 1.0)),
                        float(item.get("calories", 0.0)),
                        float(item.get("protein_g", 0.0)),
                        float(item.get("carbs_g", 0.0)),
                        float(item.get("fat_g", 0.0)),
                        float(item.get("fiber_g", 0.0)),
                        float(item.get("confidence", 1.0)),
                        int(item.get("confirmed_by_user", 1)),
                    ),
                )
            conn.commit()
            return meal_id

    def get_today_meals(self, user_id: int = 1) -> List[Dict[str, Any]]:
        """Fetch meals recorded today."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            today_str = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                """
                SELECT * FROM meals
                WHERE user_id = ? AND (date(created_at) = ? OR date(created_at, 'localtime') = ?)
                ORDER BY created_at ASC
                """,
                (user_id, today_str, today_str),
            )
            meals = [dict(r) for r in cursor.fetchall()]
            for m in meals:
                cursor.execute(
                    "SELECT * FROM meal_items WHERE meal_id = ?", (m["id"],)
                )
                m["items"] = [dict(it) for it in cursor.fetchall()]
            return meals

    def get_all_meals(self, user_id: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch recent meals with items."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM meals
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
            meals = [dict(r) for r in cursor.fetchall()]
            for m in meals:
                cursor.execute(
                    "SELECT * FROM meal_items WHERE meal_id = ?", (m["id"],)
                )
                m["items"] = [dict(it) for it in cursor.fetchall()]
            return meals

    def save_feedback(self, feedback_data: Dict[str, Any], user_id: int = 1) -> int:
        """Save meal recommendation feedback."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO feedback (
                    user_id, recipe_id, recipe_title, taste_rating,
                    satiety_rating, portion_suitability, would_eat_again, comments
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    feedback_data.get("recipe_id", ""),
                    feedback_data.get("recipe_title", "Custom Recommendation"),
                    int(feedback_data.get("taste_rating", 4)),
                    int(feedback_data.get("satiety_rating", 4)),
                    feedback_data.get("portion_suitability", "just_right"),
                    int(feedback_data.get("would_eat_again", 1)),
                    feedback_data.get("comments", ""),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_feedback_history(self, user_id: int = 1) -> List[Dict[str, Any]]:
        """Get past feedback entries."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM feedback
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            )
            return [dict(r) for r in cursor.fetchall()]


_db_instance: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """Singleton getter for DatabaseManager."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
    return _db_instance
