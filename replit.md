# Clash Royale Player Analyzer

## Overview
A Streamlit web application that analyzes Clash Royale player data and provides personalized improvement tips.

## Features
- Player profile lookup with stats (trophies, wins, losses, arena)
- Recent battle analysis with win rates by game mode
- Card performance tracking (which cards you win most with)
- Upcoming chest schedule
- Personalized improvement tips based on gameplay analysis
- Arena-specific advice

## Tech Stack
- **Framework:** Streamlit
- **Language:** Python 3.11
- **API:** Official Clash Royale API via RoyaleAPI proxy

## Setup
1. Get an API token from https://developer.clashroyale.com
2. Whitelist IP: `45.79.218.79` for the proxy
3. Enter your token in the sidebar
4. Enter a player tag to analyze

## Running the App
```bash
streamlit run app.py --server.port 5000
```

## Project Structure
- `app.py` - Main Streamlit application
- `.streamlit/config.toml` - Streamlit configuration
