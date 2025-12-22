import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import quote

st.set_page_config(
    page_title="Clash Royale Analyzer",
    page_icon="⚔️",
    layout="wide"
)

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
    'expLevel': 13,
    'wins': 2458,
    'losses': 1823,
    'threeCrownWins': 487,
    'challengeMaxWins': 15,
    'totalDonations': 8945,
    'battleCount': 4281,
    'arena': {'id': 9, 'name': 'Legendary Arena'},
    'clan': {'tag': '#LYG82GQ8', 'name': 'Elite Dragons'},
    'currentDeck': [
        {'name': 'Hog Rider', 'level': 12},
        {'name': 'Fireball', 'level': 13},
        {'name': 'Knight', 'level': 13},
        {'name': 'Ice Spirit', 'level': 13},
        {'name': 'The Log', 'level': 5},
        {'name': 'Skeletons', 'level': 13},
        {'name': 'Bats', 'level': 13},
        {'name': 'Inferno Dragon', 'level': 11}
    ]
}

DEMO_BATTLES = [
    {'team': [{'name': 'ProGamer2024', 'crowns': 3, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'Dredgen', 'crowns': 0, 'cards': [
        {'name': 'Mega Knight'}, {'name': 'Tornado'}, {'name': 'Inferno Dragon'}, {'name': 'Goblins'},
        {'name': 'Goblin Barrel'}, {'name': 'Princess'}, {'name': 'Archers'}, {'name': 'Valkyrie'}
    ]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 2, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'XKillzX', 'crowns': 1, 'cards': [
        {'name': 'P.E.K.K.A'}, {'name': 'Mirror'}, {'name': 'Minions'}, {'name': 'Arrows'},
        {'name': 'Elixir Collector'}, {'name': 'Dark Prince'}, {'name': 'Giant'}, {'name': 'Musketeer'}
    ]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 1, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'SkyKnight', 'crowns': 1, 'cards': [
        {'name': 'Royal Giant'}, {'name': 'Clone'}, {'name': 'Rage'}, {'name': 'Goblins'},
        {'name': 'Fire Spirits'}, {'name': 'Guards'}, {'name': 'Musketeer'}, {'name': 'Wizard'}
    ]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 3, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'IceWizard99', 'crowns': 0, 'cards': [
        {'name': 'Golem'}, {'name': 'Night Witch'}, {'name': 'Balloon'}, {'name': 'Arrows'},
        {'name': 'Elixir Collector'}, {'name': 'Bomber'}, {'name': 'Skeletons'}, {'name': 'Tombstone'}
    ]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 2, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'LavaLoon', 'crowns': 1, 'cards': [
        {'name': 'Lava Hound'}, {'name': 'Balloon'}, {'name': 'Minions'}, {'name': 'Fire Spirits'},
        {'name': 'Arrows'}, {'name': 'Guards'}, {'name': 'Barbarians'}, {'name': 'Furnace'}
    ]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 3, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'MirrorMaster', 'crowns': 0, 'cards': [
        {'name': 'Three Musketeers'}, {'name': 'Mirror'}, {'name': 'Clone'}, {'name': 'Fireball'},
        {'name': 'Furnace'}, {'name': 'Inferno Tower'}, {'name': 'Minions'}, {'name': 'Bats'}
    ]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 2, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'EGiant_User', 'crowns': 1, 'cards': [
        {'name': 'Electro Giant'}, {'name': 'Rage'}, {'name': 'Clone'}, {'name': 'Heal Spirit'},
        {'name': 'Guards'}, {'name': 'Goblins'}, {'name': 'Zap'}, {'name': 'Arrows'}
    ]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 3, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'CrossbowTower', 'crowns': 0, 'cards': [
        {'name': 'X-Bow'}, {'name': 'Inferno Tower'}, {'name': 'Fireball'}, {'name': 'Arrows'},
        {'name': 'Barbarians'}, {'name': 'Knight'}, {'name': 'Elixir Collector'}, {'name': 'Tesla'}
    ]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 2, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'GiantSkeleton', 'crowns': 0, 'cards': [
        {'name': 'Giant Skeleton'}, {'name': 'Poison'}, {'name': 'Minion Horde'}, {'name': 'Barbarians'},
        {'name': 'Goblins'}, {'name': 'Arrows'}, {'name': 'Bats'}, {'name': 'Tombstone'}
    ]}], 'gameMode': {'name': 'Ladder'}},
    {'team': [{'name': 'ProGamer2024', 'crowns': 3, 'cards': [
        {'name': 'Hog Rider'}, {'name': 'Fireball'}, {'name': 'Knight'}, {'name': 'Ice Spirit'},
        {'name': 'The Log'}, {'name': 'Skeletons'}, {'name': 'Bats'}, {'name': 'Inferno Dragon'}
    ]}], 'opponent': [{'name': 'SkeletonKing', 'crowns': 0, 'cards': [
        {'name': 'Skeleton King'}, {'name': 'Arrows'}, {'name': 'Goblins'}, {'name': 'Fire Spirits'},
        {'name': 'Knight'}, {'name': 'Barbarians'}, {'name': 'Minions'}, {'name': 'Valkyrie'}
    ]}], 'gameMode': {'name': 'Ladder'}},
]

