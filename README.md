# FitFuel AI — From Movement to Nutrition

> **Adaptive precision nutrition decision support connecting computer-vision exercise performance, meal-photo analysis, and machine learning personalization (IEEE PID 09).**

---

## 1. Project Overview

FitFuel AI is an intelligent fitness and precision nutrition platform. Instead of relying purely on static, self-reported logs, FitFuel AI directly analyzes:
1. **Physical Movement**: 20-second computer vision exercise tests (push-ups, squats, sit-ups) capturing repetition cadence, range-of-motion, and form consistency via MediaPipe Pose.
2. **Plate Nutrition**: Meal photographs analyzed with multi-scale neural recognition, texture-gated plate detection, and a mandatory **human-in-the-loop confirmation fallback**.
3. **Adaptive Targets (IEEE PID 09 Phase 1)**: Gradient Boosting and Random Forest regression predicting dynamic TDEE, EPOC recovery, and individualized protein targets from exercise kinematics.
4. **ML Recommendation Ranker (IEEE PID 09 Phase 2)**: Regularized Ridge model scoring meals across 11-D multi-modal features with continuous online adaptation from user ratings.
5. **KNN Nutrient-Space Swaps (IEEE PID 09 Phase 3)**: Unsupervised cosine clustering optimizing food substitutions for protein boost, glycemic load reduction, and satiety.
6. **Relational Local Persistence**: Privacy-first SQLite engine with foreign-key referential integrity and zero raw media retention.

---

## 2. Scientific & Product Boundaries

- **BMI**: Calculated deterministically from measured height and weight. We make **no claim** of predicting BMI or body fat from photos.
- **Movement**: Labeled as an **"exercise performance profile"**, not a clinical fitness diagnosis.
- **Protein & Metabolism**: We make **no claim** of measuring biological protein absorption from exercise. Targets are evidence-based general guidelines.
- **Food Vision**: Labeled with **`~`** (estimated values) and always user-confirmable.
- **Disclaimer**: FitFuel AI is a wellness and educational decision-support prototype, not a substitute for licensed medical or dietetic consultation.

---

## 3. Project Architecture

```
FITRUN/
├── app.py                           # Master Streamlit UI & Navigation
├── requirements.txt                 # Dependencies
├── README.md                        # Documentation & setup guide
├── .gitignore                       # Clean repository exclusions for Git & GitHub
├── .env.example                     # Environment configuration template
├── data/
│   ├── foods.csv                    # Global foods database
│   ├── indian_foods.csv             # Indian traditional foods database
│   └── recipes.csv                  # Curated recipes & meals catalog
├── database/
│   ├── __init__.py
│   ├── database.py                  # SQLite engine (users, exercises, meals, feedback)
│   ├── schema.sql                   # Standard SQL DDL relational schema definition
│   ├── seed_data.sql                # Demonstration dataset SQL insert statements
│   ├── seed_db.py                   # Database setup, reset, and seeding CLI
│   └── README.md                    # Database documentation & ERD diagram
├── modules/
│   ├── __init__.py
│   ├── exercise/                    # MediaPipe Pose tracking & 20s test orchestrator
│   ├── food/                        # Multi-scale neural vision & portion estimation
│   ├── nutrition/                   # Energy, BMI, and ML Regressor (PID 09 Phase 1)
│   └── recommendation/              # ML Ranker (Phase 2) & KNN Swaps (Phase 3)
├── ui/                              # Sleek Apple-inspired dark fitness UI screens
├── tests/                           # 47 comprehensive automated unit tests
└── models/                          # Pretrained vision & neural checkpoints
```

---

## 4. Quick Start Guide

### Step 1: Create and Activate Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Initialize / Seed Database
The application automatically creates the database on launch. To populate rich demo workouts, meal logs, and taste feedback immediately:
```powershell
python database/seed_db.py --demo
```

### Step 4: Launch FitFuel AI
```powershell
streamlit run app.py
```
The application will open automatically in your browser at `http://localhost:8501`.

---

## 5. Publishing to GitHub

The repository is configured with a production-grade `.gitignore` that automatically excludes transient local databases (`*.db`), virtual environments (`.venv/`), and cache files.

To publish this project to your GitHub account:

```powershell
# 1. Initialize Git repository (if not already done)
git init

# 2. Stage all project files (safe exclusions applied automatically)
git add .

# 3. Create your initial commit
git commit -m "feat: initial FitFuel AI release with IEEE PID 09 ML and SQLite database"

# 4. Link your remote GitHub repository
git branch -M main
git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git

# 5. Push code to GitHub
git push -u origin main
```

---

## 6. Running Automated Tests

Run the complete 47-test automated verification suite:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

| Test Suite | Tests | Status | Scope |
|---|---|---|---|
| `test_database.py` | 6 | **PASS** | SQLite schema tables, CRUD operations, transactions, seed script. |
| `test_knn_swaps.py` | 6 | **PASS** | 6D nutrient space vectorization, GI modeling, multi-objective swaps. |
| `test_ml_energy.py` | 5 | **PASS** | Gradient Boosting & Random Forest energy regressors, XAI attribution. |
| `test_ml_ranker.py` | 5 | **PASS** | Regularized Ridge ranking, multi-modal features, online adaptation. |
| `test_nutrition.py` | 8 | **PASS** | Mifflin-St Jeor formulas, BMR, TDEE, protein targets, food lookup. |
| `test_exercise.py` | 4 | **PASS** | Pose detector, push-up/squat tracker, synthetic movement fallback. |
| `test_food_detector.py` | 4 | **PASS** | Food vision detector, portion estimator, macro aggregator. |
| `test_recommendation.py` | 5 | **PASS** | Safe recipe filtering, allergen exclusions, meal swap engine. |
| **Total** | **47** | **100% PASS** | Zero failures, zero warnings, sub-5s execution. |

---

## 7. Open-Source References & Acknowledgments

- **IEEE PID 09** (*Varshney et al., ICAIIHI 2023*): Precision nutrition machine learning framework (GBM/RF regression, KNN clustering, Explainable AI).
- **GC_Fit** (MIT License): Kinematic joint-angle tracking and rep-counting concepts.
- **Food-Image-Recognition** (MIT License): Food classification concepts and nutrition pipeline structure.
- **NutriMind**: Content-based recommendation architecture and macro similarity vectors.
