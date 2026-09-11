"""FitFuel AI Exercise Analyzer.

Orchestrates 20-second movement assessments with live webcam processing
and video file analysis.
"""

from __future__ import annotations

import math
import time
from typing import Any, Callable, Dict, Generator, Optional, Tuple

import numpy as np

from .pose_detector import PoseDetector
from .pushup import PushupTracker
from .situp import SitupTracker
from .squat import SquatTracker


class ExerciseAnalyzer:
    """Master controller for fitness scans and repetition assessment."""

    def __init__(self) -> None:
        self.detector = PoseDetector()
        self.pushup_tracker = PushupTracker()
        self.situp_tracker = SitupTracker()
        self.squat_tracker = SquatTracker()

    def get_tracker(self, exercise_name: str) -> Any:
        """Return dedicated kinematic tracker for exercise."""
        name = exercise_name.lower()
        if name == "pushup":
            return self.pushup_tracker
        elif name == "situp":
            return self.situp_tracker
        elif name == "squat":
            return self.squat_tracker
        return self.pushup_tracker

    def analyze_frame(
        self,
        frame: np.ndarray,
        exercise_name: str,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process a single frame from webcam or video file.

        Args:
            frame: BGR image frame.
            exercise_name: 'pushup', 'situp', or 'squat'.

        Returns:
            Tuple of (annotated_frame, tracker_state_dict).
        """
        tracker = self.get_tracker(exercise_name)

        if not self.detector.is_available or frame is None:
            return frame, {
                "state": "IDLE",
                "total_reps": tracker.total_reps,
                "valid_reps": tracker.valid_reps,
                "feedback": "Computer Vision module unavailable. Please check camera access.",
            }

        results, landmarks = self.detector.process_frame(frame)
        annotated_frame = self.detector.draw_skeleton(frame, results)

        if landmarks:
            state_info = tracker.update(landmarks)
        else:
            state_info = {
                "state": tracker.state,
                "total_reps": tracker.total_reps,
                "valid_reps": tracker.valid_reps,
                "feedback": "Step into camera frame",
            }

        return annotated_frame, state_info

    def analyze_video_file(
        self,
        video_path: str,
        exercise_name: str,
        progress_callback: Optional[Callable[[float, int, int], None]] = None,
    ) -> Dict[str, Any]:
        """Process an uploaded workout video file and return real repetition kinematics.

        Args:
            video_path: Absolute or relative path to MP4/MOV/AVI video file.
            exercise_name: 'pushup', 'situp', or 'squat'.
            progress_callback: Optional callback(fraction_completed, total_reps, valid_reps).

        Returns:
            Dictionary containing structured biomechanical summary metrics and sample keyframes.
        """
        import cv2

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {
                "exercise": exercise_name,
                "duration_sec": 0.0,
                "repetitions": 0,
                "valid_repetitions": 0,
                "tempo_sec_per_rep": 0.0,
                "range_of_motion_score": 0.0,
                "form_consistency_score": 0.0,
                "intensity_tier": "low",
                "annotated_keyframes": [],
                "error": "Could not open video file.",
            }

        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0 or math.isnan(fps):
            fps = 30.0

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            total_frames = 300
        duration_sec = round(total_frames / fps, 2)

        tracker = self.get_tracker(exercise_name)
        tracker.reset()

        # Step calculation: sample at ~20-25 FPS for optimal speed and accuracy
        step = max(1, int(round(fps / 20.0)))

        frame_idx = 0
        analyzed_frames = 0
        annotated_keyframes: List[np.ndarray] = []
        last_saved_rep = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            frame_idx += 1
            if frame_idx % step != 0:
                continue

            analyzed_frames += 1
            current_time_sec = round(frame_idx / fps, 3)

            results, landmarks = self.detector.process_frame(frame)
            if landmarks:
                state_info = tracker.update(landmarks, timestamp_sec=current_time_sec)

                # Capture an annotated keyframe on rep inflection or when rep count increments
                if tracker.valid_reps > last_saved_rep and len(annotated_keyframes) < 4:
                    annotated = self.detector.draw_skeleton(frame.copy(), results)
                    annotated_keyframes.append(annotated)
                    last_saved_rep = tracker.valid_reps

            if progress_callback:
                progress_fraction = min(1.0, frame_idx / max(total_frames, 1))
                progress_callback(progress_fraction, tracker.total_reps, tracker.valid_reps)

        cap.release()

        # If no keyframe was captured during reps, grab at least 1 frame with skeleton if possible
        if not annotated_keyframes and self.detector.is_available:
            cap2 = cv2.VideoCapture(video_path)
            ret, frame = cap2.read()
            if ret and frame is not None:
                res, lm = self.detector.process_frame(frame)
                annotated_keyframes.append(self.detector.draw_skeleton(frame, res))
            cap2.release()

        summary = tracker.compute_summary_metrics(test_duration_sec=duration_sec)
        summary["annotated_keyframes"] = annotated_keyframes
        summary["total_frames_analyzed"] = analyzed_frames
        summary["video_fps"] = round(fps, 1)

        return summary
