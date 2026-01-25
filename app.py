"""
Dublin Trip App - The White Jersey
A Streamlit mobile app for tracking Dublin trip activities.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Optional
from streamlit_gsheets import GSheetsConnection

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

def render_logo():
    """Render brutalist logo header."""
    st.markdown("""
    <div style="
        font-family: 'JetBrains Mono', 'Courier New', monospace;
        background: #1a1a1a;
        border: 4px solid #FF6B00;
        padding: 16px;
        text-align: center;
        margin-bottom: 16px;
    ">
        <div style="
            color: #00994d;
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: 0.25em;
            line-height: 1.2;
        ">DUBLIN</div>
        <div style="
            color: #FF6B00;
            font-size: 0.9rem;
            letter-spacing: 0.4em;
            border-top: 2px solid #00994d;
            border-bottom: 2px solid #00994d;
            padding: 6px 0;
            margin: 6px 0;
        ">RACING TRIP</div>
        <div style="
            color: #ffffff;
            font-size: 1.2rem;
            font-weight: 700;
            letter-spacing: 0.3em;
        ">2025</div>
    </div>
    """, unsafe_allow_html=True)

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

    /* Mobile-friendly container */
    .block-container {
        padding: 1rem 1rem !important;
        max-width: 100% !important;
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
# USER IDENTIFICATION
# =============================================================================

def get_current_user() -> Optional[str]:
    """Get current user from query params (?id=name)."""
    params = st.query_params
    user_id = params.get("id", None)
    return user_id

def check_user_submitted_rule(user_id: str) -> bool:
    """Check if user has submitted a Steward's Rule."""
    rules_df = load_sheet_data("Rules")
    if rules_df.empty:
        return False
    return user_id in rules_df["user_id"].values

# =============================================================================
# FEATURE: LEGISLATION (Landing Page)
# =============================================================================

