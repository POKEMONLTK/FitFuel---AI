"""Unit tests for FitFuel AI Food Recognition and Plate Vision."""

import io
import unittest
import numpy as np
from PIL import Image

from modules.food.food_detector import FoodDetector


class TestFoodDetector(unittest.TestCase):
    """Test suite for neural vision and texture-gated plate detection."""

    def setUp(self):
        self.detector = FoodDetector()

    def test_classifier_loaded(self):
        """Ensure MediaPipe classifier is loaded if model file exists."""
        self.assertIsNotNone(self.detector.classifier)

    def test_blank_white_plate_zero_fabrication(self):
        """A blank smooth white plate must NOT fabricate white rice or default meals."""
        white_plate = Image.fromarray(np.full((256, 256, 3), 245, dtype=np.uint8))
        res = self.detector.detect_foods(white_plate)
        self.assertEqual(res["foods"], [])
        self.assertEqual(res["confidence_score"], 0.0)
        self.assertTrue(res["requires_user_confirmation"])

    def test_dark_empty_image(self):
        """Dark empty photos must return 0 foods with an informative message."""
        dark_img = Image.fromarray(np.full((256, 256, 3), 15, dtype=np.uint8))
        res = self.detector.detect_foods(dark_img)
        self.assertEqual(res["foods"], [])
        self.assertIn("No distinct food items", res["status_message"])

    def test_invalid_input_handling(self):
        """Corrupted or invalid input bytes must not crash the detector."""
        res = self.detector.detect_foods(b"corrupted_bytes_here")
        self.assertEqual(res["foods"], [])
        self.assertTrue(res["requires_user_confirmation"])

    def test_pil_image_input(self):
        """Valid PIL images must process cleanly."""
        img = Image.new("RGB", (200, 200), color="green")
        res = self.detector.detect_foods(img)
        self.assertIsInstance(res["foods"], list)
        self.assertIn("confidence_score", res)
        self.assertIn("status_message", res)

    def test_zero_fabrication_policy(self):
        """Never return hardcoded 4 dishes (White Rice, Dal, Roti, Sabzi) blindly."""
        grey_img = Image.fromarray(np.full((256, 256, 3), 128, dtype=np.uint8))
        res = self.detector.detect_foods(grey_img)
        self.assertNotIn("White Rice (Cooked)", [f["name"] for f in res["foods"]])

    def test_paneer_curry_detection(self):
        """A paneer makhani / butter masala dish in a handi must be detected accurately."""
        from pathlib import Path
        test_img = Path("scratch_user_dish.png")
        if test_img.exists():
            res = self.detector.detect_foods(test_img)
            self.assertEqual(len(res["foods"]), 1)
            self.assertEqual(res["foods"][0]["name"], "Paneer Butter Masala (Paneer Makhani)")
            self.assertGreaterEqual(res["foods"][0]["confidence"], 0.90)


if __name__ == "__main__":
    unittest.main()
