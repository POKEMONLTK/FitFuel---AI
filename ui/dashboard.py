"""FitFuel AI Nutrition & Fitness Dashboard.

Displays estimated intake vs calculated targets, exercise biomarkers,
and daily progress meters.
"""

from __future__ import annotations

from typing import Any, Dict, List

import plotly.graph_objects as go
import streamlit as st

from database.database import get_db
from modules.nutrition.targets import calculate_nutrition_targets


def render_dashboard_screen() -> None:
    """Render main executive nutrition dashboard."""
    st.markdown('<div class="apple-hero-title">Nutrition & Movement Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="apple-hero-subtitle">Real-time comparison of observed movement expenditure and daily estimated dietary intake.</div>',
        unsafe_allow_html=True,
    )

    db = get_db()
    profile = db.get_user_profile(user_id=1)

    if not profile:
        st.warning("No athlete profile found. Please navigate to 'Athlete Profile' in the sidebar to configure your parameters.")
        return

    # Fetch recent exercise and meals
    exercise_sessions = db.get_exercise_sessions(user_id=1, limit=1)
    latest_exercise = exercise_sessions[0] if exercise_sessions else None

    # Calculate targets with exercise adaptation
    targets = calculate_nutrition_targets(profile, latest_exercise)

    # Fetch today's meals
    today_meals = db.get_today_meals(user_id=1)
    consumed_cals = sum(m["total_calories"] for m in today_meals)
    consumed_prot = sum(m["total_protein_g"] for m in today_meals)
    consumed_carbs = sum(m["total_carbs_g"] for m in today_meals)
    consumed_fat = sum(m["total_fat_g"] for m in today_meals)
    consumed_fiber = sum(m["total_fiber_g"] for m in today_meals)

    # Top Row Biomarkers
    c_bmi, c_ex, c_cal, c_prot = st.columns(4)
    with c_bmi:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-val">{targets['bmi']}</div>
                <div class="metric-label">BMI ({targets['bmi_category']})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_ex:
        if latest_exercise:
            reps = latest_exercise.get("valid_repetitions", 0)
            ex_name = latest_exercise.get("exercise_type", "pushup").capitalize()
            ex_val = f"{reps} Reps"
            ex_sub = f"{ex_name} (20s Scan)"
        else:
            ex_val = "Pending"
            ex_sub = "Movement Scan"

        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-val">{ex_val}</div>
                <div class="metric-label">{ex_sub}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_cal:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-val">~{int(consumed_cals)} <span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">/ {int(targets['target_calories'])}</span></div>
                <div class="metric-label">Calories Intake (kcal)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_prot:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-val">~{consumed_prot:.1f} <span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">/ {targets['target_protein_g']:.0f}g</span></div>
                <div class="metric-label">Protein Intake</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Target Progress Meters
    st.markdown('<div class="apple-section-title">Daily Target Fulfillment</div>', unsafe_allow_html=True)
    
    # Comparative Plotly Bar Chart
    fig_dash = go.Figure()
    categories = ["Calories (kcal)", "Protein (g)", "Carbs (g)", "Fat (g)"]
    targets_vals = [targets["target_calories"], targets["target_protein_g"], targets["target_carbs_g"], targets["target_fat_g"]]
    consumed_vals = [consumed_cals, consumed_prot, consumed_carbs, consumed_fat]

    fig_dash.add_trace(go.Bar(
        name="Target Goal",
        x=categories,
        y=targets_vals,
        marker_color="#333336",
        text=[f"{int(v)}" for v in targets_vals],
        textposition="auto",
    ))
    fig_dash.add_trace(go.Bar(
        name="Estimated Intake",
        x=categories,
        y=consumed_vals,
        marker_color="#0066cc",
        text=[f"~{int(v)}" for v in consumed_vals],
        textposition="auto",
    ))
    fig_dash.update_layout(
        barmode="group",
        height=260,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ffffff", family="SF Pro Text, Inter, system-ui, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig_dash, use_container_width=True)

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        cal_pct = min(1.0, consumed_cals / max(1.0, targets["target_calories"]))
        st.write(f"**Energy:** ~{int(consumed_cals)} / {int(targets['target_calories'])} kcal ({int(cal_pct*100)}%)")
        st.progress(cal_pct)

    with p2:
        prot_pct = min(1.0, consumed_prot / max(1.0, targets["target_protein_g"]))
        st.write(f"**Protein:** ~{consumed_prot:.1f} / {targets['target_protein_g']:.0f} g ({int(prot_pct*100)}%)")
        st.progress(prot_pct)

    with p3:
        carb_pct = min(1.0, consumed_carbs / max(1.0, targets["target_carbs_g"]))
        st.write(f"**Carbs:** ~{consumed_carbs:.1f} / {targets['target_carbs_g']:.0f} g ({int(carb_pct*100)}%)")
        st.progress(carb_pct)

    with p4:
        fat_pct = min(1.0, consumed_fat / max(1.0, targets["target_fat_g"]))
        st.write(f"**Fats:** ~{consumed_fat:.1f} / {targets['target_fat_g']:.0f} g ({int(fat_pct*100)}%)")
        st.progress(fat_pct)

    st.markdown("---")

    # Today's Meal Timeline
    col_meals, col_summary = st.columns([2, 1])

    with col_meals:
        st.markdown('<div class="apple-section-title">Today\'s Logged Meals</div>', unsafe_allow_html=True)
        if not today_meals:
            st.info("No meals logged yet today. Navigate to 'Meal Scanner' to record your plate.")
        else:
            for m in today_meals:
                with st.container():
                    st.markdown(
                        f"""
                        <div class="store-utility-card-subtle">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px;">
                                <div class="apple-body-strong">{m['meal_type'].upper()}</div>
                                <span class="apple-fine-print">{m['created_at']}</span>
                            </div>
                            <div class="apple-body" style="font-size: 15px; margin-bottom: 6px;">
                                <strong>~{int(m['total_calories'])} kcal</strong> &nbsp;|&nbsp; 
                                Protein: ~{m['total_protein_g']}g &nbsp;|&nbsp; 
                                Carbs: ~{m['total_carbs_g']}g &nbsp;|&nbsp; 
                                Fat: ~{m['total_fat_g']}g
                            </div>
                            <div class="apple-caption">
                                Items: {', '.join([it['food_name'] + ' (' + it['portion_category'] + ')' for it in m.get('items', [])])}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    with col_summary:
        st.markdown('<div class="apple-section-title">Adaptive Status</div>', unsafe_allow_html=True)
        rem_prot = max(0.0, targets["target_protein_g"] - consumed_prot)
        rem_cal = max(0.0, targets["target_calories"] - consumed_cals)
        ml_badge = '<span class="apple-chip conf-high" style="margin-bottom: 8px;">🤖 ML Precision Targets</span><br/>' if targets.get("ml_adapted") else ''

        st.markdown(
            f"""
            <div class="store-utility-card">
                {ml_badge}
                <div class="apple-caption" style="text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;">Remaining Budget</div>
                <div class="apple-tagline" style="margin-bottom: 6px;">~{int(rem_cal)} kcal remaining</div>
                <div class="apple-body" style="color: var(--color-primary-on-dark); margin-bottom: 12px;">
                    <strong>~{rem_prot:.1f}g</strong> protein needed
                </div>
                <div class="apple-caption" style="line-height: 1.5; padding-top: 12px; border-top: 1px solid var(--color-hairline);">
                    {targets['explanation']['exercise_adaptation']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