DEMO_CHESTS = {
    'items': [
        {'name': 'Gold Chest', 'index': 0},
        {'name': 'Golden Chest', 'index': 1},
        {'name': 'Silver Chest', 'index': 2},
        {'name': 'Gold Chest', 'index': 3},
        {'name': 'Magical Chest', 'index': 4},
        {'name': 'Gold Chest', 'index': 5},
        {'name': 'Epic Chest', 'index': 6},
        {'name': 'Gold Chest', 'index': 7},
    ]
}

st.title("⚔️ Clash Royale Player Analyzer")
st.markdown("Analyze your stats and get personalized tips to improve your gameplay!")

col1, col2 = st.columns([0.85, 0.15])
with col2:
    demo_mode = st.toggle("🎮 Demo Mode", value=False, help="Try the analyzer with sample data")

with st.sidebar:
    st.header("Settings")
    if demo_mode:
        st.info("📌 Running in **Demo Mode** with sample data")
    
    api_token = st.text_input(
        "API Token",
        type="password",
        help="Get your token from developer.clashroyale.com",
        disabled=demo_mode
    )
    if api_token:
        st.session_state['api_token'] = api_token
    
    st.markdown("---")
    st.markdown("""
    **How to get an API Token:**
    1. Go to [developer.clashroyale.com](https://developer.clashroyale.com)
    2. Sign in with your Supercell ID
    3. Create a new API key
    4. Whitelist IP: `45.79.218.79`
    5. Copy the token here
    """)

if demo_mode:
    player_tag = "ProGamer2024"
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.info("👁️ **Demo Preview:** Showing sample player data. Try the 5 analysis tabs below!")
else:
    player_tag = st.text_input(
        "Enter Player Tag",
        placeholder="#ABC123 or ABC123",
        help="Your Clash Royale player tag (with or without #)"
    )

if demo_mode:
    profile = DEMO_PROFILE
    battles = DEMO_BATTLES
    chests = DEMO_CHESTS
elif st.button("Analyze Player", type="primary", disabled=not player_tag or not st.session_state.get('api_token')):
    if not st.session_state.get('api_token'):
        st.error("Please enter your API token in the sidebar first.")
    else:
        with st.spinner("Fetching player data..."):
            profile = get_player_profile(player_tag)
            battles = get_battle_log(player_tag)
            chests = get_upcoming_chests(player_tag)
        
        if not profile:
            st.error("Could not find player. Check the tag and API token, then try again.")
        else:
            profile = profile

if demo_mode or (not demo_mode and st.session_state.get('profile_loaded')):
    if 'profile_loaded' not in st.session_state:
        st.session_state['profile_loaded'] = False
    
    if demo_mode or st.session_state.get('profile_loaded'):
        if profile and not demo_mode:
            st.success(f"Found player: **{profile.get('name', 'Unknown')}**")

