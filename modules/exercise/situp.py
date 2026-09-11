"""FitFuel AI Sit-up Repetition Tracker.

Biomechanical tracking of trunk flexion using shoulder-hip-knee angles.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

from .pose_detector import calculate_angle


class SitupTracker:
    """Fine-tuned state-machine sit-up tracker with exponential smoothing,
    trunk angle assessment, depth percentage tracking, and noise rejection.
    """

    def __init__(
        self,
        down_angle_threshold: float = 135.0,
        up_angle_threshold: float = 75.0,
        smoothing_factor: float = 0.65,
        **kwargs: Any,
    ) -> None:
        self.down_threshold = kwargs.get("down_threshold", down_angle_threshold)
        self.up_threshold = kwargs.get("up_threshold", up_angle_threshold)
        self.alpha = kwargs.get("smoothing_factor", smoothing_factor)

        self.state = "DOWN"
        self.total_reps = 0
        self.valid_reps = 0

        self.smoothed_trunk_angle: Optional[float] = None
        self.last_rep_time: float = 0.0
        self.min_rep_interval_sec: float = 0.55

        self.rep_depths: List[float] = []
        self.rep_timestamps: List[float] = []
        self.feedback_msg = "Lie flat on the mat with knees bent"

    def reset(self) -> None:
        """Reset counter state for a fresh test."""
        self.state = "DOWN"
        self.total_reps = 0
        self.valid_reps = 0
        self.smoothed_trunk_angle = None
        self.last_rep_time = 0.0
        self.rep_depths.clear()
        self.rep_timestamps.clear()
        self.feedback_msg = "Ready to start"

    def update(
        self,
        landmarks: Dict[str, Tuple[float, float]],
        timestamp_sec: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Process extracted landmarks with EMA smoothing and biomechanical cues."""
        if not landmarks:
            return {
                "state": self.state,
                "total_reps": self.total_reps,
                "valid_reps": self.valid_reps,
                "trunk_angle": self.smoothed_trunk_angle or 0.0,
                "depth_percentage": 0.0,
                "feedback": "Step into camera frame",
            }

        # Measure shoulder-hip-knee angle
        if "right_shoulder" in landmarks and "right_hip" in landmarks and "right_knee" in landmarks:
            raw_trunk = calculate_angle(
                landmarks["right_shoulder"],
                landmarks["right_hip"],
                landmarks["right_knee"],
            )
        elif "left_shoulder" in landmarks and "left_hip" in landmarks and "left_knee" in landmarks:
            raw_trunk = calculate_angle(
                landmarks["left_shoulder"],
                landmarks["left_hip"],
                landmarks["left_knee"],
            )
        else:
            return {
                "state": self.state,
                "total_reps": self.total_reps,
                "valid_reps": self.valid_reps,
                "trunk_angle": self.smoothed_trunk_angle or 0.0,
                "depth_percentage": 0.0,
                "feedback": "Torso and knees not visible",
            }

        # Exponential moving average filter
        if self.smoothed_trunk_angle is None:
            self.smoothed_trunk_angle = raw_trunk
        else:
            self.smoothed_trunk_angle = round(
                self.alpha * raw_trunk + (1 - self.alpha) * self.smoothed_trunk_angle, 1
            )

        trunk_angle = self.smoothed_trunk_angle

        # Depth percentage: 0% when lying down (down_threshold ~135°), 100% when curled up (up_threshold ~75°)
        depth_range = max(10.0, self.down_threshold - self.up_threshold)
        depth_pct = max(0.0, min(100.0, ((self.down_threshold - trunk_angle) / depth_range) * 100.0))

        feedback = "Keep rhythmic cadence"
        now = timestamp_sec if timestamp_sec is not None else time.time()

        if self.state == "DOWN":
            if trunk_angle <= self.up_threshold:
                if (now - self.last_rep_time) >= self.min_rep_interval_sec:
                    self.state = "UP"
                    self.total_reps += 1
                    self.valid_reps += 1
                    self.last_rep_time = now
                    self.rep_depths.append(trunk_angle)
                    self.rep_timestamps.append(now)
                    feedback = "Rep counted! Controlled descent"
                else:
                    self.state = "UP"
            elif trunk_angle < 105.0:
                feedback = "Curl up further to chest height"
        elif self.state == "UP":
            if trunk_angle >= self.down_threshold:
                self.state = "DOWN"
                feedback = "Shoulders touched mat, drive back up"
            elif trunk_angle > 105.0:
                feedback = "Control the negative descent"

        self.feedback_msg = feedback

        return {
            "state": self.state,
            "total_reps": self.total_reps,
            "valid_reps": self.valid_reps,
            "trunk_angle": trunk_angle,
            "depth_percentage": round(depth_pct, 1),
            "feedback": feedback,
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
            form_consistency = round(min(1.0, max(0.4, 0.40 + 0.60 * valid_ratio)), 2)
            rom_score = round(min(1.0, max(0.5, 0.55 + 0.45 * valid_ratio)), 2)
        else:
            form_consistency = 0.0
            rom_score = 0.0

        intensity = "high" if self.valid_reps >= 14 else ("moderate" if self.valid_reps >= 7 else "low")
        return {
            "exercise": "situp",
            "duration_sec": test_duration_sec,
            "repetitions": self.total_reps,
            "valid_repetitions": self.valid_reps,
            "tempo_sec_per_rep": avg_tempo,
            "range_of_motion_score": rom_score,
            "form_consistency_score": form_consistency,
            "intensity_tier": intensity,
        }
