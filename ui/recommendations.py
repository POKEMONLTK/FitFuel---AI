"""FitFuel AI Recommendation & Explainable AI Screen.

Renders personalized meal plans, the explainable 'Why this?' panel,
intelligent meal swap suggestions, and interactive feedback mechanisms.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

import streamlit as st

from database.database import get_db
from modules.recommendation.recommender import RecommendationEngine


def render_recommendations_screen() -> None:
    """Render meal recommendations and explainable AI interface adhering to DESIGN.md."""
    st.markdown('<div class="apple-hero-title">Adaptive Nutrition Recommendations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="apple-hero-subtitle">Personalized meal options tuned to your exercise output, dietary boundaries, and macro gaps.</div>',
        unsafe_allow_html=True,
    )

    db = get_db()
    profile = db.get_user_profile(user_id=1)

    if not profile:
        st.warning("Please complete your athlete profile first.")
        return

    # Fetch latest exercise test and today's intake
    exercise_sessions = db.get_exercise_sessions(user_id=1, limit=1)
    latest_exercise = exercise_sessions[0] if exercise_sessions else None

    today_meals = db.get_today_meals(user_id=1)
    consumed_today = {
        "calories": sum(m["total_calories"] for m in today_meals),
        "protein_g": sum(m["total_protein_g"] for m in today_meals),
        "carbs_g": sum(m["total_carbs_g"] for m in today_meals),
        "fat_g": sum(m["total_fat_g"] for m in today_meals),
    }

    feedback_history = db.get_feedback_history(user_id=1)

    # Initialize recommendation engine
    engine = RecommendationEngine()
    recommendations = engine.recommend(
        user_profile=profile,
        exercise_session=latest_exercise,
        consumed_today=consumed_today,
        feedback_history=feedback_history,
        top_k=3,
    )

    # Tabs: Recommendations & Meal Swaps
    tab_rec, tab_swap = st.tabs(["✨ Recommended Meals", "🔄 'Improve This Meal' (Swap Engine)"])

    with tab_rec:
        if not recommendations:
            st.info("No matching recipes found under current strict constraints.")
            return

        for idx, rec in enumerate(recommendations):
            with st.container():
                match_label = "🤖 ML Match" if rec.get("ml_ranked") else "Match"
                st.markdown(
                    f"""
                    <div class="store-utility-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 10px;">
                            <div class="apple-tagline">#{idx+1}. {rec['title']}</div>
                            <span class="apple-chip conf-high">{match_label}: {int(rec.get('recommendation_score', 0.85)*100)}%</span>
                        </div>
                        <p class="apple-body" style="font-size: 15px; margin-bottom: 12px;">{rec.get('description', '')}</p>
                        <div style="display:flex; gap:8px; flex-wrap:wrap;">
                            <span class="apple-chip">🔥 {rec.get('calories')} kcal</span>
                            <span class="apple-chip">💪 {rec.get('protein_g')}g Protein</span>
                            <span class="apple-chip">🌾 {rec.get('carbs_g')}g Carbs</span>
                            <span class="apple-chip">🥑 {rec.get('fat_g')}g Fat</span>
                            <span class="apple-chip">🥗 {rec.get('fiber_g', 0)}g Fiber</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Explainable AI Dropdown
                with st.expander("💡 Why this meal? (Explainable AI Breakdown)", expanded=True):
                    for reason in rec.get("why_points", []):
                        st.markdown(f"- {reason}")

                    # Detailed score breakdown & XAI attribution
                    if rec.get("feature_attribution"):
                        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                        st.caption("🔬 **ML Decision Factors (IEEE PID 09 Explainability Decomposition):**")
                        top_attribs = sorted(rec["feature_attribution"].items(), key=lambda x: x[1], reverse=True)[:6]
                        attrib_cols = st.columns(3)
                        for c_i, (f_name, pct) in enumerate(top_attribs):
                            clean_label = f_name.replace("_", " ").title()
                            with attrib_cols[c_i % 3]:
                                st.markdown(
                                    f"""
                                    <div class="store-utility-card-subtle" style="padding: 10px 14px; margin-bottom: 6px;">
                                        <div class="apple-caption" style="font-size: 12px; color: var(--color-text-muted);">{clean_label}</div>
                                        <div class="apple-body-strong" style="font-size: 15px; color: var(--color-primary-on-dark);">{pct:.1f}%</div>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                    elif rec.get("score_breakdown"):
                        sb = rec.get("score_breakdown", {})
                        st.caption(
                            f"Detailed Multi-Objective Weights: "
                            f"Nutritional Match: {int(sb.get('nutrition_match', 0)*100)}% | "
                            f"Goal Alignment: {int(sb.get('goal_match', 0)*100)}% | "
                            f"Cuisine Match: {int(sb.get('cuisine_match', 0)*100)}% | "
                            f"Feedback Weight: {int(sb.get('feedback_score', 0.7)*100)}%"
                        )

                # Feedback Form for this recipe
                with st.expander("⭐ Rate This Recommendation (Feedback Loop)"):
                    with st.form(f"feedback_form_{rec.get('id', idx)}"):
                        f_col1, f_col2, f_col3 = st.columns(3)
                        with f_col1:
                            taste = st.slider("Taste / Palatability", 1, 5, 4, key=f"t_{idx}")
                        with f_col2:
                            satiety = st.slider("Satiety / Fullness", 1, 5, 4, key=f"s_{idx}")
                        with f_col3:
                            portion_suit = st.selectbox(
                                "Portion Size",
                                ["just_right", "too_small", "too_large"],
                                key=f"ps_{idx}",
                            )

                        c_again, c_comm = st.columns([1, 2])
                        with c_again:
                            would_eat = st.checkbox("Would eat this again", value=True, key=f"we_{idx}")
                        with c_comm:
                            comment = st.text_input("Optional notes / feedback", key=f"cm_{idx}")

                        sub_fb = st.form_submit_button("Submit Feedback", type="primary", use_container_width=True)
                        if sub_fb:
                            fb_data = {
                                "recipe_id": rec.get("id", f"R{idx}"),
                                "recipe_title": rec.get("title", ""),
                                "taste_rating": taste,
                                "satiety_rating": satiety,
                                "portion_suitability": portion_suit,
                                "would_eat_again": 1 if would_eat else 0,
                                "comments": comment,
                            }
                            db.save_feedback(fb_data, user_id=1)
                            # Continuous online ML adaptation (PID 09)
                            try:
                                from modules.nutrition.targets import calculate_nutrition_targets
                                current_targets = calculate_nutrition_targets(profile, latest_exercise)
                                engine.ml_ranker.adapt_with_feedback(fb_data, rec, profile, current_targets)
                            except Exception:
                                pass
                            st.success("Feedback recorded. ML ranking model adapted to your personal satiety & taste profile!")
                            st.rerun()

                st.write("")

    with tab_swap:
        st.markdown('<div class="apple-section-title">Analyze & Improve Recent Meal</div>', unsafe_allow_html=True)
        st.caption("Suggests smart macronutrient and ingredient replacements based on your recent plate.")

        if not today_meals:
            st.info("No meals logged today yet. Log your meals in 'Meal Scanner' to view customized nutritional swaps.")
            return

        latest_m = today_meals[-1]
        sample_items = latest_m.get("items", [])
        st.write(f"Analyzing most recent meal: **{latest_m['meal_type'].upper()}** ({len(sample_items)} items)")

        swaps_data = engine.suggest_meal_swaps(
            sample_items,
            goal=profile.get("goal", "muscle_gain"),
            user_profile=profile,
        )

        for s in swaps_data.get("suggestions", []):
            knn_badge = ""
            if s.get("knn_optimized"):
                sim = s.get("knn_similarity", 0.0)
                knn_badge = f'<span style="background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 2px 7px; border-radius: 9999px; font-size: 11px; font-weight: 600; margin-left: 8px;">🤖 KNN Cluster Swap (Sim: {sim:.2f})</span>'

            st.markdown(
                f"""
                <div class="store-utility-card-subtle" style="margin-bottom: 12px;">
                    <div class="apple-body-strong">
                        Swap: <span style="text-decoration:line-through; color:var(--color-body-muted);">{s['from_item']}</span> 
                        ➔ <span style="color:var(--color-primary-on-dark);">{s['to_item']}</span>{knn_badge}
                    </div>
                    <p class="apple-body" style="font-size: 14px; margin: 6px 0;">{s['reason']}</p>
                    <div class="apple-caption" style="margin-bottom: 8px;">
                        🔬 <strong>Glycemic & Satiety Benefit:</strong> {s.get('glycemic_impact', 'Balanced glycemic response')}
                    </div>
                    <div class="apple-fine-print" style="color: var(--color-primary-on-dark);">
                        📊 <strong>Nutrient Delta:</strong> {s['delta']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
