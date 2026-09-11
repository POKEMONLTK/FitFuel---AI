# FitFuel AI — Quick Start for AI Coding Agents

Read these files in order:
1. PROJECT_CONTEXT.md
2. STITCH_PROMPT.md
3. REPO_REFERENCE.md

Then generate the project.

First milestone:
- Streamlit launches.
- Profile form works.
- BMI calculates.
- Demo mode works without external models.

Second milestone:
- GC_Fit/MediaPipe exercise analyzer integrated.
- Push-up 20-second test returns structured metrics.

Third milestone:
- Meal upload works.
- Food detection/confirmation works.
- Nutrition lookup works.

Fourth milestone:
- Recommendation engine works.
- Dashboard shows targets vs estimated intake.
- "Why this?" explanation works.

Fifth milestone:
- Feedback and history work.

If any ML/CV dependency causes installation/runtime problems:
DO NOT stop the project.
Use the demo/mock fallback and keep the same module interfaces so the real model can be plugged in later.

Recommended local run:
python -m venv .venv
Windows PowerShell:
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
