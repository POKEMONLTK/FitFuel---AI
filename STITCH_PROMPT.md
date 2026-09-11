# STITCH / CODE-GENERATION MASTER PROMPT — FITFUEL AI

You are the lead full-stack AI engineer building a hackathon prototype called **FitFuel AI — From Movement to Nutrition**.

Read the entire project context before generating code.

## PRIMARY GOAL

Generate a working, polished prototype that combines:

1. User profile and anthropometric information
2. Computer-vision exercise analysis
3. Meal-photo food recognition
4. Nutrition lookup
5. Personalized nutrition recommendation
6. Explainable recommendations
7. Feedback loop

The prototype should be realistically buildable in a hackathon and should prioritize reliability over unnecessary complexity.

## IMPORTANT PRODUCT BOUNDARIES

Do NOT implement or claim:
- BMI prediction from a photograph
- protein absorption measurement
- disease diagnosis
- medical treatment
- exact calories from a single photo
- exact body-fat percentage from a photo
- clinically validated fitness diagnosis

Instead:
- Calculate BMI from user-entered height and weight.
- Call exercise results an "exercise performance profile."
- Treat food-image nutrition as estimated.
- Use transparent nutrition calculations for baseline targets.
- Use ML/recommendation logic for personalization and ranking.
- Clearly label the system as a wellness/educational prototype.

## RECOMMENDED STACK

For the 12-hour MVP use:
- Python 3.10/3.11 if compatible with dependencies
- Streamlit frontend
- OpenCV
- MediaPipe Pose
- scikit-learn
- pandas
- numpy
- SQLite or JSON/CSV for storage
- Pillow
- optional FastAPI only if necessary
- matplotlib/plotly for charts if needed

Do NOT introduce React, Docker, Kubernetes, microservices, PostgreSQL, or complex cloud infrastructure unless there is a compelling reason. The primary objective is a reliable local demo.

## REFERENCE REPOSITORIES

Exercise:
https://github.com/TheUnknown550/GC_Fit

Food image recognition:
https://github.com/MaharshSuryawala/Food-Image-Recognition

Nutrition recommendation:
https://github.com/zakaria-narjis/nutrimind

Advanced food segmentation:
https://github.com/Restok/Food-Semantic-Segmentation-and-Classification

Exercise repositories:
https://github.com/topics/exercise-recognition

Food classification:
https://github.com/topics/food-classification

Nutrition:
https://github.com/topics/nutrition-information

Use these as references/components where compatible. Do not blindly copy full applications. Adapt only relevant logic and respect each repository's license.

## CORE ARCHITECTURE

USER
 ↓
Profile
 ↓
Exercise Video ──→ Pose/Rep Analyzer
 ↓
Meal Photo ──────→ Food Analyzer
 ↓
Feature Engineering
 ↓
Nutrition Target Engine + ML Recommendation Engine
 ↓
Personalized Meal Plan
 ↓
Explanation
 ↓
Feedback
 ↓
Profile/Preference Update

## USER PROFILE

Collect:
- age
- sex
- height_cm
- weight_kg
- goal: weight loss / maintenance / muscle gain / general wellness
- activity level
- diet type: vegetarian / vegan / non-vegetarian / eggitarian
- allergies
- disliked foods
- preferred cuisine
- optional budget
- optional sleep duration

Calculate:
- BMI
- transparent estimated energy requirement
- estimated protein target/range

Make all assumptions visible in code and UI.

## EXERCISE MODULE

Use MediaPipe Pose/OpenCV and adapt the GC_Fit concept.

Initial exercises:
- push-up
- sit-up
- squat
- plank if time permits

Primary MVP:
- push-up 20-second test

Output:
- repetitions
- valid repetitions
- duration
- average tempo
- simple range-of-motion metric if reliable
- simple consistency/form score if reliable
- confidence/quality flag

Do not call this an overall clinical fitness score.

Create a clean interface:
- camera/video preview
- skeleton overlay
- countdown
- live repetition counter
- final result card

If webcam is unavailable:
- allow uploaded video
- allow demo/sample mode

## FOOD PHOTO MODULE

User uploads a meal photo.

Use the Food-Image-Recognition repository/model as a reference where practical.

Pipeline:
image
→ food prediction
→ confidence
→ user confirmation
→ portion category
→ nutrition lookup

Do not require perfect automatic portion estimation.

If prediction confidence is below a configurable threshold:
show:
"AI is not confident. Please confirm what is on the plate."

Allow:
- edit food
- remove food
- add food
- choose portion size

This human-in-the-loop fallback is REQUIRED.

## NUTRITION DATABASE

Create a compact local food database for the MVP with common foods, especially Indian foods.

Minimum examples:
- rice
- roti
- dal
- paneer
- tofu
- curd/yogurt
- milk
- oats
- egg
- chicken
- vegetables
- potato
- banana
- apple
- nuts/seeds if included
- common Indian meals

Fields:
name
serving_size
calories
protein_g
carbs_g
fat_g
fiber_g
diet_type
allergens
cuisine

