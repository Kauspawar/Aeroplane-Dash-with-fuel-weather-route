import streamlit as st
import requests
import math
import time
import random
from datetime import datetime, timezone
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="AeroNav Pro — Flight Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
#  GLOBAL CSS
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
  background: radial-gradient(ellipse at 20% 50%, #0a1628 0%, #050d1a 40%, #000810 100%);
  color: #e2e8f0;
}

/* Animated star background */
.stApp::before {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image:
    radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.4) 0%, transparent 100%),
    radial-gradient(1px 1px at 30% 70%, rgba(255,255,255,0.3) 0%, transparent 100%),
    radial-gradient(1px 1px at 60% 25%, rgba(255,255,255,0.4) 0%, transparent 100%),
    radial-gradient(1px 1px at 80% 80%, rgba(255,255,255,0.3) 0%, transparent 100%),
    radial-gradient(1px 1px at 90% 45%, rgba(255,255,255,0.2) 0%, transparent 100%);
  pointer-events: none;
  z-index: 0;
}

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #020b18 0%, #050d1a 100%) !important;
  border-right: 1px solid rgba(56,189,248,0.15) !important;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }

/* HUD title */
.hud-title {
  font-family: 'Orbitron', monospace;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 4px;
  color: #38bdf8;
  text-transform: uppercase;
}
.hud-sub {
  font-family: 'Orbitron', monospace;
  font-size: 10px;
  color: #1e4d6b;
  letter-spacing: 3px;
}

