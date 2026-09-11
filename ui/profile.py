"""FitFuel AI Profile Screen.

Handles user onboarding, anthropometric parameters, dietary constraints,
and transparent BMI / energy requirement calculation breakdowns.
"""

from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from database.database import get_db
from modules.nutrition.bmi import calculate_bmi, get_bmi_category, get_healthy_weight_range
from modules.nutrition.energy import calculate_bmr, calculate_tdee
from modules.nutrition.targets import calculate_nutrition_targets


def render_profile_screen() -> None:
    """Render profile and body metrics interface adhering to DESIGN.md."""
    st.markdown('<div class="apple-hero-title">Athlete Profile & Baseline</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="apple-hero-subtitle">Define your body parameters, nutrition preferences, and lifestyle constraints.</div>',
        unsafe_allow_html=True,
    )

    db = get_db()
    existing_profile = db.get_user_profile(user_id=1) or {}

    with st.form("profile_form"):
        st.markdown('<div class="apple-section-title">1. Anthropometrics & Baseline</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            name = st.text_input("Name / Nickname", value=st.session_state.get("p_name", existing_profile.get("name", "FitFuel Athlete")))
            age = st.number_input("Age (years)", min_value=14, max_value=90, value=int(st.session_state.get("p_age", existing_profile.get("age", 25))))
            sex = st.selectbox(
                "Biological Sex",
                options=["male", "female"],
                index=0 if st.session_state.get("p_sex", existing_profile.get("sex", "male")) == "male" else 1,
                help="Used strictly for standard Mifflin-St Jeor metabolic baseline equations.",
            )

        with c2:
            height_cm = st.number_input(
                "Height (cm)",
                min_value=120.0,
                max_value=230.0,
                value=float(st.session_state.get("p_height", existing_profile.get("height_cm", 175.0))),
                step=0.5,
            )
            weight_kg = st.number_input(
                "Weight (kg)",
                min_value=35.0,
                max_value=220.0,
                value=float(st.session_state.get("p_weight", existing_profile.get("weight_kg", 70.0))),
                step=0.5,
            )

        with c3:
            goal = st.selectbox(
                "Primary Fitness Goal",
                options=["muscle_gain", "weight_loss", "maintenance", "general_wellness"],
                format_func=lambda x: {
                    "muscle_gain": "Muscle Gain (Hypertrophy)",
                    "weight_loss": "Weight Loss (Fat Loss Deficit)",
                    "maintenance": "Maintenance (Body Recomposition)",
                    "general_wellness": "General Wellness & Energy",
                }.get(x, x),
                index=["muscle_gain", "weight_loss", "maintenance", "general_wellness"].index(
                    st.session_state.get("p_goal", existing_profile.get("goal", "muscle_gain"))
                ),
            )
            activity_level = st.selectbox(
                "General Activity Level",
                options=["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"],
                format_func=lambda x: {
                    "sedentary": "Sedentary (Desk work, little exercise)",
                    "lightly_active": "Lightly Active (1-3 days exercise/week)",
                    "moderately_active": "Moderately Active (3-5 days workout/week)",
                    "very_active": "Very Active (6-7 intense sessions/week)",
                    "extra_active": "Extra Active (Athletic physical training)",
                }.get(x, x),
                index=["sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"].index(
                    st.session_state.get("p_activity", existing_profile.get("activity_level", "moderately_active"))
                ),
            )

        st.markdown('<div class="apple-section-title" style="margin-top: 28px;">2. Dietary Preferences & Safety Boundaries</div>', unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        with d1:
            diet_type = st.selectbox(
                "Dietary Pattern",
                options=["vegetarian", "vegan", "eggitarian", "non-vegetarian"],
                format_func=lambda x: {
                    "vegetarian": "Vegetarian (Plant + Dairy)",
                    "vegan": "Strict Vegan (100% Plant-based)",
                    "eggitarian": "Eggitarian (Vegetarian + Eggs)",
                    "non-vegetarian": "Non-Vegetarian (All proteins)",
                }.get(x, x),
                index=["vegetarian", "vegan", "eggitarian", "non-vegetarian"].index(
                    st.session_state.get("p_diet", existing_profile.get("diet_type", "vegetarian"))
                ),
            )

        with d2:
            allergens = st.text_input(
                "Allergies (comma separated)",
                value=st.session_state.get("p_allergens", existing_profile.get("allergens", "none")),
                help="e.g., dairy, gluten, peanuts, tree nuts, soy, egg. Enter 'none' if none.",
            )
            disliked_foods = st.text_input(
                "Disliked Ingredients",
                value=st.session_state.get("p_dislikes", existing_profile.get("disliked_foods", "")),
                help="e.g., mushroom, eggplant, bitter gourd",
            )

        with d3:
            preferred_cuisine = st.selectbox(
                "Preferred Cuisine",
                options=["indian", "global", "mediterranean"],
                format_func=lambda x: x.capitalize(),
                index=["indian", "global", "mediterranean"].index(
                    st.session_state.get("p_cuisine", existing_profile.get("preferred_cuisine", "indian"))
                ),
            )

        st.write("")
        submit_btn = st.form_submit_button("Save Profile & Update Targets", type="primary", use_container_width=True)

    # Calculate real-time metrics
    try:
        bmi = calculate_bmi(height_cm, weight_kg)
        category, badge_color, desc = get_bmi_category(bmi)
        min_w, max_w = get_healthy_weight_range(height_cm)
        bmr = calculate_bmr(weight_kg, height_cm, age, sex)
        tdee = calculate_tdee(bmr, activity_level)

        temp_profile = {
            "name": name,
            "age": age,
            "sex": sex,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "goal": goal,
            "activity_level": activity_level,
            "diet_type": diet_type,
            "allergens": allergens,
            "disliked_foods": disliked_foods,
            "preferred_cuisine": preferred_cuisine,
        }

        # Check for recent exercise session
        recent_sessions = db.get_exercise_sessions(user_id=1, limit=1)
        recent_ex = recent_sessions[0] if recent_sessions else None

        targets = calculate_nutrition_targets(temp_profile, recent_ex)

        if submit_btn:
            temp_profile["target_calories"] = targets["target_calories"]
            temp_profile["target_protein_g"] = targets["target_protein_g"]
            temp_profile["target_carbs_g"] = targets["target_carbs_g"]
            temp_profile["target_fat_g"] = targets["target_fat_g"]
            db.save_user_profile(temp_profile, user_id=1)
            st.success("Profile saved. Daily baseline targets recalculated.")

        # Display Calculated Biomarkers
        st.markdown('<div class="apple-section-title" style="margin-top: 32px;">Biomarker & Metabolic Targets</div>', unsafe_allow_html=True)

        b1, b2, b3, b4 = st.columns(4)
        with b1:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-val">{bmi}</div>
                    <div class="metric-label">BMI ({category})</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b2:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-val">{int(targets['target_calories'])} <span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">kcal</span></div>
                    <div class="metric-label">Target Energy</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b3:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-val">{targets['target_protein_g']:.0f} <span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">g</span></div>
                    <div class="metric-label">Protein Target</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with b4:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-val">{targets['target_water_liters']} <span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">L</span></div>
                    <div class="metric-label">Hydration Target</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("Inspect Mathematical Formulas & Metabolic Assumptions"):
            st.markdown(
                f"""
                - **BMI Calculation**: ${weight_kg} \\text{{ kg}} / ({height_cm/100:.2f} \\text{{ m}})^2 = {bmi}$ ({category}). Healthy reference range for your height: **{min_w} kg – {max_w} kg**.
                - **Basal Metabolic Rate (BMR)**: Computed via Mifflin-St Jeor formula = **{bmr:.0f} kcal/day**.
                - **Total Daily Energy Expenditure (TDEE)**: BMR × PAL multiplier ({activity_level}) = **{tdee:.0f} kcal/day**.
                - **Goal Calibration**: `{goal}` adjusts baseline to **{targets['target_calories']:.0f} kcal/day**.
                - **Protein Benchmark**: Scaled at **{targets['target_protein_g']:.1f}g** ({round(targets['target_protein_g']/weight_kg, 2)} g/kg) to maximize muscle repair without excess metabolic strain.
                - **Macro Split**: ~25% healthy fats ({targets['target_fat_g']}g), remaining calories from complex carbohydrates ({targets['target_carbs_g']}g), plus {targets['target_fiber_g']}g dietary fiber.
                - **Machine Learning Regressors (IEEE PID 09)**: Real-time kinematic telemetry and workout fatigue dynamically train Gradient Boosting & Random Forest models to adapt daily TDEE and protein benchmarks beyond static clinical equations.
                """
            )

    except Exception as err:
        st.error(f"Error computing profile metrics: {err}")
