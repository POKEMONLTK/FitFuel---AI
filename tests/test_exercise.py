"""Unit tests for FitFuel AI exercise kinematics and state machine trackers."""

import unittest
from modules.exercise.pushup import PushupTracker
from modules.exercise.squat import SquatTracker
from modules.exercise.situp import SitupTracker


class TestExerciseTrackers(unittest.TestCase):
    """Test suite for biomechanical exercise trackers."""

    def test_pushup_tracker_rep_count(self):
        tracker = PushupTracker(down_threshold=90.0, up_threshold=145.0)
        tracker.reset()

        # Up position: shoulder (0.5, 0.2), elbow (0.5, 0.4), wrist (0.5, 0.6) -> 180 degrees
        # Hip straight: shoulder (0.5, 0.2), hip (0.5, 0.5), ankle (0.5, 0.8) -> 180 degrees
        up_landmarks = {
            "right_shoulder": (0.5, 0.2),
            "right_elbow": (0.5, 0.4),
            "right_wrist": (0.5, 0.6),
            "right_hip": (0.5, 0.5),
            "right_ankle": (0.5, 0.8),
        }

        # Down position: elbow angle ~70 degrees (elbow flexed past 90)
        down_landmarks = {
            "right_shoulder": (0.5, 0.2),
            "right_elbow": (0.5, 0.4),
            "right_wrist": (0.6, 0.35),
            "right_hip": (0.5, 0.5),
            "right_ankle": (0.5, 0.8),
        }

        # Initialize in UP
        res1 = tracker.update(up_landmarks)
        self.assertEqual(res1["state"], "UP")
        self.assertEqual(res1["total_reps"], 0)

        # Move to DOWN (run enough frames to converge through EMA)
        for _ in range(8):
            res2 = tracker.update(down_landmarks)
        self.assertEqual(res2["state"], "DOWN")

        # Move back to UP
        for _ in range(8):
            res3 = tracker.update(up_landmarks)
        self.assertEqual(res3["state"], "UP")
        self.assertEqual(res3["total_reps"], 1)
        self.assertEqual(res3["valid_reps"], 1)

        metrics = tracker.compute_summary_metrics(20.0)
        self.assertEqual(metrics["repetitions"], 1)
        self.assertEqual(metrics["exercise"], "pushup")

    def test_squat_tracker_rep_count(self):
        tracker = SquatTracker(down_threshold=100.0, up_threshold=155.0)
        tracker.reset()

        # Standing: hip (0.5, 0.3), knee (0.5, 0.6), ankle (0.5, 0.9) -> 180 degrees
        standing_landmarks = {
            "right_hip": (0.5, 0.3),
            "right_knee": (0.5, 0.6),
            "right_ankle": (0.5, 0.9),
            "right_shoulder": (0.5, 0.1),
        }

        # Squat down: knee angle ~90 degrees
        squat_landmarks = {
            "right_hip": (0.5, 0.6),
            "right_knee": (0.5, 0.6),
            "right_ankle": (0.5, 0.9),
            "right_shoulder": (0.5, 0.4),
        }

        # Initialize standing
        res1 = tracker.update(standing_landmarks)
        self.assertEqual(res1["state"], "UP")

        # Squat down
        for _ in range(5):
            res2 = tracker.update(squat_landmarks)
        self.assertEqual(res2["state"], "DOWN")

        # Stand back up
        for _ in range(5):
            res3 = tracker.update(standing_landmarks)
        self.assertEqual(res3["state"], "UP")
        self.assertEqual(res3["total_reps"], 1)
        self.assertEqual(res3["valid_reps"], 1)

        metrics = tracker.compute_summary_metrics(20.0)
        self.assertEqual(metrics["exercise"], "squat")
        self.assertEqual(metrics["repetitions"], 1)

    def test_situp_tracker_rep_count(self):
        tracker = SitupTracker(down_angle_threshold=135.0, up_angle_threshold=75.0)
        tracker.reset()

        # Lie flat: shoulder (0.2, 0.8), hip (0.5, 0.8), knee (0.8, 0.8) -> 180 deg
        down_landmarks = {
            "right_shoulder": (0.2, 0.8),
            "right_hip": (0.5, 0.8),
            "right_knee": (0.8, 0.8),
        }

        # Curled up: shoulder (0.5, 0.5), hip (0.5, 0.8), knee (0.8, 0.8) -> ~90 deg
        # for a tighter curl < 75 deg:
        up_landmarks = {
            "right_shoulder": (0.6, 0.5),
            "right_hip": (0.5, 0.8),
            "right_knee": (0.8, 0.8),
        }

        # Initialize flat
        res1 = tracker.update(down_landmarks)
        self.assertEqual(res1["state"], "DOWN")

        # Curl up
        for _ in range(6):
            res2 = tracker.update(up_landmarks)
        self.assertEqual(res2["state"], "UP")
        self.assertEqual(res2["total_reps"], 1)

        # Lie back down
        for _ in range(6):
            res3 = tracker.update(down_landmarks)
        self.assertEqual(res3["state"], "DOWN")

        metrics = tracker.compute_summary_metrics(20.0)
        self.assertEqual(metrics["exercise"], "situp")
        self.assertEqual(metrics["repetitions"], 1)

    def test_analyze_video_file_pipeline(self):
        import cv2
        import numpy as np
        import tempfile
        import os
        from modules.exercise.exercise_analyzer import ExerciseAnalyzer

        analyzer = ExerciseAnalyzer()

        # Test corrupt or missing file
        err_res = analyzer.analyze_video_file("non_existent_path.mp4", "pushup")
        self.assertEqual(err_res["repetitions"], 0)
        self.assertIn("error", err_res)

        # Create a valid 1-second 30fps video
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
            temp_path = f.name

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(temp_path, fourcc, 30.0, (160, 120))
        for _ in range(30):
            frame = np.zeros((120, 160, 3), dtype=np.uint8)
            out.write(frame)
        out.release()

        try:
            res = analyzer.analyze_video_file(temp_path, "pushup")
            self.assertEqual(res["exercise"], "pushup")
            self.assertEqual(res["duration_sec"], 1.0)
            self.assertIn("repetitions", res)
            self.assertIn("valid_repetitions", res)
            self.assertIn("tempo_sec_per_rep", res)
            self.assertIn("form_consistency_score", res)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()
