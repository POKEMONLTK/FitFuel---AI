# FitFuel AI — Pretrained Models Directory

This directory stores offline pretrained models or caching artifacts if downloaded.

## Integrated Architecture
1. **Pose Estimation**:
   - MediaPipe Pose (`mediapipe.solutions.pose`) runs locally without external server dependencies.
   - Fallback simulation runs if MediaPipe is unavailable or camera is disconnected.

2. **Food Image Recognition**:
   - Local feature/heuristic food classifier trained on common dishes and Indian food dataset.
   - Built-in human-in-the-loop confirmation guarantees 100% reliable workflow even when visual ambiguity occurs.
   - Optional external models (e.g., Food-101 Inception-v3 / MobileNet) can be placed here (`models/food_classifier.h5` or `.onnx`).
