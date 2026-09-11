# FitFuel AI — Relational SQLite Database Architecture

This directory houses the database schema, migration scripts, and seed data for **FitFuel AI**.

---

## 1. Relational Schema Overview

The database uses SQLite 3 with Write-Ahead Logging (`PRAGMA journal_mode=WAL`) and Foreign Key enforcement (`PRAGMA foreign_keys=ON`).

```
 +------------------+           1:N          +----------------------+
 |      users       |----------------------->|  exercise_sessions   |
 |------------------|                        +----------------------+
 | id (PK)          |
 | name             |           1:N          +----------------------+           1:N          +------------------+
 | age, sex, height |----------------------->|        meals         |----------------------->|    meal_items    |
 | weight_kg        |                        |----------------------|                        +------------------+
 | goal, diet_type  |                        | id (PK), user_id(FK) |                        | id (PK)          |
 | targets          |                        | total_calories, ...  |                        | meal_id (FK)     |
 +------------------+                        +----------------------+                        | food_name        |
          |                                                                                  | macros, portion  |
          |                     1:N          +----------------------+                        +------------------+
          +--------------------------------->|       feedback       |
                                             +----------------------+
                                             | id (PK), user_id(FK) |
                                             | recipe_title         |
                                             | taste, satiety       |
                                             +----------------------+
```

### Table Reference

| Table | Purpose | Primary Columns |
|---|---|---|
| `users` | Athlete biomarker profile & daily nutrient goals | `id`, `weight_kg`, `height_cm`, `goal`, `diet_type`, `allergens`, `target_calories`, `target_protein_g` |
| `exercise_sessions` | Kinematic movement metrics from MediaPipe Pose | `id`, `user_id`, `exercise_type`, `valid_repetitions`, `tempo_sec_per_rep`, `form_consistency_score`, `intensity_tier` |
| `meals` | Logged meals with aggregated macronutrients | `id`, `user_id`, `meal_type`, `total_calories`, `total_protein_g`, `total_carbs_g`, `total_fat_g`, `total_fiber_g` |
| `meal_items` | Individual food components detected/confirmed on plate | `id`, `meal_id`, `food_name`, `portion_category`, `calories`, `protein_g`, `carbs_g`, `fat_g`, `confidence` |
| `feedback` | Continuous ML adaptation logs (IEEE PID 09) | `id`, `user_id`, `recipe_id`, `taste_rating`, `satiety_rating`, `portion_suitability`, `comments` |

---

## 2. Privacy & Data Integrity Design

- **Zero Media Retention**: In accordance with privacy standards, video frames and meal photographs are processed in-memory. Only anonymous mathematical kinematic metrics and nutritional aggregates are persisted.
- **Cascade Deletion**: Foreign keys enforce referential integrity (`ON DELETE CASCADE`).

---

## 3. Setup & Seeding CLI (`database/seed_db.py`)

When publishing to or cloning from GitHub, the database file `fitfuel.db` is ignored by `.gitignore` to avoid committing stale local data.

The application **automatically self-initializes** the schema when launched. You can also manage it via the CLI:

### Audit Current Database
```powershell
python database/seed_db.py --check
```

### Populate Realistic Demo Data
Populates sample athlete profile, past push-up/squat workouts, and logged breakfast/lunch plates:
```powershell
python database/seed_db.py --demo
```

### Clean Rebuild / Factory Reset
```powershell
python database/seed_db.py --reset --demo
```

---

## 4. SQL Scripts

- **[`schema.sql`](schema.sql)**: Pure standard SQL DDL definitions and indexes.
- **[`seed_data.sql`](seed_data.sql)**: Standard SQL INSERT statements with sample demonstration data.