/* Glass cards */
.glass-card {
  background: rgba(10,22,40,0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(56,189,248,0.12);
  border-radius: 14px;
  padding: 16px 20px;
  box-shadow: 0 4px 32px rgba(0,0,0,0.5), inset 0 1px 0 rgba(56,189,248,0.08);
}

/* Metric cards */
.metric-hud {
  background: linear-gradient(135deg, rgba(10,22,40,0.95) 0%, rgba(5,15,30,0.95) 100%);
  border: 1px solid rgba(56,189,248,0.2);
  border-radius: 10px;
  padding: 14px 16px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.metric-hud::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #38bdf8, transparent);
}
.metric-hud-label {
  font-family: 'Orbitron', monospace;
  font-size: 9px;
  letter-spacing: 2px;
  color: #334d6b;
  text-transform: uppercase;
  margin-bottom: 6px;
}
.metric-hud-value {
  font-family: 'Orbitron', monospace;
  font-size: 22px;
  font-weight: 700;
  color: #38bdf8;
  text-shadow: 0 0 20px rgba(56,189,248,0.5);
  line-height: 1.1;
}
.metric-hud-unit {
  font-size: 10px;
  color: #1e4d6b;
  margin-top: 3px;
  font-weight: 500;
}

/* Clock */
.live-clock {
  font-family: 'Orbitron', monospace;
  font-size: 28px;
  font-weight: 900;
  color: #38bdf8;
  text-shadow: 0 0 30px rgba(56,189,248,0.6), 0 0 60px rgba(56,189,248,0.2);
  letter-spacing: 4px;
  text-align: center;
}
.live-date {
  font-family: 'Orbitron', monospace;
  font-size: 11px;
  color: #1e6b8a;
  letter-spacing: 3px;
  text-align: center;
  margin-top: 4px;
}
.live-badge {
  display: inline-block;
  background: rgba(34,197,94,0.1);
  border: 1px solid #22c55e;
  color: #22c55e;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  padding: 3px 8px;
  border-radius: 4px;
  animation: pulse-green 2s infinite;
  margin-top: 4px;
}
@keyframes pulse-green {
  0%,100% { box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
  50%      { box-shadow: 0 0 0 4px rgba(34,197,94,0); }
}

/* Alert boxes */
.alert-danger  { background:rgba(239,68,68,0.08);  border-left:3px solid #ef4444; border-radius:6px; padding:10px 14px; margin:4px 0; font-size:12px; color:#fca5a5; }
.alert-warning { background:rgba(245,158,11,0.08); border-left:3px solid #f59e0b; border-radius:6px; padding:10px 14px; margin:4px 0; font-size:12px; color:#fcd34d; }
.alert-info    { background:rgba(56,189,248,0.08); border-left:3px solid #38bdf8; border-radius:6px; padding:10px 14px; margin:4px 0; font-size:12px; color:#7dd3fc; }
.alert-ok      { background:rgba(34,197,94,0.08);  border-left:3px solid #22c55e; border-radius:6px; padding:10px 14px; margin:4px 0; font-size:12px; color:#86efac; }

/* Section headers */
.sec-head {
  font-family: 'Orbitron', monospace;
  font-size: 10px;
  letter-spacing: 3px;
  color: #1e6b8a;
  text-transform: uppercase;
  border-bottom: 1px solid rgba(56,189,248,0.1);
  padding-bottom: 8px;
  margin: 18px 0 12px;
}

/* Route cards */
.route-card {
  background: rgba(10,22,40,0.9);
  border: 1px solid rgba(56,189,248,0.1);
  border-radius: 12px;
  padding: 14px 16px;
  margin: 8px 0;
  transition: all 0.2s;
  position: relative;
  overflow: hidden;
}
.route-card.best {
  border-color: rgba(34,197,94,0.4);
  box-shadow: 0 0 20px rgba(34,197,94,0.08);
}
.route-card.best::before {
  content: '★ AI RECOMMENDED';
  position: absolute;
  top: 8px; right: 12px;
  font-family: 'Orbitron', monospace;
  font-size: 8px;
  color: #22c55e;
  letter-spacing: 2px;
}
.route-name {
  font-family: 'Orbitron', monospace;
  font-size: 12px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 10px;
}
.route-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.route-stat {
  text-align: center;
  background: rgba(56,189,248,0.04);
  border-radius: 6px;
  padding: 6px 4px;
}
.route-stat-label { font-size: 9px; color: #334d6b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 3px; }
.route-stat-val   { font-size: 14px; font-weight: 700; font-family: 'Orbitron', monospace; }

/* Fuel gauge */
.fuel-bar-bg { background: rgba(56,189,248,0.08); border-radius: 4px; height: 8px; overflow: hidden; margin: 4px 0; }
.fuel-bar-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(5,13,26,0.8) !important;
  border-bottom: 1px solid rgba(56,189,248,0.1) !important;
  gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Orbitron', monospace !important;
  font-size: 10px !important;
  letter-spacing: 2px !important;
  color: #334d6b !important;
  border-radius: 6px 6px 0 0 !important;
  padding: 10px 20px !important;
}
.stTabs [aria-selected="true"] {
  background: rgba(56,189,248,0.08) !important;
  color: #38bdf8 !important;
  border-bottom: 2px solid #38bdf8 !important;
}
.stTabs [data-baseweb="tab-panel"] {
  background: transparent !important;
  padding: 0 !important;
}

/* Buttons */
.stButton > button {
  font-family: 'Orbitron', monospace !important;
  font-size: 10px !important;
  letter-spacing: 2px !important;
  background: linear-gradient(135deg, rgba(3,105,161,0.8), rgba(2,132,199,0.8)) !important;
  border: 1px solid rgba(56,189,248,0.3) !important;
  color: #e2e8f0 !important;
  border-radius: 6px !important;
  padding: 10px !important;
  width: 100% !important;
  text-transform: uppercase !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, rgba(3,105,161,1), rgba(2,132,199,1)) !important;
  box-shadow: 0 0 20px rgba(56,189,248,0.3) !important;
}

/* Selectbox / inputs */
.stSelectbox > div > div, .stTextInput input {
  background: rgba(5,15,30,0.9) !important;
  border: 1px solid rgba(56,189,248,0.15) !important;
  color: #94a3b8 !important;
  border-radius: 6px !important;
}

div[data-testid="stVerticalBlock"] > div { gap: 0.4rem; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════
AIRPORTS = {
    # Primary airports
    "KSDL — Scottsdale":          (33.6297, -111.9135),
    "KSLC — Salt Lake City":      (40.7934, -111.9799),
    "KPHX — Phoenix Sky Harbor":  (33.4373, -111.9741),
    "KDVT — Phoenix Deer Valley": (33.6883, -112.0822),
    "KDTA — Delta Municipal":     (39.3814, -112.5170),
    "KGCN — Grand Canyon":        (35.9524, -112.1470),
    "KLAS — Las Vegas McCarran":  (36.0840, -115.1537),
    "KVNY — Van Nuys":            (34.2098, -118.4898),
    "KOAK — Oakland Intl":        (37.7213, -122.2208),
    "KSBA — Santa Barbara":       (34.4262, -119.8404),
    "KTUS — Tucson Intl":         (32.1161, -110.9410),
    "KGJT — Grand Junction":      (39.1224, -108.5270),
    "KASE — Aspen Pitkin":        (39.2232, -106.8688),
    "KAPA — Centennial Denver":   (39.5701, -104.8492),
    "KSVR — Sevier Valley":       (38.7724, -112.0877),
    # Small fields / waypoints
    "UT10 — Cedar Valley":        (40.4828, -111.9572),
    "U55 — Panguitch Muni":       (37.7045, -112.3123),
    "59AZ — Robin":               (34.7058, -112.4840),
    # Named GPS fixes
    "QUAKY — Fix":                (34.2833, -111.8500),
    "CARTL — Fix":                (35.1167, -111.9833),
    "LOFTS — Fix":                (35.6500, -112.0000),
    "GCN — Fix/Grand Canyon":     (35.9524, -112.1470),
    "BCE — Bryce Canyon VOR":     (37.6833, -112.1500),
    "NEEBO — Fix":                (39.5167, -112.0333),
}

AIRCRAFT_DB = {
    "Boeing 787-9 Dreamliner":  {"burn_kgh": 5400, "capacity_pax": 296, "range_km": 14140, "max_alt": 43000, "cruise_kts": 488},
    "Boeing 777-300ER":         {"burn_kgh": 7500, "capacity_pax": 396, "range_km": 13649, "max_alt": 43100, "cruise_kts": 490},
    "Airbus A380-800":          {"burn_kgh": 11000,"capacity_pax": 555, "range_km": 15200, "max_alt": 43000, "cruise_kts": 488},
    "Airbus A350-900":          {"burn_kgh": 5800, "capacity_pax": 369, "range_km": 15000, "max_alt": 43100, "cruise_kts": 489},
    "Boeing 737 MAX 8":         {"burn_kgh": 2500, "capacity_pax": 178, "range_km": 6570,  "max_alt": 41000, "cruise_kts": 453},
    "Airbus A320neo":           {"burn_kgh": 2300, "capacity_pax": 165, "range_km": 6300,  "max_alt": 39800, "cruise_kts": 450},
}

WX_CODES = {
    0:  ("Clear",         "☀️",  "#22c55e"),
    1:  ("Mainly Clear",  "🌤️", "#84cc16"),
    2:  ("Partly Cloudy", "⛅",  "#94a3b8"),
    3:  ("Overcast",      "☁️",  "#64748b"),
    45: ("Fog",           "🌫️", "#94a3b8"),
    48: ("Icing Fog",     "🌫️", "#60a5fa"),
    51: ("Light Drizzle", "🌦️", "#38bdf8"),
    61: ("Light Rain",    "🌧️", "#3b82f6"),
    63: ("Moderate Rain", "🌧️", "#2563eb"),
    65: ("Heavy Rain",    "🌧️", "#1d4ed8"),
    71: ("Light Snow",    "❄️",  "#bfdbfe"),
    80: ("Showers",       "🌨️", "#60a5fa"),
    95: ("Thunderstorm",  "⛈️", "#ef4444"),
    96: ("Hail Storm",    "⛈️", "#dc2626"),
    99: ("Severe Storm",  "⛈️", "#b91c1c"),
}

def wx_info(code):
    c = int(code) if code else 0
    for k in sorted(WX_CODES.keys(), reverse=True):
        if c >= k:
            return WX_CODES[k]
    return WX_CODES[0]

def wind_label(deg):
    dirs = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return dirs[round(float(deg)/22.5) % 16]

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d = lambda x: math.radians(x)
    a = math.sin(d(lat2-lat1)/2)**2 + math.cos(d(lat1))*math.cos(d(lat2))*math.sin(d(lon2-lon1)/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def interpolate_route(lat1, lon1, lat2, lon2, n=10, offset_lat=0, offset_lon=0):
    pts = []
    for i in range(n+1):
        f = i/n
        mid_offset = math.sin(f * math.pi)
        lat = lat1 + f*(lat2-lat1) + offset_lat * mid_offset
        lon = lon1 + f*(lon2-lon1) + offset_lon * mid_offset
        pts.append((round(lat,3), round(lon,3)))
    return pts

# ═══════════════════════════════════════════════════════════════
#  API CALLS
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def get_weather(lat, lon):
    try:
        r = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lon,
            "current": "wind_speed_10m,wind_direction_10m,pressure_msl,weather_code,temperature_2m,relative_humidity_2m,precipitation,visibility",
            "hourly": "wind_speed_10m,wind_direction_10m,weather_code,precipitation_probability,temperature_2m,pressure_msl",
            "forecast_days": 2, "timezone": "UTC"
        }, timeout=12)
        return r.json()
    except:
        return None

@st.cache_data(ttl=300)
def get_all_route_weather(pts_tuple):
    results = []
    for lat, lon in pts_tuple:
        w = get_weather(lat, lon)
        cur = w.get("current", {}) if w else {}
        results.append({
            "lat": lat, "lon": lon,
            "wind_speed":  float(cur.get("wind_speed_10m", 0) or 0),
            "wind_dir":    float(cur.get("wind_direction_10m", 0) or 0),
            "pressure":    float(cur.get("pressure_msl", 1013) or 1013),
            "weather_code":int(cur.get("weather_code", 0) or 0),
            "temperature": float(cur.get("temperature_2m", 15) or 15),
            "humidity":    float(cur.get("relative_humidity_2m", 50) or 50),
            "precip":      float(cur.get("precipitation", 0) or 0),
        })
    return results

@st.cache_data(ttl=600)
def get_sigmets():
    try:
        r = requests.get("https://aviationweather.gov/api/data/sigmet?format=json", timeout=10)
        return r.json()
    except:
        return []

# ═══════════════════════════════════════════════════════════════
#  AI ENGINE
# ═══════════════════════════════════════════════════════════════
def ai_fuel_analysis(aircraft, dist_km, wp_weather, cruise_alt, pax_load):
    ac = AIRCRAFT_DB[aircraft]
    base_burn = ac["burn_kgh"]
    cruise_kts = ac["cruise_kts"]
    dist_nm = dist_km * 0.539957
    base_time_h = dist_nm / cruise_kts

    # Wind factor (headwind/tailwind avg)
    avg_wind = np.mean([w["wind_speed"] for w in wp_weather]) if wp_weather else 20
    avg_dir  = np.mean([w["wind_dir"]   for w in wp_weather]) if wp_weather else 0

    # Rough headwind component
    headwind_factor = 1 + (avg_wind * 0.003 * math.cos(math.radians(avg_dir)))
    alt_factor      = 0.92 if cruise_alt >= 35000 else 0.97
    load_factor     = 0.88 + (pax_load / 100) * 0.18
    weather_penalty = 1.0
    for w in wp_weather:
        if int(w["weather_code"]) >= 95: weather_penalty += 0.04
        elif int(w["weather_code"]) >= 80: weather_penalty += 0.02
        elif int(w["weather_code"]) >= 61: weather_penalty += 0.01

    total_factor = headwind_factor * alt_factor * load_factor * weather_penalty
    actual_time_h = base_time_h * headwind_factor
    fuel_burn_total = base_burn * actual_time_h * total_factor
    fuel_per_pax = fuel_burn_total / max(1, round(ac["capacity_pax"] * pax_load/100))
    efficiency_score = max(0, min(100, 100 - (total_factor - 0.9) * 200))

    return {
        "total_fuel_kg": round(fuel_burn_total),
        "fuel_per_pax_kg": round(fuel_per_pax, 1),
        "flight_time_h": round(actual_time_h, 2),
        "efficiency_score": round(efficiency_score, 1),
        "wind_impact": round((headwind_factor - 1) * 100, 1),
        "alt_saving": round((1 - alt_factor) * 100, 1),
        "weather_penalty_pct": round((weather_penalty - 1) * 100, 1),
        "load_factor_pct": round(pax_load),
        "burn_rate_kgh": round(base_burn * total_factor),
        "co2_tonnes": round(fuel_burn_total * 3.16 / 1000, 1),
    }

# ── Predefined routes with exact GPS waypoints ─────────────────────────────
PREDEFINED_ROUTES = {
    # (origin_key, dest_key): list of route dicts, each with name+waypoints
    ("KSDL — Scottsdale", "KSLC — Salt Lake City"): [
        {
            "id": "A", "color": "#38bdf8",
            "name": "VIA DEER VALLEY & DELTA",
            "desc": "KSDL -> KDVT -> KDTA -> Cedar Valley -> KSLC",
            "wpt_coords": [
                (33.6297,-111.9135),(33.6883,-112.0822),(39.3814,-112.5170),
                (40.4828,-111.9572),(40.7934,-111.9799)
            ],
            "dist_factor":1.12,"time_factor":1.10,
        },
        {
            "id": "B", "color": "#a78bfa",
            "name": "VIA PHOENIX & GRAND CANYON",
            "desc": "KSDL -> KPHX -> Robin 59AZ -> KGCN -> Panguitch -> Cedar Valley -> KSLC",
            "wpt_coords": [
                (33.6297,-111.9135),(33.4373,-111.9741),(34.7058,-112.4840),
                (35.9524,-112.1470),(37.7045,-112.3123),(40.4828,-111.9572),
                (40.7934,-111.9799)
            ],
            "dist_factor":1.22,"time_factor":1.20,
        },
        {
            "id": "C", "color": "#34d399",
            "name": "VIA PHOENIX & SEVIER VALLEY",
            "desc": "KSDL -> KPHX -> Robin 59AZ -> KDTA -> KSVR -> KSLC",
            "wpt_coords": [
                (33.6297,-111.9135),(33.4373,-111.9741),(34.7058,-112.4840),
                (39.3814,-112.5170),(38.7724,-112.0877),(40.7934,-111.9799)
            ],
            "dist_factor":1.18,"time_factor":1.15,
        },
        {
            "id": "D", "color": "#fbbf24",
            "name": "PRIMARY — GPS FIXES",
            "desc": "KSDL -> QUAKY -> CARTL -> LOFTS -> GCN -> BCE -> NEEBO -> KSLC",
            "wpt_coords": [
                (33.6297,-111.9135),(34.2833,-111.8500),(35.1167,-111.9833),
                (35.6500,-112.0000),(35.9524,-112.1470),(37.6833,-112.1500),
                (39.5167,-112.0333),(40.7934,-111.9799)
            ],
            "dist_factor":1.08,"time_factor":1.05,
        },
    ],
    ("KLAS — Las Vegas McCarran", "KVNY — Van Nuys"): [
        {
            "id":"A","color":"#38bdf8","name":"DIRECT LAS-VNY",
            "desc":"KLAS -> KVNY direct",
            "wpt_coords":[(36.0840,-115.1537),(34.2098,-118.4898)],
            "dist_factor":1.00,"time_factor":1.00,
        },
    ],
    ("KVNY — Van Nuys", "KOAK — Oakland Intl"): [
        {
            "id":"A","color":"#38bdf8","name":"DIRECT VNY-OAK",
            "desc":"KVNY -> KOAK coastal",
            "wpt_coords":[(34.2098,-118.4898),(37.7213,-122.2208)],
            "dist_factor":1.00,"time_factor":1.00,
        },
    ],
    ("KOAK — Oakland Intl", "KSBA — Santa Barbara"): [
        {
            "id":"A","color":"#38bdf8","name":"DIRECT OAK-SBA",
            "desc":"KOAK -> KSBA coastal",
            "wpt_coords":[(37.7213,-122.2208),(34.4262,-119.8404)],
            "dist_factor":1.00,"time_factor":1.00,
        },
    ],
    ("KSDL — Scottsdale", "KTUS — Tucson Intl"): [
        {
            "id":"A","color":"#38bdf8","name":"DIRECT SDL-TUS",
            "desc":"KSDL -> KTUS direct south",
            "wpt_coords":[(33.6297,-111.9135),(32.1161,-110.9410)],
            "dist_factor":1.00,"time_factor":1.00,
        },
    ],
    ("KGJT — Grand Junction", "KAPA — Centennial Denver"): [
        {
            "id":"A","color":"#38bdf8","name":"DIRECT GJT-APA",
            "desc":"KGJT -> KAPA direct",
            "wpt_coords":[(39.1224,-108.5270),(39.5701,-104.8492)],
            "dist_factor":1.00,"time_factor":1.00,
        },
        {
            "id":"B","color":"#a78bfa","name":"VIA ASPEN",
            "desc":"KGJT -> KASE -> KAPA",
            "wpt_coords":[(39.1224,-108.5270),(39.2232,-106.8688),(39.5701,-104.8492)],
            "dist_factor":1.15,"time_factor":1.12,
        },
    ],
}

def build_waypoints_from_coords(coord_list):
    """Build interpolated waypoint list through exact GPS coords."""
    if len(coord_list) < 2:
        return coord_list
    all_pts = []
    for i in range(len(coord_list)-1):
        seg = interpolate_route(coord_list[i][0], coord_list[i][1],
                                coord_list[i+1][0], coord_list[i+1][1], n=4)
        if i < len(coord_list)-2:
            seg = seg[:-1]  # avoid duplicate junction points
        all_pts.extend(seg)
    return all_pts

def ai_route_optimizer(orig, dest, orig_coords, dest_coords):
    lat1,lon1 = orig_coords
    lat2,lon2 = dest_coords
    dist_km   = haversine(lat1,lon1,lat2,lon2)

    # Check for predefined routes first
    key = (orig, dest)
    if key in PREDEFINED_ROUTES:
        routes = []
        for r in PREDEFINED_ROUTES[key]:
            routes.append({
                "id":          r["id"],
                "name":        r["name"],
                "desc":        r["desc"],
                "color":       r["color"],
                "waypoints":   build_waypoints_from_coords(r["wpt_coords"]),
                "dist_factor": r["dist_factor"],
                "time_factor": r["time_factor"],
            })
    else:
        routes = [
            {
                "id": "A",
                "name": "DIRECT ROUTE",
                "desc": "Great circle, shortest distance",
                "waypoints": interpolate_route(lat1,lon1,lat2,lon2,10,0,0),
                "color": "#38bdf8",
                "dist_factor": 1.00,
                "time_factor": 1.00,
            },
            {
                "id": "B",
                "name": "NORTHERN ROUTE",
                "desc": "Higher latitude, jet stream advantage",
                "waypoints": interpolate_route(lat1,lon1,lat2,lon2,10, 1.5,-1.5),
                "color": "#a78bfa",
                "dist_factor": 1.04,
                "time_factor": 0.97,
            },
            {
                "id": "C",
                "name": "WEATHER AVOIDANCE",
                "desc": "Storm-clear path, longer but safer",
                "waypoints": interpolate_route(lat1,lon1,lat2,lon2,10,-1.5, 2),
                "color": "#34d399",
                "dist_factor": 1.08,
                "time_factor": 1.06,
            },
            {
                "id": "D",
                "name": "FUEL ECONOMY",
                "desc": "Optimal altitude & wind exploitation",
                "waypoints": interpolate_route(lat1,lon1,lat2,lon2,10, 0.5, 0.8),
                "color": "#fbbf24",
                "dist_factor": 1.02,
                "time_factor": 0.98,
            },
        ]

    # Score each route with mock AI weights
    for r in routes:
        d = dist_km * r["dist_factor"]
        t = (d * 0.539957) / 490 * r["time_factor"]
        fuel = 5400 * t * r["dist_factor"]
        wx_pts = r["waypoints"][::3]
        wx_data = get_all_route_weather(tuple(wx_pts))
        storm_count = sum(1 for w in wx_data if int(w["weather_code"]) >= 80)
        avg_wind    = np.mean([w["wind_speed"] for w in wx_data]) if wx_data else 20

        wx_score   = max(0, 100 - storm_count * 20 - avg_wind * 0.3)
        fuel_score = max(0, 100 - (r["dist_factor"] - 1) * 300)
        time_score = max(0, 100 - (r["time_factor"] - 0.9) * 300)
        ai_score   = wx_score * 0.4 + fuel_score * 0.35 + time_score * 0.25

        r.update({
            "dist_km":     round(d),
            "time_h":      round(t, 1),
            "fuel_kg":     round(fuel),
            "wx_score":    round(wx_score),
            "fuel_score":  round(fuel_score),
            "time_score":  round(time_score),
            "ai_score":    round(ai_score),
            "storm_count": storm_count,
            "avg_wind":    round(avg_wind),
            "wx_data":     wx_data,
        })

    routes.sort(key=lambda x: -x["ai_score"])
    routes[0]["is_best"] = True
    for r in routes[1:]: r["is_best"] = False
    return routes

# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 8px">
      <div class="hud-title">✈ AeroNav Pro</div>
      <div class="hud-sub">Flight Intelligence System</div>
    </div>
    """, unsafe_allow_html=True)

    # Live clock in sidebar
    now_utc = datetime.now(timezone.utc)
    now_ist = datetime.now()
    st.markdown(f"""
    <div style="background:rgba(56,189,248,0.04);border:1px solid rgba(56,189,248,0.12);border-radius:10px;padding:14px;margin:8px 0;text-align:center">
      <div class="live-clock">{now_utc.strftime('%H:%M:%S')}</div>
      <div class="live-date">{now_utc.strftime('%d %b %Y')} · UTC</div>
      <div style="margin-top:6px"><span class="live-badge">● LIVE</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec-head">Mission Parameters</div>', unsafe_allow_html=True)
    airport_list = list(AIRPORTS.keys())
    origin_sel = st.selectbox("Origin", airport_list, index=airport_list.index("KSDL — Scottsdale"))
    dest_sel   = st.selectbox("Destination", airport_list, index=airport_list.index("KSLC — Salt Lake City"))
    flight_num = st.text_input("Flight No.", "N131AV")
    aircraft   = st.selectbox("Aircraft", list(AIRCRAFT_DB.keys()))

    st.markdown('<div class="sec-head">Flight Parameters</div>', unsafe_allow_html=True)
    cruise_alt   = st.slider("Cruise Alt (ft)", 28000, 43000, 35000, 1000)
    cruise_speed = st.slider("Speed (knots)",   400,   600,   490,   10)
    pax_load     = st.slider("Pax Load (%)",    60,    100,   85,    5)

    st.markdown('<div class="sec-head">Display</div>', unsafe_allow_html=True)
    show_storms   = st.toggle("Storm zones",    True)
    show_sigmets  = st.toggle("Live SIGMETs",   True)
    show_jetstream= st.toggle("Jet streams",    True)
    auto_refresh  = st.toggle("Auto-refresh",   False)
    map_style     = st.selectbox("Map theme", ["Dark Aviation","Satellite","Terrain"])

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    compute_btn = st.button("⚡ COMPUTE FLIGHT PLAN", use_container_width=True)
    refresh_btn = st.button("↻  REFRESH WEATHER",    use_container_width=True)

if auto_refresh:
    time.sleep(300)
    st.rerun()

if compute_btn or "route_data" not in st.session_state:
    st.session_state.origin   = origin_sel
    st.session_state.dest     = dest_sel
    st.session_state.computed = True
    # Reset zoom/center when route changes
    if "map_zoom" in st.session_state: del st.session_state["map_zoom"]
    if "map_center_lat" in st.session_state: del st.session_state["map_center_lat"]
    if "map_center_lon" in st.session_state: del st.session_state["map_center_lon"]

origin_name = st.session_state.get("origin", origin_sel)
dest_name   = st.session_state.get("dest",   dest_sel)
orig_lat, orig_lon = AIRPORTS[origin_name]
dest_lat, dest_lon = AIRPORTS[dest_name]
icao_orig = origin_name.split("—")[0].strip()
icao_dest = dest_name.split("—")[0].strip()
dist_km   = haversine(orig_lat, orig_lon, dest_lat, dest_lon)
dist_nm   = dist_km * 0.539957

# ═══════════════════════════════════════════════════════════════
#  TOP HEADER BAR
# ═══════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
h1, h2, h3 = st.columns([2,3,2])
with h1:
    st.markdown(f"""
    <div style="padding:8px 0">
      <div style="font-family:'Orbitron',monospace;font-size:11px;color:#1e6b8a;letter-spacing:3px">FLIGHT</div>
      <div style="font-family:'Orbitron',monospace;font-size:26px;font-weight:900;color:#38bdf8;text-shadow:0 0 20px rgba(56,189,248,0.4)">{flight_num}</div>
      <div style="font-size:12px;color:#334d6b;margin-top:2px">{AIRCRAFT_DB[aircraft]["capacity_pax"]} pax · {AIRCRAFT_DB[aircraft]["range_km"]:,} km range</div>
    </div>
    """, unsafe_allow_html=True)
with h2:
    st.markdown(f"""
    <div style="text-align:center;padding:8px 0">
      <div style="font-family:'Orbitron',monospace;font-size:22px;font-weight:700;color:#f1f5f9">
        <span style="color:#38bdf8">{icao_orig}</span>
        <span style="color:#1e3a5f;font-size:16px;margin:0 16px">─────✈─────</span>
        <span style="color:#a78bfa">{icao_dest}</span>
      </div>
      <div style="font-size:12px;color:#334d6b;margin-top:4px">
        {origin_name.split("—")[1].strip()} → {dest_name.split("—")[1].strip()}
      </div>
    </div>
    """, unsafe_allow_html=True)
with h3:
    st.markdown(f"""
    <div style="text-align:right;padding:8px 0">
      <div class="live-clock" style="font-size:22px">{now_utc.strftime('%H:%M:%S')}</div>
      <div class="live-date">{now_utc.strftime('%A, %d %B %Y')}</div>
      <div style="margin-top:6px"><span class="live-badge">● LIVE DATA</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin:4px 0'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  FETCH DATA
# ═══════════════════════════════════════════════════════════════
waypoints = interpolate_route(orig_lat, orig_lon, dest_lat, dest_lon, 9)
with st.spinner("🛰️ Acquiring live weather data..."):
    wp_weather = get_all_route_weather(tuple(waypoints))
    fuel_data  = ai_fuel_analysis(aircraft, dist_km, wp_weather, cruise_alt, pax_load)
    routes     = ai_route_optimizer(origin_name, dest_name, (orig_lat,orig_lon), (dest_lat,dest_lon))
    sigmets    = get_sigmets() if show_sigmets else []

# ═══════════════════════════════════════════════════════════════
#  METRICS BAR
# ═══════════════════════════════════════════════════════════════
ac = AIRCRAFT_DB[aircraft]
eta_h = int(fuel_data["flight_time_h"])
eta_m = int((fuel_data["flight_time_h"] - eta_h) * 60)

cols = st.columns(8)
metrics = [
    ("DISTANCE",  f"{dist_nm:,.0f}",                   "NM"),
    ("ETA",       f"{eta_h}h{eta_m:02d}m",              "FLIGHT TIME"),
    ("CRUISE",    f"{cruise_alt//1000}K",               "FEET ALT"),
    ("SPEED",     f"{cruise_speed}",                    "KNOTS"),
    ("FUEL",      f"{fuel_data['total_fuel_kg']//1000}K","KG TOTAL"),
    ("EFFICIENCY",f"{fuel_data['efficiency_score']}",   "AI SCORE"),
    ("CO₂",       f"{fuel_data['co2_tonnes']}",         "TONNES"),
    ("PAX LOAD",  f"{pax_load}%",                       "CAPACITY"),
]
for col, (label, val, unit) in zip(cols, metrics):
    with col:
        st.markdown(f"""
        <div class="metric-hud">
          <div class="metric-hud-label">{label}</div>
          <div class="metric-hud-value">{val}</div>
          <div class="metric-hud-unit">{unit}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs([
    "🌍  WEATHER MAP & FORECAST",
    "⛽  AI FUEL EFFICIENCY",
    "🛣️  ROUTE OPTIMIZATION"
])

# ╔═══════════════════════════════════════════════════════════════
#  TAB 1 — WEATHER MAP
# ╚═══════════════════════════════════════════════════════════════
with tab1:
    map_col, wx_col = st.columns([4, 1])

    with map_col:
        # Build Plotly map (better than folium for this use case)
        tile_map = {
            "Dark Aviation": "carto-darkmatter",
            "Satellite":     "open-street-map",
            "Terrain":       "carto-positron",
        }
        mapbox_style = tile_map.get(map_style, "carto-darkmatter")

        fig_map = go.Figure()

        # Storm zones
        if show_storms:
            storm_zones = [
                ("Gulf of Mexico",    24,  -90, 3.5, "#ef4444"),
                ("Caribbean",         18,  -70, 3.0, "#ef4444"),
                ("E Pacific Storms",  18, -110, 3.0, "#f97316"),
                ("Great Plains",      38,  -98, 2.5, "#f59e0b"),
            ]
            for name, lat, lon, sz, col in storm_zones:
                # Draw circle approximation using scatter
                angles = np.linspace(0, 2*math.pi, 40)
                r_lat = sz
                r_lon = sz * 1.5
                clat = lat + r_lat * np.sin(angles)
                clon = lon + r_lon * np.cos(angles)
                fig_map.add_trace(go.Scattermapbox(
                    lat=list(clat) + [clat[0]],
                    lon=list(clon) + [clon[0]],
                    mode="lines",
                    line=dict(color=col, width=1),
                    opacity=0.5,
                    hovertemplate=f"⚠️ {name}<extra></extra>",
                    showlegend=False,
                    fill="toself",
                    fillcolor=col.replace("#","rgba(").rstrip(")") if False else "rgba(239,68,68,0.06)",
                ))
                fig_map.add_trace(go.Scattermapbox(
                    lat=[lat], lon=[lon],
                    mode="markers+text",
                    marker=dict(size=20, color="rgba(0,0,0,0)"),
                    text=["🌀 " + name],
                    textposition="top right",
                    hovertemplate=f"⚠️ {name}<extra></extra>",
                    showlegend=False,
                ))

        # Jet stream
        if show_jetstream:
            jet_lats = [32, 35, 38, 40, 42, 43, 42, 40]
            jet_lons = [-120, -115, -110, -105, -100, -95, -90, -85]
            fig_map.add_trace(go.Scattermapbox(
                lat=jet_lats, lon=jet_lons,
                mode="lines",
                line=dict(color="#fbbf24", width=2, dash="dot") if False else dict(color="#fbbf24", width=2),
                opacity=0.45,
                name="Jet Stream",
                hovertemplate="Subtropical Jet Stream<extra></extra>",
            ))

        # Draw alt routes first (behind), then best route on top
        sorted_routes = [r for r in routes if not r.get("is_best")] + [r for r in routes if r.get("is_best")]
        for r in sorted_routes:
            wpts = r["waypoints"]
            rlats = [p[0] for p in wpts]
            rlons = [p[1] for p in wpts]
            is_best = r.get("is_best", False)
            # Best route: thick solid line; alt routes: thinner, semi-transparent
            fig_map.add_trace(go.Scattermapbox(
                lat=rlats, lon=rlons,
                mode="lines+markers" if is_best else "lines",
                line=dict(color=r["color"], width=5 if is_best else 2),
                marker=dict(size=6, color=r["color"]) if is_best else dict(size=0),
                opacity=1.0 if is_best else 0.55,
                name=("★ " if is_best else "") + r["name"],
                hovertemplate=f"{r['name']}<br>{r['dist_km']:,} km · {r['time_h']}h<extra></extra>",
            ))

        # Real-time weather intensity overlay — all route waypoints as heat bubbles
        # Color: green = calm, yellow = moderate, red = severe
        all_wx_lats, all_wx_lons, all_wx_colors, all_wx_sizes, all_wx_hover = [], [], [], [], []
        for w in wp_weather:
            code = w["weather_code"]; ws = w["wind_speed"]
            if code >= 95:
                color = "rgba(185,28,28,0.55)"; sz = 30
            elif code >= 80 or ws > 60:
                color = "rgba(239,68,68,0.40)"; sz = 24
            elif code >= 61 or ws > 40:
                color = "rgba(245,158,11,0.35)"; sz = 20
            elif code >= 45 or ws > 25:
                color = "rgba(56,189,248,0.28)"; sz = 16
            else:
                color = "rgba(34,197,94,0.22)"; sz = 14
            all_wx_lats.append(w["lat"]); all_wx_lons.append(w["lon"])
            all_wx_colors.append(color); all_wx_sizes.append(sz)
            desc, icon, _ = wx_info(code)
            all_wx_hover.append(
                f"Temp: {w['temperature']:.1f}C  {icon} {desc}<br>"
                f"Wind: {ws:.0f} km/h {wind_label(w['wind_dir'])}<br>"
                f"Pressure: {w['pressure']:.0f} hPa  Humidity: {w['humidity']:.0f}%"
            )

        fig_map.add_trace(go.Scattermapbox(
            lat=all_wx_lats, lon=all_wx_lons,
            mode="markers",
            marker=dict(size=all_wx_sizes, color=all_wx_colors),
            hovertext=all_wx_hover,
            hovertemplate="%{hovertext}<extra>Live Weather</extra>",
            name="Live Wx Overlay",
            opacity=1.0,
        ))


        wp_lats   = [w["lat"] for w in wp_weather]
        wp_lons   = [w["lon"] for w in wp_weather]
        wp_texts  = [wx_info(w["weather_code"])[1] for w in wp_weather]
        wp_colors = [wx_info(w["weather_code"])[2] for w in wp_weather]
        wp_hover  = [
            f"WP{i}: {wx_info(w['weather_code'])[0]}<br>Wind: {w['wind_speed']:.0f} km/h {wind_label(w['wind_dir'])}<br>Temp: {w['temperature']:.1f}C<br>Pressure: {w['pressure']:.0f} hPa"
            for i, w in enumerate(wp_weather)
        ]

        # Outer ring (dark border effect)
        fig_map.add_trace(go.Scattermapbox(
            lat=wp_lats, lon=wp_lons,
            mode="markers",
            marker=dict(size=30, color="rgba(5,15,30,0.85)", opacity=1.0),
            hoverinfo="skip",
            showlegend=False,
        ))
        # Coloured dot
        fig_map.add_trace(go.Scattermapbox(
            lat=wp_lats, lon=wp_lons,
            mode="markers",
            marker=dict(size=22, color=wp_colors, opacity=1.0),
            hoverinfo="skip",
            showlegend=False,
        ))
        # Weather icon text on top
        fig_map.add_trace(go.Scattermapbox(
            lat=wp_lats, lon=wp_lons,
            mode="markers+text",
            marker=dict(size=0, color="rgba(0,0,0,0)"),
            text=wp_texts,
            hovertext=wp_hover,
            hovertemplate="%{hovertext}<extra></extra>",
            name="Waypoints",
            showlegend=True,
        ))

        # SIGMETs
        if show_sigmets and sigmets:
            sig_lats, sig_lons, sig_txt = [], [], []
            for s in sigmets[:25]:
                try:
                    sig_lats.append(float(s.get("lat",0)))
                    sig_lons.append(float(s.get("lon",0)))
                    sig_txt.append(f"SIGMET: {s.get('hazard','?')}<br>{s.get('firname','')}")
                except: pass
            if sig_lats:
                fig_map.add_trace(go.Scattermapbox(
                    lat=sig_lats, lon=sig_lons,
                    mode="markers+text",
                    marker=dict(size=16, color="#f59e0b", symbol="star"),
                    text=["⚡"]*len(sig_lats),
                    hovertext=sig_txt,
                    hovertemplate="%{hovertext}<extra></extra>",
                    name="SIGMETs",
                ))

        # Origin & Destination
        # Origin: large aircraft marker with label box
        fig_map.add_trace(go.Scattermapbox(
            lat=[orig_lat], lon=[orig_lon],
            mode="markers+text",
            marker=dict(size=22, color="#38bdf8"),
            text=[f"✈ {icao_orig}"],
            textposition="top right",
            hovertemplate=f"<b>ORIGIN: {icao_orig}</b><br>{origin_name.split(chr(8212))[1].strip()}<extra></extra>",
            name="Origin",
        ))
        # Destination
        fig_map.add_trace(go.Scattermapbox(
            lat=[dest_lat], lon=[dest_lon],
            mode="markers+text",
            marker=dict(size=22, color="#a78bfa"),
            text=[f"■ {icao_dest}"],
            textposition="top right",
            hovertemplate=f"<b>DEST: {icao_dest}</b><br>{dest_name.split(chr(8212))[1].strip()}<extra></extra>",
            name="Destination",
        ))

        center_lat = (orig_lat + dest_lat) / 2
        center_lon = (orig_lon + dest_lon) / 2

        # Auto-zoom: fit the full route in view with padding
        all_route_lats = [p[0] for r in routes for p in r["waypoints"]]
        all_route_lons = [p[1] for r in routes for p in r["waypoints"]]
        all_route_lats += [orig_lat, dest_lat]
        all_route_lons += [orig_lon, dest_lon]
        lat_span = max(all_route_lats) - min(all_route_lats)
        lon_span = max(all_route_lons) - min(all_route_lons)
        max_span = max(lat_span, lon_span, 0.1)
        # Mapbox zoom: each +1 zoom halves the visible area
        # zoom 4 ≈ 40° view, zoom 6 ≈ 10°, zoom 8 ≈ 2.5°
        import math as _math
        auto_zoom = min(9.5, max(4.0, _math.log2(160.0 / max_span) + 1.0))
        center_lat = (max(all_route_lats) + min(all_route_lats)) / 2
        center_lon = (max(all_route_lons) + min(all_route_lons)) / 2

        # Zoom level stored in session state
        if "map_zoom" not in st.session_state:
            st.session_state.map_zoom = auto_zoom
        if "map_center_lat" not in st.session_state:
            st.session_state.map_center_lat = center_lat
        if "map_center_lon" not in st.session_state:
            st.session_state.map_center_lon = center_lon

        # Zoom controls row
        zc1, zc2, zc3, zc4, zc5 = st.columns([1,1,1,1,6])
        with zc1:
            if st.button("＋", key="zoom_in", help="Zoom In"):
                st.session_state.map_zoom = min(st.session_state.map_zoom + 1, 18)
        with zc2:
            if st.button("－", key="zoom_out", help="Zoom Out"):
                st.session_state.map_zoom = max(st.session_state.map_zoom - 1, 1)
        with zc3:
            if st.button("⌖", key="zoom_fit", help="Fit Route"):
                st.session_state.map_zoom = auto_zoom
                st.session_state.map_center_lat = center_lat
                st.session_state.map_center_lon = center_lon
        with zc4:
            if st.button("⊕", key="zoom_orig", help="Go to Origin"):
                st.session_state.map_zoom = 10
                st.session_state.map_center_lat = orig_lat
                st.session_state.map_center_lon = orig_lon
        with zc5:
            st.markdown(
                f"<div style='font-family:Orbitron,monospace;font-size:10px;color:#1e6b8a;"
                f"letter-spacing:2px;padding-top:6px'>ZOOM {st.session_state.map_zoom:.1f}"
                f" &nbsp;·&nbsp; SCROLL TO ZOOM &nbsp;·&nbsp; DRAG TO PAN</div>",
                unsafe_allow_html=True
            )

        fig_map.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=st.session_state.map_center_lat,
                            lon=st.session_state.map_center_lon),
                zoom=st.session_state.map_zoom,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0),
            height=600,
            showlegend=True,
            legend=dict(
                bgcolor="rgba(5,15,30,0.92)",
                bordercolor="rgba(56,189,248,0.2)",
                borderwidth=1,
                font=dict(color="#94a3b8", size=10),
                x=0.01, y=0.01,
                xanchor="left", yanchor="bottom",
                itemsizing="constant",
                tracegroupgap=2,
            ),
            uirevision="map_view",
        )
        st.plotly_chart(fig_map, use_container_width=True, config={
            "displayModeBar": True,
            "scrollZoom": True,
            "modeBarButtonsToRemove": ["toImage"],
            "modeBarButtonsToAdd": ["zoomInMapbox", "zoomOutMapbox", "resetViewMapbox"],
        })

        # Animated wind/weather timeline
        st.markdown('<div class="sec-head">ROUTE WEATHER TIMELINE</div>', unsafe_allow_html=True)
        wp_labels = ["ORIG"] + [f"WP{i}" for i in range(1,len(wp_weather)-1)] + ["DEST"]

        fig_timeline = make_subplots(
            rows=1, cols=3,
            subplot_titles=("Wind Speed (km/h)", "Pressure (hPa)", "Temperature (°C)"),
            horizontal_spacing=0.06,
        )
        y_wind = [w["wind_speed"] for w in wp_weather]
        y_pres = [w["pressure"] for w in wp_weather]
        y_temp = [w["temperature"] for w in wp_weather]
        wind_cols = ["#ef4444" if v>60 else "#f59e0b" if v>35 else "#38bdf8" for v in y_wind]

        fig_timeline.add_trace(go.Scatter(x=wp_labels, y=y_wind, mode="lines+markers",
            line=dict(color="#38bdf8",width=2), marker=dict(color=wind_cols,size=9),
            fill="tozeroy", fillcolor="rgba(56,189,248,0.07)", name="Wind"), row=1, col=1)
        fig_timeline.add_shape(type="line", x0=0, x1=len(wp_labels)-1, y0=60, y1=60,
            line=dict(color="#ef4444",width=1,dash="dash"), row=1, col=1)
        fig_timeline.add_trace(go.Scatter(x=wp_labels, y=y_pres, mode="lines+markers",
            line=dict(color="#a78bfa",width=2), marker=dict(color="#a78bfa",size=9),
            fill="tozeroy", fillcolor="rgba(167,139,250,0.07)", name="Pressure"), row=1, col=2)
        fig_timeline.add_trace(go.Scatter(x=wp_labels, y=y_temp, mode="lines+markers",
            line=dict(color="#34d399",width=2), marker=dict(color="#34d399",size=9),
            fill="tozeroy", fillcolor="rgba(52,211,153,0.07)", name="Temp"), row=1, col=3)

        fig_timeline.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,15,30,0.6)",
            font=dict(color="#64748b", size=11),
            margin=dict(l=0,r=0,t=30,b=0), height=200, showlegend=False,
        )
        for i in range(1,4):
            fig_timeline.update_xaxes(showgrid=False, color="#1e3a5f", row=1, col=i)
            fig_timeline.update_yaxes(showgrid=True, gridcolor="rgba(30,58,95,0.5)", color="#1e3a5f", row=1, col=i)
        fig_timeline.update_annotations(font=dict(color="#64748b", size=11))
        st.plotly_chart(fig_timeline, use_container_width=True, config={"displayModeBar": False})

    # ── Weather side panel (reference-style) ───────────────────────────────────
    with wx_col:
        st.markdown('<div class="sec-head">WEATHER ALERTS</div>', unsafe_allow_html=True)

        # Route alerts first (most important)
        alerts = []
        for i, w in enumerate(wp_weather):
            code = w.get("weather_code", 0)
            ws   = w.get("wind_speed", 0)
            lbl  = "ORIG" if i==0 else "DEST" if i==len(wp_weather)-1 else f"WP{i}"
            if code >= 95:   alerts.append(("danger",  lbl, "Thunderstorm", f"{ws:.0f} km/h"))
            elif code >= 80: alerts.append(("warning", lbl, "Heavy showers", f"{ws:.0f} km/h"))
            elif ws > 70:    alerts.append(("danger",  lbl, "Extreme winds", f"{ws:.0f} km/h"))
            elif ws > 45:    alerts.append(("warning", lbl, "Strong winds",  f"{ws:.0f} km/h"))
            elif ws > 25:    alerts.append(("info",    lbl, "Moderate wind", f"{ws:.0f} km/h"))
            else:            alerts.append(("ok",      lbl, "Clear",         f"{ws:.0f} km/h"))

        if all(a[0]=="ok" for a in alerts):
            st.markdown("""
            <div style="background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.4);
                border-radius:8px;padding:12px;text-align:center;margin-bottom:8px">
              <div style="font-size:18px">✅</div>
              <div style="color:#86efac;font-weight:600;font-size:12px;margin-top:4px">Route looks clear</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="sec-head">WAYPOINTS</div>', unsafe_allow_html=True)
        for lvl, lbl, desc, wind in alerts[:10]:
            colors = {"danger":"#ef4444","warning":"#f59e0b","info":"#38bdf8","ok":"#22c55e"}
            badges = {"danger":"HIGH","warning":"MOD","info":"LOW","ok":"LOW"}
            col = colors[lvl]
            badge = badges[lvl]
            badge_bg = {"danger":"rgba(239,68,68,0.15)","warning":"rgba(245,158,11,0.15)",
                        "info":"rgba(56,189,248,0.15)","ok":"rgba(34,197,94,0.15)"}[lvl]
            wx_icon = {"danger":"⛈","warning":"🌧","info":"💨","ok":"☀️"}[lvl]
            st.markdown(f"""
            <div style="background:rgba(10,22,40,0.8);border:1px solid rgba(56,189,248,0.1);
                border-left:3px solid {col};border-radius:8px;padding:10px 12px;margin:5px 0;
                display:flex;justify-content:space-between;align-items:center">
              <div>
                <div style="font-family:'Orbitron',monospace;font-size:9px;color:#64748b;
                    letter-spacing:2px;margin-bottom:3px">{lbl}</div>
                <div style="font-size:12px;color:#94a3b8">{wx_icon} {wind}</div>
              </div>
              <div style="background:{badge_bg};border:1px solid {col};color:{col};
                  font-size:9px;font-weight:700;padding:3px 7px;border-radius:4px;
                  font-family:'Orbitron',monospace;letter-spacing:1px">{badge}</div>
            </div>
            """, unsafe_allow_html=True)

        # Origin weather card
        st.markdown('<div class="sec-head">ORIGIN · LIVE</div>', unsafe_allow_html=True)
        w0 = get_weather(orig_lat, orig_lon)
        cur0 = w0.get("current",{}) if w0 else {}
        desc0, icon0, _ = wx_info(cur0.get("weather_code",0))
        temp0  = cur0.get("temperature_2m", "--")
        wind0  = cur0.get("wind_speed_10m", "--")
        hum0   = cur0.get("relative_humidity_2m", "--")
        pres0  = cur0.get("pressure_msl","--")
        st.markdown(f"""
        <div style="background:rgba(10,22,40,0.9);border:1px solid rgba(56,189,248,0.15);
            border-top:3px solid #38bdf8;border-radius:10px;padding:14px;margin-bottom:8px">
          <div style="font-family:'Orbitron',monospace;font-size:9px;color:#38bdf8;
              letter-spacing:3px;margin-bottom:8px">{icao_orig}</div>
          <div style="font-size:26px;margin-bottom:8px">{icon0}
            <span style="font-size:12px;color:#94a3b8;margin-left:4px">{desc0}</span></div>
          <div style="font-size:22px;font-weight:700;color:#e2e8f0;font-family:'Orbitron',monospace;
              margin-bottom:10px">{temp0:.1f if isinstance(temp0,float) else temp0}°C</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11px">
            <div style="color:#475569">Wind<br><span style="color:#94a3b8;font-weight:600">{wind0:.0f if isinstance(wind0,float) else wind0} km/h</span></div>
            <div style="color:#475569">Humidity<br><span style="color:#94a3b8;font-weight:600">{hum0:.0f if isinstance(hum0,float) else hum0}%</span></div>
            <div style="color:#475569">Pressure<br><span style="color:#94a3b8;font-weight:600">{pres0:.0f if isinstance(pres0,float) else pres0} hPa</span></div>
            <div style="color:#475569">Dir<br><span style="color:#94a3b8;font-weight:600">{wind_label(cur0.get("wind_direction_10m",0))}</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Destination weather card
        st.markdown('<div class="sec-head">DESTINATION · LIVE</div>', unsafe_allow_html=True)
        wd = get_weather(dest_lat, dest_lon)
        curd = wd.get("current",{}) if wd else {}
        descd, icond, _ = wx_info(curd.get("weather_code",0))
        tempd  = curd.get("temperature_2m", "--")
        windd  = curd.get("wind_speed_10m", "--")
        humd   = curd.get("relative_humidity_2m", "--")
        presd  = curd.get("pressure_msl","--")
        st.markdown(f"""
        <div style="background:rgba(10,22,40,0.9);border:1px solid rgba(167,139,250,0.15);
            border-top:3px solid #a78bfa;border-radius:10px;padding:14px;margin-bottom:8px">
          <div style="font-family:'Orbitron',monospace;font-size:9px;color:#a78bfa;
              letter-spacing:3px;margin-bottom:8px">{icao_dest}</div>
          <div style="font-size:26px;margin-bottom:8px">{icond}
            <span style="font-size:12px;color:#94a3b8;margin-left:4px">{descd}</span></div>
          <div style="font-size:22px;font-weight:700;color:#e2e8f0;font-family:'Orbitron',monospace;
              margin-bottom:10px">{tempd:.1f if isinstance(tempd,float) else tempd}°C</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:11px">
            <div style="color:#475569">Wind<br><span style="color:#94a3b8;font-weight:600">{windd:.0f if isinstance(windd,float) else windd} km/h</span></div>
            <div style="color:#475569">Humidity<br><span style="color:#94a3b8;font-weight:600">{humd:.0f if isinstance(humd,float) else humd}%</span></div>
            <div style="color:#475569">Pressure<br><span style="color:#94a3b8;font-weight:600">{presd:.0f if isinstance(presd,float) else presd} hPa</span></div>
            <div style="color:#475569">Dir<br><span style="color:#94a3b8;font-weight:600">{wind_label(curd.get("wind_direction_10m",0))}</span></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Colour legend
        st.markdown('<div class="sec-head">MAP LEGEND</div>', unsafe_allow_html=True)
        for color, label in [
            ("#38bdf8","Best / Direct route"),
            ("#a78bfa","Alt route B"),
            ("#34d399","Alt route C"),
            ("#fbbf24","Alt route D / Jet stream"),
            ("#ef4444","Storm zone"),
            ("#f59e0b","SIGMET"),
        ]:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;font-size:11px;
                color:#475569;margin:4px 0">
              <div style="width:10px;height:10px;border-radius:2px;
                  background:{color};flex-shrink:0"></div>{label}
            </div>
            """, unsafe_allow_html=True)

# ╔═══════════════════════════════════════════════════════════════
#  TAB 2 — AI FUEL EFFICIENCY
# ╚═══════════════════════════════════════════════════════════════
with tab2:
    fd = fuel_data
    f1, f2, f3 = st.columns([1,1,1])

    # Score gauge
    with f1:
        st.markdown('<div class="sec-head">AI EFFICIENCY SCORE</div>', unsafe_allow_html=True)
        score = fd["efficiency_score"]
        score_color = "#22c55e" if score>=80 else "#f59e0b" if score>=60 else "#ef4444"
        score_label = "EXCELLENT" if score>=80 else "GOOD" if score>=65 else "MODERATE" if score>=50 else "POOR"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            number=dict(font=dict(color="#38bdf8", size=48, family="Orbitron"), suffix=""),
            gauge=dict(
                axis=dict(range=[0,100], tickcolor="#1e3a5f", tickfont=dict(color="#1e3a5f")),
                bar=dict(color=score_color, thickness=0.25),
                bgcolor="rgba(5,15,30,0.9)",
                bordercolor="rgba(56,189,248,0.1)",
                steps=[
                    dict(range=[0,50],   color="rgba(239,68,68,0.08)"),
                    dict(range=[50,75],  color="rgba(245,158,11,0.08)"),
                    dict(range=[75,100], color="rgba(34,197,94,0.08)"),
                ],
                threshold=dict(line=dict(color=score_color, width=3), thickness=0.75, value=score),
            ),
            delta=dict(reference=75, increasing=dict(color="#22c55e"), decreasing=dict(color="#ef4444")),
            title=dict(text=f"<b>{score_label}</b>", font=dict(color=score_color, size=13, family="Orbitron")),
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#64748b"),
            margin=dict(l=20,r=20,t=20,b=20),
            height=280,
        )
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar":False})

        # Burn rate
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;margin-top:8px">
          <div style="font-family:'Orbitron',monospace;font-size:9px;color:#1e6b8a;letter-spacing:2px">CURRENT BURN RATE</div>
          <div style="font-family:'Orbitron',monospace;font-size:30px;font-weight:700;color:#f59e0b;text-shadow:0 0 20px rgba(245,158,11,0.4);margin:8px 0">{fd['burn_rate_kgh']:,}</div>
          <div style="font-size:11px;color:#334d6b">kg / hour</div>
        </div>
        """, unsafe_allow_html=True)

    # Fuel breakdown
    with f2:
        st.markdown('<div class="sec-head">FUEL ANALYSIS</div>', unsafe_allow_html=True)

        # Waterfall chart
        categories = ["Base Fuel", "Wind Effect", "Alt Saving", "Wx Penalty", "Load Factor", "Total"]
        base = round(AIRCRAFT_DB[aircraft]["burn_kgh"] * fuel_data["flight_time_h"])
        wind_adj = round(base * fd["wind_impact"]/100)
        alt_save = -round(base * fd["alt_saving"]/100)
        wx_pen   = round(base * fd["weather_penalty_pct"]/100)
        load_adj = round(base * (fd["load_factor_pct"]-85)/100 * 0.18)
        total    = fd["total_fuel_kg"]

        fig_waterfall = go.Figure(go.Waterfall(
            orientation="v",
            measure=["absolute","relative","relative","relative","relative","total"],
            x=categories,
            y=[base, wind_adj, alt_save, wx_pen, load_adj, 0],
            text=[f"{v:+,}" if i>0 and i<5 else f"{v:,}" for i,v in enumerate([base,wind_adj,alt_save,wx_pen,load_adj,total])],
            textposition="outside",
            textfont=dict(color="#94a3b8", size=11),
            connector=dict(line=dict(color="rgba(56,189,248,0.2)", dash="dot")),
            increasing=dict(marker=dict(color="#ef4444")),
            decreasing=dict(marker=dict(color="#22c55e")),
            totals=dict(marker=dict(color="#38bdf8")),
        ))
        fig_waterfall.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,15,30,0.6)",
            font=dict(color="#64748b", size=11),
            margin=dict(l=0,r=0,t=10,b=0), height=280, showlegend=False,
            xaxis=dict(showgrid=False, color="#1e3a5f"),
            yaxis=dict(showgrid=True, gridcolor="rgba(30,58,95,0.5)", color="#1e3a5f", title="kg"),
        )
        st.plotly_chart(fig_waterfall, use_container_width=True, config={"displayModeBar":False})

        # Factor bars
        factors = [
            ("Wind Impact",      abs(fd["wind_impact"]),         "#38bdf8", fd["wind_impact"]>0),
            ("Alt Efficiency",   fd["alt_saving"],               "#22c55e", False),
            ("Weather Penalty",  fd["weather_penalty_pct"],      "#ef4444", True),
            ("Load Impact",      abs(fd["load_factor_pct"]-85),  "#f59e0b", fd["load_factor_pct"]>85),
        ]
        for name, val, color, is_bad in factors:
            icon = "▲" if is_bad else "▼"
            st.markdown(f"""
            <div style="margin:6px 0">
              <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
                <span style="color:#64748b">{name}</span>
                <span style="color:{color};font-weight:600">{icon} {val:.1f}%</span>
              </div>
              <div class="fuel-bar-bg">
                <div class="fuel-bar-fill" style="width:{min(val*5,100)}%;background:{color}"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # AI Recommendations
    with f3:
        st.markdown('<div class="sec-head">AI RECOMMENDATIONS</div>', unsafe_allow_html=True)

        recs = []
        if fd["wind_impact"] > 3:
            recs.append(("warning", "🌬️ Headwind detected", f"+{fd['wind_impact']:.1f}% fuel burn. Consider altitude step to find better winds."))
        if fd["weather_penalty_pct"] > 2:
            recs.append(("danger", "⛈️ Weather deviation", f"+{fd['weather_penalty_pct']:.1f}% penalty. Route C avoids storm cells."))
        if fd["load_factor_pct"] > 90:
            recs.append(("warning", "⚖️ High load factor", "Full aircraft increases fuel burn. Optimize CG for efficiency."))
        if cruise_alt < 33000:
            recs.append(("warning", "📉 Suboptimal altitude", "Step climb to FL350+ recommended for 5-8% fuel savings."))
        if fd["efficiency_score"] > 80:
            recs.append(("ok", "✅ Optimal conditions", "AI analysis confirms this is a fuel-efficient routing."))

        recs.append(("info", "🔁 Step climb profile", f"Recommend FL{cruise_alt//1000:02d}0 → FL{(cruise_alt+2000)//1000:02d}0 at midpoint."))
        recs.append(("info", "⚡ Power setting", "LRC (Long Range Cruise) mode recommended for current load."))

        for lvl, title, detail in recs[:6]:
            st.markdown(f"""
            <div class="alert-{lvl}" style="margin:6px 0">
              <div style="font-weight:700;margin-bottom:3px">{title}</div>
              <div style="font-size:11px;opacity:0.8">{detail}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="sec-head">ENVIRONMENTAL IMPACT</div>', unsafe_allow_html=True)
        co2 = fd["co2_tonnes"]
        trees = round(co2 * 45)
        st.markdown(f"""
        <div class="glass-card">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;text-align:center">
            <div>
              <div style="font-family:'Orbitron',monospace;font-size:20px;font-weight:700;color:#ef4444">{co2}</div>
              <div style="font-size:11px;color:#475569;margin-top:3px">tonnes CO₂</div>
            </div>
            <div>
              <div style="font-family:'Orbitron',monospace;font-size:20px;font-weight:700;color:#22c55e">{trees:,}</div>
              <div style="font-size:11px;color:#475569;margin-top:3px">trees to offset</div>
            </div>
            <div>
              <div style="font-family:'Orbitron',monospace;font-size:20px;font-weight:700;color:#38bdf8">{fd['fuel_per_pax_kg']:.1f}</div>
              <div style="font-size:11px;color:#475569;margin-top:3px">kg fuel / pax</div>
            </div>
            <div>
              <div style="font-family:'Orbitron',monospace;font-size:20px;font-weight:700;color:#fbbf24">{fd['total_fuel_kg']:,}</div>
              <div style="font-size:11px;color:#475569;margin-top:3px">total kg fuel</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Efficiency over route
        st.markdown('<div class="sec-head">EFFICIENCY ALONG ROUTE</div>', unsafe_allow_html=True)
        wp_labels = ["ORIG"] + [f"WP{i}" for i in range(1,len(wp_weather)-1)] + ["DEST"]
        eff_scores = []
        for w in wp_weather:
            ws = w["wind_speed"]; code = w["weather_code"]
            e = 100
            if ws > 60: e -= 15
            elif ws > 40: e -= 8
            elif ws > 25: e -= 3
            if code >= 95: e -= 20
            elif code >= 80: e -= 10
            elif code >= 61: e -= 5
            eff_scores.append(max(40, e))

        fig_eff = go.Figure(go.Scatter(
            x=wp_labels, y=eff_scores,
            mode="lines+markers",
            line=dict(color="#22c55e", width=2),
            marker=dict(color=["#22c55e" if v>=80 else "#f59e0b" if v>=60 else "#ef4444" for v in eff_scores], size=10),
            fill="tozeroy", fillcolor="rgba(34,197,94,0.07)",
        ))
        fig_eff.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,15,30,0.6)",
            margin=dict(l=0,r=0,t=0,b=0), height=160, showlegend=False,
            xaxis=dict(showgrid=False, color="#1e3a5f", tickfont=dict(size=9)),
            yaxis=dict(range=[0,110], showgrid=True, gridcolor="rgba(30,58,95,0.5)", color="#1e3a5f"),
            font=dict(color="#64748b", size=11),
        )
        st.plotly_chart(fig_eff, use_container_width=True, config={"displayModeBar":False})

