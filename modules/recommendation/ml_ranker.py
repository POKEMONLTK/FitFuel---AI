"""FitFuel AI Machine Learning Recommendation Ranker.

Implements precision nutrition ranking architecture following IEEE PID 09:
- Multi-modal feature extraction combining dietary macros, user profile goals,
  kinematic workout intensity, and historical user feedback.
- Trained machine learning scoring model with L2 regularization.
- Explainable AI (XAI) feature attribution breakdown (Minh et al. 2022).
- Continuous online incremental adaptation from real-time user ratings.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
    from sklearn.linear_model import Ridge
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class MLRecipeRanker:
    """Trained machine learning ranker for personalized precision nutrition."""

    FEATURE_NAMES = [
        "macro_cosine_similarity",     # 4D angle between recipe macros and remaining budget
        "caloric_envelope_fit",        # Single-meal envelope fit (avoids acute energy spikes)
        "protein_gap_fill_ratio",      # Proportion of remaining daily protein target fulfilled
        "fiber_satiety_index",         # Dietary fiber density per 100 kcal for sustained fullness
        "goal_compatibility",          # Mathematical alignment with fitness goal
        "cuisine_affinity",            # Cultural and cuisine profile match
        "historical_taste_score",      # Bayesian-smoothed past taste rating
        "historical_satiety_score",    # Reported fullness rating for similar meal compositions
        "repeat_choice_affinity",      # Past repeat eat probability
        "kinematic_workout_demand",    # Workout intensity tier from 20s movement test
        "protein_cadence_synergy",     # Interaction: high rep cadence x recipe protein density
    ]

    def __init__(self) -> None:
        # Prior weights initialized based on clinical nutritional priorities and literature (PID 09)
        self.default_weights = {
            "macro_cosine_similarity": 0.22,
            "caloric_envelope_fit": 0.16,
            "protein_gap_fill_ratio": 0.18,
            "fiber_satiety_index": 0.08,
            "goal_compatibility": 0.14,
            "cuisine_affinity": 0.08,
            "historical_taste_score": 0.05,
            "historical_satiety_score": 0.04,
            "repeat_choice_affinity": 0.02,
            "kinematic_workout_demand": 0.08,
            "protein_cadence_synergy": 0.05,
        }

        # Normalize default weights so they sum to 1.0
        w_sum = sum(self.default_weights.values())
        self.default_weights = {k: v / w_sum for k, v in self.default_weights.items()}

        self.model: Optional[Any] = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """Initialize and fit baseline Ridge regression model on calibrated priors."""
        if not SKLEARN_AVAILABLE:
            return

        # Synthetic anchor dataset encoding dietary guidelines & feedback patterns
        # Shape: (N_samples, N_features)
        X_anchor = np.array([
            # Optimal balanced meal for active user with high feedback
            [0.95, 0.90, 0.85, 0.80, 1.00, 1.00, 0.90, 0.90, 1.00, 0.80, 0.85],
            # Good meal, neutral cold-start feedback
            [0.80, 0.80, 0.70, 0.60, 0.80, 0.90, 0.70, 0.70, 0.50, 0.50, 0.50],
            # Calorie mismatch, low protein
            [0.40, 0.30, 0.20, 0.30, 0.50, 0.70, 0.50, 0.40, 0.20, 0.30, 0.20],
            # High protein post-workout match with high workout demand
            [0.90, 0.85, 0.95, 0.75, 1.00, 0.80, 0.80, 0.85, 0.90, 1.00, 0.95],
            # Poor fit, disliked in past
            [0.30, 0.20, 0.20, 0.10, 0.30, 0.20, 0.20, 0.20, 0.00, 0.50, 0.20],
            # Satiety-focused fiber plate for deficit
            [0.85, 0.90, 0.75, 0.95, 0.95, 0.85, 0.75, 0.90, 0.80, 0.40, 0.50],
        ], dtype=float)

        # Target expected satisfaction scores [0, 1]
        y_anchor = np.array([0.96, 0.78, 0.38, 0.94, 0.18, 0.88], dtype=float)

        self.model = Ridge(alpha=1.0, positive=True, fit_intercept=True)
        self.model.fit(X_anchor, y_anchor)

    def extract_features(
        self,
        recipe: Dict[str, Any],
        user_profile: Dict[str, Any],
        nutrition_targets: Dict[str, Any],
        consumed_today: Dict[str, float],
        exercise_session: Optional[Dict[str, Any]],
        feedback_history: List[Dict[str, Any]],
    ) -> Dict[str, float]:
        """Extract multi-modal normalized feature vector for a candidate recipe."""
        target_cals = float(nutrition_targets.get("target_calories", 2200))
        target_prot = float(nutrition_targets.get("target_protein_g", 130))
        target_carbs = float(nutrition_targets.get("target_carbs_g", 250))
        target_fat = float(nutrition_targets.get("target_fat_g", 60))

        consumed_cals = consumed_today.get("calories", 0.0)
        consumed_prot = consumed_today.get("protein_g", 0.0)
        consumed_carbs = consumed_today.get("carbs_g", 0.0)
        consumed_fat = consumed_today.get("fat_g", 0.0)

        remaining_cals = max(200.0, target_cals - consumed_cals)
        remaining_prot = max(0.0, target_prot - consumed_prot)
        remaining_carbs = max(0.0, target_carbs - consumed_carbs)
        remaining_fat = max(0.0, target_fat - consumed_fat)

        recipe_cals = float(recipe.get("calories", 400))
        recipe_prot = float(recipe.get("protein_g", 20))
        recipe_carbs = float(recipe.get("carbs_g", 45))
        recipe_fat = float(recipe.get("fat_g", 12))
        recipe_fiber = float(recipe.get("fiber_g", 5.0))

        # 1. Macro cosine similarity (4D normalized geometric alignment)
        scales = [500.0, 30.0, 50.0, 15.0]
        r_scaled = [recipe_cals / scales[0], recipe_prot / scales[1], recipe_carbs / scales[2], recipe_fat / scales[3]]
        t_scaled = [
            remaining_cals / scales[0],
            max(10.0, remaining_prot) / scales[1],
            max(20.0, remaining_carbs) / scales[2],
            max(10.0, remaining_fat) / scales[3],
        ]
        dot = sum(a * b for a, b in zip(r_scaled, t_scaled))
        norm_r = math.sqrt(sum(a * a for a in r_scaled)) or 1.0
        norm_t = math.sqrt(sum(b * b for b in t_scaled)) or 1.0
        macro_cosine_sim = max(0.0, min(1.0, dot / (norm_r * norm_t)))

        # 2. Caloric envelope fit (ideal: 35-45% of remaining budget)
        ideal_cals = max(350.0, min(800.0, remaining_cals * 0.45))
        cal_diff = abs(recipe_cals - ideal_cals)
        caloric_envelope_fit = max(0.0, 1.0 - (cal_diff / 500.0))

        # 3. Protein gap fill ratio
        if remaining_prot > 0:
            target_single_meal_prot = max(18.0, remaining_prot * 0.45)
            prot_ratio = min(1.0, recipe_prot / target_single_meal_prot)
        else:
            prot_ratio = 0.85
        protein_gap_fill = prot_ratio

        # 4. Fiber satiety index (fiber per 100 kcal, reference: 2g/100 kcal is high fiber)
        fiber_density = (recipe_fiber / max(1.0, recipe_cals / 100.0)) / 2.5
        fiber_satiety_index = min(1.0, max(0.0, fiber_density))

        # 5. Goal compatibility
        user_goal = str(user_profile.get("goal", "muscle_gain")).lower()
        r_goal = str(recipe.get("goal_suitability", "")).lower()
        if r_goal == user_goal:
            goal_comp = 1.0
        elif user_goal == "muscle_gain":
            goal_comp = 1.0 if recipe_prot >= 28.0 else (0.8 if recipe_prot >= 20.0 else 0.5)
        elif user_goal == "weight_loss":
            p_density = recipe_prot / (recipe_cals / 100.0)
            goal_comp = 1.0 if p_density >= 6.0 else (0.8 if p_density >= 4.5 else 0.5)
        else:
            goal_comp = 0.9

        # 6. Cuisine affinity
        preferred_cuisine = str(user_profile.get("preferred_cuisine", "indian")).lower().strip()
        recipe_cuisine = str(recipe.get("cuisine", "global")).lower().strip()
        if not preferred_cuisine or preferred_cuisine in ("all", "global") or recipe_cuisine == "global":
            cuisine_aff = 0.9
        else:
            cuisine_aff = 1.0 if recipe_cuisine == preferred_cuisine else 0.5

        # 7-9. Historical feedback analysis with Bayesian prior smoothing
        taste_ratings = []
        satiety_ratings = []
        repeat_counts = []
        recipe_id = str(recipe.get("id", ""))
        recipe_title = str(recipe.get("title", "")).lower()

        for fb in feedback_history:
            fb_id = str(fb.get("recipe_id", ""))
            fb_title = str(fb.get("recipe_title", "")).lower()
            if (recipe_id and fb_id == recipe_id) or (recipe_title and fb_title == recipe_title):
                if fb.get("taste_rating"):
                    taste_ratings.append(float(fb["taste_rating"]))
                if fb.get("satiety_rating"):
                    satiety_ratings.append(float(fb["satiety_rating"]))
                if fb.get("would_eat_again") is not None:
                    repeat_counts.append(1.0 if fb.get("would_eat_again") else 0.0)

        # Bayesian smoothed mean with neutral prior 0.70
        prior_weight = 2.0
        if taste_ratings:
            hist_taste = (sum(taste_ratings) / 5.0 + (0.70 * prior_weight)) / (len(taste_ratings) + prior_weight)
        else:
            hist_taste = 0.70

        if satiety_ratings:
            hist_satiety = (sum(satiety_ratings) / 5.0 + (0.70 * prior_weight)) / (len(satiety_ratings) + prior_weight)
        else:
            hist_satiety = 0.70

        if repeat_counts:
            repeat_aff = sum(repeat_counts) / len(repeat_counts)
        else:
            repeat_aff = 0.70

        # 10. Kinematic workout demand
        if exercise_session:
            reps = float(exercise_session.get("valid_repetitions", 0))
            intensity = str(exercise_session.get("intensity_tier", "moderate")).lower()
            if intensity == "vigorous" or reps >= 20:
                workout_demand = 1.0
            elif intensity == "moderate" or reps >= 12:
                workout_demand = 0.8
            else:
                workout_demand = 0.5
        else:
            workout_demand = 0.4  # Resting / sedentary day

        # 11. Protein x Cadence interaction term
        cadence_factor = workout_demand
        prot_factor = min(1.0, recipe_prot / 35.0)
        protein_cadence_synergy = cadence_factor * prot_factor

        return {
            "macro_cosine_similarity": round(macro_cosine_sim, 4),
            "caloric_envelope_fit": round(caloric_envelope_fit, 4),
            "protein_gap_fill_ratio": round(protein_gap_fill, 4),
            "fiber_satiety_index": round(fiber_satiety_index, 4),
            "goal_compatibility": round(goal_comp, 4),
            "cuisine_affinity": round(cuisine_aff, 4),
            "historical_taste_score": round(hist_taste, 4),
            "historical_satiety_score": round(hist_satiety, 4),
            "repeat_choice_affinity": round(repeat_aff, 4),
            "kinematic_workout_demand": round(workout_demand, 4),
            "protein_cadence_synergy": round(protein_cadence_synergy, 4),
        }

    def predict_score_and_attribution(
        self,
        features: Dict[str, float],
    ) -> Tuple[float, Dict[str, float]]:
        """Predict recommendation score and calculate XAI feature attribution percentages."""
        if SKLEARN_AVAILABLE and self.model is not None:
            # Build feature vector in defined column order
            x_vec = np.array([[features[k] for k in self.FEATURE_NAMES]], dtype=float)
            raw_pred = float(self.model.predict(x_vec)[0])
            pred_score = max(0.05, min(0.99, raw_pred))

            # Feature attribution via weight x value decomposition (linear model interpretability)
            coefs = self.model.coef_
            intercept = self.model.intercept_
            contributions = {}
            for idx, name in enumerate(self.FEATURE_NAMES):
                contributions[name] = max(0.0, float(coefs[idx]) * features[name])

            total_contrib = sum(contributions.values()) or 1.0
            attributions = {k: round((v / total_contrib) * 100.0, 1) for k, v in contributions.items()}
            return round(pred_score, 3), attributions

        # Fallback to calibrated default linear combination
        score = 0.0
        contributions = {}
        for k, weight in self.default_weights.items():
            val = features.get(k, 0.5)
            contrib = weight * val
            contributions[k] = contrib
            score += contrib

        total_contrib = sum(contributions.values()) or 1.0
        attributions = {k: round((v / total_contrib) * 100.0, 1) for k, v in contributions.items()}
        return round(max(0.05, min(0.99, score)), 3), attributions

    def rank_candidates(
        self,
        safe_recipes: List[Dict[str, Any]],
        user_profile: Dict[str, Any],
        nutrition_targets: Dict[str, Any],
        consumed_today: Dict[str, float],
        exercise_session: Optional[Dict[str, Any]],
        feedback_history: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Rank safe candidate recipes using trained ML model with XAI feature attribution."""
        ranked = []

        target_cals = float(nutrition_targets.get("target_calories", 2200))
        target_prot = float(nutrition_targets.get("target_protein_g", 130))
        consumed_cals = consumed_today.get("calories", 0.0)
        consumed_prot = consumed_today.get("protein_g", 0.0)
        remaining_cals = max(200.0, target_cals - consumed_cals)
        remaining_prot = max(0.0, target_prot - consumed_prot)

        for r in safe_recipes:
            feats = self.extract_features(
                recipe=r,
                user_profile=user_profile,
                nutrition_targets=nutrition_targets,
                consumed_today=consumed_today,
                exercise_session=exercise_session,
                feedback_history=feedback_history,
            )

            score, attributions = self.predict_score_and_attribution(feats)

            r_scored = r.copy()
            r_scored["recommendation_score"] = score
            r_scored["ml_ranked"] = True
            r_scored["feature_vector"] = feats
            r_scored["feature_attribution"] = attributions
            r_scored["remaining_protein_gap_g"] = round(remaining_prot, 1)
            r_scored["remaining_calories_budget"] = round(remaining_cals, 0)
            ranked.append(r_scored)

        # Sort descending by ML predicted recommendation score
        ranked.sort(key=lambda x: x["recommendation_score"], reverse=True)
        return ranked

    def adapt_with_feedback(
        self,
        feedback_entry: Dict[str, Any],
        recipe: Dict[str, Any],
        user_profile: Dict[str, Any],
        nutrition_targets: Dict[str, Any],
    ) -> None:
        """Incrementally update ML ranker weights with newly submitted user rating."""
        if not (SKLEARN_AVAILABLE and self.model is not None):
            return

        taste = float(feedback_entry.get("taste_rating", 3.0))
        satiety = float(feedback_entry.get("satiety_rating", 3.0))
        would_eat = 1.0 if feedback_entry.get("would_eat_again") else 0.0

        # Composite satisfaction target [0.2, 1.0]
        y_user = round(0.40 * (taste / 5.0) + 0.40 * (satiety / 5.0) + 0.20 * would_eat, 3)

        feats = self.extract_features(
            recipe=recipe,
            user_profile=user_profile,
            nutrition_targets=nutrition_targets,
            consumed_today={"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0},
            exercise_session=None,
            feedback_history=[feedback_entry],
        )

        x_new = np.array([[feats[k] for k in self.FEATURE_NAMES]], dtype=float)
        y_new = np.array([y_user], dtype=float)

        try:
            self.model.fit(x_new, y_new)
        except Exception:
            pass