def render_legislation_gate(user_id: str):
    """Render the Steward's Rule submission gate."""
    st.markdown("# LEGISLATION")
    st.markdown("---")

    st.markdown("""
    <div class="card">
        <h3>Welcome to Dublin 2025</h3>
        <p>Before entering, you must propose ONE Steward's Rule
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
    """Render the Guinness rating system."""
    st.markdown("## PINT CRITIC")
    st.markdown("*Rate your Guinness experiences*")
    st.markdown("---")

    ratings_df = load_sheet_data("Ratings")

    # Submit new rating
    with st.expander("RATE A PINT", expanded=True):
        with st.form("new_rating"):
            pub_name = st.text_input("Pub Name:", placeholder="e.g., The Temple Bar")

            rating = st.slider("Guinness Rating:", min_value=1, max_value=10, value=7)

            # Visual representation
            rating_display = "🍺" * rating + "⚫" * (10 - rating)
            st.markdown(f"### {rating_display}")
            st.markdown(f"**{rating}/10**")

            notes = st.text_input("Tasting Notes (optional):", placeholder="e.g., Perfect dome, creamy")

            if st.form_submit_button("SUBMIT RATING", use_container_width=True):
                if pub_name:
                    rating_data = {
                        "user_id": user_id,
                        "pub": pub_name.strip(),
                        "rating": rating,
                        "notes": notes.strip() if notes else "",
                        "timestamp": datetime.now().isoformat()
                    }
                    if append_to_sheet("Ratings", rating_data):
                        st.success(f"Rating submitted for {pub_name}!")
                        st.rerun()
                else:
                    st.error("Please enter the pub name.")

    # Display ratings
    st.markdown("### ALL RATINGS")

    if ratings_df.empty:
        st.info("No ratings yet. Time to find a pub!")
    else:
        # Group by pub and show average
        pub_averages = ratings_df.groupby("pub")["rating"].mean().sort_values(ascending=False)

        for pub, avg in pub_averages.items():
            pub_ratings = ratings_df[ratings_df["pub"] == pub]
            count = len(pub_ratings)

            st.markdown(f"""
            <div class="card">
                <strong style="font-size: 1.2rem;">{pub}</strong><br>
                <span style="color: #00994d; font-size: 1.5rem; font-weight: bold;">{avg:.1f}/10</span>
                <span style="color: #555555;">({count} rating{'s' if count > 1 else ''})</span>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# FEATURE: LEADERBOARD
# =============================================================================

def calculate_scores() -> pd.DataFrame:
    """Calculate scores for all users based on all activities."""
    rules_df = load_sheet_data("Rules")
    inquiries_df = load_sheet_data("Inquiries")
    bets_df = load_sheet_data("Bets")
    ratings_df = load_sheet_data("Ratings")

    # Get all users
    all_users = set()
    if not rules_df.empty:
        all_users.update(rules_df["user_id"].unique())

    scores = []

    for user in all_users:
        score = 0
        breakdown = []

        # Points for submitting a rule (+10)
        if not rules_df.empty and user in rules_df["user_id"].values:
            score += 10
            breakdown.append("Rule: +10")

        # Points for inquiries filed (+5 each)
        if not inquiries_df.empty:
            filed = len(inquiries_df[inquiries_df["reporter"] == user])
            if filed > 0:
                score += filed * 5
                breakdown.append(f"Inquiries filed: +{filed * 5}")

            # Penalty for being found guilty (-20 each)
            guilty_cases = inquiries_df[
                (inquiries_df["accused"] == user) &
                (inquiries_df["guilty_votes"] > inquiries_df["innocent_votes"])
            ]
            if len(guilty_cases) > 0:
                penalty = len(guilty_cases) * 20
                score -= penalty
                breakdown.append(f"Guilty verdicts: -{penalty}")

        # Points for betting (wins/losses) - euro-based
        if not bets_df.empty:
            user_bets = bets_df[bets_df["user_id"] == user]
            wins = user_bets[user_bets["result"] == "WIN"]
            losses = user_bets[user_bets["result"] == "LOSS"]

            # Profit from winning bets (payout - stake)
            if len(wins) > 0:
                profit = wins["payout"].sum() - wins["stake"].sum()
                score += int(profit)
                breakdown.append(f"Bet winnings: +{int(profit)}")

            # Lose stake from losing bets
            if len(losses) > 0:
                lost = losses["stake"].sum()
                score -= int(lost)
                breakdown.append(f"Bet losses: -{int(lost)}")

        # Points for Guinness ratings (+2 each)
        if not ratings_df.empty:
            user_ratings = len(ratings_df[ratings_df["user_id"] == user])
            if user_ratings > 0:
                score += user_ratings * 2
                breakdown.append(f"Pint ratings: +{user_ratings * 2}")

        scores.append({
            "user": user,
            "score": score,
            "breakdown": " | ".join(breakdown) if breakdown else "No activity"
        })

    return pd.DataFrame(scores).sort_values("score", ascending=False).reset_index(drop=True)

def render_leaderboard():
    """Render the live leaderboard."""
    st.markdown("## LEADERBOARD")
    st.markdown("*Live standings*")
    st.markdown("---")

    scores_df = calculate_scores()

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
        - **Rate a Guinness:** +2 pts
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

        # Show breakdown on expand
        with st.expander(f"Details for {row['user']}", expanded=False):
            st.caption(row['breakdown'])

# =============================================================================
# MAIN APP
# =============================================================================

def main():
    """Main app entry point."""
    # Get current user from query params
    user_id = get_current_user()

    # No user ID provided
    if not user_id:
        render_logo()
        st.markdown("---")
        st.error("No user ID provided.")
        st.markdown("Access the app with `?id=yourname` in the URL.")
        st.markdown("Example: `https://yourapp.streamlit.app?id=james`")
        return

    # Show current user
    st.markdown(f"**Logged in as:** `{user_id}`")

    # Check if user has submitted a rule (gate)
    if not check_user_submitted_rule(user_id):
        render_legislation_gate(user_id)
        return

    # Main app navigation
    render_logo()

    # Manual refresh button to avoid rate limits
    if st.button("REFRESH DATA", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Tab navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "RULES",
        "INQUIRY",
        "BETS",
        "PINTS",
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
        render_leaderboard()

if __name__ == "__main__":
    main()