# ╔═══════════════════════════════════════════════════════════════
#  TAB 3 — ROUTE OPTIMIZATION
# ╚═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div style="background:rgba(10,22,40,0.8);border:1px solid rgba(56,189,248,0.1);border-radius:12px;padding:16px 20px;margin-bottom:16px">
      <div style="font-family:'Orbitron',monospace;font-size:10px;color:#1e6b8a;letter-spacing:3px;margin-bottom:8px">AI ROUTE ANALYSIS · {now_utc.strftime('%d %b %Y %H:%M')} UTC</div>
      <div style="font-size:13px;color:#64748b">
        Analysing <span style="color:#38bdf8">{len(routes)}</span> possible routes from
        <span style="color:#38bdf8">{icao_orig}</span> to <span style="color:#a78bfa">{icao_dest}</span> ·
        AI weighted scoring: <span style="color:#fbbf24">Weather 40% · Fuel 35% · Time 25%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    rc1, rc2 = st.columns([3,2])

    with rc1:
        # Route comparison map
        fig_rmap = go.Figure()

        colors_r = {"A":"#38bdf8","B":"#a78bfa","C":"#34d399","D":"#fbbf24"}
        for r in routes:
            wpts = r["waypoints"]
            rlats = [p[0] for p in wpts]
            rlons = [p[1] for p in wpts]
            is_best = r.get("is_best", False)
            fig_rmap.add_trace(go.Scattermapbox(
                lat=rlats, lon=rlons, mode="lines",
                line=dict(color=r["color"], width=5 if is_best else 2),
                opacity=1.0 if is_best else 0.5,
                name=f"{'★ ' if is_best else ''}{r['name']} ({r['ai_score']}pts)",
                hovertemplate=f"{r['name']}<br>Score: {r['ai_score']}<br>{r['dist_km']:,} km · {r['time_h']}h<extra></extra>",
            ))
            # Label at midpoint
            mid = wpts[len(wpts)//2]
            fig_rmap.add_trace(go.Scattermapbox(
                lat=[mid[0]], lon=[mid[1]],
                mode="text",
                text=[f"{'★' if is_best else r['id']}"],
                textfont=dict(size=16 if is_best else 13, color=r["color"]),
                showlegend=False,
                hovertemplate=f"{r['name']}<extra></extra>",
            ))

        fig_rmap.add_trace(go.Scattermapbox(
            lat=[orig_lat], lon=[orig_lon],
            mode="markers+text",
            marker=dict(size=14, color="#38bdf8"),
            text=[icao_orig],
            textposition="top right",
            showlegend=False,
            hovertemplate=f"{icao_orig}<extra></extra>",
        ))
        fig_rmap.add_trace(go.Scattermapbox(
            lat=[dest_lat], lon=[dest_lon],
            mode="markers+text",
            marker=dict(size=14, color="#a78bfa"),
            text=[icao_dest],
            textposition="top right",
            showlegend=False,
            hovertemplate=f"{icao_dest}<extra></extra>",
        ))

        fig_rmap.update_layout(
            mapbox=dict(style="carto-darkmatter", center=dict(lat=center_lat, lon=center_lon), zoom=auto_zoom),
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=0,b=0), height=480,
            legend=dict(bgcolor="rgba(5,15,30,0.9)", bordercolor="rgba(56,189,248,0.2)",
                        borderwidth=1, font=dict(color="#64748b",size=11), x=0.01, y=0.99),
        )
        st.plotly_chart(fig_rmap, use_container_width=True, config={"displayModeBar": True, "scrollZoom": True, "modeBarButtonsToRemove": ["toImage","resetViewMapbox"]})

        # Radar comparison chart
        st.markdown('<div class="sec-head">ROUTE SCORE COMPARISON</div>', unsafe_allow_html=True)
        categories_r = ["Weather", "Fuel", "Time", "Safety", "AI Score"]
        fig_radar = go.Figure()
        for r in routes:
            safety = max(0, 100 - r["storm_count"]*15 - r["avg_wind"]*0.5)
            # Convert hex color to rgba for fillcolor (8-digit hex not supported)
            hex_col = r["color"].lstrip("#")
            rr, gg, bb = int(hex_col[0:2],16), int(hex_col[2:4],16), int(hex_col[4:6],16)
            fill_rgba = f"rgba({rr},{gg},{bb},0.13)"
            fig_radar.add_trace(go.Scatterpolar(
                r=[r["wx_score"], r["fuel_score"], r["time_score"], safety, r["ai_score"]],
                theta=categories_r,
                fill="toself",
                fillcolor=fill_rgba,
                line=dict(color=r["color"], width=2 if r.get("is_best") else 1),
                opacity=0.9 if r.get("is_best") else 0.5,
                name=r["name"],
            ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="rgba(5,15,30,0.8)",
                radialaxis=dict(visible=True, range=[0,100], color="#1e3a5f", gridcolor="rgba(30,58,95,0.5)"),
                angularaxis=dict(color="#64748b", gridcolor="rgba(30,58,95,0.3)"),
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#64748b", size=11),
            margin=dict(l=40,r=40,t=20,b=20), height=300,
            legend=dict(bgcolor="rgba(5,15,30,0.8)", bordercolor="rgba(56,189,248,0.1)", font=dict(color="#64748b",size=11)),
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar":False})

    with rc2:
        st.markdown('<div class="sec-head">ROUTE DETAILS</div>', unsafe_allow_html=True)

        for r in routes:
            is_best = r.get("is_best", False)
            card_class = "route-card best" if is_best else "route-card"
            border_top = "border-top:3px solid " + r["color"]
            eta_h2 = int(r["time_h"]); eta_m2 = int((r["time_h"]-eta_h2)*60)

            wx_color = "#22c55e" if r["wx_score"]>=80 else "#f59e0b" if r["wx_score"]>=60 else "#ef4444"
            fuel_color = "#22c55e" if r["fuel_score"]>=80 else "#f59e0b" if r["fuel_score"]>=60 else "#ef4444"
            time_color = "#22c55e" if r["time_score"]>=80 else "#f59e0b" if r["time_score"]>=60 else "#ef4444"
            ai_color   = "#22c55e" if r["ai_score"]>=80 else "#f59e0b" if r["ai_score"]>=70 else "#ef4444"

            st.markdown(f"""
            <div class="{card_class}" style="{border_top}">
              <div class="route-name" style="color:{r['color']}">{r['id']}. {r['name']}</div>
              <div style="font-size:11px;color:#475569;margin-bottom:10px">{r['desc']}</div>
              <div class="route-stats">
                <div class="route-stat">
                  <div class="route-stat-label">Distance</div>
                  <div class="route-stat-val" style="color:#94a3b8">{r['dist_km']:,}<span style="font-size:9px"> km</span></div>
                </div>
                <div class="route-stat">
                  <div class="route-stat-label">ETA</div>
                  <div class="route-stat-val" style="color:#94a3b8">{eta_h2}h{eta_m2:02d}m</div>
                </div>
                <div class="route-stat">
                  <div class="route-stat-label">Fuel</div>
                  <div class="route-stat-val" style="color:#f59e0b">{r['fuel_kg']//1000}K<span style="font-size:9px"> kg</span></div>
                </div>
                <div class="route-stat">
                  <div class="route-stat-label">AI Score</div>
                  <div class="route-stat-val" style="color:{ai_color}">{r['ai_score']}</div>
                </div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:10px">
                <div style="text-align:center">
                  <div style="font-size:9px;color:#334d6b;letter-spacing:1px">WEATHER</div>
                  <div style="font-family:'Orbitron',monospace;font-size:16px;font-weight:700;color:{wx_color}">{r['wx_score']}</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:9px;color:#334d6b;letter-spacing:1px">FUEL</div>
                  <div style="font-family:'Orbitron',monospace;font-size:16px;font-weight:700;color:{fuel_color}">{r['fuel_score']}</div>
                </div>
                <div style="text-align:center">
                  <div style="font-size:9px;color:#334d6b;letter-spacing:1px">TIME</div>
                  <div style="font-family:'Orbitron',monospace;font-size:16px;font-weight:700;color:{time_color}">{r['time_score']}</div>
                </div>
              </div>
              {"<div style='margin-top:10px;padding:6px 10px;background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:6px;font-family:Orbitron,monospace;font-size:9px;color:#22c55e;letter-spacing:2px;text-align:center'>★ AI RECOMMENDED ROUTE</div>" if is_best else ""}
            </div>
            """, unsafe_allow_html=True)

        # Summary table
        st.markdown('<div class="sec-head">QUICK COMPARISON</div>', unsafe_allow_html=True)
        df_routes = pd.DataFrame([{
            "Route":    r["name"],
            "Dist(km)": r["dist_km"],
            "Time":     f"{int(r['time_h'])}h{int((r['time_h']%1)*60):02d}m",
            "Fuel(kg)": r["fuel_kg"],
            "Wx":       r["wx_score"],
            "AI ★":    r["ai_score"],
        } for r in routes])

        st.dataframe(
            df_routes.style.background_gradient(subset=["AI ★"], cmap="Blues"),
            use_container_width=True, hide_index=True,
        )

# Footer
st.markdown(f"""
<div style="text-align:center;padding:16px 0 8px;font-family:'Orbitron',monospace;font-size:9px;color:#0f2744;letter-spacing:3px;border-top:1px solid rgba(56,189,248,0.06);margin-top:16px">
  AERONAV PRO · FLIGHT INTELLIGENCE SYSTEM · {now_utc.strftime('%d %b %Y %H:%M:%S')} UTC · DATA: OPEN-METEO / NOAA AWC
</div>
""", unsafe_allow_html=True)
