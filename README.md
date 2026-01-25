# Dublin Racing Trip 2025

A mobile-first Streamlit app for tracking Dublin racing trip activities with a brutalist design aesthetic.

## Features

- **Rules** - Steward's Rule submission system
- **Inquiry** - File and vote on rule violations
- **Bets** - Leopardstown race betting tracker with fractional odds
- **Pints** - Guinness rating system across Dublin pubs
- **Scores** - Live leaderboard with point breakdowns

## Local Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
4. Add your Google Sheets API credentials to `secrets.toml`
5. Run: `streamlit run app.py`

## Access

Use URL parameter `?id=yourname` to identify yourself.

Example: `https://your-app.streamlit.app?id=james`

## Tech Stack

- Streamlit
- Google Sheets (backend)
- JetBrains Mono font
- Brutalist CSS design