if demo_mode or profile:
    if not demo_mode:
        st.session_state['profile_loaded'] = True
        st.success(f"Found player: **{profile.get('name', 'Unknown')}**")
    else:
        st.success(f"Demo Account: **{profile.get('name', 'Unknown')}** (Sample Data)")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Profile", "Battle Stats", "Card Analysis", "Upcoming Chests", "Improvement Tips"
    ])
    
    if profile:
        try:
            with tab1:
                st.header(f"👤 {profile.get('name', 'Unknown')}")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Trophies", f"🏆 {profile.get('trophies', 0)}")
                with col2:
                    st.metric("Best Trophies", f"⭐ {profile.get('bestTrophies', 0)}")
                with col3:
                    st.metric("Level", f"📊 {profile.get('expLevel', 1)}")
                with col4:
                    arena = profile.get('arena', {})
                    st.metric("Arena", arena.get('name', 'Unknown'))
                st.subheader("Battle Record")
                col1, col2, col3, col4 = st.columns(4)
                wins = profile.get('wins', 0)
                losses = profile.get('losses', 0)
                with col1:
                    st.metric("Wins", f"✅ {wins}")
                with col2:
                    st.metric("Losses", f"❌ {losses}")
                with col3:
                    st.metric("Total Battles", profile.get('battleCount', 0))
                with col4:
                    winrate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
                    st.metric("Win Rate", f"{winrate:.1f}%")
                st.subheader("Achievements")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("3 Crown Wins", profile.get('threeCrownWins', 0))
                with col2:
                    st.metric("Challenge Max Wins", profile.get('challengeMaxWins', 0))
                with col3:
                    st.metric("Cards Found", f"{profile.get('totalDonations', 0)} donated")
                clan = profile.get('clan')
                if clan:
                    st.subheader("Clan")
                    st.info(f"**{clan.get('name', 'Unknown')}** (Tag: {clan.get('tag', 'N/A')})")
                current_deck = profile.get('currentDeck', [])
                if current_deck:
                    st.subheader("Current Deck")
                    deck_cols = st.columns(8)
                    for i, card in enumerate(current_deck[:8]):
                        with deck_cols[i]:
                            st.markdown(f"**{card.get('name', 'Unknown')}**")
                            st.caption(f"Lvl {card.get('level', 1)}")
            with tab2:
                st.header("📊 Recent Battle Analysis")
                if battles:
                    battle_stats = analyze_battles(battles)
                    if battle_stats:
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Recent Battles", battle_stats['total_battles'])
                        with col2:
                            st.metric("Recent Wins", battle_stats['wins'])
                        with col3:
                            st.metric("Recent Losses", battle_stats['losses'])
                        with col4:
                            recent_wr = (battle_stats['wins'] / battle_stats['total_battles'] * 100) if battle_stats['total_battles'] > 0 else 0
                            st.metric("Recent Win Rate", f"{recent_wr:.1f}%")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Crowns Earned", f"👑 {battle_stats['crowns_earned']}")
                        with col2:
                            st.metric("Crowns Given Up", f"💀 {battle_stats['crowns_given']}")
                        if battle_stats['game_modes']:
                            st.subheader("Performance by Game Mode")
                            mode_data = []
                            for mode, stats in battle_stats['game_modes'].items():
                                wr = (stats['wins'] / stats['plays'] * 100) if stats['plays'] > 0 else 0
                                mode_data.append({'Game Mode': mode, 'Battles': stats['plays'], 'Wins': stats['wins'], 'Win Rate': f"{wr:.1f}%"})
                            st.dataframe(pd.DataFrame(mode_data), use_container_width=True)
                        st.subheader("Recent Battles")
                        for battle in battles[:10]:
                            team = battle.get('team', [{}])[0]
                            opponent = battle.get('opponent', [{}])[0]
                            team_crowns = team.get('crowns', 0)
                            opp_crowns = opponent.get('crowns', 0)
                            result = "✅ WIN" if team_crowns > opp_crowns else ("❌ LOSS" if team_crowns < opp_crowns else "🤝 DRAW")
                            game_mode = battle.get('gameMode', {}).get('name', 'Unknown')
                            with st.expander(f"{result} vs {opponent.get('name', 'Unknown')} ({team_crowns}-{opp_crowns}) - {game_mode}"):
                                st.write(f"**Your Deck:** {', '.join([c.get('name', '?') for c in team.get('cards', [])])}")
                                st.write(f"**Opponent Deck:** {', '.join([c.get('name', '?') for c in opponent.get('cards', [])])}")
                else:
                    st.info("No recent battles found.")
            with tab3:
                st.header("🃏 Card Performance Analysis")
                if battles:
                    battle_stats = analyze_battles(battles)
                    if battle_stats and battle_stats['cards_used']:
                        card_data = [{'Card': card_name, 'Times Used': stats['uses'], 'Wins': stats['wins'], 'Win Rate': (stats['wins'] / stats['uses'] * 100)} for card_name, stats in battle_stats['cards_used'].items() if stats['uses'] >= 1]
                        df = pd.DataFrame(card_data).sort_values('Win Rate', ascending=False)
                        st.subheader("Best Performing Cards")
                        best_df = df.head(5).copy()
                        best_df['Win Rate'] = best_df['Win Rate'].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(best_df, use_container_width=True)
                        st.subheader("Worst Performing Cards")
                        worst_df = df.tail(5).copy()
                        worst_df['Win Rate'] = worst_df['Win Rate'].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(worst_df, use_container_width=True)
                        st.subheader("All Cards Used")
                        all_df = df.copy()
                        all_df['Win Rate'] = all_df['Win Rate'].apply(lambda x: f"{x:.1f}%")
                        st.dataframe(all_df, use_container_width=True)
                else:
                    st.info("No battle data available for card analysis.")
            with tab4:
                st.header("📦 Upcoming Chests")
                if chests and chests.get('items'):
                    chest_items = chests['items']
                    cols_per_row = 4
                    for i in range(0, len(chest_items), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, chest in enumerate(chest_items[i:i+cols_per_row]):
                            with cols[j]:
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
                                st.markdown(f"### {emoji} +{index}")
                                st.caption(chest_name)
                else:
                    st.info("Could not fetch upcoming chests.")
            with tab5:
                st.header("💡 Personalized Improvement Tips")
                battle_stats = analyze_battles(battles) if battles else None
                tips = get_improvement_tips(profile, battle_stats)
                for i, tip in enumerate(tips, 1):
                    st.info(f"**Tip {i}:** {tip}")
                arena_id = profile.get('arena', {}).get('id', 1)
                st.subheader("Arena-Specific Advice")
                st.success(get_arena_tips(arena_id))
                st.subheader("General Pro Tips")
                pro_tips = ["**Elixir Management:** Never leak elixir! Always have a plan to spend it efficiently.", "**Card Counting:** Keep track of your opponent's cycle to predict their moves.", "**Patience:** Don't overcommit. Sometimes waiting for the right moment wins games.", "**Defense First:** A good defense often leads to a strong counter-push.", "**Learn Matchups:** Know which decks counter yours and play more carefully against them.", "**Watch Replays:** Analyze your losses to understand what went wrong.", "**Meta Awareness:** Keep up with balance changes and adjust your deck accordingly.", "**Placement Matters:** Small tile differences can change interactions dramatically."]
                for tip in pro_tips:
                    st.markdown(f"- {tip}")
        except Exception as e:
            st.error(f"Error displaying data: {str(e)}")

if not demo_mode and not player_tag:
    st.info("Enter a player tag above and click 'Analyze Player' to get started! Or toggle Demo Mode to see a sample analysis.")
    
    with st.expander("Example Analysis Features"):
        st.markdown("""
        **What you'll get:**
        - Complete player profile and statistics
        - Recent battle analysis with win rates
        - Card performance breakdown
        - Upcoming chest schedule
        - Personalized improvement tips based on your gameplay
        - Arena-specific advice
        """)

st.markdown("---")
st.caption("Clash Royale Analyzer | Data from official Clash Royale API")
