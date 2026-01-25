"""
Dublin Trip App - The White Jersey
A Streamlit mobile app for tracking Dublin trip activities.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from streamlit_gsheets import GSheetsConnection
import cloudinary
import cloudinary.uploader

# =============================================================================
# APP CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Dublin Racing Trip 2025",
    page_icon="🏇",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# LOGO
# =============================================================================

def render_header():
    """Render logo header with user stats banner."""
    st.markdown("""
    <style>
        [data-testid="stImage"] > img { background: transparent !important; }
        .logo-container img { background: transparent !important; }
    </style>
    <div class="logo-container"></div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.image("logo.png", width=140)
    with col2:
        # Show user stats if logged in and has submitted a rule
        current_user = get_current_user()
        if current_user and check_user_submitted_rule(current_user):
            scores_df = calculate_scores()
            if not scores_df.empty:
                user_row = scores_df[scores_df["user"] == current_user]
                if not user_row.empty:
                    user_score = int(user_row.iloc[0]["score"])
                    user_rank = int(user_row.index[0]) + 1

                    # Medal for top 3
                    medal = ""
                    if user_rank == 1:
                        medal = " 🥇"
                    elif user_rank == 2:
                        medal = " 🥈"
                    elif user_rank == 3:
                        medal = " 🥉"

                    # Ordinal suffix
                    if user_rank == 1:
                        suffix = "st"
                    elif user_rank == 2:
                        suffix = "nd"
                    elif user_rank == 3:
                        suffix = "rd"
                    else:
                        suffix = "th"

                    st.markdown(f"""
                    <div style="
                        background-color: #ffffff;
                        border: 3px solid #1a1a1a;
                        padding: 0.75rem;
                        text-align: right;
                        box-shadow: 4px 4px 0 #333333;
                    ">
                        <span style="color: #1a1a1a; font-size: 1rem; font-weight: 700;">
                            Hello, {current_user}!{medal}
                        </span><br>
                        <span style="color: #FF6B00; font-size: 1.2rem; font-weight: 800;">
                            {user_score} pts
                        </span>
                        <span style="color: #1a1a1a; font-size: 0.9rem;">
                            | {user_rank}{suffix} Place
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

def render_logo():
    """Render logo only (for login/intro pages)."""
    st.markdown("""
    <style>
        [data-testid="stImage"] > img { background: transparent !important; }
        .logo-container img { background: transparent !important; }
    </style>
    <div class="logo-container"></div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("logo.png", width=140)

# =============================================================================
# BRUTALIST CSS THEME
# =============================================================================

st.markdown("""
<style>
    /* Import monospace font */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');

    /* Base - Raw Concrete Background */
    .stApp {
        background-color: #d4d4d4 !important;
        color: #1a1a1a !important;
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
    }

    /* Responsive layout - 50% on desktop, full on mobile */
    @media (min-width: 768px) {
        .block-container {
            max-width: 50% !important;
            margin: 0 auto !important;
        }
    }

    @media (max-width: 767px) {
        .block-container {
            max-width: 100% !important;
            padding: 1rem !important;
        }
    }

    /* All text - Monospace */
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        font-family: 'JetBrains Mono', 'Courier New', monospace !important;
        color: #1a1a1a !important;
    }

    /* Headers - Bold Industrial */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        border-bottom: 4px solid #1a1a1a !important;
        padding-bottom: 10px !important;
    }

    h2 {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        text-transform: uppercase !important;
        border-left: 6px solid #FF6B00 !important;
        padding-left: 12px !important;
    }

    /* Buttons - Brutalist blocks */
    .stButton > button {
        background-color: #00994d !important;
        color: #ffffff !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
        border: 3px solid #1a1a1a !important;
        border-radius: 0 !important;
        padding: 0.75rem 1.5rem !important;
        width: 100% !important;
        transition: all 0.1s ease !important;
    }

    .stButton > button:hover {
        background-color: #FF6B00 !important;
        color: #1a1a1a !important;
        transform: translate(-2px, -2px) !important;
        box-shadow: 4px 4px 0 #1a1a1a !important;
    }

    .stButton > button:active {
        transform: translate(0, 0) !important;
        box-shadow: none !important;
    }

    /* Input fields - Raw boxes */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        font-family: 'JetBrains Mono', monospace !important;
        border: 3px solid #1a1a1a !important;
        border-radius: 0 !important;
        padding: 10px !important;
    }

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #FF6B00 !important;
        box-shadow: none !important;
        outline: none !important;
    }

    /* Selectbox - Brutalist dropdown */
    .stSelectbox > div > div > div {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 3px solid #1a1a1a !important;
        border-radius: 0 !important;
    }

    /* DROPDOWN FIX: Hide the keyboard_arrow text that appears on the LEFT */
    .stSelectbox [data-baseweb="select"] [data-baseweb="icon"] {
        display: none !important;
    }

    /* Hide ALL SVGs in selectbox */
    .stSelectbox svg {
        display: none !important;
    }

    /* Target the value container - hide any icons inside */
    .stSelectbox [data-baseweb="select"] > div > div:first-child svg,
    .stSelectbox [data-baseweb="select"] > div > div:first-child [data-baseweb="icon"] {
        display: none !important;
    }

    /* Force the placeholder/value text to cover any background text */
    .stSelectbox [data-baseweb="select"] > div > div:first-child {
        position: relative !important;
        z-index: 2 !important;
        background: #ffffff !important;
    }

    /* Hide icon text that appears BEFORE the value */
    .stSelectbox [data-baseweb="select"] > div::before {
        display: none !important;
    }

    /* Target spans that might contain icon text */
    .stSelectbox [data-baseweb="select"] span[aria-hidden="true"],
    .stSelectbox [data-baseweb="select"] [role="presentation"] {
        display: none !important;
        font-size: 0 !important;
    }

    /* Make sure the actual selected value is visible and on top */
    .stSelectbox [data-baseweb="select"] [data-baseweb="select-value-container"],
    .stSelectbox [data-baseweb="select"] input {
        position: relative !important;
        z-index: 3 !important;
        background: #ffffff !important;
    }

    /* Hide anything that looks like an icon container on the left */
    .stSelectbox [data-baseweb="select"] > div > div:first-child > span:first-child:not([title]) {
        display: none !important;
    }

    /* Add custom dropdown arrow on right */
    .stSelectbox [data-baseweb="select"] > div {
        position: relative !important;
        padding-right: 35px !important;
    }

    .stSelectbox [data-baseweb="select"] > div::after {
        content: "▼" !important;
        position: absolute !important;
        right: 10px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        font-size: 12px !important;
        color: #1a1a1a !important;
        pointer-events: none !important;
        z-index: 10 !important;
    }

    /* Logo - transparent background */
    .stImage, .stImage > img, [data-testid="stImage"], [data-testid="stImage"] img {
        background: transparent !important;
        background-color: transparent !important;
    }

    img {
        background: transparent !important;
    }

    /* Cards - Concrete blocks with offset shadow */
    .card {
        background-color: #ffffff;
        border: 3px solid #1a1a1a;
        border-radius: 0;
        padding: 1rem;
        margin: 0.75rem 0;
        color: #1a1a1a;
        box-shadow: 4px 4px 0 #333333;
    }

    .card strong, .card span, .card p {
        color: #1a1a1a !important;
    }

    /* Tab styling - Industrial blocks */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background-color: #1a1a1a;
        border: 3px solid #1a1a1a;
        border-radius: 0;
        padding: 0;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #d4d4d4;
        color: #1a1a1a !important;
        border-radius: 0;
        border-right: 2px solid #1a1a1a;
        padding: 12px 8px;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.02em;
    }

    .stTabs [data-baseweb="tab"]:last-child {
        border-right: none;
    }

    .stTabs [aria-selected="true"] {
        background-color: #00994d !important;
        color: #ffffff !important;
    }

    /* Metrics - Bold numbers */
    [data-testid="stMetricValue"] {
        color: #FF6B00 !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Slider - Green bar */
    .stSlider > div > div > div {
        background-color: #00994d !important;
    }

    /* Expander - Industrial drawer */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 3px solid #1a1a1a !important;
        border-radius: 0 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
    }

    .streamlit-expanderContent {
        border: 3px solid #1a1a1a !important;
        border-top: none !important;
        border-radius: 0 !important;
    }

    /* FIX: Hide keyboard_arrow_down text in expanders */
    [data-testid="stIconMaterial"] {
        font-size: 0 !important;
        width: 20px !important;
        height: 20px !important;
        display: inline-block !important;
        position: relative !important;
    }

    [data-testid="stIconMaterial"]::after {
        content: "▶" !important;
        font-size: 12px !important;
        position: absolute !important;
        left: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
    }

    details[open] [data-testid="stIconMaterial"]::after {
        content: "▼" !important;
    }

    /* Success/Error messages - Bold blocks */
    .stSuccess {
        background-color: #00994d !important;
        border: 3px solid #1a1a1a !important;
        border-radius: 0 !important;
        color: #ffffff !important;
    }

    .stError {
        background-color: #cc0000 !important;
        border: 3px solid #1a1a1a !important;
        border-radius: 0 !important;
        color: #ffffff !important;
    }

    .stInfo {
        background-color: #FF6B00 !important;
        border: 3px solid #1a1a1a !important;
        border-radius: 0 !important;
        color: #1a1a1a !important;
    }

    /* Dividers - Heavy lines */
    hr {
        border: none !important;
        border-top: 3px solid #1a1a1a !important;
        margin: 1.5rem 0 !important;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Leaderboard - Industrial rows */
    .leader-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #ffffff;
        border: 3px solid #1a1a1a;
        border-left: 8px solid #00994d;
        color: #1a1a1a;
        box-shadow: 4px 4px 0 #333333;
    }

    .leader-name {
        font-weight: 700;
        font-size: 1rem;
        color: #1a1a1a !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .leader-score {
        color: #FF6B00 !important;
        font-weight: 800;
        font-size: 1.3rem;
    }

    /* Rank colors - Bold accents */
    .rank-1 {
        border-left-color: #ffd700 !important;
        background: linear-gradient(90deg, rgba(255,215,0,0.15) 0%, #ffffff 30%) !important;
    }
    .rank-2 {
        border-left-color: #a0a0a0 !important;
    }
    .rank-3 {
        border-left-color: #cd7f32 !important;
    }

    /* Form labels */
    .stForm label {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
    }

    /* Custom scrollbar - Industrial */
    ::-webkit-scrollbar {
        width: 12px;
    }

    ::-webkit-scrollbar-track {
        background: #d4d4d4;
        border-left: 3px solid #1a1a1a;
    }

    ::-webkit-scrollbar-thumb {
        background: #1a1a1a;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #FF6B00;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# GOOGLE SHEETS CONNECTION
# =============================================================================

# Google Sheet URL
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1uWn3rXrcuoz2mWIGc1N93WUtHhuoHE5oDSg6NJBscH0/edit"

@st.cache_resource
def get_gsheets_connection():
    """Initialize Google Sheets connection."""
    return st.connection("gsheets", type=GSheetsConnection)

def load_sheet_data(worksheet: str, ttl: int = 60) -> pd.DataFrame:
    """Load data from a specific worksheet with caching."""
    try:
        conn = get_gsheets_connection()
        return conn.read(worksheet=worksheet, usecols=None, ttl=ttl)
    except Exception as e:
        st.error(f"Error loading {worksheet}: {e}")
        return pd.DataFrame()

def append_to_sheet(worksheet: str, data: dict):
    """Append a row to a specific worksheet."""
    try:
        conn = get_gsheets_connection()
        # Use cached data to avoid rate limits, clear cache after update
        existing_df = conn.read(worksheet=worksheet, usecols=None, ttl=60)
        new_row = pd.DataFrame([data])
        updated_df = pd.concat([existing_df, new_row], ignore_index=True)
        conn.update(worksheet=worksheet, data=updated_df)
        # Clear cache for this worksheet
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error saving to {worksheet}: {e}")
        return False

def update_sheet(worksheet: str, df: pd.DataFrame):
    """Update entire worksheet with dataframe."""
    try:
        conn = get_gsheets_connection()
        conn.update(worksheet=worksheet, data=df)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error updating {worksheet}: {e}")
        return False

# =============================================================================
# CLOUDINARY CONFIGURATION
# =============================================================================

def configure_cloudinary():
    """Configure Cloudinary with credentials from Streamlit secrets."""
    try:
        cloudinary.config(
            cloud_name=st.secrets["CLOUDINARY_CLOUD_NAME"],
            api_key=st.secrets["CLOUDINARY_API_KEY"],
            api_secret=st.secrets["CLOUDINARY_API_SECRET"],
            secure=True
        )
        return True
    except Exception as e:
        return False

def upload_image_to_cloudinary(file) -> Optional[str]:
    """Upload image to Cloudinary and return the URL."""
    try:
        configure_cloudinary()
        result = cloudinary.uploader.upload(
            file,
            folder="dublin-trip-2025",
            transformation=[
                {"width": 1200, "height": 1200, "crop": "limit"},
                {"quality": "auto:good"}
            ]
        )
        return result.get("secure_url")
    except Exception as e:
        st.error(f"Upload failed: {e}")
        return None

# =============================================================================
# USER AUTHENTICATION
# =============================================================================

USERS = ["JJ", "Henry", "James", "Dom", "Ash", "Max", "Gerard"]

def render_login_page():
    """Render login page with user buttons."""
    render_logo()
    st.markdown("---")

    st.markdown("## Who are you?")
    st.markdown("*Tap your name to enter*")
    st.markdown("")

    # Display user buttons in a grid
    cols = st.columns(2)
    for i, user in enumerate(USERS):
        with cols[i % 2]:
            if st.button(user, key=f"login_{user}", use_container_width=True):
                st.session_state["authenticated_user"] = user
                st.rerun()

def get_current_user() -> Optional[str]:
    """Get current user from session state."""
    return st.session_state.get("authenticated_user", None)

def check_user_submitted_rule(user_id: str) -> bool:
    """Check if user has submitted a Steward's Rule."""
    rules_df = load_sheet_data("Rules")
    if rules_df.empty:
        return False
    return user_id in rules_df["user_id"].values

# =============================================================================
# FEATURE: LEGISLATION (Landing Page)
# =============================================================================

def render_intro_page(user_id: str):
    """Render the intro page explaining activities and scoring."""
    render_logo()
    st.markdown("---")

    st.markdown(f"## Welcome, {user_id}!")

    st.markdown("""
    <div class="card">
        <h3>🏇 THE LEOPARDSTOWN LEDGER</h3>
        <p>Place your bets on the races at Leopardstown. Track your wins and losses with fractional odds.</p>
        <p><strong>Scoring:</strong> Win = +profit (payout - stake) | Loss = -stake</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3>🍺 DRINK TRACKER</h3>
        <p>Log your drinks at every pub. Track your Guinness and Jameson consumption.</p>
        <p><strong>Scoring:</strong> 🍺 Guinness +5 pts | 🥃 Jameson +5 pts | 🥤 Other +0 pts</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3>⚖️ STEWARD'S INQUIRY</h3>
        <p>Catch someone breaking a rule? File an inquiry. The group votes on guilt.</p>
        <p><strong>Scoring:</strong> +5 pts for filing | -20 pts if found guilty</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3>💬 QUOTE WALL</h3>
        <p>Log memorable quotes from the trip. Vote for your favorites.</p>
        <p><strong>Quote of the Trip</strong> gets eternal glory!</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3>🎲 SIDE BETS</h3>
        <p>Create prop bets between friends. Someone else can take the other side.</p>
        <p><strong>Scoring:</strong> Winner +stake pts | Loser -stake pts</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3>⭐ DAILY MVP</h3>
        <p>Vote for each day's Most Valuable Player. Can change your vote until end of day.</p>
        <p><strong>Scoring:</strong> +10 pts for winning daily MVP</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3>🏆 LEADERBOARD</h3>
        <p>All points are tracked live. Submit your Steward's Rule to earn +10 pts and enter the competition.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("CONTINUE TO RULES", use_container_width=True):
        st.session_state["seen_intro"] = True
        st.rerun()

def render_legislation_gate(user_id: str):
    """Render the Steward's Rule submission gate."""
    render_logo()
    st.markdown("---")

    st.markdown("## Your Steward's Rule")

    st.markdown("""
    <div class="card">
        <p>Before entering, you must propose <strong>ONE Steward's Rule</strong>
        that all participants must follow during the trip.</p>
        <p><strong>Choose wisely - your rule becomes law.</strong></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    with st.form("rule_submission"):
        rule_text = st.text_area(
            "Your Steward's Rule:",
            placeholder="e.g., 'No checking work emails after 6pm'",
            max_chars=200,
            height=100
        )

        submitted = st.form_submit_button("SUBMIT RULE", use_container_width=True)

        if submitted:
            if rule_text and len(rule_text.strip()) > 10:
                rule_data = {
                    "user_id": user_id,
                    "rule": rule_text.strip(),
                    "timestamp": datetime.now().isoformat(),
                    "votes": 0
                }
                if append_to_sheet("Rules", rule_data):
                    st.success("Rule submitted! Welcome to Dublin 2025!")
                    st.rerun()
            else:
                st.error("Please enter a proper rule (at least 10 characters).")

# =============================================================================
# FEATURE: STEWARD'S INQUIRY
# =============================================================================

def render_stewards_inquiry(user_id: str):
    """Render the rule-breaker reporting/voting system."""
    st.markdown("## STEWARD'S INQUIRY")
    st.markdown("*Report rule violations and vote on penalties*")
    st.markdown("---")

    # Load existing rules and inquiries
    rules_df = load_sheet_data("Rules")
    inquiries_df = load_sheet_data("Inquiries")

    # File new inquiry
    with st.expander("FILE NEW INQUIRY", expanded=False):
        with st.form("new_inquiry"):
            # Get list of users (excluding self)
            users = rules_df["user_id"].unique().tolist() if not rules_df.empty else []
            users = [u for u in users if u != user_id]

            accused = st.selectbox("Accused:", options=users if users else ["No users available"])

            # Get list of rules
            rule_options = rules_df["rule"].tolist() if not rules_df.empty else []
            rule_violated = st.selectbox("Rule Violated:", options=rule_options if rule_options else ["No rules yet"])

            evidence = st.text_area("Evidence/Description:", max_chars=300)

            if st.form_submit_button("FILE INQUIRY", use_container_width=True):
                if accused and rule_violated and evidence:
                    inquiry_data = {
                        "reporter": user_id,
                        "accused": accused,
                        "rule_violated": rule_violated,
                        "evidence": evidence,
                        "timestamp": datetime.now().isoformat(),
                        "guilty_votes": 0,
                        "innocent_votes": 0,
                        "status": "OPEN",
                        "voters": ""
                    }
                    if append_to_sheet("Inquiries", inquiry_data):
                        st.success("Inquiry filed!")
                        st.rerun()

    # Display open inquiries
    st.markdown("### OPEN CASES")

    if inquiries_df.empty or len(inquiries_df[inquiries_df["status"] == "OPEN"]) == 0:
        st.info("No open inquiries. Everyone is behaving... for now.")
    else:
        open_cases = inquiries_df[inquiries_df["status"] == "OPEN"]

        for idx, case in open_cases.iterrows():
            voters_list = str(case.get("voters", "")).split(",") if case.get("voters") else []
            user_voted = user_id in voters_list

            st.markdown(f"""
            <div class="card">
                <strong>ACCUSED:</strong> {case['accused']}<br>
                <strong>VIOLATION:</strong> {case['rule_violated'][:50]}...<br>
                <strong>EVIDENCE:</strong> {case['evidence'][:100]}...<br>
                <strong>VOTES:</strong> Guilty: {case['guilty_votes']} | Innocent: {case['innocent_votes']}
            </div>
            """, unsafe_allow_html=True)

            if not user_voted and case['accused'] != user_id:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("GUILTY", key=f"guilty_{idx}", use_container_width=True):
                        inquiries_df.loc[idx, "guilty_votes"] = int(case["guilty_votes"]) + 1
                        inquiries_df.loc[idx, "voters"] = ",".join(voters_list + [user_id])
                        update_sheet("Inquiries", inquiries_df)
                        st.rerun()
                with col2:
                    if st.button("INNOCENT", key=f"innocent_{idx}", use_container_width=True):
                        inquiries_df.loc[idx, "innocent_votes"] = int(case["innocent_votes"]) + 1
                        inquiries_df.loc[idx, "voters"] = ",".join(voters_list + [user_id])
                        update_sheet("Inquiries", inquiries_df)
                        st.rerun()
            elif user_voted:
                st.caption("You have voted on this case.")
            else:
                st.caption("You cannot vote on your own case.")

            st.markdown("---")

# =============================================================================
# FEATURE: LEOPARDSTOWN LEDGER
# =============================================================================

def render_leopardstown_ledger(user_id: str):
    """Render the race betting tracker."""
    st.markdown("## LEOPARDSTOWN LEDGER")
    st.markdown("*Track your race day fortunes*")
    st.markdown("---")

    bets_df = load_sheet_data("Bets")

    # Place new bet
    with st.expander("PLACE NEW BET", expanded=False):
        with st.form("new_bet"):
            col1, col2 = st.columns(2)

            with col1:
                race_num = st.number_input("Race #:", min_value=1, max_value=10, value=1)
            with col2:
                stake = st.number_input("Stake (EUR):", min_value=1.0, max_value=1000.0, value=10.0, step=5.0)

            horse = st.text_input("Horse Name:", placeholder="e.g., Lucky Charm")

            # Fractional odds input
            st.markdown("**Fractional Odds:**")
            odds_col1, odds_col2 = st.columns(2)
            with odds_col1:
                odds_num = st.number_input("Numerator:", min_value=1, max_value=100, value=5)
            with odds_col2:
                odds_den = st.number_input("Denominator:", min_value=1, max_value=20, value=1)

            st.markdown(f"**Odds: {odds_num}/{odds_den}** (Potential return: EUR {stake * (odds_num/odds_den + 1):.2f})")

            if st.form_submit_button("PLACE BET", use_container_width=True):
                if horse:
                    bet_data = {
                        "user_id": user_id,
                        "race_num": race_num,
                        "horse": horse.strip(),
                        "stake": stake,
                        "odds_num": odds_num,
                        "odds_den": odds_den,
                        "timestamp": datetime.now().isoformat(),
                        "result": "PENDING",
                        "payout": 0
                    }
                    if append_to_sheet("Bets", bet_data):
                        st.success(f"Bet placed on {horse}!")
                        st.rerun()
                else:
                    st.error("Please enter a horse name.")

    # Display user's bets
    st.markdown("### YOUR BETS")

    if bets_df.empty:
        st.info("No bets placed yet. Feeling lucky?")
    else:
        user_bets = bets_df[bets_df["user_id"] == user_id]

        if user_bets.empty:
            st.info("You haven't placed any bets yet.")
        else:
            for idx, bet in user_bets.iterrows():
                result_color = {
                    "PENDING": "#cc9900",
                    "WIN": "#00802b",
                    "LOSS": "#cc0000"
                }.get(bet["result"], "#000000")

                st.markdown(f"""
                <div class="card" style="border-left: 4px solid {result_color};">
                    <strong>Race {bet['race_num']}</strong> - {bet['horse']}<br>
                    Stake: EUR {bet['stake']} @ {bet['odds_num']}/{bet['odds_den']}<br>
                    <strong style="color: {result_color}; font-weight: bold;">{bet['result']}</strong>
                    {f" | Payout: EUR {bet['payout']}" if bet['result'] == 'WIN' else ''}
                </div>
                """, unsafe_allow_html=True)

                # Settle button for pending bets
                if bet["result"] == "PENDING":
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("WON", key=f"win_{idx}", use_container_width=True):
                            payout = bet["stake"] * (bet["odds_num"] / bet["odds_den"] + 1)
                            bets_df.loc[idx, "result"] = "WIN"
                            bets_df.loc[idx, "payout"] = round(payout, 2)
                            update_sheet("Bets", bets_df)
                            st.rerun()
                    with col2:
                        if st.button("LOST", key=f"loss_{idx}", use_container_width=True):
                            bets_df.loc[idx, "result"] = "LOSS"
                            bets_df.loc[idx, "payout"] = 0
                            update_sheet("Bets", bets_df)
                            st.rerun()

    # Display all bets by race
    st.markdown("---")
    st.markdown("### ALL BETS BY RACE")

    if bets_df.empty:
        st.info("No bets placed by anyone yet.")
    else:
        # Get unique race numbers and sort them
        races = sorted(bets_df["race_num"].unique())

        for race in races:
            race_bets = bets_df[bets_df["race_num"] == race]

            st.markdown(f"#### Race {int(race)}")

            for idx, bet in race_bets.iterrows():
                result_color = {
                    "PENDING": "#cc9900",
                    "WIN": "#00802b",
                    "LOSS": "#cc0000"
                }.get(bet["result"], "#000000")

                result_text = bet["result"]
                if bet["result"] == "WIN":
                    result_text = f"WIN (+EUR {bet['payout']})"

                st.markdown(f"""
                <div class="card" style="border-left: 4px solid {result_color};">
                    <strong>{bet['user_id']}</strong>: {bet['horse']}<br>
                    EUR {bet['stake']} @ {bet['odds_num']}/{bet['odds_den']}
                    <span style="color: {result_color}; font-weight: bold; float: right;">{result_text}</span>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("")

# =============================================================================
# FEATURE: PINT CRITIC
# =============================================================================

def render_pint_critic(user_id: str):
    """Render the drink tracking system."""
    st.markdown("## DRINK TRACKER")
    st.markdown("*Log your drinks at each pub*")
    st.markdown("---")

    ratings_df = load_sheet_data("Ratings")

    # Get list of existing pubs
    existing_pubs = []
    if not ratings_df.empty and "pub" in ratings_df.columns:
        existing_pubs = sorted(ratings_df["pub"].unique().tolist())

    # Quick add section - show existing pubs as buttons
    if existing_pubs:
        st.markdown("### QUICK ADD")
        st.markdown("*Tap a pub, then select your drink*")

        # Track selected pub in session state
        if "selected_pub" not in st.session_state:
            st.session_state.selected_pub = None

        # Display pub buttons in a grid
        cols = st.columns(2)
        for i, pub in enumerate(existing_pubs):
            with cols[i % 2]:
                if st.button(f"📍 {pub}", key=f"pub_{pub}", use_container_width=True):
                    st.session_state.selected_pub = pub

        # If a pub is selected, show drink options
        if st.session_state.selected_pub:
            st.markdown(f"**Adding drink at: {st.session_state.selected_pub}**")
            drink_cols = st.columns(3)
            with drink_cols[0]:
                if st.button("🍺 Guinness", key="quick_guinness", use_container_width=True):
                    drink_data = {
                        "user_id": user_id,
                        "pub": st.session_state.selected_pub,
                        "drink_type": "Guinness",
                        "timestamp": datetime.now().isoformat()
                    }
                    if append_to_sheet("Ratings", drink_data):
                        st.session_state.selected_pub = None
                        st.rerun()
            with drink_cols[1]:
                if st.button("🥃 Jameson", key="quick_jameson", use_container_width=True):
                    drink_data = {
                        "user_id": user_id,
                        "pub": st.session_state.selected_pub,
                        "drink_type": "Jameson",
                        "timestamp": datetime.now().isoformat()
                    }
                    if append_to_sheet("Ratings", drink_data):
                        st.session_state.selected_pub = None
                        st.rerun()
            with drink_cols[2]:
                if st.button("🥤 Other", key="quick_other", use_container_width=True):
                    drink_data = {
                        "user_id": user_id,
                        "pub": st.session_state.selected_pub,
                        "drink_type": "Other",
                        "timestamp": datetime.now().isoformat()
                    }
                    if append_to_sheet("Ratings", drink_data):
                        st.session_state.selected_pub = None
                        st.rerun()

            if st.button("Cancel", key="cancel_drink"):
                st.session_state.selected_pub = None
                st.rerun()

        st.markdown("---")

    # Add new pub section
    with st.expander("ADD NEW PUB", expanded=not existing_pubs):
        with st.form("new_pub_drink"):
            pub_name = st.text_input("Pub Name:", placeholder="e.g., The Temple Bar")
            drink_type = st.radio("Drink Type:", ["🍺 Guinness", "🥃 Jameson", "🥤 Other"], horizontal=True)

            if st.form_submit_button("ADD DRINK", use_container_width=True):
                if pub_name:
                    # Clean up drink type (remove emoji)
                    clean_drink = drink_type.split(" ", 1)[1] if " " in drink_type else drink_type
                    drink_data = {
                        "user_id": user_id,
                        "pub": pub_name.strip(),
                        "drink_type": clean_drink,
                        "timestamp": datetime.now().isoformat()
                    }
                    if append_to_sheet("Ratings", drink_data):
                        st.success(f"Drink added at {pub_name}!")
                        st.rerun()
                else:
                    st.error("Please enter the pub name.")

    # Display drink counts by pub
    st.markdown("### DRINK TALLY")

    if ratings_df.empty:
        st.info("No drinks logged yet. Time to find a pub!")
    else:
        # Group by pub and count drinks
        pub_counts = ratings_df.groupby("pub").size().sort_values(ascending=False)

        for pub in pub_counts.index:
            pub_drinks = ratings_df[ratings_df["pub"] == pub]
            total = len(pub_drinks)

            # Count by drink type
            guinness_count = len(pub_drinks[pub_drinks.get("drink_type", pd.Series()) == "Guinness"]) if "drink_type" in pub_drinks.columns else 0
            jameson_count = len(pub_drinks[pub_drinks.get("drink_type", pd.Series()) == "Jameson"]) if "drink_type" in pub_drinks.columns else 0
            other_count = len(pub_drinks[pub_drinks.get("drink_type", pd.Series()) == "Other"]) if "drink_type" in pub_drinks.columns else 0

            # For legacy data without drink_type, count as Guinness
            if "drink_type" not in pub_drinks.columns or pub_drinks["drink_type"].isna().all():
                guinness_count = total

            drink_breakdown = []
            if guinness_count > 0:
                drink_breakdown.append(f"🍺 {guinness_count}")
            if jameson_count > 0:
                drink_breakdown.append(f"🥃 {jameson_count}")
            if other_count > 0:
                drink_breakdown.append(f"🥤 {other_count}")

            breakdown_str = " | ".join(drink_breakdown) if drink_breakdown else f"🍺 {total}"

            # Build per-person breakdown
            person_breakdown = []
            for person in pub_drinks["user_id"].unique():
                person_drinks = pub_drinks[pub_drinks["user_id"] == person]
                p_guinness = len(person_drinks[person_drinks.get("drink_type", pd.Series()) == "Guinness"]) if "drink_type" in person_drinks.columns else 0
                p_jameson = len(person_drinks[person_drinks.get("drink_type", pd.Series()) == "Jameson"]) if "drink_type" in person_drinks.columns else 0
                p_other = len(person_drinks[person_drinks.get("drink_type", pd.Series()) == "Other"]) if "drink_type" in person_drinks.columns else 0
                # Handle legacy data
                if "drink_type" not in person_drinks.columns or person_drinks["drink_type"].isna().all():
                    p_guinness = len(person_drinks)

                drinks_icons = ""
                if p_guinness > 0:
                    drinks_icons += "🍺" * p_guinness
                if p_jameson > 0:
                    drinks_icons += "🥃" * p_jameson
                if p_other > 0:
                    drinks_icons += "🥤" * p_other

                if drinks_icons:
                    person_breakdown.append(f"<strong>{person}:</strong> {drinks_icons}")

            person_html = "<br>".join(person_breakdown) if person_breakdown else ""

            st.markdown(f"""
            <div class="card">
                <strong style="font-size: 1.2rem;">{pub}</strong><br>
                <span style="color: #00994d; font-size: 1.3rem; font-weight: bold;">{total} drink{'s' if total != 1 else ''}</span>
                <span style="color: #555555; font-size: 0.9rem;">({breakdown_str})</span>
                <hr style="margin: 8px 0; border: none; border-top: 1px dashed #ccc;">
                <div style="font-size: 0.85rem;">{person_html}</div>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# FEATURE: QUOTE WALL
# =============================================================================

def render_quote_wall(user_id: str):
    """Render the quote wall - submit and vote on memorable quotes."""
    st.markdown("## QUOTE WALL")
    st.markdown("*Immortalize the best lines*")
    st.markdown("---")

    quotes_df = load_sheet_data("Quotes")

    # Submit new quote
    with st.expander("ADD A QUOTE", expanded=False):
        with st.form("new_quote"):
            speaker = st.selectbox("Who said it:", options=USERS)
            quote_text = st.text_area(
                "The quote:",
                placeholder="e.g., 'I'll just have one more...'",
                max_chars=300
            )

            if st.form_submit_button("SUBMIT QUOTE", use_container_width=True):
                if quote_text and len(quote_text.strip()) > 5:
                    quote_data = {
                        "submitter": user_id,
                        "speaker": speaker,
                        "quote": quote_text.strip(),
                        "timestamp": datetime.now().isoformat(),
                        "votes": 0,
                        "voters": ""
                    }
                    if append_to_sheet("Quotes", quote_data):
                        st.success("Quote added!")
                        st.rerun()
                else:
                    st.error("Please enter a proper quote (at least 5 characters).")

    # Show Quote of the Trip (most votes)
    if not quotes_df.empty and quotes_df["votes"].max() > 0:
        top_quote = quotes_df.loc[quotes_df["votes"].idxmax()]
        st.markdown("### QUOTE OF THE TRIP")
        st.markdown(f"""
        <div class="card" style="border-left: 8px solid #ffd700; background: linear-gradient(90deg, rgba(255,215,0,0.15) 0%, #ffffff 30%);">
            <span style="font-size: 1.5rem;">"{top_quote['quote']}"</span><br>
            <span style="color: #555555;">— {top_quote['speaker']}</span><br>
            <span style="color: #FF6B00; font-weight: bold;">👍 {int(top_quote['votes'])} votes</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

    # Display all quotes
    st.markdown("### ALL QUOTES")

    if quotes_df.empty:
        st.info("No quotes yet. Someone say something memorable!")
    else:
        # Sort by votes (descending), then by timestamp (newest first)
        quotes_df = quotes_df.sort_values(["votes", "timestamp"], ascending=[False, False])

        for idx, quote in quotes_df.iterrows():
            voters_list = str(quote.get("voters", "")).split(",") if quote.get("voters") else []
            voters_list = [v for v in voters_list if v]  # Remove empty strings
            user_voted = user_id in voters_list
            vote_count = int(quote["votes"]) if pd.notna(quote["votes"]) else 0

            st.markdown(f"""
            <div class="card">
                <span style="font-size: 1.2rem;">"{quote['quote']}"</span><br>
                <span style="color: #555555;">— {quote['speaker']}</span>
                <span style="color: #888888; font-size: 0.8rem;">(submitted by {quote['submitter']})</span><br>
                <span style="color: #FF6B00; font-weight: bold;">👍 {vote_count}</span>
            </div>
            """, unsafe_allow_html=True)

            # Vote button
            if not user_voted:
                if st.button(f"👍 Vote", key=f"vote_quote_{idx}", use_container_width=True):
                    quotes_df.loc[idx, "votes"] = vote_count + 1
                    quotes_df.loc[idx, "voters"] = ",".join(voters_list + [user_id])
                    update_sheet("Quotes", quotes_df)
                    st.rerun()
            else:
                st.caption("You voted for this quote.")

            st.markdown("")


# =============================================================================
# FEATURE: SIDE BETS
# =============================================================================

def render_side_bets(user_id: str):
    """Render side bets - prop bets between friends."""
    st.markdown("## SIDE BETS")
    st.markdown("*Prop bets for bragging rights*")
    st.markdown("---")

    sidebets_df = load_sheet_data("SideBets")

    # Create new bet
    with st.expander("CREATE A BET", expanded=False):
        with st.form("new_sidebet"):
            # Select opponent
            opponents = [u for u in USERS if u != user_id]
            opponent = st.selectbox("Bet against:", options=opponents)

            description = st.text_area(
                "The Bet:",
                placeholder="e.g., 'Dom won't last past midnight'",
                max_chars=200
            )
            stake = st.number_input("Points at Stake:", min_value=5, max_value=100, value=10, step=5)

            if st.form_submit_button("CREATE BET", use_container_width=True):
                if description and len(description.strip()) > 10:
                    bet_data = {
                        "creator": user_id,
                        "description": description.strip(),
                        "stake": stake,
                        "timestamp": datetime.now().isoformat(),
                        "taker": opponent,
                        "result": "OPEN",
                        "settled_by": ""
                    }
                    if append_to_sheet("SideBets", bet_data):
                        st.success(f"Bet created with {opponent}!")
                        st.rerun()
                else:
                    st.error("Please describe the bet (at least 10 characters).")

    # Active bets (pending settlement)
    st.markdown("### ACTIVE BETS")

    if sidebets_df.empty:
        st.info("No bets yet. Create one!")
    else:
        open_bets = sidebets_df[sidebets_df["result"] == "OPEN"]

        if open_bets.empty:
            st.info("No active bets right now.")
        else:
            for idx, bet in open_bets.iterrows():
                creator = bet["creator"]
                taker = bet["taker"]
                is_creator = creator == user_id
                is_taker = taker == user_id
                is_involved = is_creator or is_taker

                st.markdown(f"""
                <div class="card" style="border-left: 4px solid #cc9900;">
                    <strong>{creator}</strong> vs <strong>{taker}</strong><br>
                    <span style="font-size: 1.1rem;">"{bet['description']}"</span><br>
                    <span style="color: #FF6B00; font-weight: bold;">{int(bet['stake'])} pts</span>
                </div>
                """, unsafe_allow_html=True)

                # Settle bet (either party can settle)
                if is_involved:
                    st.markdown("**Settle this bet:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"{creator} WON", key=f"creator_won_{idx}", use_container_width=True):
                            sidebets_df.loc[idx, "result"] = "WIN"
                            sidebets_df.loc[idx, "settled_by"] = user_id
                            update_sheet("SideBets", sidebets_df)
                            st.rerun()
                    with col2:
                        if st.button(f"{taker} WON", key=f"taker_won_{idx}", use_container_width=True):
                            sidebets_df.loc[idx, "result"] = "LOSS"
                            sidebets_df.loc[idx, "settled_by"] = user_id
                            update_sheet("SideBets", sidebets_df)
                            st.rerun()

                    # Delete option with confirmation
                    delete_key = f"delete_confirm_{idx}"
                    if delete_key not in st.session_state:
                        st.session_state[delete_key] = False

                    if not st.session_state[delete_key]:
                        if st.button("🗑️ Delete Bet", key=f"delete_{idx}", use_container_width=True):
                            st.session_state[delete_key] = True
                            st.rerun()
                    else:
                        st.warning("Are you sure you want to delete this bet?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("YES, DELETE", key=f"confirm_delete_{idx}", use_container_width=True):
                                sidebets_df = sidebets_df.drop(idx)
                                update_sheet("SideBets", sidebets_df)
                                st.session_state[delete_key] = False
                                st.rerun()
                        with col2:
                            if st.button("CANCEL", key=f"cancel_delete_{idx}", use_container_width=True):
                                st.session_state[delete_key] = False
                                st.rerun()

                st.markdown("")

    # Settled bets
    st.markdown("---")
    st.markdown("### SETTLED BETS")

    if not sidebets_df.empty:
        settled_bets = sidebets_df[sidebets_df["result"].isin(["WIN", "LOSS"])]

        if settled_bets.empty:
            st.info("No settled bets yet.")
        else:
            for idx, bet in settled_bets.iterrows():
                result = bet["result"]
                creator = bet["creator"]
                taker = bet["taker"]
                stake = int(bet["stake"])

                # Determine winner/loser
                if result == "WIN":
                    winner = creator
                    loser = taker
                else:
                    winner = taker
                    loser = creator

                result_color = "#00994d"

                st.markdown(f"""
                <div class="card" style="border-left: 4px solid {result_color};">
                    <span style="font-size: 1rem;">"{bet['description']}"</span><br>
                    <span style="color: #00994d; font-weight: bold;">🏆 {winner} wins {stake} pts from {loser}</span>
                </div>
                """, unsafe_allow_html=True)


# =============================================================================
# FEATURE: DAILY MVP
# =============================================================================

def render_mvp_vote(user_id: str):
    """Render MVP voting - vote for each day's MVP."""
    st.markdown("## DAILY MVP")
    st.markdown("*Vote for today's Most Valuable Player*")
    st.markdown("---")

    mvp_df = load_sheet_data("MVPVotes")
    today = datetime.now().strftime("%Y-%m-%d")

    # Current day voting
    st.markdown("### VOTE FOR TODAY'S MVP")

    # Check if user already voted today
    user_voted_today = False
    current_vote = None
    if not mvp_df.empty:
        user_today_votes = mvp_df[(mvp_df["voter"] == user_id) & (mvp_df["day"] == today)]
        if not user_today_votes.empty:
            user_voted_today = True
            current_vote = user_today_votes.iloc[-1]["nominee"]

    if user_voted_today:
        st.info(f"You voted for **{current_vote}** today. You can change your vote below.")

    # Vote buttons (grid of user names)
    st.markdown("*Tap a name to vote:*")
    other_users = [u for u in USERS if u != user_id]
    cols = st.columns(2)
    for i, nominee in enumerate(other_users):
        with cols[i % 2]:
            btn_label = f"⭐ {nominee}" if nominee == current_vote else nominee
            if st.button(btn_label, key=f"mvp_{nominee}", use_container_width=True):
                if user_voted_today:
                    # Update existing vote
                    for idx, row in mvp_df.iterrows():
                        if row["voter"] == user_id and row["day"] == today:
                            mvp_df.loc[idx, "nominee"] = nominee
                            mvp_df.loc[idx, "timestamp"] = datetime.now().isoformat()
                    update_sheet("MVPVotes", mvp_df)
                else:
                    # New vote
                    vote_data = {
                        "voter": user_id,
                        "nominee": nominee,
                        "day": today,
                        "timestamp": datetime.now().isoformat()
                    }
                    append_to_sheet("MVPVotes", vote_data)
                st.rerun()

    # Today's standings
    st.markdown("---")
    st.markdown("### TODAY'S STANDINGS")

    if mvp_df.empty:
        st.info("No votes yet today.")
    else:
        today_votes = mvp_df[mvp_df["day"] == today]
        if today_votes.empty:
            st.info("No votes yet today.")
        else:
            # Count votes per nominee
            vote_counts = today_votes.groupby("nominee").size().sort_values(ascending=False)

            for nominee, count in vote_counts.items():
                is_leader = nominee == vote_counts.index[0]
                leader_style = "border-left: 8px solid #ffd700; background: linear-gradient(90deg, rgba(255,215,0,0.15) 0%, #ffffff 30%);" if is_leader else ""

                st.markdown(f"""
                <div class="card" style="{leader_style}">
                    <span style="font-weight: bold; font-size: 1.1rem;">{'⭐ ' if is_leader else ''}{nominee}</span>
                    <span style="color: #FF6B00; font-weight: bold; float: right;">{count} vote{'s' if count != 1 else ''}</span>
                </div>
                """, unsafe_allow_html=True)

    # Past MVP Winners
    st.markdown("---")
    st.markdown("### PAST MVP WINNERS")

    if not mvp_df.empty:
        past_days = [d for d in mvp_df["day"].unique() if d != today]
        past_days = sorted(past_days, reverse=True)

        if not past_days:
            st.info("No past winners yet.")
        else:
            for day in past_days:
                day_votes = mvp_df[mvp_df["day"] == day]
                vote_counts = day_votes.groupby("nominee").size().sort_values(ascending=False)

                if not vote_counts.empty:
                    winner = vote_counts.index[0]
                    winner_votes = vote_counts.iloc[0]

                    st.markdown(f"""
                    <div class="card">
                        <strong>{day}</strong><br>
                        <span style="color: #FF6B00; font-weight: bold;">🏆 {winner}</span>
                        <span style="color: #555555;">({winner_votes} votes)</span>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("No past winners yet.")


# =============================================================================
# FEATURE: PHOTO WALL
# =============================================================================

def render_photo_wall(user_id: str):
    """Render the photo wall - upload and view trip photos."""
    st.markdown("## PHOTO WALL")
    st.markdown("*Capture the memories*")
    st.markdown("---")

    photos_df = load_sheet_data("Photos")

    # Check if Cloudinary is configured
    cloudinary_configured = False
    try:
        if st.secrets.get("CLOUDINARY_CLOUD_NAME"):
            cloudinary_configured = True
    except:
        pass

    if not cloudinary_configured:
        st.warning("Photo uploads not configured yet. Ask James to set up Cloudinary!")
    else:
        # Upload new photo
        with st.expander("UPLOAD A PHOTO", expanded=False):
            uploaded_file = st.file_uploader(
                "Choose an image",
                type=["jpg", "jpeg", "png", "heic"],
                key="photo_upload"
            )

            caption = st.text_input("Caption (optional):", placeholder="e.g., 'First pint at Temple Bar'")

            if uploaded_file is not None:
                # Show preview
                st.image(uploaded_file, caption="Preview", use_container_width=True)

                if st.button("UPLOAD PHOTO", use_container_width=True):
                    with st.spinner("Uploading..."):
                        image_url = upload_image_to_cloudinary(uploaded_file)

                        if image_url:
                            photo_data = {
                                "uploader": user_id,
                                "caption": caption.strip() if caption else "",
                                "image_url": image_url,
                                "timestamp": datetime.now().isoformat(),
                                "likes": 0,
                                "likers": ""
                            }
                            if append_to_sheet("Photos", photo_data):
                                st.success("Photo uploaded!")
                                st.rerun()

    # Display photo gallery
    st.markdown("### THE GALLERY")

    if photos_df.empty or "uploader" not in photos_df.columns:
        st.info("No photos yet. Be the first to capture a moment!")
    else:
        # Sort by timestamp (newest first)
        photos_df = photos_df.sort_values("timestamp", ascending=False)

        # Display photos
        for idx, photo in photos_df.iterrows():
            # Safely get likers
            likers_raw = photo.get("likers", "") if "likers" in photos_df.columns else ""
            likers_list = str(likers_raw).split(",") if pd.notna(likers_raw) and likers_raw else []
            likers_list = [l.strip() for l in likers_list if l.strip()]  # Remove empty strings
            user_liked = user_id in likers_list

            # Safely convert likes to int
            like_count = 0
            if "likes" in photos_df.columns:
                try:
                    likes_val = photo.get("likes", 0)
                    if pd.notna(likes_val) and str(likes_val).strip() != "":
                        like_count = int(float(likes_val))
                except (ValueError, TypeError):
                    like_count = 0

            st.markdown(f"""
            <div class="card" style="padding: 0.5rem;">
                <img src="{photo['image_url']}" style="width: 100%; border: 2px solid #1a1a1a;">
                <div style="padding: 0.5rem 0;">
                    <strong>{photo['uploader']}</strong>
                    {f'<br><span style="color: #555555;">{photo["caption"]}</span>' if photo.get('caption') else ''}
                    <br><span style="color: #888888; font-size: 0.75rem;">{photo['timestamp'][:10]}</span>
                    <br><span style="color: #FF6B00; font-weight: bold;">❤️ {like_count}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Like button (can't like own photos)
            if photo['uploader'] != user_id:
                if not user_liked:
                    if st.button(f"❤️ Like", key=f"like_photo_{idx}", use_container_width=True):
                        photos_df.loc[idx, "likes"] = like_count + 1
                        photos_df.loc[idx, "likers"] = ",".join(likers_list + [user_id])
                        update_sheet("Photos", photos_df)
                        st.rerun()
                else:
                    st.caption("You liked this photo.")

            st.markdown("")


# =============================================================================
# FEATURE: LEADERBOARD
# =============================================================================

def calculate_scores() -> pd.DataFrame:
    """Calculate scores for all users based on all activities."""
    rules_df = load_sheet_data("Rules")
    inquiries_df = load_sheet_data("Inquiries")
    bets_df = load_sheet_data("Bets")
    ratings_df = load_sheet_data("Ratings")
    sidebets_df = load_sheet_data("SideBets")
    mvp_df = load_sheet_data("MVPVotes")
    quotes_df = load_sheet_data("Quotes")
    photos_df = load_sheet_data("Photos")

    # Determine Quote of the Trip winner (submitter of top-voted quote)
    quote_of_trip_submitter = None
    if not quotes_df.empty and quotes_df["votes"].max() > 0:
        top_quote = quotes_df.loc[quotes_df["votes"].idxmax()]
        quote_of_trip_submitter = top_quote["submitter"]

    # Get all users
    all_users = set()
    if not rules_df.empty:
        all_users.update(rules_df["user_id"].unique())

    scores = []

    for user in all_users:
        score = 0
        breakdown = []
        line_items = []

        # Points for submitting a rule (+10)
        if not rules_df.empty and user in rules_df["user_id"].values:
            score += 10
            breakdown.append("Rule: +10")
            line_items.append({"action": "Steward's Rule submitted", "points": 10, "icon": "📜"})

        # Points for drinks - Guinness: +5, Jameson: +5, Other: 0
        if not ratings_df.empty:
            user_ratings_df = ratings_df[ratings_df["user_id"] == user]
            if len(user_ratings_df) > 0:
                drink_points = 0
                for _, rating in user_ratings_df.iterrows():
                    pub_name = rating.get("pub", "Unknown Pub")
                    drink_type = rating.get("drink_type", "Guinness") if "drink_type" in rating.index else "Guinness"
                    # Handle NaN drink_type
                    if pd.isna(drink_type):
                        drink_type = "Guinness"
                    # Set icon and points based on drink type
                    if drink_type == "Guinness":
                        icon = "🍺"
                        pts = 5
                    elif drink_type == "Jameson":
                        icon = "🥃"
                        pts = 5
                    else:
                        icon = "🥤"
                        pts = 0
                    score += pts
                    drink_points += pts
                    if pts > 0:
                        line_items.append({"action": f"{pub_name} ({drink_type})", "points": pts, "icon": icon})
                if drink_points > 0:
                    breakdown.append(f"Drinks: +{drink_points}")

        # Points for betting (wins/losses) - euro-based, with horse names
        if not bets_df.empty:
            user_bets = bets_df[bets_df["user_id"] == user]
            wins = user_bets[user_bets["result"] == "WIN"]
            losses = user_bets[user_bets["result"] == "LOSS"]

            # Individual winning bets
            if len(wins) > 0:
                total_profit = 0
                for _, bet in wins.iterrows():
                    profit = int(bet["payout"] - bet["stake"])
                    total_profit += profit
                    race_num = int(bet["race_num"])
                    horse = bet.get("horse", "Unknown")
                    line_items.append({
                        "action": f"Race {race_num}: {horse} (WIN)",
                        "points": profit,
                        "icon": "🏇"
                    })
                score += total_profit
                breakdown.append(f"Bet winnings: +{total_profit}")

            # Individual losing bets
            if len(losses) > 0:
                total_lost = 0
                for _, bet in losses.iterrows():
                    lost = int(bet["stake"])
                    total_lost += lost
                    race_num = int(bet["race_num"])
                    horse = bet.get("horse", "Unknown")
                    line_items.append({
                        "action": f"Race {race_num}: {horse} (LOSS)",
                        "points": -lost,
                        "icon": "🏇"
                    })
                score -= total_lost
                breakdown.append(f"Bet losses: -{total_lost}")

        # Points for inquiries filed (+5 each) - with accused names
        if not inquiries_df.empty:
            filed_inquiries = inquiries_df[inquiries_df["reporter"] == user]
            if len(filed_inquiries) > 0:
                for _, inquiry in filed_inquiries.iterrows():
                    accused = inquiry.get("accused", "Unknown")
                    score += 5
                    line_items.append({
                        "action": f"Filed inquiry vs {accused}",
                        "points": 5,
                        "icon": "⚖️"
                    })
                breakdown.append(f"Inquiries filed: +{len(filed_inquiries) * 5}")

            # Penalty for being found guilty (-20 each)
            guilty_cases = inquiries_df[
                (inquiries_df["accused"] == user) &
                (inquiries_df["guilty_votes"] > inquiries_df["innocent_votes"])
            ]
            if len(guilty_cases) > 0:
                for _, case in guilty_cases.iterrows():
                    rule = str(case.get("rule_violated", ""))[:30]
                    score -= 20
                    line_items.append({
                        "action": f"Found GUILTY: {rule}...",
                        "points": -20,
                        "icon": "🚨"
                    })
                breakdown.append(f"Guilty verdicts: -{len(guilty_cases) * 20}")

        # Points for side bets
        if not sidebets_df.empty:
            # Bets user created and won
            user_created_won = sidebets_df[
                (sidebets_df["creator"] == user) &
                (sidebets_df["result"] == "WIN")
            ]
            for _, bet in user_created_won.iterrows():
                stake = int(bet["stake"])
                desc = str(bet["description"])[:30]
                score += stake
                line_items.append({
                    "action": f"Side bet won: {desc}...",
                    "points": stake,
                    "icon": "🎲"
                })

            # Bets user created and lost
            user_created_lost = sidebets_df[
                (sidebets_df["creator"] == user) &
                (sidebets_df["result"] == "LOSS")
            ]
            for _, bet in user_created_lost.iterrows():
                stake = int(bet["stake"])
                desc = str(bet["description"])[:30]
                score -= stake
                line_items.append({
                    "action": f"Side bet lost: {desc}...",
                    "points": -stake,
                    "icon": "🎲"
                })

            # Bets user took and won (creator lost = taker won)
            user_took_won = sidebets_df[
                (sidebets_df["taker"] == user) &
                (sidebets_df["result"] == "LOSS")
            ]
            for _, bet in user_took_won.iterrows():
                stake = int(bet["stake"])
                desc = str(bet["description"])[:30]
                score += stake
                line_items.append({
                    "action": f"Side bet won: {desc}...",
                    "points": stake,
                    "icon": "🎲"
                })

            # Bets user took and lost (creator won = taker lost)
            user_took_lost = sidebets_df[
                (sidebets_df["taker"] == user) &
                (sidebets_df["result"] == "WIN")
            ]
            for _, bet in user_took_lost.iterrows():
                stake = int(bet["stake"])
                desc = str(bet["description"])[:30]
                score -= stake
                line_items.append({
                    "action": f"Side bet lost: {desc}...",
                    "points": -stake,
                    "icon": "🎲"
                })

            # Tally for breakdown
            total_sb_won = len(user_created_won) + len(user_took_won)
            total_sb_lost = len(user_created_lost) + len(user_took_lost)
            if total_sb_won > 0 or total_sb_lost > 0:
                breakdown.append(f"Side bets: {total_sb_won}W/{total_sb_lost}L")

        # Points for MVP wins (+25 per day)
        if not mvp_df.empty:
            # Get all unique days
            all_days = mvp_df["day"].unique()
            mvp_wins = 0
            for day in all_days:
                day_votes = mvp_df[mvp_df["day"] == day]
                vote_counts = day_votes.groupby("nominee").size()
                if not vote_counts.empty:
                    winner = vote_counts.idxmax()
                    if winner == user:
                        mvp_wins += 1
                        score += 25
                        line_items.append({
                            "action": f"MVP Winner: {day}",
                            "points": 25,
                            "icon": "⭐"
                        })
            if mvp_wins > 0:
                breakdown.append(f"MVP wins: +{mvp_wins * 25}")

        # Points for Quote of the Trip (+25)
        if quote_of_trip_submitter == user:
            score += 25
            line_items.append({
                "action": "Quote of the Trip",
                "points": 25,
                "icon": "💬"
            })
            breakdown.append("Quote of Trip: +25")

        # Points for photos (+2 per photo, +1 per like received)
        if not photos_df.empty and "uploader" in photos_df.columns:
            user_photos = photos_df[photos_df["uploader"] == user]
            if len(user_photos) > 0:
                photo_count = len(user_photos)
                photo_points = photo_count * 2
                score += photo_points
                line_items.append({
                    "action": f"Photos uploaded ({photo_count})",
                    "points": photo_points,
                    "icon": "📸"
                })

                # Count likes received
                total_likes = 0
                if "likes" in photos_df.columns:
                    for _, photo in user_photos.iterrows():
                        try:
                            likes = int(photo["likes"]) if pd.notna(photo.get("likes")) and str(photo["likes"]).strip() != "" else 0
                        except (ValueError, TypeError):
                            likes = 0
                        total_likes += likes

                if total_likes > 0:
                    score += total_likes
                    line_items.append({
                        "action": f"Photo likes received ({total_likes})",
                        "points": total_likes,
                        "icon": "❤️"
                    })

                breakdown.append(f"Photos: +{photo_points + total_likes}")

        scores.append({
            "user": user,
            "score": score,
            "breakdown": " | ".join(breakdown) if breakdown else "No activity",
            "line_items": line_items
        })

    return pd.DataFrame(scores).sort_values("score", ascending=False).reset_index(drop=True)

def render_leaderboard():
    """Render the live leaderboard."""
    scores_df = calculate_scores()

    st.markdown("## LEADERBOARD")
    st.markdown("*Live standings*")
    st.markdown("---")

    if scores_df.empty:
        st.info("No scores yet. Get involved!")
        return

    # Points system explanation
    with st.expander("SCORING SYSTEM"):
        st.markdown("""
        - **Submit a rule:** +10 pts
        - **File an inquiry:** +5 pts
        - **Found guilty:** -20 pts
        - **Winning bet:** +profit (payout - stake)
        - **Losing bet:** -stake
        - **🍺 Guinness:** +5 pts
        - **🥃 Jameson:** +5 pts
        - **🥤 Other:** +0 pts
        - **Side bet win:** +stake pts
        - **Side bet loss:** -stake pts
        - **Daily MVP:** +25 pts
        - **Quote of the Trip:** +25 pts
        - **📸 Photo uploaded:** +2 pts
        - **❤️ Photo like received:** +1 pt
        """)

    st.markdown("")

    # Display leaderboard
    for idx, row in scores_df.iterrows():
        rank = idx + 1
        rank_class = f"rank-{rank}" if rank <= 3 else ""

        medal = ""
        if rank == 1:
            medal = "🥇 "
        elif rank == 2:
            medal = "🥈 "
        elif rank == 3:
            medal = "🥉 "

        st.markdown(f"""
        <div class="leader-row {rank_class}">
            <span class="leader-name">{medal}{row['user']}</span>
            <span class="leader-score">{row['score']} pts</span>
        </div>
        """, unsafe_allow_html=True)

        # Show receipt-style breakdown on expand
        with st.expander(f"Details for {row['user']}", expanded=False):
            line_items = row.get("line_items", [])
            if line_items:
                # Build receipt HTML - keep on single lines to avoid rendering issues
                receipt_lines = []
                for item in line_items:
                    points = item["points"]
                    sign = "+" if points >= 0 else ""
                    color = "#00994d" if points >= 0 else "#cc0000"
                    receipt_lines.append(
                        f'<div style="display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #cccccc;">'
                        f'<span>{item["icon"]} {item["action"]}</span>'
                        f'<span style="color: {color}; font-weight: 700;">{sign}{points}</span>'
                        f'</div>'
                    )

                lines_html = ''.join(receipt_lines)
                receipt_html = (
                    f'<div style="background-color: #fffff8; border: 2px solid #1a1a1a; padding: 1rem; font-family: JetBrains Mono, monospace; font-size: 0.85rem;">'
                    f'<div style="text-align: center; font-weight: 800; font-size: 1rem; border-bottom: 2px solid #1a1a1a; padding-bottom: 8px; margin-bottom: 8px;">'
                    f'{row["user"].upper()}\'S SCORECARD'
                    f'</div>'
                    f'{lines_html}'
                    f'<div style="display: flex; justify-content: space-between; padding-top: 8px; margin-top: 8px; border-top: 2px solid #1a1a1a; font-weight: 800; font-size: 1.1rem;">'
                    f'<span>TOTAL</span>'
                    f'<span style="color: #FF6B00;">{row["score"]}</span>'
                    f'</div>'
                    f'</div>'
                )
                st.markdown(receipt_html, unsafe_allow_html=True)
            else:
                st.caption("No activity yet.")

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    """Main app entry point."""
    # Get current user from session state
    user_id = get_current_user()

    # Not logged in - show login page
    if not user_id:
        render_login_page()
        return

    # Check if user has seen intro page
    if not st.session_state.get("seen_intro", False):
        render_intro_page(user_id)
        return

    # Check if user has submitted a rule (gate)
    if not check_user_submitted_rule(user_id):
        render_legislation_gate(user_id)
        return

    # Show current user with logout option
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Logged in as:** `{user_id}`")
    with col2:
        if st.button("Logout", key="logout_btn"):
            del st.session_state["authenticated_user"]
            del st.session_state["seen_intro"]
            st.rerun()

    # Main app navigation
    render_header()

    # Manual refresh button to avoid rate limits
    if st.button("REFRESH DATA", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Tab navigation
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "RULES",
        "INQUIRY",
        "BETS",
        "DRINKS",
        "QUOTES",
        "SIDE BETS",
        "MVP",
        "PHOTOS",
        "SCORES"
    ])

    with tab1:
        # Show all rules
        st.markdown("## THE RULES")
        rules_df = load_sheet_data("Rules")
        if not rules_df.empty:
            for _, rule in rules_df.iterrows():
                st.markdown(f"""
                <div class="card">
                    <strong>{rule['user_id']}'s Rule:</strong><br>
                    {rule['rule']}
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        render_stewards_inquiry(user_id)

    with tab3:
        render_leopardstown_ledger(user_id)

    with tab4:
        render_pint_critic(user_id)

    with tab5:
        render_quote_wall(user_id)

    with tab6:
        render_side_bets(user_id)

    with tab7:
        render_mvp_vote(user_id)

    with tab8:
        render_photo_wall(user_id)

    with tab9:
        render_leaderboard()

if __name__ == "__main__":
    main()
