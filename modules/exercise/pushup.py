"""FitFuel AI Push-up Repetition and Form Tracker.

Fine-tuned biomechanical state machine with exponential smoothing,
depth percentage tracking, core alignment verification, and noise rejection.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

from .pose_detector import calculate_angle


class PushupTracker:
    """Fine-tuned state-machine push-up counter tracking repetitions, depth, and form consistency."""

    def __init__(
        self,
        down_threshold: float = 90.0,
        up_threshold: float = 145.0,
        hip_align_threshold: float = 140.0,
        smoothing_factor: float = 0.65,
    ) -> None:
        self.down_threshold = down_threshold
        self.up_threshold = up_threshold
        self.hip_align_threshold = hip_align_threshold
        self.alpha = smoothing_factor

        self.state = "UP"  # 'UP' or 'DOWN'
        self.total_reps = 0
        self.valid_reps = 0

        self.smoothed_elbow_angle: Optional[float] = None
        self.smoothed_hip_angle: Optional[float] = None
        self.last_rep_time: float = 0.0
        self.min_rep_interval_sec: float = 0.45

        self.rep_depths: List[float] = []
        self.rep_timestamps: List[float] = []
        self.hip_angles: List[float] = []
        self.feedback_msg = "Get into push-up position"

    def reset(self) -> None:
        """Reset counter state for a fresh test."""
        self.state = "UP"
        self.total_reps = 0
        self.valid_reps = 0
        self.smoothed_elbow_angle = None
        self.smoothed_hip_angle = None
        self.last_rep_time = 0.0
        self.rep_depths.clear()
        self.rep_timestamps.clear()
        self.hip_angles.clear()
        self.feedback_msg = "Ready to start"

    def update(
        self,
        landmarks: Dict[str, Tuple[float, float]],
        timestamp_sec: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Process extracted landmarks with exponential smoothing and form evaluation."""
        if not landmarks:
            return {
                "state": self.state,
                "total_reps": self.total_reps,
                "valid_reps": self.valid_reps,
                "elbow_angle": self.smoothed_elbow_angle or 0.0,
                "hip_angle": self.smoothed_hip_angle or 0.0,
                "depth_percentage": 0.0,
                "feedback": "Step into camera frame",
            }

        # Select side with highest visibility
        if "right_shoulder" in landmarks and "right_elbow" in landmarks and "right_wrist" in landmarks:
            raw_elbow = calculate_angle(landmarks["right_shoulder"], landmarks["right_elbow"], landmarks["right_wrist"])
            raw_hip = calculate_angle(landmarks["right_shoulder"], landmarks["right_hip"], landmarks["right_ankle"])
        elif "left_shoulder" in landmarks and "left_elbow" in landmarks and "left_wrist" in landmarks:
            raw_elbow = calculate_angle(landmarks["left_shoulder"], landmarks["left_elbow"], landmarks["left_wrist"])
            raw_hip = calculate_angle(landmarks["left_shoulder"], landmarks["left_hip"], landmarks["left_ankle"])
        else:
            return {
                "state": self.state,
                "total_reps": self.total_reps,
                "valid_reps": self.valid_reps,
                "elbow_angle": self.smoothed_elbow_angle or 0.0,
                "hip_angle": self.smoothed_hip_angle or 0.0,
                "depth_percentage": 0.0,
                "feedback": "Limbs not detected",
            }

        # Exponential moving average filter
        if self.smoothed_elbow_angle is None:
            self.smoothed_elbow_angle = raw_elbow
            self.smoothed_hip_angle = raw_hip
        else:
            self.smoothed_elbow_angle = round(self.alpha * raw_elbow + (1 - self.alpha) * self.smoothed_elbow_angle, 1)
            self.smoothed_hip_angle = round(self.alpha * raw_hip + (1 - self.alpha) * self.smoothed_hip_angle, 1)

        elbow_angle = self.smoothed_elbow_angle
        hip_angle = self.smoothed_hip_angle

        # Compute depth percentage (0% at lockout 150°, 100% at depth 90°)
        depth_pct = max(0.0, min(100.0, ((150.0 - elbow_angle) / (150.0 - self.down_threshold)) * 100.0))

        now = timestamp_sec if timestamp_sec is not None else time.time()
        form_cue = "Keep rhythmic cadence"

        # Biomechanical core check
        if hip_angle < 135.0:
            form_cue = "Keep hips elevated, engage core"
        elif hip_angle > 185.0:
            form_cue = "Don't pike your hips"

        # State transitions with hysteresis & cooldown
        if self.state == "UP":
            if elbow_angle <= self.down_threshold:
                self.state = "DOWN"
                form_cue = "Great depth! Drive up!"
            elif elbow_angle < 120.0:
                form_cue = "Go lower to break 90 degrees"
        elif self.state == "DOWN":
            if elbow_angle >= self.up_threshold:
                # Enforce minimum rep cooldown to reject sensor bounces
                if (now - self.last_rep_time) >= self.min_rep_interval_sec:
                    self.state = "UP"
                    self.total_reps += 1
                    self.last_rep_time = now
                    self.rep_depths.append(elbow_angle)
                    self.rep_timestamps.append(now)
                    self.hip_angles.append(hip_angle)

                    if hip_angle >= self.hip_align_threshold:
                        self.valid_reps += 1
                        form_cue = "Clean rep counted!"
                    else:
                        form_cue = "Sagging back: keep straight line"
                else:
                    self.state = "UP"

        self.feedback_msg = form_cue

        return {
            "state": self.state,
            "total_reps": self.total_reps,
            "valid_reps": self.valid_reps,
            "elbow_angle": elbow_angle,
            "hip_angle": hip_angle,
            "depth_percentage": round(depth_pct, 1),
            "feedback": form_cue,
        }

    def compute_summary_metrics(self, test_duration_sec: float = 20.0) -> Dict[str, Any]:
        """Compute structured post-workout metrics from completed test."""
        if len(self.rep_timestamps) > 1:
            intervals = [
                self.rep_timestamps[i] - self.rep_timestamps[i - 1]
                for i in range(1, len(self.rep_timestamps))
            ]
            avg_tempo = round(sum(intervals) / len(intervals), 2)
        elif self.valid_reps > 0:
            avg_tempo = round(test_duration_sec / max(self.valid_reps, 1), 2)
        else:
            avg_tempo = 0.0

        if self.total_reps > 0:
            valid_ratio = self.valid_reps / self.total_reps
            form_consistency = round(min(1.0, max(0.4, 0.35 + 0.65 * valid_ratio)), 2)
            rom_score = round(min(1.0, max(0.5, 0.55 + 0.45 * (self.valid_reps / max(self.total_reps, 1)))), 2)
        else:
            form_consistency = 0.0
            rom_score = 0.0

        if self.valid_reps >= 15:
            intensity = "high"
        elif self.valid_reps >= 8:
            intensity = "moderate"
        else:
            intensity = "low"

        return {
            "exercise": "pushup",
            "duration_sec": test_duration_sec,
            "repetitions": self.total_reps,
            "valid_repetitions": self.valid_reps,
            "tempo_sec_per_rep": avg_tempo,
            "range_of_motion_score": rom_score,
            "form_consistency_score": form_consistency,
            "intensity_tier": intensity,
        }
