# FitFuel AI — Complete Project Context

## 1. Project name
FitFuel AI

## 2. One-line concept
An AI-powered adaptive nutrition prototype that combines user body information, computer-vision exercise performance, and meal-photo analysis to personalize nutrition recommendations.

## 3. Hackathon objective
Build a working prototype in approximately 12 hours that demonstrates an end-to-end pipeline:

User profile
→ exercise video analysis
→ exercise performance metrics
→ meal photo analysis
→ nutrition estimation
→ personalized recommendation
→ explanation
→ feedback/adaptation.

This is a prototype/decision-support application, NOT a medical diagnostic or treatment system.

## 4. Core product statement
"From Movement to Nutrition."

Instead of relying only on self-reported activity, FitFuel AI observes simple bodyweight exercise performance and combines it with anthropometric data, dietary behavior, preferences, and goals to produce personalized nutrition guidance.

## 5. Important scientific boundaries
DO NOT claim:
- BMI can be accurately determined from a photograph.
- Protein absorption can be measured from exercise performance.
- Push-ups/sit-ups alone determine overall physical fitness.
- The system diagnoses disease or prescribes medical treatment.
- Meal photos provide exact grams/calories.
- ML alone determines medically correct protein/calorie requirements.

USE these claims instead:
- Height and weight are used to calculate BMI.
- Exercise video provides an "exercise performance profile" or activity-related features.
- Nutrition targets are estimated using established equations/guidelines.
- ML/recommendation algorithms personalize and rank food/meal recommendations.
- Meal-photo nutrition values are estimates and should be user-confirmable.
- The system is for general wellness/educational decision support.

## 6. Target demo
A user:
1. Enters age, sex, height, weight, goal, dietary preference, allergies, and optional lifestyle information.
2. Performs a 20-second push-up test using webcam/video.
3. AI counts valid repetitions and calculates simple performance metrics.
4. Optionally performs sit-ups, squats, or plank.
5. Uploads/takes a meal photo.
6. Food AI identifies likely foods.
7. User confirms food/portion if confidence is low.
8. Nutrition data is looked up from a food database.
9. System compares recent intake with estimated targets.
10. Recommendation engine proposes meals/food swaps.
11. UI explains why the recommendation was made.
12. User can provide feedback, which updates preferences/history.

## 7. 12-hour MVP priority
Must have:
- User profile
- Height/weight/BMI calculation
- 20-second push-up video analysis
- Rep counter
- Basic form/range/tempo metrics if reliable
- Meal photo upload
- Food recognition OR human-confirmed food recognition fallback
- Nutrition lookup
- Basic personalized meal recommendation
- Explanation panel
- Attractive dashboard

Nice-to-have:
- Sit-ups
- Squats
- Plank
- Weekly diet history
- Feedback loop
- Meal swap
- Simple ML ranking

Do NOT spend MVP time on:
- Genetic data
- Wearables
- Clinical diagnosis
- Protein absorption prediction
- BMI-from-photo
- Exact calorie estimation from a single image
- Training a large model from scratch
- Complex microservices
- Native Android/iOS app

## 8. Recommended architecture

FRONTEND
- Streamlit for fastest prototype.
- Optional React/Next.js only if the team already has frontend expertise.

APPLICATION LAYER
- Python.
- FastAPI is optional; direct Python modules are acceptable for the 12-hour MVP.

COMPUTER VISION
- MediaPipe Pose + OpenCV.
- Use an existing open-source rep-counting implementation as the starting point.
- Exercise analyzer should output structured JSON/dict data.

FOOD VISION
- Start with an existing food-image classifier.
- If confidence is low, ask the user to confirm detected food.
- Do not require exact automatic portion estimation for MVP.

NUTRITION
- Use a structured nutrition database.
- Store calories, protein, carbohydrates, fat, fiber and relevant metadata.
- User-specific calorie/protein targets should be generated using transparent formulas/rules, not arbitrary ML predictions.

ML / RECOMMENDATION
- Content-based recommendation / nearest-neighbor or Random Forest/Gradient Boosting for personalization/ranking.
- ML should personalize food choices, ranking, adherence and preference matching.
- Deterministic nutrition calculations remain separate from ML.

