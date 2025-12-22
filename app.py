import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import quote

st.set_page_config(
    page_title="Clash Royale Analyzer",
    page_icon="⚔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3), inset 0 1px 0 rgba(255,255,255,0.1); }
        50% { box-shadow: 0 10px 50px rgba(102, 126, 234, 0.5), inset 0 1px 0 rgba(255,255,255,0.15); }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Main container padding */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #5a4a96 100%);
        padding: 2.5rem 3rem;
        border-radius: 24px;
        margin: 0 auto 2.5rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4), inset 0 1px 0 rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.1);
        animation: glow 3s ease-in-out infinite;
        position: relative;
        overflow: hidden;
        max-width: 1200px;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 3s infinite;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.8rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3), 0 0 40px rgba(102, 126, 234, 0.2);
        letter-spacing: -1px;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.95);
        font-size: 1.15rem;
        margin-top: 0.75rem;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    
    .stat-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f1629 100%);
        border-radius: 20px;
        padding: 2rem 1.5rem;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
        backdrop-filter: blur(10px);
        cursor: pointer;
    }
    
    .stat-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.4), inset 0 1px 0 rgba(255,255,255,0.1);
        border-color: rgba(102, 126, 234, 0.6);
    }
    
    .stat-value {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
    }
    
    .stat-label {
        color: #8a8aaa;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-top: 0.75rem;
        font-weight: 600;
    }
    
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 2.5rem 0 1.25rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.4);
        letter-spacing: -0.5px;
    }
    
    .card-item {
        background: linear-gradient(135deg, #1f1f3d 0%, #2d2d5a 50%, #252547 100%);
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        border: 1px solid rgba(102, 126, 234, 0.4);
        box-shadow: 0 4px 16px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.3s ease;
        backdrop-filter: blur(8px);
    }
    
    .card-item:hover {
        transform: translateY(-4px);
        border-color: rgba(102, 126, 234, 0.6);
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.25), inset 0 1px 0 rgba(255,255,255,0.1);
    }
    
    .card-name {
        font-weight: 700;
        color: #fff;
        font-size: 0.95rem;
        letter-spacing: -0.3px;
    }
    
    .card-level {
        color: #667eea;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.4rem;
    }
    
    .battle-win {
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.15) 0%, rgba(39, 174, 96, 0.1) 100%);
        border-left: 5px solid #2ecc71;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 12px rgba(46, 204, 113, 0.15);
        border: 1px solid rgba(46, 204, 113, 0.3);
        transition: all 0.3s ease;
    }
    
    .battle-win:hover {
        box-shadow: 0 6px 20px rgba(46, 204, 113, 0.25);
        transform: translateX(4px);
    }
    
    .battle-loss {
        background: linear-gradient(135deg, rgba(231, 76, 60, 0.15) 0%, rgba(192, 57, 43, 0.1) 100%);
        border-left: 5px solid #e74c3c;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 12px rgba(231, 76, 60, 0.15);
        border: 1px solid rgba(231, 76, 60, 0.3);
        transition: all 0.3s ease;
    }
    
    .battle-loss:hover {
        box-shadow: 0 6px 20px rgba(231, 76, 60, 0.25);
        transform: translateX(4px);
    }
    
    .battle-draw {
        background: linear-gradient(135deg, rgba(149, 165, 166, 0.15) 0%, rgba(127, 140, 141, 0.1) 100%);
        border-left: 5px solid #95a5a6;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 4px 12px rgba(149, 165, 166, 0.15);
        border: 1px solid rgba(149, 165, 166, 0.3);
        transition: all 0.3s ease;
    }
    
    .battle-draw:hover {
        box-shadow: 0 6px 20px rgba(149, 165, 166, 0.25);
        transform: translateX(4px);
    }
    
    .tip-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-left: 5px solid #667eea;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.15);
        border: 1px solid rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .tip-card:hover {
        box-shadow: 0 6px 24px rgba(102, 126, 234, 0.25);
        transform: translateX(4px);
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    .chest-card {
        background: linear-gradient(135deg, #2d2d5a 0%, #1f1f3d 50%, #252547 100%);
        border-radius: 18px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid rgba(255, 215, 0, 0.4);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.1);
        transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
        cursor: pointer;
    }
    
    .chest-card:hover {
        transform: translateY(-6px) scale(1.08);
        border-color: rgba(255, 215, 0, 0.6);
        box-shadow: 0 12px 32px rgba(255, 215, 0, 0.2);
    }
    
    .demo-banner {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 50%, #e74c3c 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        margin: 1.5rem auto 2rem;
        box-shadow: 0 8px 24px rgba(243, 156, 18, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: glow 3s ease-in-out infinite;
        max-width: 1200px;
    }
    
    .demo-banner p {
        color: white;
        font-weight: 700;
        margin: 0;
        font-size: 1.05rem;
        letter-spacing: 0.3px;
    }
    
    .clan-badge {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 50%, #21618c 100%);
        padding: 1.25rem 2rem;
        border-radius: 16px;
        display: inline-block;
        box-shadow: 0 8px 24px rgba(52, 152, 219, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .clan-badge:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(52, 152, 219, 0.4);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(26, 26, 46, 0.6);
        padding: 0.6rem;
        border-radius: 14px;
        border: 1px solid rgba(102, 126, 234, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 0.85rem 1.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
        color: rgba(255, 255, 255, 0.6);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #fff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f1629 100%);
        border-radius: 18px;
        padding: 1.5rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2), inset 0 1px 0 rgba(255,255,255,0.1);
    }
    
    div[data-testid="stMetric"] label {
        color: #8a8aaa;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
    }
    
    .stExpander {
        background: linear-gradient(135deg, rgba(26, 26, 46, 0.7) 0%, rgba(22, 33, 62, 0.7) 100%);
        border-radius: 14px;
        border: 1px solid rgba(102, 126, 234, 0.2) !important;
        transition: all 0.3s ease;
    }
    
    .stExpander:hover {
        border-color: rgba(102, 126, 234, 0.4) !important;
    }
    
    .pro-tip {
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.15) 0%, rgba(39, 174, 96, 0.1) 100%);
        border-left: 5px solid #2ecc71;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 0.75rem 0;
        box-shadow: 0 4px 12px rgba(46, 204, 113, 0.15);
        border: 1px solid rgba(46, 204, 113, 0.3);
        transition: all 0.3s ease;
    }
    
    .pro-tip:hover {
        box-shadow: 0 6px 20px rgba(46, 204, 113, 0.25);
        transform: translateX(4px);
    }
    
    .arena-tip {
        background: linear-gradient(135deg, rgba(241, 196, 15, 0.2) 0%, rgba(243, 156, 18, 0.15) 100%);
        border: 1px solid rgba(241, 196, 15, 0.4);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 6px 20px rgba(241, 196, 15, 0.15);
        transition: all 0.3s ease;
    }
    
    .arena-tip:hover {
        box-shadow: 0 10px 30px rgba(241, 196, 15, 0.25);
        transform: translateY(-3px);
    }
    
    .input-section {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f1629 100%);
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.9rem 2.5rem;
        font-weight: 700;
        border-radius: 12px;
        transition: all 0.4s cubic-bezier(0.23, 1, 0.320, 1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        letter-spacing: 0.3px;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(-2px);
    }
    
    .toggle-container {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

API_BASE_URL = "https://proxy.royaleapi.dev/v1"

def get_headers():
    api_token = st.session_state.get('api_token', '')
    return {"Authorization": f"Bearer {api_token}"}

def encode_tag(tag):
    tag = tag.strip().upper()
    if not tag.startswith('#'):
        tag = '#' + tag
    return quote(tag, safe='')

def get_player_profile(player_tag):
    encoded_tag = encode_tag(player_tag)
    response = requests.get(f"{API_BASE_URL}/players/{encoded_tag}", headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

def get_battle_log(player_tag):
    encoded_tag = encode_tag(player_tag)
    response = requests.get(f"{API_BASE_URL}/players/{encoded_tag}/battlelog", headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

def get_upcoming_chests(player_tag):
    encoded_tag = encode_tag(player_tag)
    response = requests.get(f"{API_BASE_URL}/players/{encoded_tag}/upcomingchests", headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

def analyze_battles(battles):
    if not battles:
        return None
    
    stats = {
        'total_battles': len(battles),
        'wins': 0,
        'losses': 0,
        'draws': 0,
        'crowns_earned': 0,
        'crowns_given': 0,
        'cards_used': {},
        'game_modes': {}
    }
    
    for battle in battles:
        team = battle.get('team', [{}])[0]
        opponent = battle.get('opponent', [{}])[0]
        
        team_crowns = team.get('crowns', 0)
        opp_crowns = opponent.get('crowns', 0)
        
        stats['crowns_earned'] += team_crowns
        stats['crowns_given'] += opp_crowns
        
        if team_crowns > opp_crowns:
            stats['wins'] += 1
        elif team_crowns < opp_crowns:
            stats['losses'] += 1
        else:
            stats['draws'] += 1
        
        cards = team.get('cards', [])
        for card in cards:
            card_name = card.get('name', 'Unknown')
            if card_name not in stats['cards_used']:
                stats['cards_used'][card_name] = {'uses': 0, 'wins': 0}
            stats['cards_used'][card_name]['uses'] += 1
            if team_crowns > opp_crowns:
                stats['cards_used'][card_name]['wins'] += 1
        
        game_mode = battle.get('gameMode', {}).get('name', 'Unknown')
        if game_mode not in stats['game_modes']:
            stats['game_modes'][game_mode] = {'plays': 0, 'wins': 0}
        stats['game_modes'][game_mode]['plays'] += 1
        if team_crowns > opp_crowns:
            stats['game_modes'][game_mode]['wins'] += 1
    
    return stats

def get_improvement_tips(profile, battle_stats):
    tips = []
    
    if profile:
        wins = profile.get('wins', 0)
        losses = profile.get('losses', 0)
        if wins + losses > 0:
            overall_winrate = wins / (wins + losses) * 100
            if overall_winrate < 45:
                tips.append("Your overall win rate is below 45%. Consider practicing with a simpler, proven deck to build fundamentals.")
            elif overall_winrate < 50:
                tips.append("Your win rate is slightly below 50%. Focus on one deck and master it before experimenting with others.")
        
        three_crown_wins = profile.get('threeCrownWins', 0)
        if wins > 0:
            three_crown_ratio = three_crown_wins / wins * 100
            if three_crown_ratio < 20:
                tips.append("You have a low 3-crown win rate. Try practicing more aggressive plays when you have an elixir advantage.")
            elif three_crown_ratio > 60:
                tips.append("High 3-crown rate! You're aggressive. Consider balancing with some defensive cards for tough matchups.")
        
        challenge_max = profile.get('challengeMaxWins', 0)
        if challenge_max < 6:
            tips.append("Work on challenge performance. Try to analyze your losses and identify patterns in what beats you.")
        elif challenge_max >= 12:
            tips.append("Excellent challenge record! You have strong competitive skills. Consider joining tournaments.")
    
    if battle_stats:
        recent_winrate = battle_stats['wins'] / battle_stats['total_battles'] * 100 if battle_stats['total_battles'] > 0 else 0
        
        if recent_winrate < 40:
            tips.append("Recent performance is struggling. Take a break, watch pro replays, or try a different deck archetype.")
        elif recent_winrate > 65:
            tips.append("You're on a hot streak! Keep playing while you're in the zone.")
        
        if battle_stats['draws'] > battle_stats['total_battles'] * 0.15:
            tips.append("High draw rate detected. Consider adding a win condition or spell that can finish towers.")
        
        if battle_stats['cards_used']:
            sorted_cards = sorted(
                battle_stats['cards_used'].items(),
                key=lambda x: x[1]['wins'] / x[1]['uses'] if x[1]['uses'] >= 3 else 0,
                reverse=True
            )
            
            best_cards = [c[0] for c in sorted_cards[:3] if c[1]['uses'] >= 3]
            worst_cards = [c[0] for c in sorted_cards[-3:] if c[1]['uses'] >= 3 and c[1]['wins'] / c[1]['uses'] < 0.4]
            
            if best_cards:
                tips.append(f"Your best performing cards recently: {', '.join(best_cards)}. Build decks around these!")
            if worst_cards:
                tips.append(f"Consider replacing these underperforming cards: {', '.join(worst_cards)}.")
    
    if not tips:
        tips.append("Keep playing and analyzing your games. Consistency and learning from mistakes are key to improvement!")
    
    return tips

def get_arena_tips(arena_id):
    arena_tips = {
        1: "Focus on learning card interactions. Skeleton Army and Giant are great starting cards.",
        2: "Unlock Mini P.E.K.K.A soon - it's excellent for taking down tanks!",
        3: "Balloon becomes available. Learn to counter it with air-targeting troops.",
        4: "Hog Rider unlocked! Master cycle decks to climb efficiently.",
        5: "Wizard is available. Great splash damage but expensive - manage your elixir!",
        6: "Elite Barbarians appear here. Always have a counter ready (Skeleton Army, P.E.K.K.A).",
        7: "Royal Giant unlocked. Learn building placements to counter siege decks.",
        8: "Mega Knight appears. Don't panic - use single-target troops like Inferno Dragon.",
        9: "You're approaching Legendary Arena. Focus on one meta deck and master it.",
    }
    return arena_tips.get(arena_id, "Keep climbing! Study top ladder decks and adapt to the meta.")

DEMO_PROFILE = {
    'tag': '#2PP8Q8QJV',
    'name': 'ProGamer2024',
    'trophies': 7542,
    'bestTrophies': 8123,
    'expLevel': 14,
    'wins': 2458,
    'losses': 1823,
    'threeCrownWins': 487,
    'challengeMaxWins': 15,
    'totalDonations': 8945,
    'battleCount': 4281,
    'arena': {'id': 9, 'name': 'Legendary Arena'},
    'clan': {'tag': '#LYG82GQ8', 'name': 'Elite Dragons'},
    'currentDeck': [
        {'name': 'Hog Rider', 'level': 14},
        {'name': 'Fireball', 'level': 14},
        {'name': 'Knight', 'level': 14},
        {'name': 'Ice Spirit', 'level': 14},
        {'name': 'The Log', 'level': 14},
        {'name': 'Skeletons', 'level': 14},
        {'name': 'Bats', 'level': 14},
        {'name': 'Inferno Dragon', 'level': 14}
    ]
}

DEMO_BATTLES = [
    {'team': [{'name': 'ProGamer2024', 'crowns': 3, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'Dredgen', 'crowns': 0, 'cards': [{'name': 'Mega Knight'}, {'name': 'Tornado'}, {'name': 'Inferno Dragon'}, {'name': 'Goblins'}, {'name': 'Goblin Barrel'}, {'name': 'Princess'}, {'name': 'Archers'}, {'name': 'Valkyrie'}]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 2, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'XKillzX', 'crowns': 1, 'cards': [{'name': 'P.E.K.K.A'}, {'name': 'Mirror'}, {'name': 'Minions'}, {'name': 'Arrows'}, {'name': 'Elixir Collector'}, {'name': 'Dark Prince'}, {'name': 'Giant'}, {'name': 'Musketeer'}]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 1, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'SkyKnight', 'crowns': 1, 'cards': [{'name': 'Royal Giant'}, {'name': 'Clone'}, {'name': 'Rage'}, {'name': 'Goblins'}, {'name': 'Fire Spirits'}, {'name': 'Guards'}, {'name': 'Musketeer'}, {'name': 'Wizard'}]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 3, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'IceWizard99', 'crowns': 0, 'cards': [{'name': 'Golem'}, {'name': 'Night Witch'}, {'name': 'Balloon'}, {'name': 'Arrows'}, {'name': 'Elixir Collector'}, {'name': 'Bomber'}, {'name': 'Skeletons'}, {'name': 'Tombstone'}]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 2, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'LavaLoon', 'crowns': 1, 'cards': [{'name': 'Lava Hound'}, {'name': 'Balloon'}, {'name': 'Minions'}, {'name': 'Fire Spirits'}, {'name': 'Arrows'}, {'name': 'Guards'}, {'name': 'Barbarians'}, {'name': 'Furnace'}]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 0, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'MirrorMaster', 'crowns': 2, 'cards': [{'name': 'Three Musketeers'}, {'name': 'Mirror'}, {'name': 'Clone'}, {'name': 'Fireball'}, {'name': 'Furnace'}, {'name': 'Inferno Tower'}, {'name': 'Minions'}, {'name': 'Bats'}]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 2, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'EGiant_User', 'crowns': 1, 'cards': [{'name': 'Electro Giant'}, {'name': 'Rage'}, {'name': 'Clone'}, {'name': 'Heal Spirit'}, {'name': 'Guards'}, {'name': 'Goblins'}, {'name': 'Zap'}, {'name': 'Arrows'}]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 3, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'CrossbowTower', 'crowns': 0, 'cards': [{'name': 'X-Bow'}, {'name': 'Inferno Tower'}, {'name': 'Fireball'}, {'name': 'Arrows'}, {'name': 'Barbarians'}, {'name': 'Knight'}, {'name': 'Elixir Collector'}, {'name': 'Tesla'}]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 1, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'GiantSkeleton', 'crowns': 3, 'cards': [{'name': 'Giant Skeleton'}, {'name': 'Poison'}, {'name': 'Minion Horde'}, {'name': 'Barbarians'}, {'name': 'Goblins'}, {'name': 'Arrows'}, {'name': 'Bats'}, {'name': 'Tombstone'}]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 3, 'cards': [{'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'}, {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}]}], 'opponent': [{'name': 'SkeletonKing', 'crowns': 0, 'cards': [{'name': 'Skeleton King'}, {'name': 'Arrows'}, {'name': 'Goblins'}, {'name': 'Fire Spirits'}, {'name': 'Knight'}, {'name': 'Barbarians'}, {'name': 'Minions'}, {'name': 'Valkyrie'}]}], 'gameMode': {'name': 'Ladder'}},
]

DEMO_CHESTS = {
    'items': [
        {'name': 'Gold Chest', 'index': 0},
        {'name': 'Golden Chest', 'index': 1},
        {'name': 'Silver Chest', 'index': 2},
        {'name': 'Gold Chest', 'index': 3},
        {'name': 'Magical Chest', 'index': 4},
        {'name': 'Legendary Chest', 'index': 8},
        {'name': 'Epic Chest', 'index': 12},
        {'name': 'Mega Lightning Chest', 'index': 20},
    ]
}

st.markdown("""
<div style="display: flex; justify-content: center; width: 100%;">
<div class="main-header">
    <h1>👑 Clash Royale Analyzer</h1>
</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1], gap="large")
with col3:
    demo_mode = st.toggle("📊 Demo", value=False, help="Try with sample data")

with st.sidebar:
    st.markdown("### ⚙️ Settings")
    if demo_mode:
        st.success("✨ Demo Mode Active")
    
    api_token = st.text_input(
        "🔑 API Token",
        type="password",
        help="Get from developer.clashroyale.com",
        disabled=demo_mode,
        placeholder="Paste your token here..."
    )
    if api_token:
        st.session_state['api_token'] = api_token
    
    st.markdown("---")
    st.markdown("""
    ### 🚀 Quick Setup
    
    1. **Get Token** → [developer.clashroyale.com](https://developer.clashroyale.com)
    2. **Sign in** with Supercell ID
    3. **Create API key** & whitelist `45.79.218.79`
    4. **Paste here** and search
    """)

profile = None
battles = None
chests = None

st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)

if demo_mode:
    player_tag = "ProGamer2024"
    st.markdown("""
    <div class="demo-banner">
        <p>🎮 Demo Mode: Explore with sample player data from ProGamer2024</p>
    </div>
    """, unsafe_allow_html=True)
    profile = DEMO_PROFILE
    battles = DEMO_BATTLES
    chests = DEMO_CHESTS
else:
    st.markdown("### 🔍 Search Player")
    player_tag = st.text_input(
        "Player Tag",
        placeholder="e.g., #ABC123 or ABC123",
        help="Find your tag in your Clash Royale profile",
        label_visibility="collapsed"
    )
    analyze_btn = st.button("🔍 Search", type="primary", disabled=not player_tag or not st.session_state.get('api_token'), use_container_width=True)
    
    if analyze_btn:
        if not st.session_state.get('api_token'):
            st.error("⚠️ Please add your API token in Settings first")
        else:
            with st.spinner("🔄 Loading..."):
                profile = get_player_profile(player_tag)
                battles = get_battle_log(player_tag)
                chests = get_upcoming_chests(player_tag)
            
            if not profile:
                st.error("❌ Player not found. Check tag and API token.")

if profile:
    if demo_mode:
        pass
    else:
        st.success(f"Found player: **{profile.get('name', 'Unknown')}**")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Profile", "Battle Stats", "Card Analysis", "Upcoming Chests", "Improvement Tips"
    ])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"## {profile.get('name', 'Unknown')}")
            st.caption(f"Tag: {profile.get('tag', 'N/A')}")
        
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Trophies", f"{profile.get('trophies', 0):,}")
        with col2:
            st.metric("Best Trophies", f"{profile.get('bestTrophies', 0):,}")
        with col3:
            st.metric("Level", profile.get('expLevel', 1))
        with col4:
            arena = profile.get('arena', {})
            st.metric("Arena", arena.get('name', 'Unknown'))
        
        st.markdown("### Battle Record")
        col1, col2, col3, col4 = st.columns(4)
        wins = profile.get('wins', 0)
        losses = profile.get('losses', 0)
        with col1:
            st.metric("Wins", f"{wins:,}")
        with col2:
            st.metric("Losses", f"{losses:,}")
        with col3:
            st.metric("Total Battles", f"{profile.get('battleCount', 0):,}")
        with col4:
            winrate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
            st.metric("Win Rate", f"{winrate:.1f}%")
        
        st.markdown("### Achievements")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("3 Crown Wins", f"{profile.get('threeCrownWins', 0):,}")
        with col2:
            st.metric("Challenge Max Wins", profile.get('challengeMaxWins', 0))
        with col3:
            st.metric("Total Donations", f"{profile.get('totalDonations', 0):,}")
        
        clan = profile.get('clan')
        if clan:
            st.markdown("### Clan")
            st.markdown(f"""
            <div class="clan-badge">
                <strong>{clan.get('name', 'Unknown')}</strong><br>
                <span style="opacity: 0.8;">Tag: {clan.get('tag', 'N/A')}</span>
            </div>
            """, unsafe_allow_html=True)
        
        current_deck = profile.get('currentDeck', [])
        if current_deck:
            st.markdown("### Current Deck")
            deck_cols = st.columns(8)
            for i, card in enumerate(current_deck[:8]):
                with deck_cols[i]:
                    st.markdown(f"""
                    <div class="card-item">
                        <div class="card-name">{card.get('name', 'Unknown')}</div>
                        <div class="card-level">Lvl {card.get('level', 1)}</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("## Recent Battle Analysis")
        
        if battles:
            battle_stats = analyze_battles(battles)
            
            if battle_stats:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Recent Battles", battle_stats['total_battles'])
                with col2:
                    st.metric("Wins", battle_stats['wins'])
                with col3:
                    st.metric("Losses", battle_stats['losses'])
                with col4:
                    recent_wr = (battle_stats['wins'] / battle_stats['total_battles'] * 100) if battle_stats['total_battles'] > 0 else 0
                    st.metric("Win Rate", f"{recent_wr:.1f}%")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Crowns Earned", battle_stats['crowns_earned'])
                with col2:
                    st.metric("Crowns Lost", battle_stats['crowns_given'])
                with col3:
                    st.metric("Draws", battle_stats['draws'])
                
                if battle_stats['game_modes']:
                    st.markdown("### Performance by Game Mode")
                    mode_data = []
                    for mode, stats in battle_stats['game_modes'].items():
                        wr = (stats['wins'] / stats['plays'] * 100) if stats['plays'] > 0 else 0
                        mode_data.append({'Game Mode': mode, 'Battles': stats['plays'], 'Wins': stats['wins'], 'Win Rate': f"{wr:.1f}%"})
                    st.dataframe(pd.DataFrame(mode_data), use_container_width=True, hide_index=True)
                
                st.markdown("### Recent Battles")
                for battle in battles[:10]:
                    team = battle.get('team', [{}])[0]
                    opponent = battle.get('opponent', [{}])[0]
                    team_crowns = team.get('crowns', 0)
                    opp_crowns = opponent.get('crowns', 0)
                    
                    if team_crowns > opp_crowns:
                        result_class = "battle-win"
                        result_text = "VICTORY"
                        result_icon = "🏆"
                    elif team_crowns < opp_crowns:
                        result_class = "battle-loss"
                        result_text = "DEFEAT"
                        result_icon = "💀"
                    else:
                        result_class = "battle-draw"
                        result_text = "DRAW"
                        result_icon = "🤝"
                    
                    game_mode = battle.get('gameMode', {}).get('name', 'Unknown')
                    
                    st.markdown(f"""
                    <div class="{result_class}">
                        <strong>{result_icon} {result_text}</strong> vs {opponent.get('name', 'Unknown')} &nbsp;|&nbsp; 
                        <strong>{team_crowns} - {opp_crowns}</strong> &nbsp;|&nbsp; {game_mode}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No recent battles found.")
    
    with tab3:
        st.markdown("## Card Performance Analysis")
        
        if battles:
            battle_stats = analyze_battles(battles)
            
            if battle_stats and battle_stats['cards_used']:
                card_data = [{'Card': card_name, 'Times Used': stats['uses'], 'Wins': stats['wins'], 'Win Rate': (stats['wins'] / stats['uses'] * 100)} for card_name, stats in battle_stats['cards_used'].items() if stats['uses'] >= 1]
                df = pd.DataFrame(card_data).sort_values('Win Rate', ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Best Performing Cards")
                    best_df = df.head(5).copy()
                    best_df['Win Rate'] = best_df['Win Rate'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(best_df, use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("### Needs Improvement")
                    worst_df = df.tail(5).copy()
                    worst_df['Win Rate'] = worst_df['Win Rate'].apply(lambda x: f"{x:.1f}%")
                    st.dataframe(worst_df, use_container_width=True, hide_index=True)
                
                st.markdown("### All Cards Used")
                all_df = df.copy()
                all_df['Win Rate'] = all_df['Win Rate'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(all_df, use_container_width=True, hide_index=True)
        else:
            st.info("No battle data available for card analysis.")
    
    with tab4:
        st.markdown("## Upcoming Chests")
        
        if chests and chests.get('items'):
            chest_items = chests['items']
            
            cols = st.columns(4)
            for i, chest in enumerate(chest_items[:8]):
                with cols[i % 4]:
                    chest_name = chest.get('name', 'Unknown')
                    index = chest.get('index', 0)
                    
                    emoji = "📦"
                    if "Giant" in chest_name:
                        emoji = "🎁"
                    elif "Magical" in chest_name:
                        emoji = "✨"
                    elif "Legendary" in chest_name:
                        emoji = "👑"
                    elif "Epic" in chest_name:
                        emoji = "💜"
                    elif "Gold" in chest_name:
                        emoji = "💰"
                    elif "Mega" in chest_name:
                        emoji = "⚡"
                    
                    st.markdown(f"""
                    <div class="chest-card">
                        <div style="font-size: 2.5rem;">{emoji}</div>
                        <div style="font-weight: 600; color: #fff; margin-top: 0.5rem;">{chest_name}</div>
                        <div style="color: #667eea; font-size: 0.9rem;">+{index} chests away</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
        else:
            st.info("Could not fetch upcoming chests.")
    
    with tab5:
        st.markdown("## Personalized Improvement Tips")
        
        battle_stats = analyze_battles(battles) if battles else None
        tips = get_improvement_tips(profile, battle_stats)
        
        for i, tip in enumerate(tips, 1):
            st.markdown(f"""
            <div class="tip-card">
                <strong>Tip {i}:</strong> {tip}
            </div>
            """, unsafe_allow_html=True)
        
        arena_id = profile.get('arena', {}).get('id', 1)
        st.markdown("### Arena-Specific Advice")
        st.markdown(f"""
        <div class="arena-tip">
            <strong>For your current arena:</strong><br>{get_arena_tips(arena_id)}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Pro Tips from Top Players")
        pro_tips = [
            ("Elixir Management", "Never leak elixir! Always have a plan to spend it efficiently."),
            ("Card Counting", "Keep track of your opponent's cycle to predict their moves."),
            ("Patience Wins", "Don't overcommit. Sometimes waiting for the right moment wins games."),
            ("Defense First", "A good defense often leads to a strong counter-push."),
            ("Know Your Matchups", "Understand which decks counter yours and play carefully against them."),
            ("Learn from Losses", "Watch your replays to understand what went wrong."),
            ("Stay Meta-Aware", "Keep up with balance changes and adjust your deck accordingly."),
            ("Placement Precision", "Small tile differences can change card interactions dramatically."),
        ]
        
        cols = st.columns(2)
        for i, (title, tip) in enumerate(pro_tips):
            with cols[i % 2]:
                st.markdown(f"""
                <div class="pro-tip">
                    <strong>{title}</strong><br>
                    {tip}
                </div>
                """, unsafe_allow_html=True)

if not profile and not demo_mode:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 16px; border: 1px solid rgba(102, 126, 234, 0.2);">
            <h3 style="color: #667eea;">Get Started</h3>
            <p style="color: #a0a0a0;">Enter your player tag above to analyze your stats, or enable Demo Mode to explore the features.</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 1rem; color: #666;">
    <p>Clash Royale Analyzer | Powered by Official Clash Royale API</p>
</div>
""", unsafe_allow_html=True)
