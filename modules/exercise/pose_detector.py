"""FitFuel AI Pose Detector.

Wraps MediaPipe Pose for robust joint angle calculation and landmark tracking,
with zero-crash fallback for environments where CV libraries are missing.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# Safe import of OpenCV and MediaPipe
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except (ImportError, AttributeError):
    MEDIAPIPE_AVAILABLE = False


def calculate_angle(
    a: Tuple[float, float],
    b: Tuple[float, float],
    c: Tuple[float, float],
) -> float:
    """Calculate the interior angle (in degrees) at vertex b between segments ba and bc.

    Args:
        a: Coordinates of first point (x, y).
        b: Coordinates of vertex point (x, y).
        c: Coordinates of third point (x, y).

    Returns:
        Angle in degrees between 0.0 and 180.0.
    """
    radians = math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return round(angle, 1)


class PoseDetector:
    """Wraps MediaPipe Pose solution with landmark normalization and angle calculations."""

    def __init__(
        self,
        min_detection_confidence: float = 0.6,
        min_tracking_confidence: float = 0.6,
    ) -> None:
        self.is_available = CV2_AVAILABLE and MEDIAPIPE_AVAILABLE
        self.pose = None

        if self.is_available:
            try:
                self.mp_pose = mp.solutions.pose
                self.mp_drawing = mp.solutions.drawing_utils
                self.pose = self.mp_pose.Pose(
                    min_detection_confidence=min_detection_confidence,
                    min_tracking_confidence=min_tracking_confidence,
                    model_complexity=1,
                )
            except Exception:
                self.is_available = False

    def process_frame(self, frame: np.ndarray) -> Tuple[Optional[Any], Optional[Dict[str, Tuple[float, float]]]]:
        """Extract landmarks from a single BGR or RGB video frame.

        Args:
            frame: OpenCV image matrix.

        Returns:
            Tuple of (raw_results, landmarks_dict).
        """
        if not self.is_available or self.pose is None or frame is None:
            return None, None

        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if CV2_AVAILABLE else frame
        results = self.pose.process(rgb_frame)

        if not results.pose_landmarks:
            return results, None

        landmarks = results.pose_landmarks.landmark
        lm_map = {
            "nose": (landmarks[0].x, landmarks[0].y),
            "left_shoulder": (landmarks[11].x, landmarks[11].y),
            "right_shoulder": (landmarks[12].x, landmarks[12].y),
            "left_elbow": (landmarks[13].x, landmarks[13].y),
            "right_elbow": (landmarks[14].x, landmarks[14].y),
            "left_wrist": (landmarks[15].x, landmarks[15].y),
            "right_wrist": (landmarks[16].x, landmarks[16].y),
            "left_hip": (landmarks[23].x, landmarks[23].y),
            "right_hip": (landmarks[24].x, landmarks[24].y),
            "left_knee": (landmarks[25].x, landmarks[25].y),
            "right_knee": (landmarks[26].x, landmarks[26].y),
            "left_ankle": (landmarks[27].x, landmarks[27].y),
            "right_ankle": (landmarks[28].x, landmarks[28].y),
        }
        return results, lm_map

    def draw_skeleton(self, frame: np.ndarray, results: Any) -> np.ndarray:
        """Render pose landmarks and connections directly onto frame."""
        if not self.is_available or results is None or not results.pose_landmarks or not CV2_AVAILABLE:
            return frame

        annotated = frame.copy()
        self.mp_drawing.draw_landmarks(
            annotated,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(color=(0, 255, 128), thickness=2, circle_radius=3),
            self.mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
        )
        return annotated

    def draw_hud_overlay(
        self,
        frame: np.ndarray,
        exercise: str,
        state_info: Dict[str, Any],
        elapsed_sec: float,
        total_sec: float = 20.0,
        countdown_num: Optional[Union[int, str]] = None,
    ) -> np.ndarray:
        """Render transparent AR HUD metrics overlay on live camera video feed."""
        if not CV2_AVAILABLE or frame is None:
            return frame

        canvas = frame.copy()
        h, w = canvas.shape[:2]

        # 1. Top HUD bar
        overlay = canvas.copy()
        cv2.rectangle(overlay, (0, 0), (w, 85), (15, 23, 42), -1)  # Deep slate #0f172a
        cv2.addWeighted(overlay, 0.75, canvas, 0.25, 0, canvas)

        # Bottom accent border on HUD bar
        cv2.line(canvas, (0, 85), (w, 85), (16, 185, 129), 2)  # Emerald green line

        # Rep count (Large green)
        valid_reps = state_info.get("valid_reps", 0)
        total_reps = state_info.get("total_reps", 0)
        state = state_info.get("state", "READY")
        feedback = state_info.get("feedback", "Get into position")
        angle = state_info.get("elbow_angle", state_info.get("knee_angle", state_info.get("trunk_angle", 0.0)))

        cv2.putText(canvas, f"REPS: {valid_reps}", (18, 42), cv2.FONT_HERSHEY_DUPLEX, 1.1, (0, 255, 128), 2)
        cv2.putText(canvas, f"(Total: {total_reps})", (18, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (160, 180, 200), 1)

        # Exercise & State
        state_color = (0, 240, 255) if state == "DOWN" else (0, 255, 128)
        cv2.putText(canvas, f"{exercise.upper()} | {state}", (w // 2 - 90, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.75, state_color, 2)
        if angle > 0:
            cv2.putText(canvas, f"Joint Angle: {angle:.0f} deg", (w // 2 - 80, 68), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 220, 240), 1)

        # Timer countdown
        rem_sec = max(0.0, total_sec - elapsed_sec)
        cv2.putText(canvas, f"TIME: {rem_sec:.1f}s", (w - 180, 36), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2)
        progress_width = int((elapsed_sec / max(1.0, total_sec)) * 160)
        cv2.rectangle(canvas, (w - 180, 50), (w - 20, 62), (40, 50, 65), -1)
        cv2.rectangle(canvas, (w - 180, 50), (w - 180 + progress_width, 62), (16, 185, 129), -1)

        # Coach coaching banner at bottom
        cv2.rectangle(canvas, (10, h - 45), (w - 10, h - 10), (15, 23, 42), -1)
        cv2.rectangle(canvas, (10, h - 45), (w - 10, h - 10), (6, 182, 212), 1)
        cv2.putText(canvas, f"COACH: {feedback}", (25, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

        # Countdown overlay if active
        if countdown_num is not None:
            overlay_cd = canvas.copy()
            center_x, center_y = w // 2, h // 2
            cv2.circle(overlay_cd, (center_x, center_y), 110, (15, 23, 42), -1)
            cv2.addWeighted(overlay_cd, 0.7, canvas, 0.3, 0, canvas)
            cv2.circle(canvas, (center_x, center_y), 110, (16, 185, 129), 4)

            cd_str = str(countdown_num)
            font_scale = 3.2 if len(cd_str) <= 2 else 1.6
            thickness = 6 if len(cd_str) <= 2 else 3
            text_size = cv2.getTextSize(cd_str, cv2.FONT_HERSHEY_DUPLEX, font_scale, thickness)[0]
            text_x = center_x - text_size[0] // 2
            text_y = center_y + text_size[1] // 2
            cv2.putText(canvas, cd_str, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, font_scale, (0, 255, 128), thickness)

        return canvas

    def create_synthetic_frame(
        self,
        exercise: str,
        phase: float,
        rep_count: int,
        elapsed_sec: float,
        width: int = 640,
        height: int = 480,
    ) -> np.ndarray:
        """Generate a synthetic pose visualization for offline testing.

        Args:
            exercise: 'pushup', 'situp', or 'squat'.
            phase: Oscillation cycle between 0.0 (top) and 1.0 (bottom).
            rep_count: Current repetition count.
            elapsed_sec: Elapsed duration.
            width: Image width.
            height: Image height.

        Returns:
            RGB numpy image with visual skeleton and HUD metrics.
        """
        # Dark modern UI canvas
        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        canvas[:] = (18, 22, 28)  # Deep slate background

        if CV2_AVAILABLE:
            # Draw subtle grid
            for y in range(40, height, 40):
                cv2.line(canvas, (0, y), (width, y), (28, 34, 44), 1)
            for x in range(40, width, 40):
                cv2.line(canvas, (x, 0), (x, height), (28, 34, 44), 1)

            # Ground line
            cv2.line(canvas, (40, 420), (600, 420), (50, 60, 75), 2)

            # Render exercise stick-figure avatar based on phase
            if exercise == "pushup":
                # Pushup side profile: head, shoulder, elbow, wrist, hip, knee, ankle
                # phase: 0 = UP (straight arms), 1 = DOWN (chest near ground)
                shoulder_y = int(320 + phase * 60)
                elbow_y = int(350 + phase * 40)
                elbow_x = int(240 - phase * 20)
                wrist = (220, 415)
                shoulder = (260, shoulder_y)
                elbow = (elbow_x, elbow_y)
                hip = (380, shoulder_y + 10)
                ankle = (520, 415)
                head = (230, shoulder_y - 20)

                # Connect limbs
                cv2.line(canvas, shoulder, elbow, (0, 230, 150), 4)
                cv2.line(canvas, elbow, wrist, (0, 230, 150), 4)
                cv2.line(canvas, shoulder, hip, (0, 200, 255), 4)
                cv2.line(canvas, hip, ankle, (0, 200, 255), 4)
                cv2.circle(canvas, head, 14, (240, 240, 255), -1)
                for pt in [shoulder, elbow, wrist, hip, ankle]:
                    cv2.circle(canvas, pt, 6, (255, 255, 255), -1)

            elif exercise == "squat":
                # Squat profile: standing vs deep squat
                hip_y = int(260 + phase * 90)
                knee_y = int(330 + phase * 20)
                hip = (320, hip_y)
                shoulder = (320, hip_y - 80)
                head = (320, hip_y - 110)
                knee = (360, knee_y)
                ankle = (330, 415)

                cv2.line(canvas, shoulder, hip, (0, 200, 255), 4)
                cv2.line(canvas, hip, knee, (0, 230, 150), 4)
                cv2.line(canvas, knee, ankle, (0, 230, 150), 4)
                cv2.circle(canvas, head, 16, (240, 240, 255), -1)
                for pt in [shoulder, hip, knee, ankle]:
                    cv2.circle(canvas, pt, 6, (255, 255, 255), -1)
            else:
                # Default situp
                torso_angle = phase * 60
                hip = (320, 400)
                cv2.circle(canvas, hip, 8, (255, 255, 255), -1)

            # HUD Display Overlays
            cv2.rectangle(canvas, (20, 20), (280, 110), (30, 38, 50), -1)
            cv2.rectangle(canvas, (20, 20), (280, 110), (0, 200, 255), 1)

            cv2.putText(
                canvas,
                f"EXERCISE: {exercise.upper()}",
                (35, 48),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (200, 220, 255),
                1,
            )
            cv2.putText(
                canvas,
                f"REPS: {rep_count}",
                (35, 78),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 128),
                2,
            )
            cv2.putText(
                canvas,
                f"TIME: {elapsed_sec:.1f}s / 20.0s",
                (35, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (180, 190, 200),
                1,
            )

            status_text = "DOWN" if phase > 0.6 else "UP"
            cv2.putText(
                canvas,
                f"STATE: {status_text}",
                (440, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 200, 255),
                2,
            )

        return canvas