DATABASE
For MVP use SQLite or JSON/CSV.
Tables/collections:
users
exercise_sessions
meals
meal_items
food_catalog
feedback

## 9. Data flow

USER
→ Profile data
→ Exercise video
→ Meal photo
→ Feature extraction
→ Fitness/exercise performance profile
→ Nutrition target engine
→ Food/nutrition lookup
→ Recommendation engine
→ Personalized meal plan
→ Explanation
→ Feedback
→ User profile update

## 10. Exercise analysis

Input:
- webcam stream or uploaded video
- preferably full body visible
- good lighting
- side/front view depending on exercise

Pose landmarks:
- nose
- shoulders
- elbows
- wrists
- hips
- knees
- ankles

Possible features:
- valid repetitions
- duration
- repetition tempo
- range of motion
- movement consistency
- simple form score

Example output:
{
  "exercise": "pushup",
  "duration_sec": 20,
  "repetitions": 17,
  "valid_repetitions": 16,
  "tempo_sec_per_rep": 1.25,
  "range_of_motion_score": 0.88,
  "form_consistency_score": 0.82
}

Do not present the resulting score as a clinical fitness diagnosis.

## 11. Food-photo analysis

Pipeline:
meal image
→ food recognition
→ confidence
→ user confirmation when needed
→ portion category/estimate
→ nutrition database lookup
→ meal nutrition estimate

Example:
{
  "foods": [
    {"name": "rice", "confidence": 0.94, "portion": "medium"},
    {"name": "dal", "confidence": 0.91, "portion": "medium"},
    {"name": "roti", "confidence": 0.88, "portion": "2 pieces"}
  ]
}

Show "~" or "estimated" for nutrition values.

## 12. Nutrition engine

Inputs:
- age
- sex
- height
- weight
- activity level
- goal
- exercise performance
- dietary preference
- allergies
- recent food intake

Outputs:
- estimated energy target
- estimated protein target/range
- carbohydrate/fat targets if implemented
- food/meal ranking

Keep formulas transparent and explainable.

## 13. Recommendation engine

Recommendation score can combine:
- nutrition match
- goal match
- dietary preference
- allergy safety
- food dislikes
- cuisine preference
- previous feedback
- availability/budget if implemented
- recent dietary gaps

Example:
RecommendationScore =
0.30 * nutrition_match +
0.20 * goal_match +
0.15 * preference_match +
0.15 * allergy_safety +
0.10 * cuisine_match +
0.10 * feedback_score

Weights are prototype choices and should not be presented as clinically validated.

## 14. Explainable AI

Every recommendation should have a "Why?" section.

Example:
"Recommended because:
- it fits your stated dietary preference,
- it helps close the estimated protein gap,
- it matches your preferred cuisine,
- you previously rated similar meals positively."

Avoid unexplained black-box recommendations.

## 15. Feedback loop

After a meal:
- taste rating
- satiety rating
- would eat again
- portion suitability
- optional comment

Store feedback and use it to adjust future ranking.

## 16. Privacy-by-design

Preferred behavior:
- Process exercise video locally where possible.
- Do not retain raw exercise video unless explicitly needed.
- Store extracted metrics rather than raw video.
- Allow meal images to be deleted.
- Avoid collecting medical records.
- Clearly state that uploaded images/videos are used for analysis.
- Use minimal personal data for the demo.

## 17. Safety UX

Include:
"FitFuel AI provides general wellness and nutrition guidance for demonstration purposes. It is not a substitute for a doctor or registered dietitian. Users with medical conditions, pregnancy, eating disorders, significant allergies, or other special nutritional needs should seek professional advice."

For high-risk input, avoid generating aggressive diet/exercise advice.

## 18. Suggested project structure

FitFuel-AI/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── data/
│   ├── foods.csv
│   ├── recipes.csv
│   └── indian_foods.csv
├── modules/
│   ├── exercise/
│   │   ├── pose_detector.py
│   │   ├── pushup.py
│   │   ├── situp.py
│   │   ├── squat.py
│   │   └── exercise_analyzer.py
│   ├── food/
│   │   ├── food_detector.py
│   │   ├── portion_estimator.py
│   │   └── nutrition_lookup.py
│   ├── nutrition/
│   │   ├── bmi.py
│   │   ├── energy.py
│   │   ├── protein.py
│   │   └── targets.py
│   └── recommendation/
│       ├── recommender.py
│       ├── ranking.py
│       └── personalization.py
├── database/
│   └── database.py
├── ui/
│   ├── profile.py
│   ├── exercise.py
│   ├── meal_scanner.py
│   └── dashboard.py
└── models/
    └── README.md

