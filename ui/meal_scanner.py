"""FitFuel AI Meal Scanner & Nutrition Estimation Screen.

Processes meal photographs, provides human-in-the-loop candidate confirmation,
scales portion categories, and aggregates itemized macronutrient estimates.
"""

from __future__ import annotations

import io
from typing import Any, Dict, List

import plotly.express as px
import streamlit as st
from PIL import Image

from database.database import get_db
from modules.food.food_detector import FoodDetector
from modules.food.nutrition_lookup import NutritionLookup
from modules.food.portion_estimator import PortionEstimator


def render_meal_scanner_screen() -> None:
    """Render meal photo analysis and human confirmation interface adhering to DESIGN.md."""
    st.markdown('<div class="apple-hero-title">Meal Scanner & Food Vision</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="apple-hero-subtitle">Upload or photograph your meal to estimate nutrients with human-in-the-loop verification.</div>',
        unsafe_allow_html=True,
    )

    db = get_db()
    detector = FoodDetector()
    lookup = NutritionLookup()

    # Session state storage for active meal items
    if "scanned_meal_items" not in st.session_state:
        st.session_state["scanned_meal_items"] = []
    if "detection_done" not in st.session_state:
        st.session_state["detection_done"] = False
    if "detection_status" not in st.session_state:
        st.session_state["detection_status"] = ""

    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown('<div class="apple-section-title">1. Plate Input</div>', unsafe_allow_html=True)
        source_mode = st.radio(
            "Image Source",
            options=["upload_file", "camera_snap"],
            format_func=lambda x: {
                "upload_file": "📁 Upload Meal Photo (JPG, PNG)",
                "camera_snap": "📸 Snap Live Plate Photo",
            }.get(x, x),
        )

        if source_mode == "upload_file":
            uploaded_file = st.file_uploader("Upload meal image", type=["jpg", "jpeg", "png"])
            if uploaded_file:
                img = Image.open(uploaded_file)
                st.image(img, caption="Uploaded Plate", use_container_width=True)
                if st.button("Detect Foods", use_container_width=True, type="primary"):
                    with st.spinner("Analyzing neural visual textures and food signatures..."):
                        res = detector.detect_foods(img)
                        st.session_state["scanned_meal_items"] = res["foods"]
                        st.session_state["detection_done"] = True
                        st.session_state["detection_status"] = res.get("status_message", "")
                        st.session_state["scanned_image"] = img
                        st.rerun()

        else:
            cam_pic = st.camera_input("Take a photo of your plate")
            if cam_pic:
                img = Image.open(cam_pic)
                st.image(img, caption="Snapped Plate", use_container_width=True)
                if st.button("Detect Foods", use_container_width=True, type="primary"):
                    with st.spinner("Analyzing neural visual textures and food signatures..."):
                        res = detector.detect_foods(img)
                        st.session_state["scanned_meal_items"] = res["foods"]
                        st.session_state["detection_done"] = True
                        st.session_state["detection_status"] = res.get("status_message", "")
                        st.session_state["scanned_image"] = img
                        st.rerun()

    with c_right:
        st.markdown('<div class="apple-section-title">2. Plate Verification & Builder</div>', unsafe_allow_html=True)
        st.caption("AI food recognition is approximate. Confirm detected items, adjust portions, or search and add dishes.")

        # Show detection status banner if available
        if st.session_state.get("detection_status"):
            if st.session_state["scanned_meal_items"]:
                st.success(f"🤖 {st.session_state['detection_status']}")
            else:
                st.info(f"ℹ️ {st.session_state['detection_status']}")

        # Action bar: Add Item and Clear Plate
        all_food_names = lookup.get_all_food_names()
        with st.expander("➕ Add / Search Any Food Item", expanded=not bool(st.session_state["scanned_meal_items"])):
            add_c1, add_c2, add_c3 = st.columns([3, 2, 1])
            with add_c1:
                manual_food = st.selectbox("Select dish", options=["(Choose item...)"] + all_food_names, key="add_manual_food")
            with add_c2:
                manual_portion = st.selectbox(
                    "Portion",
                    options=PortionEstimator.get_portion_options(),
                    index=1,
                    key="add_manual_portion",
                )
            with add_c3:
                st.write("")
                st.write("")
                if st.button("Add", key="btn_manual_add", use_container_width=True, type="secondary"):
                    if manual_food != "(Choose item...)":
                        st.session_state["scanned_meal_items"].append({
                            "name": manual_food,
                            "portion_category": manual_portion,
                            "confidence": 1.0,
                        })
                        st.rerun()

        # Meal Category and Active Plate List
        if not st.session_state["scanned_meal_items"]:
            st.markdown(
                """
                <div class="store-utility-card" style="text-align: center; padding: 40px 24px;">
                    <div style="font-size: 2.5rem; margin-bottom: 8px;">🥗</div>
                    <div class="apple-tagline" style="margin-bottom: 6px;">Your Plate is Empty</div>
                    <p class="apple-caption">
                        Upload a meal photo to auto-detect, or use <strong>Add / Search Any Food Item</strong> above.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            meal_type = "lunch"
        else:
            top_col1, top_col2 = st.columns([3, 1])
            with top_col1:
                meal_type = st.selectbox(
                    "Meal Category",
                    options=["breakfast", "lunch", "dinner", "snack"],
                    index=1,
                    format_func=lambda x: x.capitalize(),
                )
            with top_col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Clear Plate", use_container_width=True):
                    st.session_state["scanned_meal_items"] = []
                    st.session_state["detection_status"] = ""
                    st.session_state["detection_done"] = False
                    st.rerun()

            st.write(f"**Items on Plate ({len(st.session_state['scanned_meal_items'])}):**")
            items_to_keep = []

            for idx, item in enumerate(st.session_state["scanned_meal_items"]):
                curr_name = item.get("name", all_food_names[0])
                curr_portion = item.get("portion_category", "medium")
                conf = item.get("confidence", 0.90)

                with st.expander(f"🍽️ {curr_name} ({curr_portion})", expanded=True):
                    col_name, col_portion, col_del = st.columns([3, 2, 1])

                    with col_name:
                        current_idx = all_food_names.index(curr_name) if curr_name in all_food_names else 0
                        chosen_name = st.selectbox(
                            f"Food #{idx+1}",
                            options=all_food_names,
                            index=current_idx,
                            key=f"food_select_{idx}",
                        )

                    with col_portion:
                        portion_options = PortionEstimator.get_portion_options()
                        p_idx = portion_options.index(curr_portion) if curr_portion in portion_options else 1
                        chosen_portion = st.selectbox(
                            f"Portion #{idx+1}",
                            options=portion_options,
                            index=p_idx,
                            key=f"portion_select_{idx}",
                        )

                    with col_del:
                        st.write("")
                        st.write("")
                        remove_item = st.checkbox("Remove", key=f"del_{idx}")

                    if not remove_item:
                        pill_class = "conf-high" if conf >= 0.85 else "conf-med"
                        conf_text = "Verified Manual Item" if conf >= 0.99 else f"AI Confidence: {int(conf*100)}%"
                        st.markdown(
                            f"""
                            <div style="font-size:0.8rem; color:#94a3b8; margin-top:-6px;">
                                <span class="confidence-pill {pill_class}">{conf_text}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        items_to_keep.append({
                            "name": chosen_name,
                            "portion_category": chosen_portion,
                            "confidence": conf,
                        })

            st.session_state["scanned_meal_items"] = items_to_keep

    # 3. NUTRITION BREAKDOWN ROLLUP
    if st.session_state.get("scanned_meal_items"):
        st.markdown("---")
        st.markdown('<div class="apple-section-title">3. Estimated Plate Nutrition (~)</div>', unsafe_allow_html=True)

        # Calculate rolled up nutrients
        aggregated_meal = lookup.aggregate_meal(st.session_state["scanned_meal_items"], meal_type=meal_type)

        n1, n2, n3, n4, n5 = st.columns(5)
        with n1:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-val">~{int(aggregated_meal['total_calories'])}</div>
                    <div class="metric-label">Calories (kcal)</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with n2:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-val">~{aggregated_meal['total_protein_g']:.0f}<span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">g</span></div>
                    <div class="metric-label">Protein</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with n3:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-val">~{aggregated_meal['total_carbs_g']:.0f}<span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">g</span></div>
                    <div class="metric-label">Carbs</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with n4:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-val">~{aggregated_meal['total_fat_g']:.0f}<span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">g</span></div>
                    <div class="metric-label">Fats</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with n5:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-val">~{aggregated_meal['total_fiber_g']:.0f}<span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">g</span></div>
                    <div class="metric-label">Fiber</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Macro Donut Chart
        chart_col, table_col = st.columns([1, 2])
        with chart_col:
            macros = aggregated_meal["macro_percentages"]
            fig = px.pie(
                values=[macros["protein"], macros["carbs"], macros["fat"]],
                names=["Protein", "Carbs", "Fat"],
                color=["Protein", "Carbs", "Fat"],
                color_discrete_map={"Protein": "#0066cc", "Carbs": "#2997ff", "Fat": "#86868b"},
                hole=0.62,
            )
            fig.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                height=220,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                font=dict(color="#ffffff", family="SF Pro Text, Inter, system-ui, sans-serif"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with table_col:
            st.write("**Itemized Nutrition Breakdown:**")
            table_data = []
            for item in aggregated_meal["items"]:
                table_data.append({
                    "Food": item["name"],
                    "Portion": item["portion_category"],
                    "Calories (kcal)": f"~{item['calories']}",
                    "Protein (g)": f"~{item['protein_g']}",
                    "Carbs (g)": f"~{item['carbs_g']}",
                    "Fat (g)": f"~{item['fat_g']}",
                })
            st.dataframe(table_data, use_container_width=True)

        # Instant Meal Improvement Swaps
        with st.expander("🔄 View Smart Nutritional Swaps for this Plate", expanded=True):
            from modules.recommendation.recommender import RecommendationEngine
            engine = RecommendationEngine()
            profile = db.get_user_profile(user_id=1)
            swaps = engine.suggest_meal_swaps(
                aggregated_meal["items"],
                goal=profile.get("goal", "muscle_gain") if profile else "muscle_gain",
                user_profile=profile,
            )
            for sw in swaps.get("suggestions", []):
                knn_badge = ""
                if sw.get("knn_optimized"):
                    sim = sw.get("knn_similarity", 0.0)
                    knn_badge = f'<span style="background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 2px 7px; border-radius: 9999px; font-size: 11px; font-weight: 600; margin-left: 8px;">🤖 KNN Cluster Swap (Sim: {sim:.2f})</span>'
                st.markdown(
                    f"""
                    <div class="store-utility-card-subtle" style="margin-bottom: 10px;">
                        <div class="apple-body-strong">
                            Swap: <span style="text-decoration: line-through; color: var(--color-body-muted);">{sw['from_item']}</span> ➔ <span style="color: var(--color-primary-on-dark);">{sw['to_item']}</span>{knn_badge}
                        </div>
                        <div class="apple-caption" style="margin-top: 4px;">{sw['reason']}</div>
                        <div class="apple-fine-print" style="margin-top: 6px; color: var(--color-primary-on-dark);">🔬 {sw.get('glycemic_impact', '')} | <strong>{sw['delta']}</strong></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Save to Database Button
        if st.button("Log Meal to Today's Dashboard", use_container_width=True, type="primary"):
            meal_id = db.save_meal(
                meal_info={
                    "meal_type": meal_type,
                    "total_calories": aggregated_meal["total_calories"],
                    "total_protein_g": aggregated_meal["total_protein_g"],
                    "total_carbs_g": aggregated_meal["total_carbs_g"],
                    "total_fat_g": aggregated_meal["total_fat_g"],
                    "total_fiber_g": aggregated_meal["total_fiber_g"],
                    "image_note": f"Scanned {len(aggregated_meal['items'])} items ({meal_type})",
                },
                items=aggregated_meal["items"],
                user_id=1,
            )
            st.success(f"🎉 Meal logged! (ID #{meal_id}). Daily nutrition targets updated.")
