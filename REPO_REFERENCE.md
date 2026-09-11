# FitFuel AI — Repository Reference

## Primary repositories

### 1. GC_Fit — exercise repetition tracking
https://github.com/TheUnknown550/GC_Fit

Purpose:
- MediaPipe Pose
- OpenCV
- push-up counting
- sit-up counting
- squat counting
- real-time webcam

Repository README describes it as a lightweight privacy-first rep counter and lists an MIT license.

### 2. Food-Image-Recognition — food photo classification
https://github.com/MaharshSuryawala/Food-Image-Recognition

Purpose:
- food image classification
- Food-101
- Inception-v3 transfer learning
- nutrition information pipeline
- FoodData Central source

Repository README lists MIT license.

Important:
- Food-101 is not a comprehensive Indian-food model.
- Do not claim exact portion or nutrition from the image.
- Use user confirmation fallback.

### 3. NutriMind — nutrition recommendation architecture
https://github.com/zakaria-narjis/nutrimind

Purpose:
- FastAPI
- Streamlit
- scikit-learn
- BMI/BMR/TDEE
- content-based food recommendation
- cosine similarity
- nearest neighbors
- large recipe dataset

Use this mainly as an architectural/reference source.

### 4. Food Semantic Segmentation and Classification
https://github.com/Restok/Food-Semantic-Segmentation-and-Classification

Purpose:
- FoodSeg103
- Nutrition5K
- food segmentation
- food classification
- portion-estimation research direction

Use only as an advanced/future reference for the 12-hour MVP.

## Useful GitHub topic pages

Exercise recognition:
https://github.com/topics/exercise-recognition

Food classification:
https://github.com/topics/food-classification

Nutrition information:
https://github.com/topics/nutrition-information

## Integration strategy

DO NOT merge all repositories wholesale.

Recommended:
GC_Fit → adapt exercise logic into modules/exercise/
Food-Image-Recognition → adapt classifier/nutrition lookup ideas into modules/food/
NutriMind → adapt recommendation/nutrition target architecture into modules/recommendation/
Your own code → profile, safety, integration, explainability, feedback, UI, demo mode.

## Licensing

Always inspect the repository LICENSE file before redistributing code or models. Keep required copyright/license notices where applicable.

## Research/technical caveats

- Exercise repetition counts can be affected by camera angle, lighting, occlusion and clothing.
- A 20-second push-up test is not a clinical measure of overall fitness.
- BMI is calculated from height and weight, not reliably from a photograph.
- Food image recognition is uncertain for mixed dishes.
- Portion estimation from a single 2D image is approximate.
- Protein absorption cannot be inferred from exercise performance.
- Nutrition recommendations should be framed as general wellness guidance unless validated clinically.

## Suggested architecture

Streamlit
↓
Python application modules
↓
MediaPipe/OpenCV + food classifier
↓
Feature engineering
↓
Nutrition target engine
↓
Recommendation engine
↓
SQLite/CSV
↓
Dashboard