## 19. GitHub repositories to reference

PRIMARY — Exercise:
https://github.com/TheUnknown550/GC_Fit
Use for MediaPipe/OpenCV push-up, sit-up and squat repetition counting. MIT licensed according to its repository README.

PRIMARY — Food image recognition:
https://github.com/MaharshSuryawala/Food-Image-Recognition
Uses Food-101 and a nutrition-data pipeline; repository is MIT licensed according to its README. Use as a starting point, not as a guarantee of accurate Indian-food recognition or exact portion size.

PRIMARY — Nutrition recommendation:
https://github.com/zakaria-narjis/nutrimind
Content-based recommendation using nutritional vectors/cosine similarity, with FastAPI, Streamlit and scikit-learn. Useful architecture/reference for the recommendation layer.

ADVANCED / FUTURE — Food segmentation:
https://github.com/Restok/Food-Semantic-Segmentation-and-Classification
Research-oriented food classification/segmentation using FoodSeg103/Nutrition5K and lightweight CNN approaches. Do not make this a 12-hour MVP dependency.

Exercise-recognition topic:
https://github.com/topics/exercise-recognition

Food-classification topic:
https://github.com/topics/food-classification

Nutrition-information topic:
https://github.com/topics/nutrition-information

## 20. Integration rule

Do not blindly merge entire repositories.

Extract/adapt only the useful modules:
- GC_Fit → pose/rep logic
- Food-Image-Recognition → food image classification concepts/model/data pipeline
- NutriMind → recommendation/nutrition-target architecture
- Build the integration, user profile, safety layer, explanation layer and feedback loop ourselves.

Do not claim that FitFuel AI's models were trained from scratch if open-source components are used.

## 21. Demo narrative

1. "Tell us about yourself."
2. User enters height/weight/age/goal/diet.
3. "Let's measure your exercise performance."
4. User performs 20-second push-ups.
5. AI displays live skeleton, reps and basic performance metrics.
6. "Now show us what you actually eat."
7. User uploads meal photo.
8. AI detects foods and asks for confirmation if uncertain.
9. Nutrition estimate appears.
10. Dashboard shows intake vs estimated target.
11. AI suggests a better meal or food swap.
12. "Why?" panel explains the recommendation.
13. User rates the meal.
14. Recommendation profile updates.

## 22. Winning differentiator

The project is not just a diet generator.

The differentiator is:
"Adaptive nutrition based on observed movement + observed dietary behavior."

The core loop:
ASSESS → ANALYZE → RECOMMEND → FEEDBACK → ADAPT

## 23. UI requirements

Design should look like a modern AI fitness/nutrition product:
- dark/clean modern dashboard
- large numeric metrics
- exercise camera screen with pose skeleton
- live rep counter
- food image upload/camera
- confidence badges
- nutrition cards
- progress bars
- recommendation cards
- "Why this?" expandable explanation
- meal swap interaction
- feedback buttons
- responsive layout

Avoid overly complicated navigation.

## 24. Technical quality requirements

- Modular Python code.
- Type hints where practical.
- Clear error handling.
- Never crash when camera is unavailable.
- Provide image upload fallback if webcam is unavailable.
- Provide manual food confirmation fallback.
- Keep model loading cached.
- Avoid loading huge datasets on every request.
- Use environment variables for API keys.
- Do not hard-code secrets.
- Keep a README with exact Windows setup instructions.
- Provide requirements.txt.
- Provide a demo/sample-data mode so the app can still be shown if computer vision fails.

## 25. Prototype acceptance criteria

A judge should be able to:
1. Open the app.
2. Create a profile.
3. Run a 20-second exercise test.
4. See rep counting.
5. Upload a food photo.
6. See food recognition or confirmation.
7. See nutrition estimates.
8. Receive a personalized recommendation.
9. Understand why it was recommended.
10. Submit feedback.
11. See the profile/recommendation change.

If all 11 work, the prototype is successful.
