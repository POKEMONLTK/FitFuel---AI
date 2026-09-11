"""FitFuel AI Custom Styling & Theme.

Strictly adheres to DESIGN.md:
- Apple photography-first design system
- SF Pro Display & SF Pro Text typography hierarchy with negative letter-spacing
- Single Action Blue (#0066cc) interactive accent
- Zero decorative gradients, zero shadows on chrome
- Pure product drop shadow only under imagery
- Pill buttons (rounded.pill 9999px) with active scale(0.96) micro-interaction
- 18px radius (rounded.lg) utility cards with 1px hairline borders
- Weight ladder 300 / 400 / 600 / 700 (500 deliberately absent)
"""

import streamlit as st


def apply_custom_styles() -> None:
    """Inject custom CSS rules adhering strictly to DESIGN.md."""
    st.markdown(
        """
        <style>
        /* ==========================================================================
           APPLE SYSTEM TYPOGRAPHY & COLOR TOKENS (DESIGN.md)
           ========================================================================== */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        :root {
            --color-primary: #0066cc;
            --color-primary-focus: #0071e3;
            --color-primary-on-dark: #2997ff;
            --color-ink: #1d1d1f;
            --color-body-dark: #ffffff;
            --color-body-muted: #86868b;
            --color-ink-muted-80: #333333;
            --color-ink-muted-48: #7a7a7a;
            --color-hairline: rgba(255, 255, 255, 0.12);
            --color-hairline-light: rgba(0, 0, 0, 0.08);
            --color-canvas: #ffffff;
            --color-canvas-parchment: #f5f5f7;
            --color-surface-pearl: #fafafc;
            --color-surface-tile-1: #272729;
            --color-surface-tile-2: #2a2a2c;
            --color-surface-tile-3: #252527;
            --color-surface-black: #000000;
            --font-display: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Inter", system-ui, sans-serif;
            --font-text: "SF Pro Text", -apple-system, BlinkMacSystemFont, "Inter", system-ui, sans-serif;
        }

        /* Base Application Canvas */
        .stApp {
            background-color: var(--color-surface-tile-3);
            color: var(--color-body-dark);
            font-family: var(--font-text);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        /* Sidebar Navigation Chassis */
        [data-testid="stSidebar"] {
            background-color: var(--color-surface-black) !important;
            border-right: 1px solid var(--color-hairline) !important;
        }

        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3 {
            font-family: var(--font-display) !important;
            font-weight: 600 !important;
            color: #ffffff !important;
        }

        /* ==========================================================================
           TYPOGRAPHIC HIERARCHY (DESIGN.md)
           ========================================================================== */
        .apple-hero-title {
            font-family: var(--font-display);
            font-size: 40px;
            font-weight: 600;
            line-height: 1.10;
            letter-spacing: -0.28px;
            color: #ffffff;
            margin-bottom: 8px;
            padding-top: 4px;
        }

        .apple-hero-subtitle {
            font-family: var(--font-display);
            font-size: 19px;
            font-weight: 400;
            line-height: 1.38;
            letter-spacing: 0.196px;
            color: var(--color-body-muted);
            margin-bottom: 24px;
        }

        .apple-section-title {
            font-family: var(--font-display);
            font-size: 24px;
            font-weight: 600;
            line-height: 1.2;
            letter-spacing: 0;
            color: #ffffff;
            margin-top: 20px;
            margin-bottom: 12px;
        }

        .apple-tagline {
            font-family: var(--font-display);
            font-size: 21px;
            font-weight: 600;
            line-height: 1.19;
            letter-spacing: 0.231px;
            color: #ffffff;
        }

        .apple-body {
            font-family: var(--font-text);
            font-size: 17px;
            font-weight: 400;
            line-height: 1.47;
            letter-spacing: -0.374px;
            color: var(--color-body-dark);
        }

        .apple-body-muted {
            font-family: var(--font-text);
            font-size: 17px;
            font-weight: 400;
            line-height: 1.47;
            letter-spacing: -0.374px;
            color: var(--color-body-muted);
        }

        .apple-body-strong {
            font-family: var(--font-text);
            font-size: 17px;
            font-weight: 600;
            line-height: 1.24;
            letter-spacing: -0.374px;
            color: #ffffff;
        }

        .apple-caption {
            font-family: var(--font-text);
            font-size: 14px;
            font-weight: 400;
            line-height: 1.43;
            letter-spacing: -0.224px;
            color: var(--color-body-muted);
        }

        .apple-fine-print {
            font-family: var(--font-text);
            font-size: 12px;
            font-weight: 400;
            line-height: 1.2;
            letter-spacing: -0.12px;
            color: var(--color-ink-muted-48);
        }

        /* ==========================================================================
           CONTAINERS & SURFACES (DESIGN.md)
           ========================================================================== */
        /* store-utility-card: rounded.lg (18px), 1px hairline border, zero box-shadow */
        .fitfuel-card, .store-utility-card {
            background-color: var(--color-surface-tile-1) !important;
            border-radius: 18px !important;
            padding: 24px !important;
            margin-bottom: 20px !important;
            border: 1px solid var(--color-hairline) !important;
            box-shadow: none !important;
        }

        .store-utility-card-subtle {
            background-color: var(--color-surface-tile-2) !important;
            border-radius: 18px !important;
            padding: 20px !important;
            margin-bottom: 16px !important;
            border: 1px solid var(--color-hairline) !important;
            box-shadow: none !important;
        }

        /* Metric Box: rounded.lg (18px), hairline border, display value */
        .metric-box {
            background-color: var(--color-surface-tile-1);
            border-radius: 18px;
            padding: 20px 16px;
            text-align: center;
            border: 1px solid var(--color-hairline);
            box-shadow: none;
            transition: border-color 0.2s ease;
        }
        .metric-box:hover {
            border-color: rgba(255, 255, 255, 0.28);
        }
        .metric-val {
            font-family: var(--font-display);
            font-size: 34px;
            font-weight: 600;
            line-height: 1.2;
            letter-spacing: -0.374px;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .metric-label {
            font-family: var(--font-text);
            font-size: 14px;
            font-weight: 400;
            color: var(--color-body-muted);
            letter-spacing: -0.224px;
        }

        /* Signature Product Photography Shadow (The only drop-shadow in the system) */
        .product-photo-shadow {
            border-radius: 18px !important;
            box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0 !important;
        }
        div[data-testid="stImage"] img {
            border-radius: 18px !important;
            box-shadow: rgba(0, 0, 0, 0.22) 3px 5px 30px 0;
        }

        /* Chips & Pills */
        .apple-chip, .confidence-pill {
            display: inline-flex;
            align-items: center;
            padding: 6px 14px;
            border-radius: 9999px;
            font-family: var(--font-text);
            font-size: 13px;
            font-weight: 400;
            letter-spacing: -0.224px;
            background-color: rgba(255, 255, 255, 0.08);
            color: #ffffff;
            border: 1px solid var(--color-hairline);
            margin-right: 6px;
        }
        .conf-high {
            background-color: rgba(0, 102, 204, 0.2);
            color: var(--color-primary-on-dark);
            border-color: rgba(41, 151, 255, 0.35);
        }
        .conf-med {
            background-color: rgba(255, 255, 255, 0.1);
            color: var(--color-body-muted);
            border-color: var(--color-hairline);
        }

        /* Safety & Status Banner */
        .safety-banner {
            background-color: var(--color-surface-tile-1);
            border: 1px solid var(--color-hairline);
            padding: 14px 20px;
            border-radius: 18px;
            font-family: var(--font-text);
            font-size: 14px;
            line-height: 1.43;
            color: var(--color-body-muted);
            margin-bottom: 24px;
            box-shadow: none;
        }
        .safety-banner strong {
            color: #ffffff;
            font-weight: 600;
        }

        /* Recommendation Highlights */
        .rec-card {
            background-color: var(--color-surface-tile-1);
            border: 1px solid var(--color-hairline);
            border-radius: 18px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: none;
        }
        .rec-header {
            font-family: var(--font-display);
            font-size: 21px;
            font-weight: 600;
            color: #ffffff;
            letter-spacing: 0.231px;
        }
        .why-box {
            background-color: var(--color-surface-tile-2);
            border: 1px solid var(--color-hairline);
            padding: 16px 20px;
            border-radius: 14px;
            margin-top: 14px;
            font-family: var(--font-text);
            font-size: 14px;
            line-height: 1.47;
            color: #ffffff;
        }

        /* ==========================================================================
           INTERACTIVE CONTROLS & STREAMLIT OVERRIDES
           ========================================================================== */
        /* Primary Buttons: rounded.pill (9999px), Action Blue #0066cc, active scale(0.96) */
        .stButton > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button {
            background-color: var(--color-primary) !important;
            color: #ffffff !important;
            font-family: var(--font-text) !important;
            font-size: 16px !important;
            font-weight: 400 !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            border: none !important;
            box-shadow: none !important;
            transition: transform 0.15s ease, background-color 0.15s ease !important;
        }
        .stButton > button[kind="primary"]:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: var(--color-primary-focus) !important;
        }
        .stButton > button[kind="primary"]:active,
        div[data-testid="stFormSubmitButton"] > button:active {
            transform: scale(0.96) !important;
        }
        .stButton > button[kind="primary"]:focus,
        div[data-testid="stFormSubmitButton"] > button:focus {
            outline: 2px solid var(--color-primary-focus) !important;
            outline-offset: 2px !important;
        }

        /* Secondary Pill Buttons: rounded.pill (9999px), hairline or blue border, active scale(0.96) */
        .stButton > button[kind="secondary"],
        .stButton > button:not([kind="primary"]) {
            background-color: transparent !important;
            color: #ffffff !important;
            font-family: var(--font-text) !important;
            font-size: 16px !important;
            font-weight: 400 !important;
            border-radius: 9999px !important;
            padding: 10px 24px !important;
            border: 1px solid var(--color-hairline) !important;
            box-shadow: none !important;
            transition: transform 0.15s ease, border-color 0.15s ease !important;
        }
        .stButton > button[kind="secondary"]:hover,
        .stButton > button:not([kind="primary"]):hover {
            border-color: var(--color-primary-on-dark) !important;
            color: var(--color-primary-on-dark) !important;
        }
        .stButton > button[kind="secondary"]:active,
        .stButton > button:not([kind="primary"]):active {
            transform: scale(0.96) !important;
        }

        /* Form Inputs (Text inputs, Number inputs, Selectboxes): rounded.lg (14px/18px) or pill */
        div[data-baseweb="input"] {
            border-radius: 12px !important;
            border: 1px solid var(--color-hairline) !important;
            background-color: var(--color-surface-tile-2) !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: var(--color-primary-focus) !important;
            box-shadow: 0 0 0 1px var(--color-primary-focus) !important;
        }
        div[data-baseweb="select"] > div {
            border-radius: 12px !important;
            border: 1px solid var(--color-hairline) !important;
            background-color: var(--color-surface-tile-2) !important;
        }

        /* Radio Options */
        div[data-testid="stRadio"] div[role="radiogroup"] {
            gap: 10px;
        }

        /* Streamlit Tabs: Clean SF Pro indicator */
        button[data-baseweb="tab"] {
            font-family: var(--font-text) !important;
            font-size: 15px !important;
            font-weight: 400 !important;
            color: var(--color-body-muted) !important;
            border-bottom: 2px solid transparent !important;
            padding: 10px 16px !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #ffffff !important;
            border-bottom: 2px solid var(--color-primary-on-dark) !important;
            font-weight: 600 !important;
        }

        /* Streamlit Progress Bars: Action Blue fill */
        .stProgress > div > div > div > div {
            background-color: var(--color-primary) !important;
            border-radius: 9999px !important;
        }
        .stProgress > div > div {
            background-color: var(--color-surface-tile-1) !important;
            border-radius: 9999px !important;
        }

        /* Expanders: 18px rounded utility card style */
        div[data-testid="stExpander"] {
            border-radius: 18px !important;
            border: 1px solid var(--color-hairline) !important;
            background-color: var(--color-surface-tile-1) !important;
            box-shadow: none !important;
            overflow: hidden !important;
            margin-bottom: 12px !important;
        }
        details summary {
            font-family: var(--font-text) !important;
            font-weight: 600 !important;
            color: #ffffff !important;
        }

        /* DataFrame & Tables */
        div[data-testid="stDataFrame"] {
            border-radius: 18px !important;
            overflow: hidden !important;
            border: 1px solid var(--color-hairline) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_safety_disclaimer() -> None:
    """Render mandatory persistent wellness prototype disclaimer adhering to DESIGN.md."""
    st.markdown(
        """
        <div class="safety-banner">
            🛡️ <strong>FitFuel AI Wellness Prototype:</strong> Educational and decision-support guidance only.
            Not a medical diagnostic tool or clinical treatment system. Always consult a licensed healthcare professional for personalized medical or dietary needs.
        </div>
        """,
        unsafe_allow_html=True,
    )