Keep data easy to extend.

## RECOMMENDATION ENGINE

Use a hybrid design.

Layer 1: deterministic nutrition target calculation.
Layer 2: hard constraints:
- allergies
- diet type
- prohibited foods
Layer 3: recommendation ranking:
- nutrition match
- goal match
- preference match
- cuisine match
- previous feedback
Layer 4: generate meal suggestions.

You may use:
- cosine similarity / nearest neighbors inspired by NutriMind
- Random Forest / Gradient Boosting for a lightweight ranking model if there is enough local data
- rule-based fallback if ML model is unavailable

The application MUST work without a trained ML model. A deterministic fallback is required.

## DIET TRACKING

Allow user to:
- upload breakfast photo
- upload lunch photo
- upload dinner photo
- upload snack photo

Store detected/confirmed foods and estimated nutrition.

Dashboard:
- estimated calories consumed
- protein consumed
- carbs consumed
- fat consumed
- fiber consumed
- target vs consumed
- recent meals

Use wording such as:
"Estimated intake"

## MEAL SWAP

Add a feature:
"Improve this meal"

Example:
Current meal:
rice + dal + roti

Possible suggestion:
slightly reduce carbohydrate-heavy portion
increase dal
add curd/tofu
add vegetables

The exact changes should be based on the user's estimated target and preferences.

## EXPLAINABLE AI

Every recommendation card should have:
"Why this?"

Examples:
- matches vegetarian preference
- helps address estimated protein gap
- fits calorie target
- matches Indian cuisine preference
- user previously liked similar foods

Do not fabricate medical explanations.

## FEEDBACK

After recommendation:
- taste rating 1–5
- satiety rating 1–5
- portion rating
- would eat again: yes/no
- optional comment

Use feedback to modify future food ranking/preferences.

## PRIVACY

Prefer local processing for exercise video.
Do not store raw exercise video by default.
Store extracted metrics.
Allow meal-image deletion.
Never expose API keys.
Use .env for secrets.

## SAFETY

Show a persistent but unobtrusive disclaimer:
"General wellness prototype — not medical advice."

If the user enters a high-risk medical condition or special situation, do not produce aggressive or therapeutic dietary instructions. Instead advise professional consultation.

## UI

Create a polished modern dashboard.

Pages/tabs:
1. Home
2. Profile
3. Fitness Scan
4. Meal Scanner
5. Nutrition Dashboard
6. Recommendations
7. History

Hero:
"From Movement to Nutrition."

Dashboard cards:
- BMI
- Exercise performance
- Protein target
- Calories target
- Today's estimated intake
- Goal progress

Fitness Scan:
- camera/video
- skeleton
- countdown
- live reps
- final performance metrics

Meal Scanner:
- upload/camera
- detected foods
- confidence
- edit/confirm controls
- estimated nutrition

Recommendation:
- meal card
- nutrition summary
- "Why this?"
- "Swap meal"
- feedback

## ERROR HANDLING

The app must gracefully handle:
- webcam unavailable
- image upload failure
- unsupported file
- model unavailable
- low-confidence food detection
- missing nutrition record
- missing food API key
- empty database
- ML model missing

Always provide a usable fallback.

## DEMO MODE

Create a "Demo Mode" that works without camera/model dependencies.

Demo data:
- 20-year-old user
- 175 cm
- 78 kg
- vegetarian
- muscle/fitness goal
- 17 push-ups in 20 seconds
- sample meal containing rice/dal/roti/vegetables

The demo must show the entire end-to-end flow.

## CODE QUALITY

Generate:
- modular code
- type hints
- docstrings for major functions
- configuration file
- requirements.txt
- .env.example
- README.md
- clear Windows installation commands
- clear run command
- sample data
- tests for pure calculation functions

Avoid unnecessary abstraction.

## ACCEPTANCE TEST

The finished prototype must allow this flow:

Profile
→ start fitness test
→ complete/skip demo exercise
→ see rep count
→ upload meal
→ confirm foods
→ see estimated nutrition
→ see target vs intake
→ receive personalized recommendation
→ click "Why?"
→ give feedback
→ see updated preference/history

## IMPLEMENTATION PRIORITY

P0:
- Streamlit app
- profile
- BMI
- nutrition target calculations
- exercise rep counting or demo fallback
- meal photo upload
- food confirmation
- nutrition database
- recommendation
- dashboard

P1:
- actual food classifier integration
- sit-up/squat
- feedback persistence
- charts

P2:
- advanced segmentation
- real ML ranking
- wearable integration
- cloud deployment

Never let P2 features break P0.

## FINAL OUTPUT EXPECTATION

Generate the complete project, not a conceptual mockup.

Before writing each module, make sure it fits the architecture.

When an external repository is unavailable or incompatible, implement a clean local fallback rather than stopping.

Do not invent claims about model accuracy.

Do not claim clinical validation.

The final application should feel like a polished hackathon prototype and be easy for a developer to run locally.
