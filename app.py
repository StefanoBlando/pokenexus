import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import pandas as pd
import base64
import os
import requests
import plotly.graph_objects as go
import plotly.express as px
import random
import math
import time
from datetime import datetime
import json 

# ==========================================
# 1. CONFIGURAZIONE E STILE
# ==========================================
st.set_page_config(page_title="PokéNexus", layout="wide", page_icon="🔴")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "icons")

# --- SESSION STATE ---
defaults = {
    'balance': 3000, 'wins': 0, 'losses': 0,
    'badges': [], 'ribbons': [], 'trophies': [],
    'inventory': {'Poké Ball': 5},
    'saved_team': ["None"] * 6,
    'pc_box': [],
    'weather': 'Clear',
    'safari_enc': None,
    'wtp_mon': None, 'wtp_reveal': False
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');

    /* --- AUDIO FIX: Rende il player invisibile ma attivo --- */
    /* Usiamo opacity 0 e pointer-events none invece di display:none per evitare blocchi browser */
    .stAudio {
        height: 0px !important;
        width: 0px !important;
        opacity: 0 !important;
        overflow: hidden !important;
        position: absolute !important;
        pointer-events: none;
    }

    /* SFONDO APP */
    .stApp {
        background-color: #121212;
        background-image: linear-gradient(rgba(41, 182, 246, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(41, 182, 246, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
    }
    
    /* SIDEBAR */
    [data-testid="stSidebar"] { background-color: #DC0A2D; border-right: 6px solid #89061C; }
    
    /* TAB STYLING */
    div[data-baseweb="tab-list"] { gap: 10px; margin-bottom: 20px; }
    button[data-baseweb="tab"] {
        flex-grow: 1; background-color: rgba(255, 255, 255, 0.05); border: 1px solid #333;
        border-radius: 8px 8px 0 0; padding: 10px 0; font-family: 'Orbitron', sans-serif; font-size: 13px; transition: all 0.3s;
    }
    button[data-baseweb="tab"]:hover { background-color: rgba(41, 182, 246, 0.2); border-color: #29b6f6; }
    button[data-baseweb="tab"][aria-selected="true"] { background-color: #29b6f6; color: black !important; font-weight: bold; }

    /* WIDGETS */
    .status-bar {
        font-family: 'Share Tech Mono', monospace; color: #fff; background: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 5px;
        display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* PC BOX */
    .pc-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr)); gap: 10px; padding: 15px; background: rgba(0,0,0,0.2); border-radius: 10px; border: 1px solid #333; }
    .pc-slot { 
        background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
        border: 1px solid #444; border-radius: 8px; text-align: center; padding: 5px; transition: transform 0.2s;
    }
    .pc-slot:hover { transform: scale(1.05); border-color: #29b6f6; box-shadow: 0 0 10px rgba(41, 182, 246, 0.2); }
    
    /* POKE CENTER */
    .nurse-box { background: rgba(255, 100, 100, 0.1); border: 2px solid #ff5050; border-radius: 15px; padding: 20px; text-align: center; margin-bottom: 20px; }
    
    /* GENERAL UI */
    .sys-log { font-family: 'Share Tech Mono', monospace; font-size: 10px; color: #00ff00; background: #000; padding: 5px; border: 1px solid #555; border-radius: 3px; opacity: 0.9; }
    .team-card { background: rgba(255, 255, 255, 0.05); border: 1px solid #444; border-radius: 10px; padding: 10px; text-align: center; transition: all 0.3s ease; height: 100%; }
    .team-card:hover { border-color: #29b6f6; box-shadow: 0 0 15px rgba(41, 182, 246, 0.3); transform: translateY(-5px); }
    .rotom-eye-container { display: flex; justify-content: center; margin: 0 auto 10px auto; background: #000; padding: 8px; border-radius: 50%; width: 100px; height: 100px; border: 4px solid #f0f0f0; box-shadow: 0 0 15px rgba(0,0,0,0.5); }
    .rotom-eye { width: 100%; height: 100%; background: radial-gradient(circle at 30% 30%, #fff 5%, #29b6f6 20%, #0277bd 100%); border-radius: 50%; animation: blink 4s infinite; }
    @keyframes blink { 0%, 96%, 100% { transform: scaleY(1); } 98% { transform: scaleY(0.1); } }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif !important; text-transform: uppercase; color: #f0f0f0; }
    .type-badge { padding: 2px 8px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.7em; text-shadow: 1px 1px 0px #000; border: 1px solid rgba(255,255,255,0.3); display: inline-block; font-family: 'Share Tech Mono'; }
    .battle-log-area { font-family: 'Share Tech Mono'; font-size: 12px; color: #29b6f6; background: #000; padding: 10px; border-radius: 5px; max-height: 300px; overflow-y: auto; }
    .alive { opacity: 1.0; border: 2px solid #00ff00; border-radius: 50%; }
    .dead { opacity: 0.3; filter: grayscale(100%); border: 2px solid #ff0000; border-radius: 50%; }
    
    /* BADGES */
    .badge-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; margin-top: 10px; }
    .badge-slot { width: 100%; aspect-ratio: 1; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.2); border: 1px solid #555; font-size: 18px; }
    .badge-earned { background: radial-gradient(circle, #fff 10%, gold 100%); border: 1px solid gold; box-shadow: 0 0 10px gold; animation: pop 0.3s ease; }
    .badge-locked { filter: grayscale(100%) opacity(0.3); }
    @keyframes pop { 0% { transform: scale(0.5); } 80% { transform: scale(1.2); } 100% { transform: scale(1); } }
    
    /* SHOP */
    .shop-item { background: rgba(0,0,0,0.5); padding: 10px; border: 1px solid #444; border-radius: 8px; text-align:center; height: 100%; }
    
    /* WTP GAME */
    .silhouette { filter: brightness(0) invert(1); transition: filter 1s ease; }
    .revealed { filter: none; }
</style>
""", unsafe_allow_html=True)

# METEO CSS
weather_css = {
    "Clear": "linear-gradient(rgba(41, 182, 246, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(41, 182, 246, 0.03) 1px, transparent 1px)",
    "Sun": "linear-gradient(rgba(255, 165, 0, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 165, 0, 0.05) 1px, transparent 1px)",
    "Rain": "linear-gradient(rgba(0, 0, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 0, 255, 0.05) 1px, transparent 1px)",
    "Sand": "linear-gradient(rgba(194, 178, 128, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(194, 178, 128, 0.05) 1px, transparent 1px)"
}
bg_style = weather_css.get(st.session_state.weather, weather_css["Clear"])
st.markdown(f"<style>.stApp {{ background-image: {bg_style} !important; }}</style>", unsafe_allow_html=True)

# ==========================================
# 2. DATI (DATABASE COMPLETO)
# ==========================================
TRAINER_CLASSES = sorted(["Ace Trainer", "Gym Leader", "Researcher", "Team Rocket", "Hiker", "Youngster", "Champion", "Black Belt", "Psychic", "Dragon Tamer"])
REGIONS = ["Kanto", "Johto", "Sinnoh", "Unova", "Kalos", "Alola", "Galar", "Paldea"]

# POKEMON DALLE UOVA (Pool espanso)
EGG_POOL = [
    "pichu", "cleffa", "igglybuff", "togepi", "tyrogue", "smoochum", "elekid", "magby", 
    "azurill", "wynaut", "bonsly", "mime-jr", "happiny", "munchlax", "riolu", "mantyke",
    "larvitar", "bagon", "dratini", "gible", "beldum", "deino", "goomy", "jangmo-o", "dreepy", "frigibax"
]

# OGGETTI NEGOZIO (Solo strumenti base + Piccone)
SHOP_ITEMS = {
    # BALLS
    "Poké Ball": {"price": 200, "icon": "🔴", "desc": "Basic catch rate (1x)."},
    "Great Ball": {"price": 600, "icon": "🔵", "desc": "Better catch rate (1.5x)."},
    "Ultra Ball": {"price": 1200, "icon": "🟡", "desc": "High catch rate (2x)."},
    
    # CURE
    "Potion": {"price": 300, "icon": "🧪", "desc": "Restores 20 HP."},
    "Super Potion": {"price": 700, "icon": "🧪", "desc": "Restores 60 HP."},
    "Hyper Potion": {"price": 1200, "icon": "🧪", "desc": "Restores 120 HP."},
    "Max Potion": {"price": 2500, "icon": "🧪", "desc": "Fully restores HP."},
    "Full Restore": {"price": 3000, "icon": "✨", "desc": "Fully restores HP & Status."},
    "Moomoo Milk": {"price": 500, "icon": "🥛", "desc": "Cheap healing (100 HP)."},
    
    # STATUS & REVIVE
    "Revive": {"price": 1500, "icon": "💎", "desc": "Revive fainted Pokémon."},
    "Max Revive": {"price": 4000, "icon": "💎", "desc": "Revive with full HP."},
    "Full Heal": {"price": 600, "icon": "💊", "desc": "Cures all status problems."},
    
    # UTILITÀ
    "Escape Rope": {"price": 550, "icon": "➰", "desc": "Escapes from caves."},
    "Repel": {"price": 350, "icon": "💨", "desc": "Repels weak wild Pokémon."},
    "Max Repel": {"price": 700, "icon": "💨", "desc": "Repels wild Pokémon for longer."},
    
    # STRUMENTI MINIERA
    "Pickaxe": {"price": 500, "icon": "⛏️", "desc": "Dig for Stones & Fossils in the Underground."}
}

# DATABASE FOSSILI COMPLETO (Gen 1-6)
# Mappa: "Nome Strumento" -> "Pokemon"
FOSSILS = {
    # Gen 1 (Kanto)
    "Helix Fossil": "omanyte",
    "Dome Fossil": "kabuto",
    "Old Amber": "aerodactyl",
    # Gen 3 (Hoenn)
    "Root Fossil": "lileep",
    "Claw Fossil": "anorith",
    # Gen 4 (Sinnoh)
    "Skull Fossil": "cranidos",
    "Armor Fossil": "shieldon",
    # Gen 5 (Unova)
    "Cover Fossil": "tirtouga",
    "Plume Fossil": "archen",
    # Gen 6 (Kalos)
    "Jaw Fossil": "tyrunt",
    "Sail Fossil": "amaura"
}

# DATABASE EVOLUZIONI (PIETRE)
# Include tutte le evoluzioni tramite pietra principali
EVOLUTION_DB = {
    # --- FIRE STONE ---
    "eevee": {"Fire Stone": "flareon", "Water Stone": "vaporeon", "Thunder Stone": "jolteon", "Leaf Stone": "leafeon", "Ice Stone": "glaceon"},
    "growlithe": {"Fire Stone": "arcanine"},
    "growlithe-hisui": {"Fire Stone": "arcanine-hisui"},
    "vulpix": {"Fire Stone": "ninetales"},
    "pansear": {"Fire Stone": "simisear"},
    "capsakid": {"Fire Stone": "scovillain"},
    
    # --- WATER STONE ---
    "poliwhirl": {"Water Stone": "poliwrath"},
    "shellder": {"Water Stone": "cloyster"},
    "staryu": {"Water Stone": "starmie"},
    "lombre": {"Water Stone": "ludicolo"},
    "panpour": {"Water Stone": "simipour"},
    
    # --- THUNDER STONE ---
    "pikachu": {"Thunder Stone": "raichu"},
    "eelektrik": {"Thunder Stone": "eelektross"},
    "tadbulb": {"Thunder Stone": "bellibolt"},
    "magneton": {"Thunder Stone": "magnezone"}, # (Modern Logic)
    "nosepass": {"Thunder Stone": "probopass"}, # (Modern Logic)
    
    # --- LEAF STONE ---
    "gloom": {"Leaf Stone": "vileplume", "Sun Stone": "bellossom"},
    "weepinbell": {"Leaf Stone": "victreebel"},
    "exeggcute": {"Leaf Stone": "exeggutor"},
    "nuzleaf": {"Leaf Stone": "shiftry"},
    "pansage": {"Leaf Stone": "simisage"},
    "voltorb-hisui": {"Leaf Stone": "electrode-hisui"},
    
    # --- MOON STONE ---
    "nidorina": {"Moon Stone": "nidoqueen"},
    "nidorino": {"Moon Stone": "nidoking"},
    "clefairy": {"Moon Stone": "clefable"},
    "jigglypuff": {"Moon Stone": "wigglytuff"},
    "skitty": {"Moon Stone": "delcatty"},
    "munna": {"Moon Stone": "musharna"},
    
    # --- SUN STONE ---
    "sunkern": {"Sun Stone": "sunflora"},
    "cottonee": {"Sun Stone": "whimsicott"},
    "petilil": {"Sun Stone": "lilligant"},
    "helioptile": {"Sun Stone": "heliolisk"},
    
    # --- SHINY STONE (Pietrabrillo) ---
    "togetic": {"Shiny Stone": "togekiss"},
    "roselia": {"Shiny Stone": "roserade"},
    "minccino": {"Shiny Stone": "cinccino"},
    "floette": {"Shiny Stone": "florges"},
    
    # --- DUSK STONE (Neropietra) ---
    "murkrow": {"Dusk Stone": "honchkrow"},
    "misdreavus": {"Dusk Stone": "mismagius"},
    "lampent": {"Dusk Stone": "chandelure"},
    "doublade": {"Dusk Stone": "aegislash"},
    
    # --- DAWN STONE (Pietralba) ---
    "kirlia": {"Dawn Stone": "gallade"}, # (Maschio, ma qui semplifichiamo)
    "snorunt": {"Dawn Stone": "froslass"}, # (Femmina, ma qui semplifichiamo)
    
    # --- ICE STONE (Pietragelo) ---
    "vulpix-alola": {"Ice Stone": "ninetales-alola"},
    "sandshrew-alola": {"Ice Stone": "sandslash-alola"},
    "darumaka-galar": {"Ice Stone": "darmanitan-galar"},
    "cetoddle": {"Ice Stone": "cetitan"},
    "crabrawler": {"Ice Stone": "crabominable"}
}

SAFARI_POOLS = {
    "Common": ["rattata", "pidgey", "caterpie", "weedle", "zubat", "geodude", "magikarp", "bidoof", "sentret", "hoothoot", "poochyena", "zigzagoon", "wurmple", "starly", "patrat", "lillipup", "bunnelby", "fletchling", "yungoos", "pikipek", "skwovet", "rookidee", "lechonk", "tarountula"],
    "Rare": ["pikachu", "eevee", "scyther", "pinsir", "tauros", "kangaskhan", "dratini", "bagon", "gible", "heracross", "skarmory", "larvitar", "beldum", "riolu", "zorua", "axew", "deino", "goomy", "jangmo-o", "dreepy", "frigibax"],
    "Legendary": ["articuno", "zapdos", "moltres", "mewtwo", "mew", "lugia", "ho-oh", "rayquaza", "kyogre", "groudon", "dialga", "palkia", "giratina", "reshiram", "zekrom", "kyurem", "xerneas", "yveltal", "zygarde", "cosmog", "necrozma", "zacian", "zamazenta", "eternatus", "koraidon", "miraidon"]
}

NPC_DB = {
    "Kanto": {
        "Gym Leaders": {
            "Brock": (["geodude", "onix"], "Boulder Badge", 1500), "Misty": (["staryu", "starmie"], "Cascade Badge", 2000),
            "Lt. Surge": (["voltorb", "pikachu", "raichu"], "Thunder Badge", 2500), "Erika": (["victreebel", "tangela", "vileplume"], "Rainbow Badge", 3000),
            "Sabrina": (["kadabra", "mr-mime", "venomoth", "alakazam"], "Marsh Badge", 3500), "Blaine": (["growlithe", "ponyta", "rapidash", "arcanine"], "Volcano Badge", 4000),
            "Giovanni": (["rhyhorn", "dugtrio", "nidoqueen", "nidoking", "rhydon"], "Earth Badge", 5000)
        },
        "Elite 4": {
            "Lorelei": (["dewgong", "cloyster", "slowbro", "jynx", "lapras"], "Ice Ribbon", 6000), "Bruno": (["onix", "hitmonchan", "hitmonlee", "machamp"], "Fight Ribbon", 6000),
            "Agatha": (["gengar", "golbat", "haunter", "arbok", "gengar"], "Ghost Ribbon", 6000), "Lance": (["gyarados", "dragonair", "aerodactyl", "dragonite"], "Dragon Ribbon", 6500)
        },
        "Champion": { "Blue": (["pidgeot", "alakazam", "rhydon", "gyarados", "exeggutor", "charizard"], "Kanto Trophy", 10000) }
    },
    "Johto": {
        "Gym Leaders": { "Whitney": (["clefairy", "miltank"], "Plain Badge", 2000), "Morty": (["gastly", "haunter", "gengar"], "Fog Badge", 2500), "Clair": (["dragonair", "kingdra"], "Rising Badge", 4000) },
        "Champion": { "Red": (["pikachu", "espeon", "snorlax", "venusaur", "charizard", "blastoise"], "Legend Trophy", 20000) }
    },
    "Sinnoh": {
        "Gym Leaders": { "Volkner": (["raichu", "luxray", "electivire"], "Beacon Badge", 3000) },
        "Champion": { "Cynthia": (["spiritomb", "roserade", "togekiss", "lucario", "milotic", "garchomp"], "Sinnoh Trophy", 15000) }
    }
}

TYPE_CHART = {
    "Normal":   {"Rock": 0.5, "Ghost": 0, "Steel": 0.5}, "Fire": {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 2, "Bug": 2, "Rock": 0.5, "Dragon": 0.5, "Steel": 2},
    "Water":    {"Fire": 2, "Water": 0.5, "Grass": 0.5, "Ground": 2, "Rock": 2, "Dragon": 0.5}, "Electric": {"Water": 2, "Electric": 0.5, "Grass": 0.5, "Ground": 0, "Flying": 2, "Dragon": 0.5},
    "Grass":    {"Fire": 0.5, "Water": 2, "Grass": 0.5, "Poison": 0.5, "Ground": 2, "Flying": 0.5, "Bug": 0.5, "Rock": 2, "Dragon": 0.5, "Steel": 0.5},
    "Ice":      {"Fire": 0.5, "Water": 0.5, "Grass": 2, "Ice": 0.5, "Ground": 2, "Flying": 2, "Dragon": 2, "Steel": 0.5},
    "Fighting": {"Normal": 2, "Ice": 2, "Poison": 0.5, "Flying": 0.5, "Psychic": 0.5, "Bug": 0.5, "Rock": 2, "Ghost": 0, "Dark": 2, "Steel": 2, "Fairy": 0.5},
    "Poison":   {"Grass": 2, "Poison": 0.5, "Ground": 0.5, "Rock": 0.5, "Ghost": 0.5, "Steel": 0, "Fairy": 2},
    "Ground":   {"Fire": 2, "Electric": 2, "Grass": 0.5, "Poison": 2, "Flying": 0, "Bug": 0.5, "Rock": 2, "Steel": 2},
    "Flying":   {"Electric": 0.5, "Grass": 2, "Fighting": 2, "Bug": 2, "Rock": 0.5, "Steel": 0.5},
    "Psychic":  {"Fighting": 2, "Poison": 2, "Psychic": 0.5, "Dark": 0, "Steel": 0.5},
    "Bug":      {"Fire": 0.5, "Grass": 2, "Fighting": 0.5, "Poison": 0.5, "Flying": 0.5, "Psychic": 2, "Ghost": 0.5, "Dark": 2, "Steel": 0.5, "Fairy": 0.5},
    "Rock":     {"Fire": 2, "Ice": 2, "Fighting": 0.5, "Ground": 0.5, "Flying": 2, "Bug": 2, "Steel": 0.5},
    "Ghost":    {"Normal": 0, "Psychic": 2, "Ghost": 2, "Dark": 0.5}, "Dragon": {"Dragon": 2, "Steel": 0.5, "Fairy": 0},
    "Dark":     {"Fighting": 0.5, "Psychic": 2, "Ghost": 2, "Dark": 0.5, "Fairy": 0.5}, "Steel": {"Fire": 0.5, "Water": 0.5, "Electric": 0.5, "Ice": 2, "Rock": 2, "Steel": 0.5, "Fairy": 2},
    "Fairy":    {"Fire": 0.5, "Fighting": 2, "Poison": 0.5, "Dragon": 2, "Dark": 2, "Steel": 0.5}
}

TYPE_COLORS = {
    "Normal": "#A8A77A", "Fire": "#EE8130", "Water": "#6390F0", "Electric": "#F7D02C", "Grass": "#7AC74C", "Ice": "#96D9D6",
    "Fighting": "#C22E28", "Poison": "#A33EA1", "Ground": "#E2BF65", "Flying": "#A98FF3", "Psychic": "#F95587", "Bug": "#A6B91A",
    "Rock": "#B6A136", "Ghost": "#735797", "Dragon": "#6F35FC", "Dark": "#705746", "Steel": "#B7B7CE", "Fairy": "#D685AD"
}

NATURES = {
    "Hardy": {}, "Adamant": {"+": "attack", "-": "special-attack"}, "Bold": {"+": "defense", "-": "attack"},
    "Modest": {"+": "special-attack", "-": "attack"}, "Calm": {"+": "special-defense", "-": "attack"},
    "Timid": {"+": "speed", "-": "attack"}, "Jolly": {"+": "speed", "-": "special-attack"}
}

# --- STATI INIZIALI (AGGIORNATO E SICURO) ---
defaults = {
    'balance': 3000, 'wins': 0, 'losses': 0,
    'badges': [], 'ribbons': [], 'trophies': [],
    'inventory': {'Poké Ball': 5, 'Pickaxe': 3},
    'saved_team': ["None"] * 6,
    'pc_box': [],
    'weather': 'Clear',
    'safari_enc': None,
    'wtp_mon': None, 'wtp_reveal': False,
    'mission': {'desc': "Catch a Fire Type Pokemon", 'type': 'Fire', 'reward': 500, 'done': False},
    'tower_streak': 0,
    'mining_grid': [],
    'mining_rewards': [],
    # --- NUOVI STATI (Quelli che causavano l'errore) ---
    'nicknames': {},  
    'garden_plots': [{'stage': 0, 'berry': None, 'water': 0} for _ in range(4)],
    'slot_result': ["❓", "❓", "❓"] # Anche questo serve per le slot!
}

# Questo ciclo controlla e ripara la memoria se manca qualcosa
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# 3. FUNZIONI
# ==========================================

# Generatore Griglia Miniera (NUOVO)
@st.cache_data(ttl=86400, show_spinner=False)
def get_item_sprite(item_name):
    try:
        # Trasforma "Fire Stone" in "fire-stone" per l'API
        api_name = item_name.lower().replace(" ", "-")
        url = f"https://pokeapi.co/api/v2/item/{api_name}"
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            return resp.json()['sprites']['default']
        return None
    except:
        return None

# SOSTITUISCI LA FUNZIONE generate_mine_grid
def generate_mine_grid():
    # 0 = Coperto, 1 = Scavato
    grid = [[0 for _ in range(5)] for _ in range(5)]
    rewards = [[None for _ in range(5)] for _ in range(5)]
    
    # LISTA AGGIORNATA DI TUTTE LE PIETRE DISPONIBILI
    all_stones = [
        "Fire Stone", "Water Stone", "Thunder Stone", "Leaf Stone", "Moon Stone", 
        "Sun Stone", "Shiny Stone", "Dusk Stone", "Dawn Stone", "Ice Stone"
    ]
    
    # Pool di oggetti: 
    # - Pepite (soldi)
    # - Pietre (tutte le 10 varianti)
    # - Fossili (tutti quelli nel database)
    loot_pool = ["Nugget"] * 6 + all_stones * 2 + list(FOSSILS.keys()) * 2 + [None] * 12
    
    for r in range(5):
        for c in range(5):
            rewards[r][c] = random.choice(loot_pool)
            
    return grid, rewards

def generate_new_mission():
    mission_types = list(TYPE_CHART.keys())
    target_type = random.choice(mission_types)
    return {
        'desc': f"Catch a {target_type} Type Pokémon",
        'type': target_type,
        'reward': random.choice([300, 400, 500, 600]),
        'done': False
    }

def play_sound(file_name):
    sound_file_path = os.path.join(BASE_DIR, file_name)
    try:
        with open(sound_file_path, "rb") as f:
            audio_bytes = f.read()
        audio_b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
            <audio autoplay="true" style="opacity: 0; width: 0; height: 0; position: absolute; pointer-events: none;">
                <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"⚠️ Errore: Il file '{file_name}' non è stato trovato.")
    except Exception as e:
        st.error(f"⚠️ Errore Audio: {e}")

def get_rgba(hex_code, alpha=1.0):
    if not hex_code: return f"rgba(100,100,100,{alpha})"
    hex_code = hex_code.lstrip('#')
    if len(hex_code) == 3: hex_code = hex_code[0]*2 + hex_code[1]*2 + hex_code[2]*2
    try:
        r, g, b = int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
        return f"rgba({r},{g},{b},{alpha})"
    except: return f"rgba(100,100,100,{alpha})"

@st.cache_data(ttl=86400, show_spinner=False)
def get_all_pokemon_names():
    fallback_list = ["bulbasaur", "charmander", "squirtle", "pikachu", "gengar", "lucario", "garchomp", "eevee", "snorlax", "mewtwo", "charizard", "dragonite", "sylveon", "greninja", "rayquaza", "lugia", "ho-oh", "kyogre", "groudon", "arceus"]
    try:
        resp = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1025", timeout=3)
        return [p['name'] for p in resp.json()['results']]
    except: return fallback_list

all_mons = get_all_pokemon_names()

@st.cache_data(ttl=3600, show_spinner=False)
def get_pokemon_data(name, is_shiny=False):
    try:
        if not name: return None
        resp = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name.lower()}", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            bst = sum([s['base_stat'] for s in data['stats']])
            sprite_key = 'front_shiny' if is_shiny else 'front_default'
            
            sprites = data.get('sprites', {})
            other = sprites.get('other', {}).get('showdown', {})
            img_url = other.get(sprite_key) or sprites.get(sprite_key) or ""
            
            moves = [m['move']['name'].title() for m in data['moves'][:20]]
            
            return {
                "id": data['id'], "name": data['name'].title(), "types": [t['type']['name'].capitalize() for t in data['types']],
                "stats": {s['stat']['name']: s['base_stat'] for s in data['stats']},
                "abilities": [a['ability']['name'].replace('-', ' ').title() for a in data['abilities']],
                "moves": moves, "sprite": img_url, "weight": data['weight'] / 10, "height": data['height'] / 10, "bst": bst
            }
        return None
    except: return None

def get_local_icon(type_name):
    path = os.path.join(ICONS_DIR, f"{type_name.lower()}.svg")
    if not os.path.exists(path): path = os.path.join(ICONS_DIR, f"{type_name}.svg")
    if os.path.exists(path):
        with open(path, "rb") as f: return f"data:image/svg+xml;base64,{base64.b64encode(f.read()).decode()}"
    return None

def apply_nature(stats, nature_name):
    if nature_name not in NATURES or not NATURES[nature_name]: return stats
    mod = NATURES[nature_name]
    new_stats = stats.copy()
    if "+" in mod: new_stats[mod["+"]] = int(new_stats[mod["+"]] * 1.1)
    if "-" in mod: new_stats[mod["-"]] = int(new_stats[mod["-"]] * 0.9)
    return new_stats

def apply_nature_and_evs(stats, nature_name, evs_dict):
    final_stats = {}
    for stat_name, base_val in stats.items():
        ev = evs_dict.get(stat_name, 0); iv = 31
        if stat_name == 'hp': val = ((2 * base_val + iv + (ev/4)) * 50 / 100) + 10 + 50
        else:
            val = ((2 * base_val + iv + (ev/4)) * 50 / 100) + 5
            if nature_name in NATURES and NATURES[nature_name]:
                mod = NATURES[nature_name]
                if mod.get("+") == stat_name: val *= 1.1
                if mod.get("-") == stat_name: val *= 0.9
        final_stats[stat_name] = int(val)
    return final_stats

def calculate_damage_potential(attacker, defender, weather):
    atk_types = attacker['types']; def_types = defender['types']
    type_mult = 1.0
    for at in atk_types:
        local_mult = 1.0
        for dt in def_types: local_mult *= TYPE_CHART.get(at, {}).get(dt, 1.0)
        if local_mult > type_mult: type_mult = local_mult
    
    stab = 1.5 if type_mult >= 1.0 else 1.0
    weather_mod = 1.0
    if weather == "Sun" and "Fire" in atk_types: weather_mod = 1.5
    if weather == "Sun" and "Water" in atk_types: weather_mod = 0.5
    if weather == "Rain" and "Water" in atk_types: weather_mod = 1.5
    if weather == "Rain" and "Fire" in atk_types: weather_mod = 0.5
    
    if attacker['stats']['attack'] > attacker['stats']['special-attack']:
        atk_stat = attacker['stats']['attack']; def_stat = defender['stats']['defense']
    else:
        atk_stat = attacker['stats']['special-attack']; def_stat = defender['stats']['special-defense']
        
    base_dmg = ((22 * 90 * (atk_stat / max(1, def_stat))) / 50) + 2
    final_dmg = base_dmg * type_mult * stab * weather_mod
    real_hp = defender['stats']['hp'] * 1.5 + 60
    hp_pct = (final_dmg / real_hp) * 100
    return hp_pct, type_mult

def simulate_team_battle(user_team, npc_team_names, shiny_mode, weather):
    npc_team_data = []
    for name in npc_team_names:
        d = get_pokemon_data(name, shiny_mode)
        if d: d['current_hp'] = 100.0; npc_team_data.append(d)
    
    user_team_battle = []
    for p in user_team:
        p_copy = p.copy(); p_copy['current_hp'] = 100.0; user_team_battle.append(p_copy)
        
    battle_log = [f"🌍 WEATHER: {weather.upper()}"]
    u_idx = 0; n_idx = 0
    
    while u_idx < len(user_team_battle) and n_idx < len(npc_team_data):
        u_mon = user_team_battle[u_idx]; n_mon = npc_team_data[n_idx]
        battle_log.append(f"--- {u_mon['name']} VS {n_mon['name']} ---")
        
        while u_mon['current_hp'] > 0 and n_mon['current_hp'] > 0:
            u_speed = u_mon['stats']['speed']; n_speed = n_mon['stats']['speed']
            if u_speed == n_speed: u_goes_first = random.choice([True, False])
            else: u_goes_first = u_speed > n_speed
            
            dmg_u_n, eff_u = calculate_damage_potential(u_mon, n_mon, weather)
            dmg_n_u, eff_n = calculate_damage_potential(n_mon, u_mon, weather)
            
            if u_goes_first:
                n_mon['current_hp'] -= dmg_u_n
                battle_log.append(f"{u_mon['name']} attacks! {dmg_u_n:.1f}% ({eff_u}x)")
                if n_mon['current_hp'] <= 0: battle_log.append(f"💀 {n_mon['name']} fainted!"); break
                u_mon['current_hp'] -= dmg_n_u
                battle_log.append(f"{n_mon['name']} attacks! {dmg_n_u:.1f}% ({eff_n}x)")
                if u_mon['current_hp'] <= 0: battle_log.append(f"💀 {u_mon['name']} fainted!"); break
            else:
                u_mon['current_hp'] -= dmg_n_u
                battle_log.append(f"{n_mon['name']} attacks! {dmg_n_u:.1f}% ({eff_n}x)")
                if u_mon['current_hp'] <= 0: battle_log.append(f"💀 {u_mon['name']} fainted!"); break
                n_mon['current_hp'] -= dmg_u_n
                battle_log.append(f"{u_mon['name']} attacks! {dmg_u_n:.1f}% ({eff_u}x)")
                if n_mon['current_hp'] <= 0: battle_log.append(f"💀 {u_mon['name']} fainted!"); break

        if u_mon['current_hp'] <= 0: u_idx += 1
        if n_mon['current_hp'] <= 0: n_idx += 1
        
    winner = "USER" if u_idx < len(user_team_battle) else "NPC"
    return winner, battle_log, user_team_battle, npc_team_data

def calculate_defensive_weaknesses(t1, t2=None):
    weaknesses = {k: 1.0 for k in TYPE_CHART.keys()}
    for atk_type in TYPE_CHART.keys():
        mult = TYPE_CHART[atk_type].get(t1, 1.0)
        if t2 and t2 != "None": mult *= TYPE_CHART[atk_type].get(t2, 1.0)
        weaknesses[atk_type] = mult
    return weaknesses

def calculate_offensive_coverage(team_data):
    hit_types = {t: 0 for t in TYPE_CHART.keys()}
    for p in team_data:
        for atk_type in p['types']:
            targets = TYPE_CHART.get(atk_type, {})
            for def_type, eff in targets.items():
                if eff >= 2.0: hit_types[def_type] += 1
    return hit_types

def create_radar(stats_dict, name, color="#29b6f6"):
    map_names = {'hp':'HP', 'attack':'Atk', 'defense':'Def', 'special-attack':'SpA', 'special-defense':'SpD', 'speed':'Spe'}
    r = [stats_dict.get(k, 0) for k in map_names.keys()]
    theta = list(map_names.values())
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=r, theta=theta, fill='toself', name=name, line=dict(color=color), fillcolor=get_rgba(color, 0.4)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 160], showticklabels=False), bgcolor='rgba(0,0,0,0)'),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(t=20, b=20, l=40, r=40), font=dict(color='white'))
    return fig

# --- FUNZIONI DI CALCOLO GRAFO (LAZY LOADING) ---
def calculate_graph_heavy():
    DefGraph = nx.DiGraph()
    for atk, targets in TYPE_CHART.items():
        for defe, eff in targets.items():
            if eff <= 0.5: DefGraph.add_edge(atk, defe, weight=(3 if eff==0 else 1))
    pagerank = nx.pagerank(DefGraph)
    SimGraph = nx.Graph()
    all_types = list(TYPE_CHART.keys())
    SimGraph.add_nodes_from(all_types)
    for i in range(len(all_types)):
        for j in range(i+1, len(all_types)):
            t1, t2 = all_types[i], all_types[j]
            tgt1 = {k for k,v in TYPE_CHART[t1].items() if v==2.0}
            tgt2 = {k for k,v in TYPE_CHART[t2].items() if v==2.0}
            if tgt1 or tgt2:
                sim = len(tgt1.intersection(tgt2)) / len(tgt1.union(tgt2))
                if sim > 0: SimGraph.add_edge(t1, t2, weight=sim)
    pos = nx.spring_layout(SimGraph, k=4.0, iterations=200, seed=42)
    scale = 650
    for k in pos: pos[k] = pos[k]*scale
    return pagerank, pos

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    # --- LOGO & HEADER ---
    st.markdown('<div class="rotom-eye-container"><div class="rotom-eye"></div></div>', unsafe_allow_html=True)
    st.markdown("""<div style="text-align: center; margin-bottom: 20px;"><h1 style="color: #ffffff; font-size: 20px; margin:0;">POKÉNEXUS</h1><div style="font-size: 10px; color: #29b6f6; font-weight:bold; letter-spacing:3px;">SYSTEM v23.0</div></div>""", unsafe_allow_html=True)
    
    # --- STATUS BAR ---
    now = datetime.now().strftime("%H:%M")
    st.markdown(f"""<div class="status-bar"><span>🕒 {now}</span><span>💰 ${st.session_state.balance}</span></div>""", unsafe_allow_html=True)
    st.caption("🌦️ WEATHER: " + st.session_state.weather)
    st.session_state.weather = st.selectbox("Weather", ["Clear", "Sun", "Rain", "Sand"], label_visibility="collapsed")
    
    st.markdown("---")
    
    # --- TRAINER INFO ---
    trainer_name = st.text_input("Name", "Red", label_visibility="collapsed")
    c_class, c_reg = st.columns(2)
    with c_class: trainer_class = st.selectbox("Class", TRAINER_CLASSES, label_visibility="collapsed")
    with c_reg: trainer_region = st.selectbox("Region", REGIONS, label_visibility="collapsed")
    
    # --- BADGES ---
    st.markdown(f"<div style='margin-top:10px; font-size:12px; color:#aaa;'>{trainer_region.upper()} BADGES</div>", unsafe_allow_html=True)
    region_badges = []
    if trainer_region in NPC_DB and "Gym Leaders" in NPC_DB[trainer_region]:
        for leader, data in NPC_DB[trainer_region]["Gym Leaders"].items(): region_badges.append(data[1])
    badge_html = "<div class='badge-grid'>"
    for b_name in region_badges:
        css_class = "badge-earned" if b_name in st.session_state.badges else "badge-locked"
        badge_html += f"<div class='badge-slot {css_class}' title='{b_name}'>🛡️</div>"
    badge_html += "</div>"
    st.markdown(badge_html, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- MISSIONI GIORNALIERE (NUOVO) ---
    st.caption("📜 ACTIVE MISSION")
    
    # Se per qualche motivo lo stato missione non esiste, crealo
    if 'mission' not in st.session_state:
        st.session_state.mission = generate_new_mission()
        
    mission = st.session_state.mission
    
    if mission['done']:
        st.success("MISSION COMPLETE!")
        if st.button("🎁 CLAIM REWARD", use_container_width=True):
            st.session_state.balance += mission['reward']
            st.toast(f"Received ${mission['reward']}!", icon="💰")
            st.session_state.mission = generate_new_mission()
            time.sleep(1)
            st.rerun()
    else:
        # Mostra l'obiettivo
        st.info(f"🎯 {mission['desc']}")
        st.caption(f"Reward: ${mission['reward']}")
        
        # Bottone per cambiare missione (costa soldi)
        if st.button("🔄 Reroll ($100)", use_container_width=True):
            if st.session_state.balance >= 100:
                st.session_state.balance -= 100
                st.session_state.mission = generate_new_mission()
                st.rerun()
            else:
                st.error("Not enough cash!")

    st.markdown("---")

    # --- INVENTARIO ---
    if st.session_state.inventory:
        with st.expander("🎒 INVENTORY"):
            for item, qty in st.session_state.inventory.items(): st.write(f"{item} x{qty}")
        st.markdown("---")

    # --- PARTNER ---
    st.caption("🐾 PARTNER")
    default_idx = all_mons.index("pikachu") if "pikachu" in all_mons else 0
    partner_name = st.selectbox("Select Partner", all_mons, index=default_idx)
    partner_data = get_pokemon_data(partner_name)
    if partner_data:
        st.markdown(f"""<div style="text-align:center;"><img src="{partner_data['sprite']}" width="100" style="filter: drop-shadow(0 0 5px rgba(255,255,255,0.5));"></div>""", unsafe_allow_html=True)
        # Audio Player visibile per il partner
        audio_url = f"https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/{partner_data['id']}.ogg"
        st.markdown(f"""<audio src="{audio_url}" controlslist="nodownload" style="width:100%; height:30px; margin-top:5px; opacity:0.8;" controls></audio>""", unsafe_allow_html=True)

    st.markdown("---")
    shiny_mode = st.toggle("✨ SHINY MODE", value=False)
    
    # --- SAVE / LOAD SYSTEM (NUOVO) ---
    st.markdown("---")
    with st.expander("⚙️ SYSTEM / SAVE DATA"):
        st.caption("Download your progress to keep it safe.")
        
        # 1. Preparazione Dati
        save_data = {
            'balance': st.session_state.balance,
            'wins': st.session_state.wins,
            'losses': st.session_state.losses,
            'badges': st.session_state.badges,
            'ribbons': st.session_state.ribbons,
            'trophies': st.session_state.trophies,
            'inventory': st.session_state.inventory,
            'pc_box': st.session_state.pc_box,
            'saved_team': st.session_state.saved_team,
            'mission': st.session_state.mission
        }
        json_str = json.dumps(save_data)
        
        # 2. Download Button
        st.download_button(
            label="💾 DOWNLOAD SAVE FILE",
            data=json_str,
            file_name="pokenexus_save.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.markdown("---")
        
        # 3. Upload Button
        uploaded_file = st.file_uploader("Load Save File", type=["json"], label_visibility="collapsed")
        
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                # Ripristina stato
                for k, v in data.items():
                    st.session_state[k] = v
                
                st.toast("Game Loaded Successfully!", icon="✅")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error loading file: {e}")

# ==========================================
# 5. TABS PRINCIPALI (AGGIORNATA v24.1)
# ==========================================
st.title("🔴 POKÉNEXUS ANALYTICS")

# Abbiamo rinominato SLOTS in ARCADE
tabs = st.tabs([
    "🕸️ NETWORK", "📖 POKÉDEX", "📊 STATS", "🧮 CALC", "⚔️ ARENA", 
    "🛡️ TEAM", "🏪 PLAZA", "🌲 SAFARI", "💻 BOX", "🎮 PLAY", 
    "⛏️ MINE", "🪪 CARD", "🎰 ARCADE", "🍓 FARM"
])

# --- TAB 1: NETWORK ---
with tabs[0]:
    col_c, col_n = st.columns([1, 4])
    with col_c:
        st.markdown("### ⚙️ Filters")
        focus = st.multiselect("Focus Type", list(TYPE_CHART.keys()), max_selections=1)
        physics = st.toggle("Gravity", False)
        if not os.path.exists(ICONS_DIR): st.warning("⚠️ Icons folder missing!")
    with col_n:
        pagerank, positions = calculate_graph_heavy()
        min_pr, max_pr = min(pagerank.values()), max(pagerank.values())
        
        net = Network(height="700px", width="100%", bgcolor="#050505", font_color="white")
        for t in TYPE_CHART.keys():
            x, y = positions[t][0], positions[t][1]
            size = 40 + ((pagerank.get(t, 0) - min_pr) / (max_pr - min_pr)) * 40
            color_conf = {"background": TYPE_COLORS[t], "border": "#ffffff", "highlight": {"background": TYPE_COLORS[t], "border": "#ffffff"}, "hover": {"background": TYPE_COLORS[t], "border": "#ffffff"}}
            node_args = {"label": t, "x": x, "y": y, "size": size, "borderWidth": 2, "borderWidthSelected": 5, "color": color_conf, "physics": physics, "font": {"size": 18, "color": "white", "face": "Verdana", "vadjust": -(size+30)}}
            img = get_local_icon(t)
            if img: node_args["shape"] = "circularImage"; node_args["image"] = img; node_args["imagePadding"] = 5
            else: node_args["shape"] = "dot"
            net.add_node(t, **node_args)
        for atk, targets in TYPE_CHART.items():
            for defe, eff in targets.items():
                if eff == 2.0:
                    if focus and (atk not in focus and defe not in focus): continue
                    c_line = TYPE_COLORS[atk]
                    edge_color = {"color": get_rgba(c_line, 0.15), "highlight": get_rgba(c_line, 1.0), "hover": get_rgba(c_line, 1.0), "inherit": False, "opacity": 1.0}
                    net.add_edge(atk, defe, width=2, color=edge_color)
        phys_str = "true" if physics else "false"
        net.set_options(f"""var options = {{ "interaction": {{"zoomView": true, "hover": true}}, "physics": {{"enabled": {phys_str}, "solver": "forceAtlas2Based"}} }}""")
        net.save_graph("net.html")
        try:
            with open("net.html", 'r') as f: components.html(f.read(), height=710)
        except: pass

# --- TAB 2: POKEDEX ---
with tabs[1]:
    c_search, _ = st.columns([1, 2])
    name_sel = c_search.selectbox("Search Data", all_mons, index=all_mons.index("gengar") if "gengar" in all_mons else 0)
    if name_sel:
        data = get_pokemon_data(name_sel, shiny_mode)
        if data:
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                st.markdown(f"""<div style="text-align:center; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; border: 1px solid #444;"><h3 style="color:#aaa;">#{data['id']}</h3><img src="{data['sprite']}" width="150"><h2 style="color:white;">{data['name']}</h2></div>""", unsafe_allow_html=True)
                # Player Audio Dex (visibile e controllabile)
                audio_url = f"https://raw.githubusercontent.com/PokeAPI/cries/main/cries/pokemon/latest/{data['id']}.ogg"
                st.markdown(f"""<audio src="{audio_url}" controlslist="nodownload" style="width:100%; margin-top:10px;" controls></audio>""", unsafe_allow_html=True)
            with c2:
                st.markdown("#### TYPE")
                for t in data['types']:
                    c = TYPE_COLORS.get(t, "#555")
                    st.markdown(f"<span class='type-badge' style='background:{c}'>{t}</span>", unsafe_allow_html=True)
                st.markdown("#### INFO")
                st.write(f"**Abilities:** {', '.join(data['abilities'])}")
                with st.expander("⚔️ MOVE POOL (Top 20)"):
                    st.write(", ".join(data['moves'][:20]) + "...")
            with c3:
                st.plotly_chart(create_radar(data['stats'], data['name']), use_container_width=True)

# --- TAB 3: STATISTICS ---
with tabs[2]:
    st.markdown("### 🧬 EVS CALCULATOR (Level 50)")
    c_p, c_g = st.columns([1, 2])
    with c_p:
        sel_mon = st.selectbox("Target Pokémon", all_mons, index=all_mons.index("garchomp"))
        mon_data = get_pokemon_data(sel_mon, shiny_mode)
        sel_nature = st.selectbox("Nature", list(NATURES.keys()))
        evs = {}
        evs['hp'] = st.slider("HP", 0, 252, 0)
        evs['attack'] = st.slider("Atk", 0, 252, 252)
        evs['defense'] = st.slider("Def", 0, 252, 0)
        evs['special-attack'] = st.slider("SpA", 0, 252, 0)
        evs['special-defense'] = st.slider("SpD", 0, 252, 4)
        evs['speed'] = st.slider("Spe", 0, 252, 252)
    with c_g:
        if mon_data:
            final_stats = apply_nature_and_evs(mon_data['stats'], sel_nature, evs)
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=list(mon_data['stats'].values()), theta=list(mon_data['stats'].keys()), fill='toself', name='Base Stats'))
            fig.add_trace(go.Scatterpolar(r=list(final_stats.values()), theta=list(final_stats.keys()), fill='toself', name='Lvl 50 Trained'))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True), bgcolor='rgba(0,0,0,0)'), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig, use_container_width=True)
            st.write("**Final Stats at Lvl 50:**")
            cols = st.columns(6)
            for idx, (k, v) in enumerate(final_stats.items()): cols[idx].metric(k.upper(), v, delta=v - mon_data['stats'][k])

# --- TAB 4: CALCULATOR ---
with tabs[3]:
    st.markdown("### 🧮 DEFENSIVE TYPE CALCULATOR")
    c_t1, c_t2 = st.columns(2)
    with c_t1: type1 = st.selectbox("Primary Type", list(TYPE_CHART.keys()))
    with c_t2: type2 = st.selectbox("Secondary Type", ["None"] + list(TYPE_CHART.keys()))
    if st.button("CALCULATE"):
        effs = calculate_defensive_weaknesses(type1, type2)
        weak_4x = [k for k,v in effs.items() if v >= 4.0]; weak_2x = [k for k,v in effs.items() if v == 2.0]
        resist_05 = [k for k,v in effs.items() if v == 0.5]; resist_025 = [k for k,v in effs.items() if v == 0.25]
        immune = [k for k,v in effs.items() if v == 0.0]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.error("⚠️ WEAKNESSES")
            if weak_4x: st.markdown("**4x Dmg:** " + " ".join([f"<span class='type-badge' style='background:{TYPE_COLORS[t]}'>{t}</span>" for t in weak_4x]), unsafe_allow_html=True)
            if weak_2x: st.markdown("**2x Dmg:** " + " ".join([f"<span class='type-badge' style='background:{TYPE_COLORS[t]}'>{t}</span>" for t in weak_2x]), unsafe_allow_html=True)
        with c2:
            st.success("🛡️ RESISTANCES")
            if resist_05: st.markdown("**0.5x Dmg:** " + " ".join([f"<span class='type-badge' style='background:{TYPE_COLORS[t]}'>{t}</span>" for t in resist_05]), unsafe_allow_html=True)
            if resist_025: st.markdown("**0.25x Dmg:** " + " ".join([f"<span class='type-badge' style='background:{TYPE_COLORS[t]}'>{t}</span>" for t in resist_025]), unsafe_allow_html=True)
        with c3:
            st.info("👻 IMMUNITIES")
            if immune: st.markdown("**0x Dmg:** " + " ".join([f"<span class='type-badge' style='background:{TYPE_COLORS[t]}'>{t}</span>" for t in immune]), unsafe_allow_html=True)

# --- TAB 5: BATTLE ARENA (Con Battle Tower) ---
with tabs[4]:
    st.markdown("### ⚔️ BATTLE SIMULATION")
    
    # Selettore Modalità
    mode = st.radio("Mode", ["Practice (1v1)", "🏰 Battle Tower (Endless)"], horizontal=True, label_visibility="collapsed")
    
    if mode == "Practice (1v1)":
        st.caption("Simulation Mode: Test your stats against any opponent.")
        c_sel1, c_vs, c_sel2 = st.columns([2, 1, 2])
        with c_sel1:
            p1_name = st.selectbox("CHALLENGER", all_mons, index=all_mons.index("garchomp"))
            p1_nature = st.selectbox("Nature P1", list(NATURES.keys()))
            p1 = get_pokemon_data(p1_name, shiny_mode)
            if p1: p1['stats'] = apply_nature(p1['stats'], p1_nature)
        with c_sel2:
            p2_name = st.selectbox("OPPONENT", all_mons, index=all_mons.index("sylveon"))
            p2_nature = st.selectbox("Nature P2", list(NATURES.keys()))
            p2 = get_pokemon_data(p2_name, shiny_mode)
            if p2: p2['stats'] = apply_nature(p2['stats'], p2_nature)
        with c_vs: st.markdown("<br><br><h1 style='text-align:center; color:#29b6f6;'>VS</h1>", unsafe_allow_html=True)

        if p1 and p2:
            col_p1, col_stats, col_p2 = st.columns([1, 2, 1])
            with col_p1:
                st.markdown(f"""<div style="text-align:center; border: 1px solid #29b6f6; border-radius:10px; padding:10px;"><h3 style="color:#29b6f6">{p1['name']}</h3><img src="{p1['sprite']}" width="140" style="transform: scaleX(-1);"><br>{' '.join([f'<span class="type-badge" style="background:{TYPE_COLORS.get(t,"#555")}">{t}</span>' for t in p1['types']])}</div>""", unsafe_allow_html=True)
            with col_p2:
                st.markdown(f"""<div style="text-align:center; border: 1px solid #ff0050; border-radius:10px; padding:10px;"><h3 style="color:#ff0050">{p2['name']}</h3><img src="{p2['sprite']}" width="140"><br>{' '.join([f'<span class="type-badge" style="background:{TYPE_COLORS.get(t,"#555")}">{t}</span>' for t in p2['types']])}</div>""", unsafe_allow_html=True)

            with col_stats:
                p1_speed = p1['stats']['speed']; p2_speed = p2['stats']['speed']
                first = p1 if p1_speed >= p2_speed else p2
                dmg_1_to_2, eff_1 = calculate_damage_potential(p1, p2, st.session_state.weather)
                dmg_2_to_1, eff_2 = calculate_damage_potential(p2, p1, st.session_state.weather)
                
                hits_to_kill_p2 = math.ceil(100 / dmg_1_to_2) if dmg_1_to_2 > 0 else 999
                hits_to_kill_p1 = math.ceil(100 / dmg_2_to_1) if dmg_2_to_1 > 0 else 999
                
                if p1_speed >= p2_speed: winner = p1 if hits_to_kill_p2 <= hits_to_kill_p1 else p2
                else: winner = p2 if hits_to_kill_p1 <= hits_to_kill_p2 else p1
                    
                st.caption(f"🏆 BATTLE ANALYSIS ({st.session_state.weather})")
                st.markdown(f"""
                <div class="battle-log-area">
                > {first['name']} is faster (Spd {first['stats']['speed']}).<br>
                > {p1['name']} deals ~{dmg_1_to_2:.1f}% per hit ({eff_1}x).<br>
                > {p2['name']} deals ~{dmg_2_to_1:.1f}% per hit ({eff_2}x).<br>
                > <b>RESULT: {winner['name']} Wins!</b>
                </div>
                """, unsafe_allow_html=True)
                if winner == p1: st.success(f"{p1['name']} Dominates!")
                else: st.error(f"{p2['name']} Dominates!")

            st.markdown("---")
            stats = ['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed']
            fig = go.Figure()
            fig.add_trace(go.Bar(name=p1['name'], x=[s.upper()[:3] for s in stats], y=[p1['stats'][s] for s in stats], marker_color='#29b6f6'))
            fig.add_trace(go.Bar(name=p2['name'], x=[s.upper()[:3] for s in stats], y=[p2['stats'][s] for s in stats], marker_color='#ff0050'))
            fig.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), height=300, margin=dict(t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

    else:
        # --- BATTLE TOWER MODE ---
        st.markdown(f"### 🏰 BATTLE TOWER | STREAK: {st.session_state.tower_streak} 🔥")
        st.info("Win battles to earn Battle Points (BP). If you lose, your streak resets!")
        
        if not st.session_state.saved_team or st.session_state.saved_team[0] == "None":
            st.error("You need a Team defined in the 'TEAM' tab to enter the Tower!")
        else:
            # Genera nemico
            if st.session_state.tower_streak < 3:
                pool = SAFARI_POOLS['Common']
            elif st.session_state.tower_streak < 7:
                pool = SAFARI_POOLS['Rare']
            else:
                pool = SAFARI_POOLS['Legendary']
            
            enemy_mon = random.choice(pool)
            
            col_u, col_vs, col_e = st.columns([2,1,2])
            with col_u:
                st.markdown("**YOUR TEAM**")
                st.write(f"Members: {len([x for x in st.session_state.saved_team if x != 'None'])}")
            with col_e:
                st.markdown(f"**NEXT OPPONENT: {enemy_mon.upper()}**")
                d_en = get_pokemon_data(enemy_mon)
                st.image(d_en['sprite'], width=100)
            
            if st.button("⚔️ START BATTLE", use_container_width=True):
                valid_team = [get_pokemon_data(x, shiny_mode) for x in st.session_state.saved_team if x != "None"]
                
                with st.spinner("Fighting..."):
                    winner, logs, _, _ = simulate_team_battle(valid_team, [enemy_mon], shiny_mode, st.session_state.weather)
                    
                    if winner == "USER":
                        st.session_state.tower_streak += 1
                        reward = 500 + (st.session_state.tower_streak * 100)
                        st.session_state.balance += reward
                        st.balloons()
                        st.success(f"VICTORY! Streak: {st.session_state.tower_streak} | Won ${reward}")
                        play_sound("heal.mp3")
                    else:
                        st.error(f"DEFEAT! Your streak of {st.session_state.tower_streak} ended.")
                        st.session_state.tower_streak = 0
                        st.session_state.losses += 1
                
                with st.expander("Battle Log"):
                    st.text("\n".join(logs))

# --- TAB 6: SQUAD BUILDER ---
with tabs[5]:
    st.markdown("### 🛡️ TEAM VISUAL BUILDER")
    cols = st.columns(6)
    team_data = []
    all_mons_list = ["None"] + all_mons
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"<div class='slot-label'>SLOT {i+1}</div>", unsafe_allow_html=True)
            idx = all_mons_list.index(st.session_state.saved_team[i]) if st.session_state.saved_team[i] in all_mons_list else 0
            choice = st.selectbox(f"S{i+1}", all_mons_list, index=idx, key=f"ts_{i}", label_visibility="collapsed")
            st.session_state.saved_team[i] = choice
            if choice != "None":
                p = get_pokemon_data(choice, shiny_mode)
                if p:
                    team_data.append(p)
                    st.markdown(f"<div class='team-card'><img src='{p['sprite']}' width='80'><div style='font-size:0.8em;'>{p['name']}</div></div>", unsafe_allow_html=True)
            else: st.markdown("<div class='team-card' style='opacity:0.3; border-style:dashed;'><br>EMPTY</div>", unsafe_allow_html=True)

    if team_data:
        st.markdown("---")
        st.markdown("#### 🎯 OFFENSIVE COVERAGE")
        coverage = calculate_offensive_coverage(team_data)
        cov_cols = st.columns(9)
        for idx, (t, count) in enumerate(coverage.items()):
            bg = TYPE_COLORS[t]; opacity = 1.0 if count > 0 else 0.2
            cov_cols[idx % 9].markdown(f"<div class='coverage-box' style='background:{bg}; opacity:{opacity}; font-weight:bold; text-align:center; padding:5px; border-radius:4px;'>{t[:3]}<br>{count}</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🏟️ NPC TEAM CHALLENGE")
        c_reg, c_rank, c_train = st.columns(3)
        with c_reg: reg_sel = st.selectbox("Region", list(NPC_DB.keys()))
        with c_rank: rank_sel = st.selectbox("Rank", list(NPC_DB[reg_sel].keys()))
        with c_train: trainer_sel = st.selectbox("Trainer", list(NPC_DB[reg_sel][rank_sel].keys()))
            
        if st.button("🔴 SIMULATE FULL BATTLE"):
            npc_info = NPC_DB[reg_sel][rank_sel][trainer_sel]
            with st.spinner(f"Simulating..."):
                winner, battle_log, u_team_end, n_team_end = simulate_team_battle(team_data, npc_info[0], shiny_mode, st.session_state.weather)
                c_res1, c_res2 = st.columns(2)
                with c_res1:
                    st.markdown("#### YOUR TEAM")
                    html_u = "".join([f"<img src='{p['sprite']}' class='{'alive' if p['current_hp']>0 else 'dead'}' width='50' style='margin:2px;'>" for p in u_team_end])
                    st.markdown(html_u, unsafe_allow_html=True)
                with c_res2:
                    st.markdown(f"#### {trainer_sel.upper()}'S TEAM")
                    html_n = "".join([f"<img src='{p['sprite']}' class='{'alive' if p['current_hp']>0 else 'dead'}' width='50' style='margin:2px;'>" for p in n_team_end])
                    st.markdown(html_n, unsafe_allow_html=True)
                
                if winner == "USER": 
                    st.toast(f"🏆 YOU WON! Received ${npc_info[2]} & {npc_info[1]}!", icon="🎉")
                    st.session_state.wins += 1; st.session_state.balance += npc_info[2]
                    if rank_sel == "Gym Leaders" and npc_info[1] not in st.session_state.badges: st.session_state.badges.append(npc_info[1])
                    if rank_sel == "Elite 4" and npc_info[1] not in st.session_state.ribbons: st.session_state.ribbons.append(npc_info[1])
                    if rank_sel == "Champion" and npc_info[1] not in st.session_state.trophies: st.session_state.trophies.append(npc_info[1])
                else: 
                    st.error("💀 DEFEAT!"); st.session_state.losses += 1
                
                with st.expander("📜 FULL BATTLE LOG"): st.text("\n".join(battle_log))

# --- TAB 7: PLAZA ---
with tabs[6]:
    st.markdown("### 🏪 POKÉPLAZA")
    c_center, c_egg, c_mart = st.columns([1, 1, 1.5])
    
    with c_center:
        st.markdown("<div class='nurse-box'><h3>🏥 POKÉ CENTER</h3><p>Rest Team</p></div>", unsafe_allow_html=True)
        if st.button("💖 HEAL", use_container_width=True):
            st.toast("Team healed!", icon="💚")
            play_sound("heal.mp3")

    with c_egg:
        st.markdown("<div class='nurse-box' style='border-color:#ffd700; background:rgba(255, 215, 0, 0.1);'><h3>🥚 HATCHERY</h3><p>Rare Baby Mons</p></div>", unsafe_allow_html=True)
        if st.button("🥚 BUY EGG ($1000)", use_container_width=True):
            if st.session_state.balance >= 1000:
                st.session_state.balance -= 1000
                hatched = random.choice(EGG_POOL)
                st.session_state.pc_box.append(hatched)
                st.balloons()
                st.toast(f"Hatched {hatched.upper()}!", icon="🐣")
                d_hatched = get_pokemon_data(hatched, shiny_mode)
                if d_hatched: st.image(d_hatched['sprite'], width=100)
                play_sound("heal.mp3") 
            else:
                st.error("Not enough cash!")

    with c_mart:
        st.markdown(f"### 🛒 MART | 💰 ${st.session_state.balance}")
        cols = st.columns(3)
        for idx, (item, details) in enumerate(SHOP_ITEMS.items()):
            with cols[idx % 3]:
                st.markdown(f"<div class='shop-item'><div style='font-size:20px;'>{details['icon']}</div><b style='font-size:12px;'>{item}</b><br><span style='color:#00ff80; font-size:12px;'>${details['price']}</span></div>", unsafe_allow_html=True)
                if st.button(f"BUY", key=f"buy_{item}"):
                    if st.session_state.balance >= details['price']:
                        st.session_state.balance -= details['price']
                        st.session_state.inventory[item] = st.session_state.inventory.get(item, 0) + 1
                        st.toast(f"Bought {item}!", icon="🛍️"); st.rerun()
                    else: st.error("No cash!")
# --- TAB 8: SAFARI ZONE (INFINITE & ALL POKEMON) ---
with tabs[7]:
    st.markdown("### 🌲 SAFARI ZONE")
    
    balls_count = st.session_state.inventory.get('Poké Ball', 0)
    st.info(f"You have {balls_count} Poké Balls available.")
    
    c_act, c_vis = st.columns([1, 2])
    
    # --- CERCA NELL'ERBA ALTA ---
    with c_act:
        if st.button("🔍 SEARCH TALL GRASS", use_container_width=True):
            with st.spinner("Wild Pokémon appeared..."):
                found_mon = None
                final_rarity = "Common"
                
                # --- LOGICA INFINITA (REJECTION SAMPLING) ---
                # Peschiamo da TUTTI i pokemon esistenti (all_mons)
                # Ma bilanciamo le probabilità in base alla forza (BST)
                for _ in range(10): # Proviamo 10 volte a trovare un pokemon adatto
                    candidate_name = random.choice(all_mons)
                    data = get_pokemon_data(candidate_name, shiny_mode)
                    
                    if not data: continue
                    
                    bst = data['bst']
                    
                    # Definisci Rarità in base alle statistiche totali
                    if bst >= 580:
                        rarity = "Legendary"
                        keep_chance = 0.02 # 2% di probabilità se è leggendario
                    elif bst >= 480:
                        rarity = "Rare"
                        keep_chance = 0.20 # 20% di probabilità se è forte
                    else:
                        rarity = "Common"
                        keep_chance = 1.0  # 100% se è comune
                    
                    # Tira il dado
                    if random.random() < keep_chance:
                        found_mon = data
                        final_rarity = rarity
                        break
                
                # Fallback: Se dopo 10 tentativi non abbiamo tenuto nulla (sfiga), prendiamo l'ultimo
                if not found_mon:
                    found_mon = data
                    final_rarity = "Legendary" if data['bst'] >= 580 else "Rare" if data['bst'] >= 480 else "Common"

                # Salva l'incontro
                st.session_state.safari_enc = {"name": found_mon['name'], "rarity": final_rarity}
                st.rerun()
    
    # --- VISUALIZZA INCONTRO ---
    with c_vis:
        if st.session_state.safari_enc:
            enc = st.session_state.safari_enc
            d = get_pokemon_data(enc["name"], shiny_mode)
            
            if d:
                # Colori titolo
                color_map = {"Common": "#aaaaaa", "Rare": "#00aaff", "Legendary": "#ffaa00"}
                c_code = color_map.get(enc['rarity'], "#fff")
                
                if enc['rarity'] == "Legendary":
                    st.warning("⚠️ A POWERFUL PRESENCE IS NEAR!")
                
                st.markdown(f"<h3 style='color:{c_code}; text-align:center; border-bottom:2px solid {c_code};'>WILD {enc['name'].upper()}</h3>", unsafe_allow_html=True)
                st.caption(f"Class: {enc['rarity']} | BST: {d['bst']}")
                
                st.image(d['sprite'], width=200)
                
                c1, c2 = st.columns(2)
                
                # CATTURA
                if c1.button("🔴 THROW BALL", use_container_width=True):
                    if balls_count > 0:
                        st.session_state.inventory["Poké Ball"] -= 1
                        
                        # Percentuali di Cattura
                        base_rate = 0.70 if enc['rarity'] == 'Common' else 0.40 if enc['rarity'] == 'Rare' else 0.15
                        # Bonus Medaglie
                        if len(st.session_state.badges) > 4: base_rate += 0.1
                        
                        if random.random() < base_rate:
                            # --- PRESO! ---
                            st.session_state.pc_box.append(enc['name'])
                            
                            play_sound("catch.mp3") # Assicurati di avere il file
                            st.balloons()
                            st.toast(f"Gotcha! {enc['name']} sent to PC!", icon="📦")
                            
                            # Mission Check
                            mission = st.session_state.mission
                            if not mission['done'] and mission['type'] in d['types']:
                                st.session_state.mission['done'] = True
                                st.balloons()
                                st.toast("🎯 MISSION COMPLETE!", icon="🏆")
                            
                            st.session_state.safari_enc = None
                            time.sleep(3.5)
                            st.rerun()
                        else:
                            st.error(f"Darn! The wild {enc['name']} broke free!")
                    else:
                        st.warning("No Balls!")
                
                # FUGA
                if c2.button("🏃 RUN AWAY", use_container_width=True):
                    st.session_state.safari_enc = None
                    st.rerun()

# --- TAB 9: PC STORAGE (MERGED: NICKNAMES + WONDER TRADE) ---
with tabs[8]:
    st.markdown("### 💻 PC STORAGE SYSTEM")
    
    # 1. FOSSIL LAB (Tuo codice originale mantenuto)
    my_fossils = {k: v for k, v in st.session_state.inventory.items() if k in FOSSILS and v > 0}
    if my_fossils:
        st.markdown("#### 🦴 FOSSIL LAB")
        f_cols = st.columns(len(my_fossils))
        for i, (f_name, qty) in enumerate(my_fossils.items()):
            with f_cols[i]:
                f_sprite = get_item_sprite(f_name)
                if f_sprite: st.image(f_sprite, width=80)
                else: st.markdown("🦴")
                st.markdown(f"**{f_name}**")
                if st.button("🧬 REVIVE", key=f"rev_{f_name}"):
                    pokemon_result = FOSSILS[f_name]
                    st.session_state.inventory[f_name] -= 1
                    if st.session_state.inventory[f_name] == 0: del st.session_state.inventory[f_name]
                    st.session_state.pc_box.append(pokemon_result)
                    st.toast(f"Success! {f_name} revived!", icon="🦕")
                    play_sound("win.mp3") 
                    time.sleep(1.5) 
                    st.rerun()
        st.markdown("---")

    # 2. BOX POKEMON (Tuo codice originale mantenuto)
    c_info, c_action = st.columns([2, 1])
    with c_info: st.caption(f"Captured: {len(st.session_state.pc_box)}")
    
    if st.session_state.pc_box:
        cols = st.columns(5)
        for i, mon_name in enumerate(st.session_state.pc_box):
            d = get_pokemon_data(mon_name, shiny_mode)
            if d:
                with cols[i % 5]:
                    # Recupera nickname se esiste
                    display_name = st.session_state.nicknames.get(i, d['name'])
                    
                    st.markdown(f"""
                    <div style="background:rgba(255,255,255,0.05); border:1px solid #444; border-radius:10px; padding:10px; text-align:center; margin-bottom:5px;">
                        <img src='{d['sprite']}' width='60'>
                        <div style='font-size:12px; font-weight:bold; color:#29b6f6;'>{display_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # --- FEATURE A: RENAME (Mantenuta tua versione con Expander) ---
                    with st.expander("✏️ Name"):
                        new_nick = st.text_input("Nick", value=display_name, key=f"input_nick_{i}", label_visibility="collapsed")
                        if st.button("Save", key=f"save_nick_{i}"):
                            st.session_state.nicknames[i] = new_nick
                            st.toast(f"Renamed to {new_nick}!", icon="🏷️")
                            st.rerun()

                    # --- FEATURE B: EVOLUZIONE (Mantenuta tua logica) ---
                    possible_evos = EVOLUTION_DB.get(mon_name.lower())
                    if possible_evos:
                        stone_found = None; target = None
                        for s, r in possible_evos.items():
                            if st.session_state.inventory.get(s, 0) > 0:
                                stone_found = s; target = r; break
                        if stone_found:
                            if st.button("⚡ EVO", key=f"evo_{i}"):
                                st.session_state.inventory[stone_found] -= 1
                                st.session_state.pc_box[i] = target
                                play_sound("win.mp3") 
                                st.toast(f"Evolved into {target.upper()}!", icon="✨")
                                time.sleep(1.5)
                                st.rerun()
                    
                    # --- FEATURE C: RILASCIO (Mantenuta tua logica di re-indicizzazione) ---
                    if st.button("❌ REL", key=f"rel_{i}"):
                        st.session_state.pc_box.pop(i)
                        # Rimuovi nickname
                        if i in st.session_state.nicknames: del st.session_state.nicknames[i]
                        # Scala tutti i nickname successivi (Fondamentale!)
                        new_nicks = {}
                        for idx, name in st.session_state.nicknames.items():
                            if idx < i: new_nicks[idx] = name
                            elif idx > i: new_nicks[idx - 1] = name
                        st.session_state.nicknames = new_nicks
                        
                        st.session_state.balance += 100
                        st.rerun()
    else:
        st.info("Your PC is empty.")

    st.markdown("---")

    # 3. WONDER TRADE (NUOVO - AGGIUNTO IN CODA)
    with st.expander("📡 WONDER TRADE (Global Exchange)", expanded=True):
        st.info("Trade a Pokémon to receive a random one from the world!")
        
        if st.session_state.pc_box:
            # Dropdown: mostra i nomi (o nickname) dei pokemon disponibili
            trade_options = {i: st.session_state.nicknames.get(i, st.session_state.pc_box[i]) for i in range(len(st.session_state.pc_box))}
            
            trade_idx = st.selectbox("Select Pokémon to trade:", list(trade_options.keys()), format_func=lambda x: trade_options[x].upper())
            
            if st.button("🚀 LAUNCH TRADE"):
                # Animazione finta
                with st.spinner("Connecting to Global Network..."):
                    time.sleep(1.0)
                
                # 1. Rimuovi il vecchio Pokémon (Logica POP come nel rilascio)
                old_mon_name = st.session_state.pc_box.pop(trade_idx)
                
                # 2. Gestione Nickname (Come nel rilascio: cancelliamo e riordiniamo)
                if trade_idx in st.session_state.nicknames: del st.session_state.nicknames[trade_idx]
                
                new_nicks = {}
                for idx, name in st.session_state.nicknames.items():
                    if idx < trade_idx: new_nicks[idx] = name
                    elif idx > trade_idx: new_nicks[idx - 1] = name
                st.session_state.nicknames = new_nicks
                
                # 3. Aggiungi il nuovo Pokémon (Random)
                new_mon = random.choice(all_mons)
                st.session_state.pc_box.append(new_mon)
                
                # Suono Jackpot per l'effetto sorpresa
                play_sound("jackpot.mp3") 
                st.balloons()
                st.success(f"TRADE COMPLETED! Sent {old_mon_name} -> Received {new_mon.upper()}!")
                
                time.sleep(2.5)
                st.rerun()
        else:
            st.warning("You need Pokémon to trade.")
# --- TAB 11: THE UNDERGROUND (BIG ICONS VERSION) ---
with tabs[10]:
    st.markdown("### ⛏️ THE UNDERGROUND")
    
    if not st.session_state.mining_grid:
        st.session_state.mining_grid, st.session_state.mining_rewards = generate_mine_grid()
        
    picks = st.session_state.inventory.get("Pickaxe", 0)
    c_stat, c_reset = st.columns([3, 1])
    c_stat.info(f"Pickaxes Available: {picks}")
    
    if c_reset.button("🔄 New Mine"):
        st.session_state.mining_grid, st.session_state.mining_rewards = generate_mine_grid()
        st.rerun()

    grid = st.session_state.mining_grid
    rewards = st.session_state.mining_rewards
    
    # Dizionario Icone Backup
    fallback_icons = {
        "Nugget": "💰", 
        "Fire Stone": "🔥", "Water Stone": "💧", "Thunder Stone": "⚡", 
        "Leaf Stone": "🍃", "Moon Stone": "🌙", "Sun Stone": "☀️", 
        "Shiny Stone": "✨", "Dusk Stone": "🌑", "Dawn Stone": "🌅", "Ice Stone": "❄️",
        "Helix Fossil": "🐚", "Dome Fossil": "🐞", "Old Amber": "🦟",
        "Root Fossil": "🪸", "Claw Fossil": "🦞", 
        "Skull Fossil": "💀", "Armor Fossil": "🛡️",
        "Cover Fossil": "🐢", "Plume Fossil": "🪶",
        "Jaw Fossil": "🦖", "Sail Fossil": "🦕"
    }

    # Griglia 5x5
    for r in range(5):
        cols = st.columns(5)
        for c in range(5):
            with cols[c]:
                is_dug = grid[r][c] == 1
                loot = rewards[r][c]
                
                if not is_dug:
                    # ROCCIA (Bottone di Streamlit, dimensione standard)
                    if st.button("🪨", key=f"mine_{r}_{c}", help="Dig here!"):
                        if picks > 0:
                            st.session_state.inventory["Pickaxe"] -= 1
                            st.session_state.mining_grid[r][c] = 1
                            if loot:
                                st.toast(f"You found a {loot}!", icon="💎")
                                st.session_state.inventory[loot] = st.session_state.inventory.get(loot, 0) + 1
                                if loot == "Nugget": st.session_state.balance += 1000
                            st.rerun()
                        else:
                            st.error("No Pickaxes!")
                else:
                    # SCAVATO (Qui possiamo controllare la grandezza!)
                    if loot:
                        sprite_url = get_item_sprite(loot)
                        if sprite_url:
                            # Immagine Ufficiale: Forza larghezza massima
                            st.markdown(f"""<div style="display:flex;justify-content:center;align-items:center;height:60px;"><img src="{sprite_url}" style="width:80px; max-width:100%;"></div>""", unsafe_allow_html=True)
                        else:
                            # Emoji Fallback: Font molto grande (40px)
                            icon = fallback_icons.get(loot, "💎")
                            st.markdown(f"""<div style="font-size:40px;text-align:center;line-height:1.2;">{icon}</div>""", unsafe_allow_html=True)
                    else:
                        # Buco vuoto
                        st.markdown("""<div style="font-size:40px;text-align:center;opacity:0.1;line-height:1.2;">🕳️</div>""", unsafe_allow_html=True)

# --- TAB 12: TRAINER CARD (FIX BLINDATO) ---
with tabs[11]:
    st.markdown("### 🪪 TRAINER CARD")
    
    total_mons = len(st.session_state.pc_box)
    
    # 1. Definiamo lo stile in una variabile a parte per pulizia
    card_style = "background: linear-gradient(135deg, #DC0A2D 0%, #89061C 100%); padding: 20px; border-radius: 15px; border: 2px solid gold; box-shadow: 0 10px 20px rgba(0,0,0,0.5); color: white; font-family: sans-serif; max-width: 600px; margin: auto;"
    
    # 2. Costruiamo l'HTML come una somma di stringhe (senza indentazione HTML)
    # HEADER
    html_code = f"<div style='{card_style}'>"
    html_code += f"<div style='display:flex; justify-content:space-between; align-items:center; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom:10px;'><div style='font-size:24px; font-weight:bold;'>TRAINER {trainer_name.upper()}</div><div style='font-size:14px; opacity:0.8;'>ID: {random.randint(10000, 99999)}</div></div>"
    
    # STATS BODY
    html_code += f"<div style='display:flex; margin-top: 20px;'><div style='flex:1; line-height: 1.6;'><div><b>MONEY:</b> ${st.session_state.balance}</div><div><b>POKÉDEX:</b> {total_mons}</div><div><b>WINS:</b> {st.session_state.wins}</div><div><b>BADGES:</b> {len(st.session_state.badges)}</div></div><div style='flex:1; text-align:right;'><div style='font-size:80px; line-height: 1;'>👤</div></div></div>"
    
    # TEAM ROW
    html_code += "<div style='background: rgba(0,0,0,0.3); padding: 10px; border-radius: 10px; margin-top: 15px;'><div style='font-size:12px; margin-bottom:5px; opacity: 0.8;'>CURRENT TEAM</div><div style='display:flex; justify-content:space-around; align-items:center;'>"
    
    # LOOP TEAM (Aggiungiamo le immagini una per una alla stringa)
    for mon in st.session_state.saved_team:
        if mon != "None":
            d = get_pokemon_data(mon)
            if d:
                html_code += f"<img src='{d['sprite']}' width='50' style='filter: drop-shadow(0 0 3px rgba(0,0,0,0.5));'>"
        else:
            html_code += "<div style='width:40px; height:40px; border:2px dashed #555; border-radius:50%; opacity: 0.3;'></div>"
            
    # CHIUSURA
    html_code += "</div></div></div>"
    
    # Renderizziamo tutto in un colpo solo
    st.markdown(html_code, unsafe_allow_html=True)
    st.caption("Take a screenshot to share!")

# --- TAB 13: ROCKET ARCADE (CON AUDIO) ---
with tabs[12]:
    st.markdown("### 🎰 ROCKET ARCADE")
    
    col_machine, col_info = st.columns([2, 1])
    
    with col_info:
        st.markdown("""
        <div style="background:#222; padding:15px; border-radius:10px; border:1px solid #444;">
            <h4 style="margin:0; color:#ff0050;">PRIZES</h4>
            <ul style="font-size:12px; list-style:none; padding:0;">
                <li>🍒🍒🍒 : $300</li>
                <li>💎💎💎 : $1.000</li>
                <li>7️⃣7️⃣7️⃣ : $5.000</li>
                <li>⚡⚡⚡ : <b>PORYGON</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.info(f"Coins: ${st.session_state.balance}")

    with col_machine:
        st.markdown("<div style='text-align:center; font-size:14px; margin-bottom:10px;'>INSERT COIN ($100)</div>", unsafe_allow_html=True)
        
        # Simboli
        symbols = ["🍒", "🍊", "🍇", "💎", "7️⃣", "⚡"]
        
        # Stato iniziale
        if 'slot_result' not in st.session_state:
            st.session_state.slot_result = ["❓", "❓", "❓"]
            
        r1, r2, r3 = st.columns(3)
        style_box = "font-size:60px; text-align:center; background:#333; border-radius:10px; border:2px solid #555;"
        
        with r1: st.markdown(f"<div style='{style_box}'>{st.session_state.slot_result[0]}</div>", unsafe_allow_html=True)
        with r2: st.markdown(f"<div style='{style_box}'>{st.session_state.slot_result[1]}</div>", unsafe_allow_html=True)
        with r3: st.markdown(f"<div style='{style_box}'>{st.session_state.slot_result[2]}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🕹️ PLAY", use_container_width=True):
            if st.session_state.balance >= 100:
                st.session_state.balance -= 100
                
                # Logica Pesata (Weighted RNG)
                pool = ["🍒"]*30 + ["🍊"]*30 + ["🍇"]*30 + ["💎"]*15 + ["7️⃣"]*5 + ["⚡"]*2
                s1, s2, s3 = random.choice(pool), random.choice(pool), random.choice(pool)
                st.session_state.slot_result = [s1, s2, s3]
                
                # Check Win & Play Sounds
                if s1 == s2 == s3:
                    if s1 == "🍒": 
                        win = 300; st.session_state.balance += win
                        st.success(f"NICE! You won ${win}")
                        play_sound("win.mp3") # Suono vittoria piccola
                    elif s1 == "💎": 
                        win = 1000; st.session_state.balance += win
                        st.balloons(); st.success(f"BIG WIN! +${win}")
                        play_sound("jackpot.mp3") # Suono vittoria grande
                    elif s1 == "7️⃣": 
                        win = 5000; st.session_state.balance += win
                        st.balloons(); st.success(f"JACKPOT! +${win}")
                        play_sound("jackpot.mp3") # Suono vittoria grande
                    elif s1 == "⚡":
                        st.balloons()
                        st.session_state.pc_box.append("porygon")
                        st.success("JACKPOT! YOU WON A PORYGON!")
                        play_sound("jackpot.mp3") # Suono vittoria grande
                    else:
                        win = 200; st.session_state.balance += win
                        st.success(f"WINNER! +${win}")
                        play_sound("win.mp3")
                else:
                    st.error("No luck...")
                    play_sound("lose.mp3") # Suono sconfitta
                
                # Pausa fondamentale per far sentire il suono prima che la pagina si ricarichi
                time.sleep(1.5) 
                st.rerun()
            else:
                st.error("Insert Coin!")

# --- TAB 14: BERRY GARDEN (SENZA AUDIO) ---
with tabs[13]:
    st.markdown("### 🍓 BERRY GARDEN")
    
    # Controlla semi nell'inventario
    seeds = {k: v for k, v in st.session_state.inventory.items() if "Seed" in k}
    
    c_inv, c_water = st.columns([2, 1])
    with c_inv:
        if seeds:
            st.caption("Your Seeds:")
            st.text(" | ".join([f"{k}: {v}" for k, v in seeds.items()]))
        else:
            st.warning("No seeds! Buy them at the Plaza.")
            
    with c_water:
        # Bottone "Annaffia Tutto" per far avanzare il tempo
        if st.button("💧 WATER ALL", help="Advances growth stage"):
            change = False
            for plot in st.session_state.garden_plots:
                if plot['berry'] is not None and plot['stage'] < 3:
                    plot['stage'] += 1
                    change = True
            if change:
                st.toast("You watered the plants. They grew!", icon="🌱")
                st.rerun()
            else:
                st.info("Nothing to water.")

    st.markdown("---")
    
    # 4 VASI
    cols = st.columns(4)
    for i in range(4):
        plot = st.session_state.garden_plots[i]
        with cols[i]:
            st.markdown(f"<div style='text-align:center; border:2px dashed #444; border-radius:10px; padding:10px; min-height:150px;'>", unsafe_allow_html=True)
            
            # STATO: VUOTO
            if plot['berry'] is None:
                st.markdown("🕳️<br><small>Empty Soil</small>", unsafe_allow_html=True)
                # Selectbox per scegliere cosa piantare
                if seeds:
                    to_plant = st.selectbox("Plant:", list(seeds.keys()), key=f"plant_sel_{i}", label_visibility="collapsed")
                    if st.button("Plant", key=f"btn_plant_{i}"):
                        st.session_state.inventory[to_plant] -= 1
                        if st.session_state.inventory[to_plant] == 0: del st.session_state.inventory[to_plant]
                        
                        # Salva nel vaso (rimuovi "Seed" dal nome per avere il nome della bacca)
                        berry_name = to_plant.replace(" Seed", "")
                        st.session_state.garden_plots[i] = {'stage': 1, 'berry': berry_name, 'water': 0}
                        st.rerun()
            
            # STATO: CRESCITA
            elif plot['stage'] < 3:
                icon = "🌱" if plot['stage'] == 1 else "🌿"
                st.markdown(f"<div style='font-size:40px;'>{icon}</div>", unsafe_allow_html=True)
                st.caption(f"Growing: {plot['berry']}")
                st.progress(plot['stage'] / 3)
            
            # STATO: PRONTO
            elif plot['stage'] >= 3:
                st.markdown("<div style='font-size:40px;'>🍓</div>", unsafe_allow_html=True)
                st.markdown(f"**{plot['berry']} Ready!**")
                if st.button("HARVEST", key=f"harv_{i}"):
                    # Dai 2-4 bacche a caso
                    yield_amt = random.randint(2, 4)
                    item_name = plot['berry'] # Es. "Oran Berry"
                    st.session_state.inventory[item_name] = st.session_state.inventory.get(item_name, 0) + yield_amt
                    
                    # Reset Vaso
                    st.session_state.garden_plots[i] = {'stage': 0, 'berry': None, 'water': 0}
                    
                    st.toast(f"Harvested {yield_amt}x {item_name}!", icon="🧺")
                    st.balloons()
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
# ==========================================
# 6. FOOTER & DISCLAIMER (FIXED)
# ==========================================
st.markdown("---")
current_year = datetime.now().year

footer_html = f"""
<div style="text-align: center; font-family: monospace; color: #888; margin-top: 20px; font-size: 12px;">
    <p style="margin-bottom: 5px;">
        <b>POKÉNEXUS v1.0</b> | App & Code &copy; {current_year} <b>STEFANO BLANDO</b>
    </p>
    <p style="font-size: 10px; opacity: 0.7;">
        Pokémon and Pokémon character names are trademarks of Nintendo.<br>
        This is a non-profit fan project created for educational purposes.<br>
        No copyright infringement intended.
    </p>
    <p style="font-size: 10px; opacity: 0.7;">
        Data provided by <a href="https://pokeapi.co/" target="_blank" style="color: #29b6f6; text-decoration: none;">PokéAPI</a>.
    </p>
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)