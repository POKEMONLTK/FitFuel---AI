"""FitFuel AI History & Feedback Log Screen.

Provides transparent timelines of exercise sessions, logged meals,
visual trend analytics, and historical recommendation feedback.
"""

from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from database.database import get_db


def render_history_screen() -> None:
    """Render historical telemetry logs, visual charts, and feedback records adhering to DESIGN.md."""
    st.markdown('<div class="apple-hero-title">History & Analytics Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="apple-hero-subtitle">Audit past exercise scans, daily meal logs, and adaptation feedback stored in your local SQLite database.</div>',
        unsafe_allow_html=True,
    )

    db = get_db()
    tab_ex, tab_meals, tab_fb = st.tabs(["🏋️ Exercise Sessions", "🥗 Meal History", "💬 Feedback Log"])

    # 1. EXERCISE SESSIONS TAB
    with tab_ex:
        sessions = db.get_exercise_sessions(user_id=1, limit=50)
        if not sessions:
            st.info("No exercise sessions recorded yet.")
        else:
            # Interactive Trend Chart
            if len(sessions) >= 2:
                chron_sessions = list(reversed(sessions))
                x_labels = [f"#{i+1} ({s.get('created_at', '')[-8:]})" for i, s in enumerate(chron_sessions)]
                valid_reps = [s.get("valid_repetitions", 0) for s in chron_sessions]
                total_reps = [s.get("repetitions", 0) for s in chron_sessions]

                fig_ex = go.Figure()
                fig_ex.add_trace(go.Bar(x=x_labels, y=valid_reps, name="Valid Reps", marker_color="#0066cc"))
                fig_ex.add_trace(go.Bar(x=x_labels, y=[t - v for t, v in zip(total_reps, valid_reps)], name="Invalid/Incomplete", marker_color="#333336"))
                fig_ex.update_layout(
                    barmode="stack",
                    title="Exercise Repetition Progression Over Time",
                    height=280,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ffffff", family="SF Pro Text, Inter, system-ui, sans-serif"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_ex, use_container_width=True)

            table = []
            for s in sessions:
                table.append({
                    "Timestamp": s.get("created_at"),
                    "Exercise": s.get("exercise_type", "").capitalize(),
                    "Total Reps": s.get("repetitions"),
                    "Valid Reps": s.get("valid_repetitions"),
                    "Avg Tempo": f"{s.get('tempo_sec_per_rep', 1.25):.2f}s",
                    "Form Score": f"{int((s.get('form_consistency_score') or 0.8) * 100)}%",
                    "Intensity": (s.get("intensity_tier") or "moderate").capitalize(),
                })
            st.dataframe(table, use_container_width=True)

    # 2. MEAL HISTORY TAB
    with tab_meals:
        meals = db.get_all_meals(user_id=1, limit=50)
        if not meals:
            st.info("No meals recorded yet. Log your first meal in 'Meal Scanner'!")
        else:
            if len(meals) >= 2:
                chron_meals = list(reversed(meals))
                meal_labels = [f"{m['meal_type'].capitalize()} ({m.get('created_at', '')[-8:]})" for m in chron_meals]
                cals = [m["total_calories"] for m in chron_meals]
                prots = [m["total_protein_g"] for m in chron_meals]

                fig_m = go.Figure()
                fig_m.add_trace(go.Scatter(x=meal_labels, y=cals, name="Calories (kcal)", line=dict(color="#0066cc", width=3)))
                fig_m.add_trace(go.Bar(x=meal_labels, y=prots, name="Protein (g)", yaxis="y2", marker_color="#2997ff", opacity=0.7))
                fig_m.update_layout(
                    title="Nutrient Distribution Across Recent Meals",
                    yaxis=dict(title=dict(text="Calories (kcal)", font=dict(color="#0066cc"))),
                    yaxis2=dict(title=dict(text="Protein (g)", font=dict(color="#2997ff")), overlaying="y", side="right"),
                    height=280,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ffffff", family="SF Pro Text, Inter, system-ui, sans-serif"),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                )
                st.plotly_chart(fig_m, use_container_width=True)

            meal_table = []
            for m in meals:
                meal_table.append({
                    "Timestamp": m.get("created_at"),
                    "Meal Type": m.get("meal_type", "").capitalize(),
                    "Calories (kcal)": f"~{int(m.get('total_calories', 0))}",
                    "Protein (g)": f"~{m.get('total_protein_g', 0)}",
                    "Carbs (g)": f"~{m.get('total_carbs_g', 0)}",
                    "Fat (g)": f"~{m.get('total_fat_g', 0)}",
                    "Fiber (g)": f"~{m.get('total_fiber_g', 0)}",
                    "Items": ", ".join([it["food_name"] for it in m.get("items", [])]),
                })
            st.dataframe(meal_table, use_container_width=True)

    # 3. FEEDBACK LOG TAB
    with tab_fb:
        feedback_list = db.get_feedback_history(user_id=1)
        if not feedback_list:
            st.info("No meal feedback recorded yet. Visit 'Recommendations' to rate a meal!")
        else:
            # Summary KPIs
            avg_taste = sum(f.get("taste_rating", 3) for f in feedback_list) / len(feedback_list)
            avg_satiety = sum(f.get("satiety_rating", 3) for f in feedback_list) / len(feedback_list)
            eat_again_pct = (sum(1 for f in feedback_list if f.get("would_eat_again")) / len(feedback_list)) * 100

            k1, k2, k3 = st.columns(3)
            with k1:
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <div class="metric-val">{avg_taste:.1f} <span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">/ 5.0</span></div>
                        <div class="metric-label">Avg Taste Score</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with k2:
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <div class="metric-val">{avg_satiety:.1f} <span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">/ 5.0</span></div>
                        <div class="metric-label">Avg Fullness Score</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with k3:
                st.markdown(
                    f"""
                    <div class="metric-box">
                        <div class="metric-val">{int(eat_again_pct)}%</div>
                        <div class="metric-label">Repeat Preference</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.write("")
            fb_table = []
            for f in feedback_list:
                fb_table.append({
                    "Timestamp": f.get("created_at"),
                    "Meal / Recipe": f.get("recipe_title"),
                    "Taste Rating": f"{f.get('taste_rating')} / 5 ⭐",
                    "Satiety Rating": f"{f.get('satiety_rating')} / 5 🥗",
                    "Portion": f.get("portion_suitability", "").replace("_", " ").capitalize(),
                    "Would Eat Again": "Yes ✅" if f.get("would_eat_again") else "No ❌",
                    "Comments": f.get("comments", ""),
                })
            st.dataframe(fb_table, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="apple-section-title">Database Management</div>', unsafe_allow_html=True)
    if st.button("Reset Database Tables", use_container_width=True):
        db.init_db()
        st.success("Database tables refreshed.")
        st.rerun()
