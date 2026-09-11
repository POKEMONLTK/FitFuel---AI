-- ====================================================================
-- FitFuel AI — Demonstration Seed Data SQL Script
-- Populates Realistic Athlete Biomarkers, Exercise Tests, Meals, and Feedback
-- ====================================================================

-- 1. Athlete Profile
INSERT OR REPLACE INTO users (
    id, name, age, sex, height_cm, weight_kg, goal,
    activity_level, diet_type, allergens, disliked_foods,
    preferred_cuisine, target_calories, target_protein_g,
    target_carbs_g, target_fat_g, updated_at
) VALUES (
    1, 'FitFuel Athlete', 25, 'male', 175.0, 70.0, 'muscle_gain',
    'moderately_active', 'vegetarian', 'none', '',
    'indian', 2280.0, 138.0, 270.0, 68.0, CURRENT_TIMESTAMP
);

-- 2. Recent Kinematic Movement Sessions (MediaPipe Pose 20-Second Tests)
INSERT INTO exercise_sessions (
    user_id, exercise_type, duration_sec, repetitions, valid_repetitions,
    tempo_sec_per_rep, range_of_motion_score, form_consistency_score,
    intensity_tier, metrics_json, created_at
) VALUES 
(
    1, 'pushup', 20.0, 16, 14,
    1.25, 0.92, 0.88, 'high',
    '{"exercise": "pushup", "duration_sec": 20, "repetitions": 16, "valid_repetitions": 14, "tempo_sec_per_rep": 1.25, "range_of_motion_score": 0.92, "form_consistency_score": 0.88, "intensity_tier": "high", "estimated_cadence_score": 0.89, "inferred_power_watts": 210.0}',
    datetime('now', '-2 hours')
),
(
    1, 'squat', 20.0, 12, 11,
    1.65, 0.90, 0.91, 'moderate',
    '{"exercise": "squat", "duration_sec": 20, "repetitions": 12, "valid_repetitions": 11, "tempo_sec_per_rep": 1.65, "range_of_motion_score": 0.90, "form_consistency_score": 0.91, "intensity_tier": "moderate", "estimated_cadence_score": 0.84, "inferred_power_watts": 185.0}',
    datetime('now', '-1 day')
),
(
    1, 'situp', 20.0, 14, 13,
    1.40, 0.87, 0.86, 'moderate',
    '{"exercise": "situp", "duration_sec": 20, "repetitions": 14, "valid_repetitions": 13, "tempo_sec_per_rep": 1.40, "range_of_motion_score": 0.87, "form_consistency_score": 0.86, "intensity_tier": "moderate", "estimated_cadence_score": 0.82, "inferred_power_watts": 160.0}',
    datetime('now', '-2 days')
);

-- 3. Today's Logged Meals
INSERT INTO meals (
    id, user_id, meal_type, total_calories, total_protein_g,
    total_carbs_g, total_fat_g, total_fiber_g, image_note, created_at
) VALUES 
(
    101, 1, 'breakfast', 425.0, 15.2, 66.0, 11.4, 7.8,
    'Scanned breakfast: Rolled oats with chia seeds, banana, and crushed almonds',
    datetime('now', '-4 hours')
),
(
    102, 1, 'lunch', 590.0, 29.5, 54.0, 27.0, 8.4,
    'Scanned lunch: Paneer bhurji with 2 whole wheat rotis and cucumber salad',
    datetime('now', '-1 hour')
);

-- 4. Itemized Meal Components
INSERT INTO meal_items (
    meal_id, food_name, portion_category, portion_multiplier,
    calories, protein_g, carbs_g, fat_g, fiber_g, confidence, confirmed_by_user
) VALUES
-- Breakfast items
(101, 'Rolled Oats Porridge', 'medium', 1.0, 240.0, 8.2, 42.0, 4.2, 5.0, 0.95, 1),
(101, 'Banana (Medium)', 'small', 1.0, 105.0, 1.3, 27.0, 0.3, 3.1, 0.98, 1),
(101, 'Crushed Almonds & Chia', 'small', 0.5, 80.0, 5.7, 3.0, 6.9, 2.5, 0.88, 1),

-- Lunch items
(102, 'Paneer Bhurji', 'medium', 1.0, 310.0, 20.5, 8.0, 22.0, 1.2, 0.94, 1),
(102, 'Chapati / Roti (Whole Wheat)', 'medium', 2.0, 240.0, 7.0, 42.0, 4.0, 4.8, 0.96, 1),
(102, 'Cucumber & Tomato Salad', 'medium', 1.0, 40.0, 2.0, 8.0, 1.0, 2.4, 0.92, 1);

-- 5. User Feedback Logs (Continuous Reinforcement Learning & Personalization)
INSERT INTO feedback (
    user_id, recipe_id, recipe_title, taste_rating,
    satiety_rating, portion_suitability, would_eat_again, comments, created_at
) VALUES 
(
    1, 'R04', 'Paneer Tikka with Mint Chutney', 5, 5, 'just_right', 1,
    'Fantastic post-workout meal. Kept me full for 4 hours and easily closed my protein gap.',
    datetime('now', '-1 day')
),
(
    1, 'R12', 'Dal Tadka with Brown Rice & Sprout Salad', 4, 4, 'just_right', 1,
    'Great fiber and clean energy, didn''t cause any post-meal slump.',
    datetime('now', '-2 days')
),
(
    1, 'R18', 'Sprouted Moong & Vegetable Khichdi', 4, 5, 'just_right', 1,
    'Gentle on digestion with great micronutrient balance.',
    datetime('now', '-3 days')
);
