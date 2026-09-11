"""FitFuel AI — From Movement to Nutrition.

Main Streamlit Application Entry Point.
Coordinates modular pipelines: user profiling, exercise computer vision,
food recognition with human-in-the-loop fallback, adaptive nutrition calculations,
and explainable recommendations.
"""

from __future__ import annotations

import streamlit as st

from database.database import get_db
from ui.dashboard import render_dashboard_screen
from ui.exercise import render_exercise_screen
from ui.history import render_history_screen
from ui.meal_scanner import render_meal_scanner_screen
from ui.profile import render_profile_screen
from ui.recommendations import render_recommendations_screen
from ui.styles import apply_custom_styles, render_safety_disclaimer


def render_home_screen() -> None:
    """Render welcome screen and application workflow guide adhering to DESIGN.md."""
    st.markdown('<div class="apple-hero-title">FitFuel AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="apple-hero-subtitle">From movement to nutrition. Adaptive decision-support powered by computer-vision exercise performance and meal-photo analysis.</div>',
        unsafe_allow_html=True,
    )

    db = get_db()
    profile = db.get_user_profile(user_id=1)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown(
            """
            <div class="store-utility-card">
                <div class="apple-tagline" style="margin-bottom: 12px;">The Adaptive Core Loop</div>
                <p class="apple-body" style="margin-bottom: 18px;">
                    Most nutrition trackers rely entirely on self-reported activity logs.
                    <strong>FitFuel AI observes your actual exercise movement</strong> (repetition cadence, depth, and form)
                    and combines it with your anthropometric baseline and meal photos to deliver 
                    <strong>transparent, explainable dietary guidance</strong>.
                </p>
                <div class="store-utility-card-subtle" style="margin-bottom: 0;">
                    <div class="apple-caption" style="letter-spacing: 0.04em; color: #ffffff;">
                        ASSESS (Profile) &nbsp;➔&nbsp; ANALYZE (Movement + Meals) &nbsp;➔&nbsp; RECOMMEND &nbsp;➔&nbsp; FEEDBACK &nbsp;➔&nbsp; ADAPT
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="apple-section-title">Workflow Architecture</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1:
            st.markdown(
                """
                <div class="store-utility-card-subtle">
                    <div class="apple-body-strong" style="margin-bottom: 8px;">1. Athlete Profile</div>
                    <div class="apple-caption" style="line-height: 1.5;">
                        Anthropometric baseline, goals, dietary boundaries, and Mifflin-St Jeor metabolic expenditure targets.
                    </div>
                    <div class="apple-body-strong" style="margin-top: 16px; margin-bottom: 8px;">2. Movement Scan</div>
                    <div class="apple-caption" style="line-height: 1.5;">
                        20-second active kinematic assessment with MediaPipe Pose skeleton tracking, repetition counting, and cadence.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with s2:
            st.markdown(
                """
                <div class="store-utility-card-subtle">
                    <div class="apple-body-strong" style="margin-bottom: 8px;">3. Meal Scanner</div>
                    <div class="apple-caption" style="line-height: 1.5;">
                        Plate photography and food vision with human-in-the-loop candidate confirmation and macro aggregation.
                    </div>
                    <div class="apple-body-strong" style="margin-top: 16px; margin-bottom: 8px;">4. Adaptive Guidance</div>
                    <div class="apple-caption" style="line-height: 1.5;">
                        Executive target-vs-intake dashboard, explainable 'Why this?' reasoning, and meal swap recommendations.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        # Athlete Status Card
        if profile:
            st.markdown(
                f"""
                <div class="store-utility-card">
                    <div class="apple-caption" style="text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Active Athlete Profile</div>
                    <div class="apple-tagline" style="margin-bottom: 12px;">{profile.get('name', 'Athlete')}</div>
                    <div class="apple-body" style="font-size: 15px; line-height: 1.7;">
                        • <strong>Age / Sex:</strong> {profile.get('age')} yrs, {profile.get('sex', 'male').capitalize()}<br/>
                        • <strong>Body Mass:</strong> {profile.get('weight_kg')} kg ({profile.get('height_cm')} cm)<br/>
                        • <strong>Primary Goal:</strong> {str(profile.get('goal', '')).replace('_', ' ').title()}<br/>
                        • <strong>Dietary Preference:</strong> {str(profile.get('diet_type', '')).capitalize()}<br/>
                        • <strong>Target Calories:</strong> ~{int(profile.get('target_calories', 2200))} kcal/day
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="store-utility-card">
                    <div class="apple-caption" style="text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Getting Started</div>
                    <div class="apple-tagline" style="margin-bottom: 8px;">Set Up Your Baseline</div>
                    <p class="apple-body" style="font-size: 15px;">
                        Configure your athlete profile with height, weight, and goals to personalize your daily nutrition baseline.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main() -> None:
    """Application main controller."""
    st.set_page_config(
        page_title="FitFuel AI — From Movement to Nutrition",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize styling and disclaimers
    apply_custom_styles()
    render_safety_disclaimer()

    # Sidebar Navigation
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; padding: 12px 0 24px 0;">
                <div style="font-size: 2.4rem; margin-bottom: 6px;">⚡</div>
                <div class="apple-tagline" style="font-size: 20px; letter-spacing: -0.25px;">FitFuel AI</div>
                <div class="apple-fine-print" style="letter-spacing: 0.08em; text-transform: uppercase; margin-top: 4px;">
                    From Movement to Nutrition
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        nav_selection = st.radio(
            "Navigation",
            options=[
                "🏠 Home",
                "👤 Athlete Profile",
                "🏋️ Movement Scan",
                "🥗 Meal Scanner",
                "📊 Nutrition Dashboard",
                "✨ Recommendations",
                "📜 History & Feedback",
            ],
            index=0,
        )

        st.markdown("---")
        st.markdown(
            """
            <div class="apple-fine-print" style="margin-top: 20px; line-height: 1.5;">
                FitFuel AI Prototype v1.0<br/>
                Decision-Support Prototype<br/>
                Computer Vision & Nutrition Intelligence
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Route navigation
    if nav_selection == "🏠 Home":
        render_home_screen()
    elif nav_selection == "👤 Athlete Profile":
        render_profile_screen()
    elif nav_selection == "🏋️ Movement Scan":
        render_exercise_screen()
    elif nav_selection == "🥗 Meal Scanner":
        render_meal_scanner_screen()
    elif nav_selection == "📊 Nutrition Dashboard":
        render_dashboard_screen()
    elif nav_selection == "✨ Recommendations":
        render_recommendations_screen()
    elif nav_selection == "📜 History & Feedback":
        render_history_screen()


if __name__ == "__main__":
    main()
