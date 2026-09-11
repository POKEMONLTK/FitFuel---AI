-- ====================================================================
-- FitFuel AI — Relational SQLite Database Schema
-- Architecture for Personalized Nutrition, Kinematic Vision, & ML Ranking
-- ====================================================================

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- 1. Athlete Profiles Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT DEFAULT 'FitFuel Athlete',
    age INTEGER DEFAULT 25,
    sex TEXT DEFAULT 'male' CHECK (sex IN ('male', 'female', 'other')),
    height_cm REAL DEFAULT 175.0,
    weight_kg REAL DEFAULT 70.0,
    goal TEXT DEFAULT 'muscle_gain' CHECK (goal IN ('muscle_gain', 'weight_loss', 'maintenance', 'general_wellness')),
    activity_level TEXT DEFAULT 'moderately_active' CHECK (activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active')),
    diet_type TEXT DEFAULT 'vegetarian' CHECK (diet_type IN ('vegan', 'vegetarian', 'eggitarian', 'non-vegetarian')),
    allergens TEXT DEFAULT 'none',
    disliked_foods TEXT DEFAULT '',
    preferred_cuisine TEXT DEFAULT 'indian',
    target_calories REAL DEFAULT 2200.0,
    target_protein_g REAL DEFAULT 130.0,
    target_carbs_g REAL DEFAULT 260.0,
    target_fat_g REAL DEFAULT 65.0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Kinematic Movement Sessions Table (MediaPipe Pose Tracking)
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
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 3. Logged Meals Table (Aggregated Nutrition)
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
    total_calories REAL NOT NULL,
    total_protein_g REAL NOT NULL,
    total_carbs_g REAL NOT NULL,
    total_fat_g REAL NOT NULL,
    total_fiber_g REAL DEFAULT 0.0,
    image_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- 4. Itemized Meal Components Table (Human-in-the-Loop Vision Items)
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

-- 5. User Feedback & Continuous ML Adaptation Table (IEEE PID 09)
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    recipe_id TEXT,
    recipe_title TEXT NOT NULL,
    taste_rating INTEGER NOT NULL CHECK (taste_rating BETWEEN 1 AND 5),
    satiety_rating INTEGER NOT NULL CHECK (satiety_rating BETWEEN 1 AND 5),
    portion_suitability TEXT CHECK (portion_suitability IN ('too_small', 'just_right', 'too_large')),
    would_eat_again INTEGER NOT NULL CHECK (would_eat_again IN (0, 1)),
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Indexes for Fast Query Execution & Real-time Streamlit Dashboard
CREATE INDEX IF NOT EXISTS idx_exercise_user_time ON exercise_sessions (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_meals_user_time ON meals (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_meal_items_meal_id ON meal_items (meal_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user_time ON feedback (user_id, created_at DESC);
