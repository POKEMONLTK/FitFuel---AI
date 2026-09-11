"""FitFuel AI Exercise & Movement Scan Screen.

Runs 20-second kinematic tests with MediaPipe Pose, real-time skeleton overlay,
rep counting, cadence analysis, and zero-dependency synthetic simulation.
"""

import os
import tempfile
import time
from typing import Any, Dict

import numpy as np
import streamlit as st
from PIL import Image

from database.database import get_db
from modules.exercise.exercise_analyzer import ExerciseAnalyzer
from modules.exercise.pose_detector import CV2_AVAILABLE, MEDIAPIPE_AVAILABLE

try:
    import cv2
except ImportError:
    pass


def render_exercise_screen() -> None:
    """Render movement analysis test interface adhering to DESIGN.md."""
    st.markdown('<div class="apple-hero-title">Movement Scan & Exercise Performance</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="apple-hero-subtitle">Measure muscular endurance and exercise tempo with 20-second computer vision tests.</div>',
        unsafe_allow_html=True,
    )

    db = get_db()
    analyzer = ExerciseAnalyzer()

    col_ctrl, col_info = st.columns([1, 2])
    with col_ctrl:
        exercise_choice = st.selectbox(
            "Select Exercise",
            options=["pushup", "squat", "situp"],
            format_func=lambda x: {
                "pushup": "Push-up 20s Test (Primary MVP)",
                "squat": "Squat 20s Test",
                "situp": "Sit-up 20s Test",
            }.get(x, x),
        )

        input_mode = st.radio(
            "Testing Mode",
            options=["webcam", "upload_video"],
            format_func=lambda x: {
                "webcam": "📷 Live Webcam (MediaPipe Pose)",
                "upload_video": "📁 Upload Workout Video",
            }.get(x, x),
        )

    with col_info:
        st.markdown(
            f"""
            <div class="store-utility-card">
                <div class="apple-tagline" style="margin-bottom: 10px;">20-Second {exercise_choice.upper()} Protocol</div>
                <div class="apple-body" style="font-size: 15px; line-height: 1.6;">
                    • <strong>Goal:</strong> Complete maximum valid repetitions within 20 seconds.<br/>
                    • <strong>Key Form Criteria:</strong> Break 90° joint angle, maintain spinal alignment, rhythmic tempo.<br/>
                    • <strong>Adaptive Impact:</strong> Observed muscular output adjusts daily protein benchmark and macro targets.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 1. LIVE CONTINUOUS WEBCAM VIDEO STREAM
    if input_mode == "webcam":
        st.markdown('<div class="apple-section-title">Live Kinematic Video Feed & Push-up Analysis</div>', unsafe_allow_html=True)
        if not (CV2_AVAILABLE and MEDIAPIPE_AVAILABLE):
            st.warning("MediaPipe/OpenCV is not currently active in this Python environment. Please check your webcam and permissions.")
        else:
            st.markdown(
                """
                <div class="store-utility-card-subtle" style="margin-bottom: 18px;">
                    <div class="apple-body" style="font-size: 15px;">
                        💡 <strong>Real-Time Kinematic Tracking:</strong> Position your webcam to capture your full side profile. 
                        Click <strong>Start Live Workout</strong> to begin the 3-second countdown and 20-second active rep-counting test with overlay HUD.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            w_col1, w_col2, w_col3 = st.columns([1, 1, 1])
            with w_col1:
                test_duration = st.selectbox(
                    "Workout Duration",
                    options=[20, 30, 45, 60],
                    format_func=lambda x: f"{x} Seconds (Standard Assessment)" if x == 20 else f"{x} Seconds",
                    index=0,
                )
            with w_col2:
                camera_idx = st.number_input(
                    "Camera Index",
                    min_value=0,
                    max_value=3,
                    value=0,
                    step=1,
                    help="Default webcam is index 0. If you have an external USB camera, try 1.",
                )
            with w_col3:
                feed_target = st.selectbox(
                    "Display Target",
                    options=["browser_stream", "native_window"],
                    format_func=lambda x: "🖥️ Live In-Browser Video Feed" if x == "browser_stream" else "⚡ Native Window (Popout / High FPS)",
                )

            col_btn1, col_btn2 = st.columns([1, 1])
            start_live = col_btn1.button("🔴 Start Live Workout & Record", type="primary", use_container_width=True)
            stop_placeholder = col_btn2.empty()

            video_container = st.empty()
            hud_metrics = st.empty()

            if start_live:
                cap = cv2.VideoCapture(int(camera_idx))
                if not cap.isOpened():
                    st.error(f"❌ Could not access camera index #{camera_idx}. Ensure webcam is connected and not in use by another app.")
                else:
                    tracker = analyzer.get_tracker(exercise_choice)
                    tracker.reset()

                    # Phase 1: 3-Second Preparation Countdown
                    for cd in [3, 2, 1]:
                        t_end = time.time() + 1.0
                        while time.time() < t_end:
                            ret, frame = cap.read()
                            if not ret:
                                break
                            frame = cv2.flip(frame, 1)  # Mirror view
                            annotated_prep, _ = analyzer.analyze_frame(frame, exercise_choice)
                            annotated_prep = analyzer.detector.draw_hud_overlay(
                                annotated_prep,
                                exercise=exercise_choice,
                                state_info={"state": "PREPARING", "valid_reps": 0, "total_reps": 0, "feedback": "Get into pushup position!"},
                                elapsed_sec=0.0,
                                total_sec=float(test_duration),
                                countdown_num=cd,
                            )
                            annotated_rgb = cv2.cvtColor(annotated_prep, cv2.COLOR_BGR2RGB)
                            video_container.image(annotated_rgb, use_container_width=True)
                            time.sleep(0.03)

                    # Phase 2: Live Recording & Real-Time Computer Vision Analysis
                    start_time = time.time()
                    elapsed = 0.0

                    while elapsed < test_duration:
                        ret, frame = cap.read()
                        if not ret:
                            st.warning("Webcam stream interrupted.")
                            break

                        frame = cv2.flip(frame, 1)
                        elapsed = time.time() - start_time

                        annotated, state_info = analyzer.analyze_frame(frame, exercise_choice)
                        annotated_hud = analyzer.detector.draw_hud_overlay(
                            annotated,
                            exercise=exercise_choice,
                            state_info=state_info,
                            elapsed_sec=elapsed,
                            total_sec=float(test_duration),
                        )

                        if feed_target == "native_window":
                            cv2.imshow("FitFuel AI - Live Kinematic Tracker (Press 'q' to stop)", annotated_hud)
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                        else:
                            annotated_rgb = cv2.cvtColor(annotated_hud, cv2.COLOR_BGR2RGB)
                            video_container.image(annotated_rgb, use_container_width=True)

                        # Update live telemetry metrics
                        rem = max(0.0, test_duration - elapsed)
                        hud_metrics.markdown(
                            f"""
                            <div style="display:flex; gap:12px; margin-top:8px;">
                                <div class="metric-box" style="flex:1; border-left-color:#10b981;">
                                    <div class="metric-val">{state_info.get('valid_reps', 0)}</div>
                                    <div class="metric-label">Valid Reps</div>
                                </div>
                                <div class="metric-box" style="flex:1; border-left-color:#06b6d4;">
                                    <div class="metric-val">{state_info.get('total_reps', 0)}</div>
                                    <div class="metric-label">Total Attempts</div>
                                </div>
                                <div class="metric-box" style="flex:1; border-left-color:#f59e0b;">
                                    <div class="metric-val">{rem:.1f}s</div>
                                    <div class="metric-label">Time Remaining</div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        time.sleep(0.02)

                    # Release camera hardware
                    cap.release()
                    if feed_target == "native_window":
                        cv2.destroyAllWindows()

                    # Phase 3: Post-Workout Analytics & Database Sync
                    actual_duration = round(min(float(test_duration), elapsed), 1)
                    result = tracker.compute_summary_metrics(actual_duration)
                    db.save_exercise_session(result, user_id=1)
                    st.session_state["latest_exercise_result"] = result

                    st.balloons()
                    st.success(f"🎉 Live Workout Complete! Recorded {result.get('valid_repetitions')} valid reps in {actual_duration}s. Targets updated.")
                    _render_results_card(result)

            elif "latest_exercise_result" in st.session_state:
                _render_results_card(st.session_state["latest_exercise_result"])

    # 3. UPLOAD VIDEO MODE
    else:
        st.subheader("📁 Upload Workout Video File")
        uploaded_video = st.file_uploader(
            f"Upload MP4 / MOV / AVI video of your {exercise_choice} workout",
            type=["mp4", "mov", "avi"],
        )
        if uploaded_video:
            st.video(uploaded_video)
            if st.button("🚀 Analyze Uploaded Video", use_container_width=True, type="primary"):
                # Save uploaded file to temp file for OpenCV frame decoding
                suffix = os.path.splitext(uploaded_video.name)[-1] or ".mp4"
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
                    tmp_file.write(uploaded_video.read())
                    temp_video_path = tmp_file.name

                progress_bar = st.progress(0.0)
                status_text = st.empty()
                status_text.caption("Initializing video kinematic pipeline and loading pose model...")

                def update_progress(pct: float, total_reps: int, valid_reps: int) -> None:
                    progress_bar.progress(pct)
                    status_text.caption(
                        f"Analyzing video kinematics: {int(pct * 100)}% processed (Detected: {total_reps} total reps, {valid_reps} valid)"
                    )

                try:
                    with st.spinner("Processing video frames and computing repetition kinematics..."):
                        result = analyzer.analyze_video_file(
                            video_path=temp_video_path,
                            exercise_name=exercise_choice,
                            progress_callback=update_progress,
                        )

                    progress_bar.progress(1.0)
                    status_text.caption("Kinematic analysis completed!")

                    db.save_exercise_session(result, user_id=1)
                    st.session_state["latest_exercise_result"] = result
                    st.balloons()
                    st.success(
                        f"🎉 Video Analysis Complete! Detected {result.get('repetitions', 0)} total reps "
                        f"({result.get('valid_repetitions', 0)} valid reps) in {result.get('duration_sec', 0)}s."
                    )
                    _render_results_card(result)

                except Exception as e:
                    st.error(f"Error analyzing video: {str(e)}")
                finally:
                    if os.path.exists(temp_video_path):
                        try:
                            os.remove(temp_video_path)
                        except Exception:
                            pass

        elif "latest_exercise_result" in st.session_state:
            _render_results_card(st.session_state["latest_exercise_result"])


def _render_results_card(result: Dict[str, Any]) -> None:
    """Render structured metrics card conforming to DESIGN.md."""
    st.markdown("---")
    st.markdown('<div class="apple-section-title">Structured Exercise Performance Profile</div>', unsafe_allow_html=True)

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-val">{result.get('repetitions', 0)}</div>
                <div class="metric-label">Total Repetitions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-val">{result.get('valid_repetitions', 0)}</div>
                <div class="metric-label">Valid Repetitions</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-val">{result.get('tempo_sec_per_rep', 1.25):.2f}<span style="font-size:16px; font-weight:400; color:var(--color-body-muted);">s</span></div>
                <div class="metric-label">Avg Tempo / Rep</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with r4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-val">{int(result.get('form_consistency_score', 0.85) * 100)}%</div>
                <div class="metric-label">Form Quality</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="store-utility-card" style="margin-top: 20px;">
            <div class="apple-body" style="font-size: 15px; line-height: 1.6;">
                <strong>Biomechanical Profile:</strong> 
                Completed <strong>{result.get('valid_repetitions')} valid {result.get('exercise')} repetitions</strong> 
                at an average cadence of <strong>{result.get('tempo_sec_per_rep')} seconds per rep</strong>.
                Range of motion score: <strong>{result.get('range_of_motion_score')}</strong>.
                Form consistency rating: <strong>{result.get('form_consistency_score')}</strong>.
            </div>
            <div class="apple-fine-print" style="margin-top: 10px;">
                Note: This profile reflects exercise performance telemetry; it is not a clinical fitness diagnosis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Movement Skeleton Keyframe Gallery
    keyframes = result.get("annotated_keyframes", [])
    if keyframes:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(f"📸 Verified Movement Skeleton Keyframes ({len(keyframes)} captured)", expanded=True):
            cols = st.columns(len(keyframes))
            for i, kf in enumerate(keyframes):
                with cols[i]:
                    rgb_kf = cv2.cvtColor(kf, cv2.COLOR_BGR2RGB) if CV2_AVAILABLE else kf
                    st.image(rgb_kf, caption=f"Rep Phase #{i+1}", use_container_width=True)
