import streamlit as st
import requests
import math
import time
import random
from datetime import datetime, timezone
import plotly.graph_objects as go
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
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #020b18 0%, #050d1a 100%) !important;
  border-right: 1px solid rgba(56,189,248,0.15) !important;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }

.hud-title { font-family:'Orbitron',monospace; font-size:13px; font-weight:700; letter-spacing:4px; color:#38bdf8; text-transform:uppercase; }
.hud-sub   { font-family:'Orbitron',monospace; font-size:10px; color:#1e4d6b; letter-spacing:3px; }

.glass-card { background:rgba(10,22,40,0.85); border:1px solid rgba(56,189,248,0.12); border-radius:14px; padding:16px 20px; box-shadow:0 4px 32px rgba(0,0,0,0.5); }

.metric-hud { background:linear-gradient(135deg,rgba(10,22,40,0.95),rgba(5,15,30,0.95)); border:1px solid rgba(56,189,248,0.2); border-radius:10px; padding:14px 16px; text-align:center; position:relative; overflow:hidden; }
.metric-hud::before { content:''; position:absolute; top:0;left:0;right:0; height:2px; background:linear-gradient(90deg,transparent,#38bdf8,transparent); }
.metric-hud-label { font-family:'Orbitron',monospace; font-size:9px; letter-spacing:2px; color:#334d6b; text-transform:uppercase; margin-bottom:6px; }
.metric-hud-value { font-family:'Orbitron',monospace; font-size:22px; font-weight:700; color:#38bdf8; text-shadow:0 0 20px rgba(56,189,248,0.5); line-height:1.1; }
.metric-hud-unit  { font-size:10px; color:#1e4d6b; margin-top:3px; font-weight:500; }

.live-clock { font-family:'Orbitron',monospace; font-size:28px; font-weight:900; color:#38bdf8; text-shadow:0 0 30px rgba(56,189,248,0.6); letter-spacing:4px; text-align:center; }
.live-date  { font-family:'Orbitron',monospace; font-size:11px; color:#1e6b8a; letter-spacing:3px; text-align:center; margin-top:4px; }
.live-badge { display:inline-block; background:rgba(34,197,94,0.1); border:1px solid #22c55e; color:#22c55e; font-size:9px; font-weight:700; letter-spacing:2px; padding:3px 8px; border-radius:4px; }
@keyframes pulse-green { 0%,100%{box-shadow:0 0 0 0 rgba(34,197,94,0.4)} 50%{box-shadow:0 0 0 4px rgba(34,197,94,0)} }

.alert-danger  { background:rgba(239,68,68,0.08);  border-left:3px solid #ef4444; border-radius:6px; padding:10px 14px; margin:4px 0; font-size:12px; color:#fca5a5; }
.alert-warning { background:rgba(245,158,11,0.08); border-left:3px solid #f59e0b; border-radius:6px; padding:10px 14px; margin:4px 0; font-size:12px; color:#fcd34d; }
.alert-info    { background:rgba(56,189,248,0.08); border-left:3px solid #38bdf8; border-radius:6px; padding:10px 14px; margin:4px 0; font-size:12px; color:#7dd3fc; }
.alert-ok      { background:rgba(34,197,94,0.08);  border-left:3px solid #22c55e; border-radius:6px; padding:10px 14px; margin:4px 0; font-size:12px; color:#86efac; }

.sec-head { font-family:'Orbitron',monospace; font-size:10px; letter-spacing:3px; color:#1e6b8a; text-transform:uppercase; border-bottom:1px solid rgba(56,189,248,0.1); padding-bottom:8px; margin:18px 0 12px; }

.route-card { background:rgba(10,22,40,0.9); border:1px solid rgba(56,189,248,0.1); border-radius:12px; padding:14px 16px; margin:8px 0; position:relative; overflow:hidden; }
.route-card.best { border-color:rgba(34,197,94,0.4); box-shadow:0 0 20px rgba(34,197,94,0.08); }
.route-name { font-family:'Orbitron',monospace; font-size:12px; font-weight:700; margin-bottom:10px; }
.route-stats { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; }
.route-stat { text-align:center; background:rgba(56,189,248,0.04); border-radius:6px; padding:6px 4px; }
.route-stat-label { font-size:9px; color:#334d6b; text-transform:uppercase; letter-spacing:1px; margin-bottom:3px; }
.route-stat-val   { font-size:14px; font-weight:700; font-family:'Orbitron',monospace; }

.fuel-bar-bg   { background:rgba(56,189,248,0.08); border-radius:4px; height:8px; overflow:hidden; margin:4px 0; }
.fuel-bar-fill { height:100%; border-radius:4px; }

.stTabs [data-baseweb="tab-list"]  { background:rgba(5,13,26,0.8) !important; border-bottom:1px solid rgba(56,189,248,0.1) !important; gap:4px !important; }
.stTabs [data-baseweb="tab"]       { font-family:'Orbitron',monospace !important; font-size:10px !important; letter-spacing:2px !important; color:#334d6b !important; border-radius:6px 6px 0 0 !important; padding:10px 20px !important; }
.stTabs [aria-selected="true"]     { background:rgba(56,189,248,0.08) !important; color:#38bdf8 !important; border-bottom:2px solid #38bdf8 !important; }
.stTabs [data-baseweb="tab-panel"] { background:transparent !important; padding:0 !important; }

.stButton > button { font-family:'Orbitron',monospace !important; font-size:10px !important; letter-spacing:2px !important; background:linear-gradient(135deg,rgba(3,105,161,0.8),rgba(2,132,199,0.8)) !important; border:1px solid rgba(56,189,248,0.3) !important; color:#e2e8f0 !important; border-radius:6px !important; padding:10px !important; width:100% !important; text-transform:uppercase !important; }
.stButton > button:hover { background:linear-gradient(135deg,rgba(3,105,161,1),rgba(2,132,199,1)) !important; box-shadow:0 0 20px rgba(56,189,248,0.3) !important; }

.stSelectbox > div > div, .stTextInput input { background:rgba(5,15,30,0.9) !important; border:1px solid rgba(56,189,248,0.15) !important; color:#94a3b8 !important; border-radius:6px !important; }
div[data-testid="stVerticalBlock"] > div { gap:0.4rem; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════════
AIRPORTS = {
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
    "UT10 — Cedar Valley":        (40.4828, -111.9572),
    "U55 — Panguitch Muni":       (37.7045, -112.3123),
    "59AZ — Robin":               (34.7058, -112.4840),
    "QUAKY — Fix":                (34.2833, -111.8500),
    "CARTL — Fix":                (35.1167, -111.9833),
    "LOFTS — Fix":                (35.6500, -112.0000),
    "GCN — Fix/Grand Canyon":     (35.9524, -112.1470),
    "BCE — Bryce Canyon VOR":     (37.6833, -112.1500),
    "NEEBO — Fix":                (39.5167, -112.0333),
    # International
    "VIDP — New Delhi":           (28.5665,  77.1031),
    "VABB — Mumbai":              (19.0896,  72.8656),
    "EGLL — London Heathrow":     (51.4775,  -0.4614),
    "KJFK — New York JFK":        (40.6413, -73.7781),
    "OMDB — Dubai":               (25.2528,  55.3644),
    "WSSS — Singapore Changi":    (1.3644,  103.9915),
    "RJTT — Tokyo Haneda":        (35.5494,  139.7798),
    "YSSY — Sydney":              (-33.9399, 151.1753),
}

AIRCRAFT_DB = {
    "Boeing 787-9 Dreamliner":  {"burn_kgh":5400,  "capacity_pax":296, "range_km":14140, "max_alt":43000, "cruise_kts":488},
    "Boeing 777-300ER":         {"burn_kgh":7500,  "capacity_pax":396, "range_km":13649, "max_alt":43100, "cruise_kts":490},
    "Airbus A380-800":          {"burn_kgh":11000, "capacity_pax":555, "range_km":15200, "max_alt":43000, "cruise_kts":488},
    "Airbus A350-900":          {"burn_kgh":5800,  "capacity_pax":369, "range_km":15000, "max_alt":43100, "cruise_kts":489},
    "Boeing 737 MAX 8":         {"burn_kgh":2500,  "capacity_pax":178, "range_km":6570,  "max_alt":41000, "cruise_kts":453},
    "Airbus A320neo":           {"burn_kgh":2300,  "capacity_pax":165, "range_km":6300,  "max_alt":39800, "cruise_kts":450},
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
#  API CALLS (no cache = always live)
# ═══════════════════════════════════════════════════════════════
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
            "lat":          lat,
            "lon":          lon,
            "wind_speed":   float(cur.get("wind_speed_10m", 0) or 0),
            "wind_dir":     float(cur.get("wind_direction_10m", 0) or 0),
            "pressure":     float(cur.get("pressure_msl", 1013) or 1013),
            "weather_code": int(cur.get("weather_code", 0) or 0),
            "temperature":  float(cur.get("temperature_2m", 15) or 15),
            "humidity":     float(cur.get("relative_humidity_2m", 50) or 50),
            "precip":       float(cur.get("precipitation", 0) or 0),
            "data_time":    cur.get("time", "—"),
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
    dist_nm    = dist_km * 0.539957
    base_time  = dist_nm / ac["cruise_kts"]
    avg_wind   = np.mean([w["wind_speed"] for w in wp_weather]) if wp_weather else 20
    avg_dir    = np.mean([w["wind_dir"]   for w in wp_weather]) if wp_weather else 0
    wf  = 1 + (avg_wind * 0.003 * math.cos(math.radians(avg_dir)))
    af  = 0.92 if cruise_alt >= 35000 else 0.97
    lf  = 0.88 + (pax_load / 100) * 0.18
    wp_ = 1.0
    for w in wp_weather:
        if int(w["weather_code"]) >= 95:   wp_ += 0.04
        elif int(w["weather_code"]) >= 80: wp_ += 0.02
        elif int(w["weather_code"]) >= 61: wp_ += 0.01
    tf          = wf * af * lf * wp_
    actual_time = base_time * wf
    total_fuel  = ac["burn_kgh"] * actual_time * tf
    fuel_per_pax = total_fuel / max(1, round(ac["capacity_pax"] * pax_load/100))
    score        = max(0, min(100, 100 - (tf - 0.9) * 200))
    return {
        "total_fuel_kg":     round(total_fuel),
        "fuel_per_pax_kg":   round(fuel_per_pax, 1),
        "flight_time_h":     round(actual_time, 2),
        "efficiency_score":  round(score, 1),
        "wind_impact":       round((wf-1)*100, 1),
        "alt_saving":        round((1-af)*100, 1),
        "weather_penalty_pct": round((wp_-1)*100, 1),
        "load_factor_pct":   round(pax_load),
        "burn_rate_kgh":     round(ac["burn_kgh"] * tf),
        "co2_tonnes":        round(total_fuel * 3.16 / 1000, 1),
    }

PREDEFINED_ROUTES = {
    ("KSDL — Scottsdale", "KSLC — Salt Lake City"): [
        {"id":"A","color":"#38bdf8","name":"VIA DEER VALLEY & DELTA","desc":"KSDL → KDVT → KDTA → Cedar Valley → KSLC",
         "wpt_coords":[(33.6297,-111.9135),(33.6883,-112.0822),(39.3814,-112.5170),(40.4828,-111.9572),(40.7934,-111.9799)],"dist_factor":1.12,"time_factor":1.10},
        {"id":"B","color":"#a78bfa","name":"VIA PHOENIX & GRAND CANYON","desc":"KSDL → KPHX → Robin → KGCN → Panguitch → KSLC",
         "wpt_coords":[(33.6297,-111.9135),(33.4373,-111.9741),(34.7058,-112.4840),(35.9524,-112.1470),(37.7045,-112.3123),(40.4828,-111.9572),(40.7934,-111.9799)],"dist_factor":1.22,"time_factor":1.20},
        {"id":"C","color":"#34d399","name":"VIA PHOENIX & SEVIER VALLEY","desc":"KSDL → KPHX → Robin → KDTA → KSVR → KSLC",
         "wpt_coords":[(33.6297,-111.9135),(33.4373,-111.9741),(34.7058,-112.4840),(39.3814,-112.5170),(38.7724,-112.0877),(40.7934,-111.9799)],"dist_factor":1.18,"time_factor":1.15},
        {"id":"D","color":"#fbbf24","name":"PRIMARY — GPS FIXES","desc":"KSDL → QUAKY → CARTL → LOFTS → GCN → BCE → NEEBO → KSLC",
         "wpt_coords":[(33.6297,-111.9135),(34.2833,-111.8500),(35.1167,-111.9833),(35.6500,-112.0000),(35.9524,-112.1470),(37.6833,-112.1500),(39.5167,-112.0333),(40.7934,-111.9799)],"dist_factor":1.08,"time_factor":1.05},
    ],
    ("KLAS — Las Vegas McCarran","KVNY — Van Nuys"):[
        {"id":"A","color":"#38bdf8","name":"DIRECT LAS-VNY","desc":"KLAS → KVNY direct","wpt_coords":[(36.0840,-115.1537),(34.2098,-118.4898)],"dist_factor":1.00,"time_factor":1.00}],
    ("KVNY — Van Nuys","KOAK — Oakland Intl"):[
        {"id":"A","color":"#38bdf8","name":"DIRECT VNY-OAK","desc":"KVNY → KOAK coastal","wpt_coords":[(34.2098,-118.4898),(37.7213,-122.2208)],"dist_factor":1.00,"time_factor":1.00}],
    ("KGJT — Grand Junction","KAPA — Centennial Denver"):[
        {"id":"A","color":"#38bdf8","name":"DIRECT GJT-APA","desc":"KGJT → KAPA direct","wpt_coords":[(39.1224,-108.5270),(39.5701,-104.8492)],"dist_factor":1.00,"time_factor":1.00},
        {"id":"B","color":"#a78bfa","name":"VIA ASPEN","desc":"KGJT → KASE → KAPA","wpt_coords":[(39.1224,-108.5270),(39.2232,-106.8688),(39.5701,-104.8492)],"dist_factor":1.15,"time_factor":1.12}],
}

def build_waypoints_from_coords(coord_list):
    if len(coord_list) < 2: return coord_list
    all_pts = []
    for i in range(len(coord_list)-1):
        seg = interpolate_route(coord_list[i][0], coord_list[i][1], coord_list[i+1][0], coord_list[i+1][1], n=4)
        if i < len(coord_list)-2: seg = seg[:-1]
        all_pts.extend(seg)
    return all_pts

def ai_route_optimizer(orig, dest, orig_coords, dest_coords):
    lat1,lon1 = orig_coords; lat2,lon2 = dest_coords
    dist_km   = haversine(lat1,lon1,lat2,lon2)
    key = (orig, dest)
    if key in PREDEFINED_ROUTES:
        routes = [{"id":r["id"],"name":r["name"],"desc":r["desc"],"color":r["color"],
                   "waypoints":build_waypoints_from_coords(r["wpt_coords"]),
                   "dist_factor":r["dist_factor"],"time_factor":r["time_factor"]} for r in PREDEFINED_ROUTES[key]]
    else:
        routes = [
            {"id":"A","name":"DIRECT ROUTE","desc":"Great circle shortest distance","waypoints":interpolate_route(lat1,lon1,lat2,lon2,10,0,0),"color":"#38bdf8","dist_factor":1.00,"time_factor":1.00},
            {"id":"B","name":"NORTHERN ROUTE","desc":"Higher latitude jet stream advantage","waypoints":interpolate_route(lat1,lon1,lat2,lon2,10,1.5,-1.5),"color":"#a78bfa","dist_factor":1.04,"time_factor":0.97},
            {"id":"C","name":"WEATHER AVOIDANCE","desc":"Storm-clear path longer but safer","waypoints":interpolate_route(lat1,lon1,lat2,lon2,10,-1.5,2),"color":"#34d399","dist_factor":1.08,"time_factor":1.06},
            {"id":"D","name":"FUEL ECONOMY","desc":"Optimal altitude and wind exploitation","waypoints":interpolate_route(lat1,lon1,lat2,lon2,10,0.5,0.8),"color":"#fbbf24","dist_factor":1.02,"time_factor":0.98},
        ]
    for r in routes:
        d = dist_km * r["dist_factor"]; t = (d*0.539957)/490*r["time_factor"]; fuel = 5400*t*r["dist_factor"]
        wx_pts = r["waypoints"][::3]
        wx_data = get_all_route_weather(tuple(wx_pts))
        storm_count = sum(1 for w in wx_data if int(w["weather_code"]) >= 80)
        avg_wind    = np.mean([w["wind_speed"] for w in wx_data]) if wx_data else 20
        wx_score    = max(0, 100 - storm_count*20 - avg_wind*0.3)
        fuel_score  = max(0, 100 - (r["dist_factor"]-1)*300)
        time_score  = max(0, 100 - (r["time_factor"]-0.9)*300)
        ai_score    = wx_score*0.4 + fuel_score*0.35 + time_score*0.25
        r.update({"dist_km":round(d),"time_h":round(t,1),"fuel_kg":round(fuel),
                  "wx_score":round(wx_score),"fuel_score":round(fuel_score),
                  "time_score":round(time_score),"ai_score":round(ai_score),
                  "storm_count":storm_count,"avg_wind":round(avg_wind),"wx_data":wx_data})
    routes.sort(key=lambda x:-x["ai_score"])
    routes[0]["is_best"] = True
    for r in routes[1:]: r["is_best"] = False
    return routes

# ═══════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""<div style="padding:16px 0 8px"><div class="hud-title">✈ AeroNav Pro</div><div class="hud-sub">Flight Intelligence System</div></div>""", unsafe_allow_html=True)
    now_utc = datetime.now(timezone.utc)
    st.markdown(f"""
    <div style="background:rgba(56,189,248,0.04);border:1px solid rgba(56,189,248,0.12);border-radius:10px;padding:14px;margin:8px 0;text-align:center">
      <div class="live-clock">{now_utc.strftime('%H:%M:%S')}</div>
      <div class="live-date">{now_utc.strftime('%d %b %Y')} · UTC</div>
      <div style="margin-top:6px"><span class="live-badge">● LIVE</span></div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec-head">Mission Parameters</div>', unsafe_allow_html=True)
    airport_list = list(AIRPORTS.keys())
    origin_sel = st.selectbox("Origin",      airport_list, index=airport_list.index("KSDL — Scottsdale"))
    dest_sel   = st.selectbox("Destination", airport_list, index=airport_list.index("KSLC — Salt Lake City"))
    flight_num = st.text_input("Flight No.", "N131AV")
    aircraft   = st.selectbox("Aircraft", list(AIRCRAFT_DB.keys()))

    st.markdown('<div class="sec-head">Flight Parameters</div>', unsafe_allow_html=True)
    cruise_alt   = st.slider("Cruise Alt (ft)", 28000, 43000, 35000, 1000)
    cruise_speed = st.slider("Speed (knots)",   400,   600,   490,   10)
    pax_load     = st.slider("Pax Load (%)",    60,    100,   85,    5)

    st.markdown('<div class="sec-head">Display</div>', unsafe_allow_html=True)
    show_storms    = st.toggle("Storm zones",   True)
    show_sigmets   = st.toggle("Live SIGMETs",  True)
    show_jetstream = st.toggle("Jet streams",   True)
    auto_refresh   = st.toggle("Auto-refresh",  False)
    map_style      = st.selectbox("Map theme", ["Dark Aviation","Satellite","Terrain"])

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    compute_btn = st.button("⚡ COMPUTE FLIGHT PLAN", use_container_width=True)
    refresh_btn = st.button("↻  REFRESH WEATHER",     use_container_width=True)

if refresh_btn:
    st.cache_data.clear()
    st.rerun()
if auto_refresh:
    time.sleep(300)
    st.rerun()

if compute_btn or "route_data" not in st.session_state:
    st.session_state.origin   = origin_sel
    st.session_state.dest     = dest_sel
    st.session_state.computed = True
    for k in ["map_zoom","map_center_lat","map_center_lon"]:
        if k in st.session_state: del st.session_state[k]

origin_name = st.session_state.get("origin", origin_sel)
dest_name   = st.session_state.get("dest",   dest_sel)
orig_lat, orig_lon = AIRPORTS[origin_name]
dest_lat, dest_lon = AIRPORTS[dest_name]
icao_orig = origin_name.split("—")[0].strip()
icao_dest = dest_name.split("—")[0].strip()
dist_km   = haversine(orig_lat, orig_lon, dest_lat, dest_lon)
dist_nm   = dist_km * 0.539957

# ═══════════════════════════════════════════════════════════════
#  HEADER BAR
# ═══════════════════════════════════════════════════════════════
now_utc = datetime.now(timezone.utc)
h1, h2, h3 = st.columns([2,3,2])
with h1:
    st.markdown(f"""
    <div style="padding:8px 0">
      <div style="font-family:'Orbitron',monospace;font-size:11px;color:#1e6b8a;letter-spacing:3px">FLIGHT</div>
      <div style="font-family:'Orbitron',monospace;font-size:26px;font-weight:900;color:#38bdf8;text-shadow:0 0 20px rgba(56,189,248,0.4)">{flight_num}</div>
      <div style="font-size:12px;color:#334d6b;margin-top:2px">{AIRCRAFT_DB[aircraft]["capacity_pax"]} pax · {AIRCRAFT_DB[aircraft]["range_km"]:,} km range</div>
    </div>""", unsafe_allow_html=True)
with h2:
    st.markdown(f"""
    <div style="text-align:center;padding:8px 0">
      <div style="font-family:'Orbitron',monospace;font-size:22px;font-weight:700">
        <span style="color:#38bdf8">{icao_orig}</span>
        <span style="color:#1e3a5f;font-size:16px;margin:0 16px">─────✈─────</span>
        <span style="color:#a78bfa">{icao_dest}</span>
      </div>
      <div style="font-size:12px;color:#334d6b;margin-top:4px">{origin_name.split("—")[1].strip()} → {dest_name.split("—")[1].strip()}</div>
      <div style="font-size:10px;color:#1e4d6b;margin-top:2px;font-family:'Orbitron',monospace">DATA: {now_utc.strftime('%H:%M:%S')} UTC</div>
    </div>""", unsafe_allow_html=True)
with h3:
    st.markdown(f"""
    <div style="text-align:right;padding:8px 0">
      <div class="live-clock" style="font-size:22px">{now_utc.strftime('%H:%M:%S')}</div>
      <div class="live-date">{now_utc.strftime('%A, %d %B %Y')}</div>
      <div style="margin-top:6px"><span class="live-badge">● LIVE DATA</span></div>
    </div>""", unsafe_allow_html=True)

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
ac_data = AIRCRAFT_DB[aircraft]
eta_h = int(fuel_data["flight_time_h"])
eta_m = int((fuel_data["flight_time_h"] - eta_h) * 60)

cols = st.columns(8)
metrics = [
    ("DISTANCE",   f"{dist_nm:,.0f}",                      "NM"),
    ("ETA",        f"{eta_h}h{eta_m:02d}m",                "FLIGHT TIME"),
    ("CRUISE",     f"{cruise_alt//1000}K",                  "FEET ALT"),
    ("SPEED",      f"{cruise_speed}",                       "KNOTS"),
    ("FUEL",       f"{fuel_data['total_fuel_kg']//1000}K",  "KG TOTAL"),
    ("EFFICIENCY", f"{fuel_data['efficiency_score']}",      "AI SCORE"),
    ("CO₂",        f"{fuel_data['co2_tonnes']}",            "TONNES"),
    ("PAX LOAD",   f"{pax_load}%",                         "CAPACITY"),
]
for col, (label, val, unit) in zip(cols, metrics):
    with col:
        st.markdown(f'<div class="metric-hud"><div class="metric-hud-label">{label}</div><div class="metric-hud-value">{val}</div><div class="metric-hud-unit">{unit}</div></div>', unsafe_allow_html=True)

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["🌍  WEATHER MAP & FORECAST", "⛽  AI FUEL EFFICIENCY", "🛣️  ROUTE OPTIMIZATION"])

# ╔═══════════════════════════════════════════════════════════════
#  TAB 1 — WEATHER MAP
# ╚═══════════════════════════════════════════════════════════════
with tab1:
    map_col, wx_col = st.columns([4, 1])

    with map_col:
        fig_map = go.Figure()

        # ── STORM ZONES ──────────────────────────────────────────
        if show_storms:
            storm_zones = [
                ("Gulf of Mexico",  24, -90,  3.5, "#ef4444"),
                ("Caribbean",       18, -70,  3.0, "#ef4444"),
                ("E Pacific",       18,-110,  3.0, "#f97316"),
                ("Great Plains",    38, -98,  2.5, "#f59e0b"),
            ]
            for sname, slat, slon, sz, scol in storm_zones:
                angles = np.linspace(0, 2*math.pi, 40)
                clat = slat + sz*np.sin(angles)
                clon = slon + sz*1.5*np.cos(angles)
                fig_map.add_trace(go.Scattermapbox(
                    lat=list(clat)+[clat[0]], lon=list(clon)+[clon[0]],
                    mode="lines", line=dict(color=scol, width=1), opacity=0.5,
                    hovertemplate=f"⚠️ {sname}<extra></extra>", showlegend=False,
                    fill="toself", fillcolor="rgba(239,68,68,0.05)"))
                # glow halo
                fig_map.add_trace(go.Scattermapbox(lat=[slat], lon=[slon], mode="markers",
                    marker=dict(size=36, color=scol, opacity=0.20), hoverinfo="skip", showlegend=False))
                # ring
                fig_map.add_trace(go.Scattermapbox(lat=[slat], lon=[slon], mode="markers",
                    marker=dict(size=28, color=scol, opacity=0.80), hoverinfo="skip", showlegend=False))
                # dark disc
                fig_map.add_trace(go.Scattermapbox(lat=[slat], lon=[slon], mode="markers",
                    marker=dict(size=22, color="rgba(6,14,28,0.96)", opacity=1.0), hoverinfo="skip", showlegend=False))
                # emoji icon
                fig_map.add_trace(go.Scattermapbox(lat=[slat], lon=[slon],
                    mode="markers+text", marker=dict(size=0, color="rgba(0,0,0,0)"),
                    text=["🌀"], textfont=dict(size=20),
                    hovertemplate=f"⚠️ {sname}<extra></extra>", showlegend=False))

        # ── JET STREAM ───────────────────────────────────────────
        if show_jetstream:
            fig_map.add_trace(go.Scattermapbox(
                lat=[32,35,38,40,42,43,42,40], lon=[-120,-115,-110,-105,-100,-95,-90,-85],
                mode="lines", line=dict(color="#fbbf24", width=3), opacity=0.55,
                name="Jet Stream", hovertemplate="Jet Stream<extra></extra>"))

        # ── ROUTE LINES ──────────────────────────────────────────
        sorted_routes = [r for r in routes if not r.get("is_best")] + [r for r in routes if r.get("is_best")]
        for r in sorted_routes:
            wpts = r["waypoints"]
            rlats = [p[0] for p in wpts]; rlons = [p[1] for p in wpts]
            is_best = r.get("is_best", False)
            fig_map.add_trace(go.Scattermapbox(
                lat=rlats, lon=rlons,
                mode="lines+markers" if is_best else "lines",
                line=dict(color=r["color"], width=5 if is_best else 2),
                marker=dict(size=5, color=r["color"]) if is_best else dict(size=0),
                opacity=1.0 if is_best else 0.50,
                name=("★ " if is_best else "") + r["name"],
                hovertemplate=f"{r['name']}<br>{r['dist_km']:,} km · {r['time_h']}h<extra></extra>"))

        # ── LIVE WEATHER INTENSITY OVERLAY ────────────────────────
        for w in wp_weather:
            code = w["weather_code"]; ws = w["wind_speed"]
            if code >= 95:           color="rgba(185,28,28,0.50)";  sz=30
            elif code>=80 or ws>60:  color="rgba(239,68,68,0.38)";  sz=24
            elif code>=61 or ws>40:  color="rgba(245,158,11,0.32)"; sz=20
            elif code>=45 or ws>25:  color="rgba(56,189,248,0.25)"; sz=16
            else:                    color="rgba(34,197,94,0.20)";  sz=14
            fig_map.add_trace(go.Scattermapbox(lat=[w["lat"]], lon=[w["lon"]], mode="markers",
                marker=dict(size=sz, color=color),
                hoverinfo="skip", showlegend=False))

        # ── WAYPOINT WEATHER ICONS ────────────────────────────────
        # Build proper badge: glow halo → coloured ring → dark disc → emoji on top
        wp_lats   = [w["lat"]  for w in wp_weather]
        wp_lons   = [w["lon"]  for w in wp_weather]
        wp_texts  = [wx_info(w["weather_code"])[1] for w in wp_weather]
        wp_colors = [wx_info(w["weather_code"])[2] for w in wp_weather]
        wp_hover  = [
            f"<b>WP{i}</b> · {wx_info(w['weather_code'])[0]}<br>"
            f"💨 Wind: {w['wind_speed']:.0f} km/h {wind_label(w['wind_dir'])}<br>"
            f"🌡 Temp: {w['temperature']:.1f}°C<br>"
            f"🔵 Pressure: {w['pressure']:.0f} hPa<br>"
            f"💧 Humidity: {w['humidity']:.0f}%<br>"
            f"🕐 {w.get('data_time','—')} UTC"
            for i, w in enumerate(wp_weather)
        ]

        # Layer 1 — outer glow halo (soft, large)
        fig_map.add_trace(go.Scattermapbox(lat=wp_lats, lon=wp_lons, mode="markers",
            marker=dict(size=42, color=wp_colors, opacity=0.15),
            hoverinfo="skip", showlegend=False))
        # Layer 2 — coloured ring (the visible "circle border")
        fig_map.add_trace(go.Scattermapbox(lat=wp_lats, lon=wp_lons, mode="markers",
            marker=dict(size=32, color=wp_colors, opacity=0.90),
            hoverinfo="skip", showlegend=False))
        # Layer 3 — dark disc (inner background so emoji reads clearly)
        fig_map.add_trace(go.Scattermapbox(lat=wp_lats, lon=wp_lons, mode="markers",
            marker=dict(size=26, color="rgba(4,10,24,0.96)", opacity=1.0),
            hoverinfo="skip", showlegend=False))
        # Layer 4 — emoji weather icon ON TOP (this is what user sees inside the circle)
        fig_map.add_trace(go.Scattermapbox(lat=wp_lats, lon=wp_lons,
            mode="markers+text",
            marker=dict(size=0, color="rgba(0,0,0,0)"),
            text=wp_texts,
            textfont=dict(size=22),
            hovertext=wp_hover,
            hovertemplate="%{hovertext}<extra></extra>",
            name="Waypoints", showlegend=True))

        # ── SIGMETs ──────────────────────────────────────────────
        if show_sigmets and sigmets:
            sig_lats, sig_lons, sig_txt = [], [], []
            for s in sigmets[:25]:
                try:
                    sig_lats.append(float(s.get("lat",0)))
                    sig_lons.append(float(s.get("lon",0)))
                    sig_txt.append(f"SIGMET: {s.get('hazard','?')}<br>{s.get('firname','')}")
                except: pass
            if sig_lats:
                fig_map.add_trace(go.Scattermapbox(lat=sig_lats, lon=sig_lons,
                    mode="markers+text", marker=dict(size=18, color="#f59e0b", symbol="star"),
                    text=["⚡"]*len(sig_lats), hovertext=sig_txt,
                    hovertemplate="%{hovertext}<extra></extra>", name="SIGMETs"))

        # ── AIRPORT MARKERS ───────────────────────────────────────
        # Origin: teal badge
        fig_map.add_trace(go.Scattermapbox(lat=[orig_lat], lon=[orig_lon], mode="markers",
            marker=dict(size=28, color="#38bdf8", opacity=0.25), hoverinfo="skip", showlegend=False))
        fig_map.add_trace(go.Scattermapbox(lat=[orig_lat], lon=[orig_lon],
            mode="markers+text", marker=dict(size=22, color="#38bdf8"),
            text=[f"✈ {icao_orig}"], textposition="top right",
            textfont=dict(size=13, color="#38bdf8"),
            hovertemplate=f"<b>ORIGIN: {icao_orig}</b><br>{origin_name.split(chr(8212))[1].strip()}<extra></extra>",
            name="Origin"))
        # Destination: purple badge
        fig_map.add_trace(go.Scattermapbox(lat=[dest_lat], lon=[dest_lon], mode="markers",
            marker=dict(size=28, color="#a78bfa", opacity=0.25), hoverinfo="skip", showlegend=False))
        fig_map.add_trace(go.Scattermapbox(lat=[dest_lat], lon=[dest_lon],
            mode="markers+text", marker=dict(size=22, color="#a78bfa"),
            text=[f"■ {icao_dest}"], textposition="top right",
            textfont=dict(size=13, color="#a78bfa"),
            hovertemplate=f"<b>DEST: {icao_dest}</b><br>{dest_name.split(chr(8212))[1].strip()}<extra></extra>",
            name="Destination"))

        # ── AUTO ZOOM ─────────────────────────────────────────────
        all_lats = [p[0] for r in routes for p in r["waypoints"]] + [orig_lat, dest_lat]
        all_lons = [p[1] for r in routes for p in r["waypoints"]] + [orig_lon, dest_lon]
        lat_span = max(all_lats) - min(all_lats)
        lon_span = max(all_lons) - min(all_lons)
        max_span = max(lat_span, lon_span, 0.1)
        auto_zoom   = min(9.5, max(4.0, math.log2(160.0/max_span)+1.0))
        center_lat  = (max(all_lats)+min(all_lats))/2
        center_lon  = (max(all_lons)+min(all_lons))/2

        if "map_zoom"       not in st.session_state: st.session_state.map_zoom       = auto_zoom
        if "map_center_lat" not in st.session_state: st.session_state.map_center_lat = center_lat
        if "map_center_lon" not in st.session_state: st.session_state.map_center_lon = center_lon

        # Zoom controls
        zc1,zc2,zc3,zc4,zc5 = st.columns([1,1,1,1,6])
        with zc1:
            if st.button("＋", key="zoom_in",   help="Zoom In"):   st.session_state.map_zoom = min(st.session_state.map_zoom+1, 18)
        with zc2:
            if st.button("－", key="zoom_out",  help="Zoom Out"):  st.session_state.map_zoom = max(st.session_state.map_zoom-1, 1)
        with zc3:
            if st.button("⌖",  key="zoom_fit",  help="Fit Route"): st.session_state.map_zoom=auto_zoom; st.session_state.map_center_lat=center_lat; st.session_state.map_center_lon=center_lon
        with zc4:
            if st.button("⊕",  key="zoom_orig", help="Go to Origin"): st.session_state.map_zoom=10; st.session_state.map_center_lat=orig_lat; st.session_state.map_center_lon=orig_lon
        with zc5:
            st.markdown(f"<div style='font-family:Orbitron,monospace;font-size:10px;color:#1e6b8a;letter-spacing:2px;padding-top:6px'>ZOOM {st.session_state.map_zoom:.1f} &nbsp;·&nbsp; SCROLL TO ZOOM &nbsp;·&nbsp; DRAG TO PAN</div>", unsafe_allow_html=True)

        tile_styles = {"Dark Aviation":"carto-darkmatter","Satellite":"open-street-map","Terrain":"carto-positron"}
        fig_map.update_layout(
            mapbox=dict(style=tile_styles.get(map_style,"carto-darkmatter"),
                        center=dict(lat=st.session_state.map_center_lat, lon=st.session_state.map_center_lon),
                        zoom=st.session_state.map_zoom),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0,r=0,t=0,b=0), height=600, showlegend=True,
            legend=dict(bgcolor="rgba(5,15,30,0.92)", bordercolor="rgba(56,189,248,0.2)", borderwidth=1,
                        font=dict(color="#94a3b8",size=10), x=0.01, y=0.01,
                        xanchor="left", yanchor="bottom", itemsizing="constant", tracegroupgap=2),
            uirevision="map_view")
        st.plotly_chart(fig_map, use_container_width=True, config={
            "displayModeBar": True, "scrollZoom": True,
            "modeBarButtonsToRemove": ["toImage"],
            "modeBarButtonsToAdd": ["zoomInMapbox","zoomOutMapbox","resetViewMapbox"]})

        # ── ROUTE WEATHER TIMELINE ────────────────────────────────
        st.markdown('<div class="sec-head">ROUTE WEATHER TIMELINE</div>', unsafe_allow_html=True)
        wp_labels = ["ORIG"] + [f"WP{i}" for i in range(1,len(wp_weather)-1)] + ["DEST"]
        fig_tl = make_subplots(rows=1, cols=3,
            subplot_titles=("Wind Speed (km/h)","Pressure (hPa)","Temperature (°C)"),
            horizontal_spacing=0.06)
        y_wind = [w["wind_speed"]  for w in wp_weather]
        y_pres = [w["pressure"]    for w in wp_weather]
        y_temp = [w["temperature"] for w in wp_weather]
        wc_    = ["#ef4444" if v>60 else "#f59e0b" if v>35 else "#38bdf8" for v in y_wind]
        fig_tl.add_trace(go.Scatter(x=wp_labels, y=y_wind, mode="lines+markers",
            line=dict(color="#38bdf8",width=2), marker=dict(color=wc_,size=9),
            fill="tozeroy", fillcolor="rgba(56,189,248,0.07)", name="Wind"), row=1, col=1)
        fig_tl.add_shape(type="line", x0=0, x1=len(wp_labels)-1, y0=60, y1=60,
            line=dict(color="#ef4444",width=1,dash="dash"), row=1, col=1)
        fig_tl.add_trace(go.Scatter(x=wp_labels, y=y_pres, mode="lines+markers",
            line=dict(color="#a78bfa",width=2), marker=dict(color="#a78bfa",size=9),
            fill="tozeroy", fillcolor="rgba(167,139,250,0.07)", name="Pressure"), row=1, col=2)
        fig_tl.add_trace(go.Scatter(x=wp_labels, y=y_temp, mode="lines+markers",
            line=dict(color="#34d399",width=2), marker=dict(color="#34d399",size=9),
            fill="tozeroy", fillcolor="rgba(52,211,153,0.07)", name="Temp"), row=1, col=3)
        fig_tl.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,15,30,0.6)",
            font=dict(color="#64748b",size=11), margin=dict(l=0,r=0,t=30,b=0), height=200, showlegend=False)
        for i in range(1,4):
            fig_tl.update_xaxes(showgrid=False, color="#1e3a5f", row=1, col=i)
            fig_tl.update_yaxes(showgrid=True, gridcolor="rgba(30,58,95,0.5)", color="#1e3a5f", row=1, col=i)
        fig_tl.update_annotations(font=dict(color="#64748b",size=11))
        st.plotly_chart(fig_tl, use_container_width=True, config={"displayModeBar":False})

    # ── WEATHER SIDE PANEL ────────────────────────────────────────
    with wx_col:
        # Live airport weather cards
        for lbl, lat, lon, icao, col_ in [("ORIGIN",orig_lat,orig_lon,icao_orig,"#38bdf8"),("DEST",dest_lat,dest_lon,icao_dest,"#a78bfa")]:
            w = get_weather(lat, lon)
            cur = w.get("current",{}) if w else {}
            desc, icon, _ = wx_info(cur.get("weather_code",0))
            st.markdown(f"""
            <div style="background:rgba(10,22,40,0.9);border:1px solid rgba(56,189,248,0.12);border-top:3px solid {col_};border-radius:10px;padding:14px;margin:8px 0">
              <div style="font-family:'Orbitron',monospace;font-size:9px;color:{col_};letter-spacing:3px;margin-bottom:6px">{lbl} · {icao}</div>
              <div style="font-size:10px;color:#1e4d6b;margin-bottom:8px;font-family:'Orbitron',monospace">🕐 {cur.get('time','—')} UTC</div>
              <div style="font-size:28px;margin-bottom:8px">{icon}</div>
              <div style="font-size:13px;color:#e2e8f0;font-weight:600;margin-bottom:8px">{desc}</div>
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:12px;color:#475569">
                <div>🌡 <span style="color:#94a3b8">{cur.get('temperature_2m','—')}°C</span></div>
                <div>💨 <span style="color:#94a3b8">{cur.get('wind_speed_10m','—')} km/h</span></div>
                <div>🧭 <span style="color:#94a3b8">{wind_label(cur.get('wind_direction_10m',0))}</span></div>
                <div>💧 <span style="color:#94a3b8">{cur.get('relative_humidity_2m','—')}%</span></div>
                <div>🔵 <span style="color:#94a3b8">{cur.get('pressure_msl','—')} hPa</span></div>
                <div>🌧 <span style="color:#94a3b8">{cur.get('precipitation','—')} mm</span></div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Waypoint alerts
        st.markdown('<div class="sec-head">WEATHER ALERTS</div>', unsafe_allow_html=True)
        alerts = []
        for i, w in enumerate(wp_weather):
            code = w.get("weather_code",0); ws = w.get("wind_speed",0)
            lbl_ = "ORIG" if i==0 else "DEST" if i==len(wp_weather)-1 else f"WP{i}"
            if code>=95:   alerts.append(("danger",  lbl_, "Thunderstorm",  f"{ws:.0f} km/h"))
            elif code>=80: alerts.append(("warning", lbl_, "Heavy showers", f"{ws:.0f} km/h"))
            elif ws>70:    alerts.append(("danger",  lbl_, "Extreme winds", f"{ws:.0f} km/h"))
            elif ws>45:    alerts.append(("warning", lbl_, "Strong winds",  f"{ws:.0f} km/h"))
            elif ws>25:    alerts.append(("info",    lbl_, "Moderate wind", f"{ws:.0f} km/h"))
            else:          alerts.append(("ok",      lbl_, "Clear",         f"{ws:.0f} km/h"))
        if all(a[0]=="ok" for a in alerts):
            st.markdown('<div class="alert-ok" style="text-align:center">✅ Route looks clear</div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head">WAYPOINTS</div>', unsafe_allow_html=True)
        for lvl, lbl_, desc_, wind_ in alerts[:10]:
            colors_ = {"danger":"#ef4444","warning":"#f59e0b","info":"#38bdf8","ok":"#22c55e"}
            badges_ = {"danger":"HIGH","warning":"MOD","info":"LOW","ok":"CLR"}
            icons_  = {"danger":"⛈","warning":"🌧","info":"💨","ok":"☀️"}
            col_    = colors_[lvl]
            bb_     = {"danger":"rgba(239,68,68,0.15)","warning":"rgba(245,158,11,0.15)","info":"rgba(56,189,248,0.15)","ok":"rgba(34,197,94,0.15)"}[lvl]
            st.markdown(f"""
            <div style="background:rgba(10,22,40,0.8);border:1px solid rgba(56,189,248,0.1);border-left:3px solid {col_};border-radius:8px;padding:10px 12px;margin:5px 0;display:flex;justify-content:space-between;align-items:center">
              <div>
                <div style="font-family:'Orbitron',monospace;font-size:9px;color:#64748b;letter-spacing:2px;margin-bottom:3px">{lbl_}</div>
                <div style="font-size:12px;color:#94a3b8">{icons_[lvl]} {wind_}</div>
              </div>
              <div style="background:{bb_};border:1px solid {col_};color:{col_};font-size:9px;font-weight:700;padding:3px 7px;border-radius:4px;font-family:'Orbitron',monospace">{badges_[lvl]}</div>
            </div>""", unsafe_allow_html=True)

        # 24h forecast bar
        st.markdown('<div class="sec-head">24H WIND — ORIGIN</div>', unsafe_allow_html=True)
        w0 = get_weather(orig_lat, orig_lon)
        if w0 and "hourly" in w0:
            hrs  = w0["hourly"].get("time",[])[:24]
            wspd = w0["hourly"].get("wind_speed_10m",[])[:24]
            fig_fc = go.Figure(go.Bar(x=[t[-5:] for t in hrs], y=wspd,
                marker_color=["#ef4444" if v>60 else "#f59e0b" if v>35 else "#38bdf8" for v in wspd], opacity=0.8))
            fig_fc.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,15,30,0.5)",
                margin=dict(l=0,r=0,t=0,b=0), height=130, showlegend=False,
                xaxis=dict(showgrid=False, color="#1e3a5f", tickfont=dict(size=8)),
                yaxis=dict(showgrid=True, gridcolor="rgba(30,58,95,0.5)", color="#1e3a5f"))
            st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar":False})

        # Legend
        st.markdown('<div class="sec-head">LEGEND</div>', unsafe_allow_html=True)
        for col_, lbl_ in [("#38bdf8","Active route"),("#a78bfa","Alt routes"),("#fbbf24","Jet stream"),("#ef4444","Storm zone"),("#f59e0b","SIGMET")]:
            st.markdown(f'<div style="display:flex;align-items:center;gap:8px;font-size:12px;color:#475569;margin:4px 0"><div style="width:12px;height:12px;border-radius:3px;background:{col_};flex-shrink:0"></div>{lbl_}</div>', unsafe_allow_html=True)

# ╔═══════════════════════════════════════════════════════════════
#  TAB 2 — AI FUEL EFFICIENCY
# ╚═══════════════════════════════════════════════════════════════
with tab2:
    fd = fuel_data
    f1, f2, f3 = st.columns([1,1,1])

    with f1:
        st.markdown('<div class="sec-head">AI EFFICIENCY SCORE</div>', unsafe_allow_html=True)
        score = fd["efficiency_score"]
        sc    = "#22c55e" if score>=80 else "#f59e0b" if score>=60 else "#ef4444"
        slbl  = "EXCELLENT" if score>=80 else "GOOD" if score>=65 else "MODERATE" if score>=50 else "POOR"
        fig_g = go.Figure(go.Indicator(mode="gauge+number+delta", value=score,
            number=dict(font=dict(color="#38bdf8",size=48,family="Orbitron"), suffix=""),
            gauge=dict(
                axis=dict(range=[0,100], tickcolor="#1e3a5f", tickfont=dict(color="#1e3a5f")),
                bar=dict(color=sc, thickness=0.25), bgcolor="rgba(5,15,30,0.9)",
                bordercolor="rgba(56,189,248,0.1)",
                steps=[dict(range=[0,50],color="rgba(239,68,68,0.06)"),
                       dict(range=[50,75],color="rgba(245,158,11,0.06)"),
                       dict(range=[75,100],color="rgba(34,197,94,0.06)")],
                threshold=dict(line=dict(color=sc,width=3), thickness=0.75, value=score)),
            delta=dict(reference=75, increasing=dict(color="#22c55e"), decreasing=dict(color="#ef4444")),
            title=dict(text=f"<b>{slbl}</b>", font=dict(color=sc,size=13,family="Orbitron"))))
        fig_g.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#64748b"),
            margin=dict(l=20,r=20,t=20,b=20), height=280)
        st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar":False})
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;margin-top:8px">
          <div style="font-family:'Orbitron',monospace;font-size:9px;color:#1e6b8a;letter-spacing:2px">CURRENT BURN RATE</div>
          <div style="font-family:'Orbitron',monospace;font-size:30px;font-weight:700;color:#f59e0b;text-shadow:0 0 20px rgba(245,158,11,0.4);margin:8px 0">{fd['burn_rate_kgh']:,}</div>
          <div style="font-size:11px;color:#334d6b">kg / hour</div>
        </div>""", unsafe_allow_html=True)

    with f2:
        st.markdown('<div class="sec-head">FUEL BREAKDOWN</div>', unsafe_allow_html=True)
        base   = round(ac_data["burn_kgh"] * fd["flight_time_h"])
        ww_    = round(base * fd["wind_impact"]/100)
        as_    = round(base * fd["alt_saving"]/100)
        wp_p   = round(base * fd["weather_penalty_pct"]/100)
        fig_wf = go.Figure(go.Waterfall(orientation="v",
            measure=["absolute","relative","relative","relative","total"],
            x=["Base Fuel","Wind Effect","Alt Saving","Wx Penalty","Total"],
            y=[base, ww_, -as_, wp_p, 0],
            text=[f"{v:,}" for v in [base,ww_,-as_,wp_p,fd["total_fuel_kg"]]],
            textposition="outside", textfont=dict(color="#94a3b8",size=11),
            connector=dict(line=dict(color="rgba(56,189,248,0.2)",dash="dot")),
            increasing=dict(marker=dict(color="#ef4444")),
            decreasing=dict(marker=dict(color="#22c55e")),
            totals=dict(marker=dict(color="#38bdf8"))))
        fig_wf.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,15,30,0.6)",
            font=dict(color="#64748b",size=11), margin=dict(l=0,r=0,t=10,b=0),
            height=280, showlegend=False,
            xaxis=dict(showgrid=False,color="#1e3a5f"),
            yaxis=dict(showgrid=True,gridcolor="rgba(30,58,95,0.5)",color="#1e3a5f",title="kg"))
        st.plotly_chart(fig_wf, use_container_width=True, config={"displayModeBar":False})
        for nm, val, col_, bad in [
            ("Wind Impact",     abs(fd["wind_impact"]),        "#38bdf8", fd["wind_impact"]>0),
            ("Alt Efficiency",  fd["alt_saving"],              "#22c55e", False),
            ("Weather Penalty", fd["weather_penalty_pct"],     "#ef4444", True),
            ("Load Impact",     abs(fd["load_factor_pct"]-85), "#f59e0b", fd["load_factor_pct"]>85),
        ]:
            icon_ = "▲" if bad else "▼"
            st.markdown(f"""
            <div style="margin:6px 0">
              <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:3px">
                <span style="color:#64748b">{nm}</span>
                <span style="color:{col_};font-weight:600">{icon_} {val:.1f}%</span>
              </div>
              <div class="fuel-bar-bg"><div class="fuel-bar-fill" style="width:{min(val*5,100)}%;background:{col_}"></div></div>
            </div>""", unsafe_allow_html=True)

    with f3:
        st.markdown('<div class="sec-head">AI RECOMMENDATIONS</div>', unsafe_allow_html=True)
        recs = []
        if fd["wind_impact"]>3:           recs.append(("warning","🌬️ Headwind detected",   f"+{fd['wind_impact']:.1f}% burn. Step to better winds."))
        if fd["weather_penalty_pct"]>2:   recs.append(("danger", "⛈️ Weather penalty",     f"+{fd['weather_penalty_pct']:.1f}%. Route C avoids storms."))
        if fd["load_factor_pct"]>90:      recs.append(("warning","⚖️ High load factor",    "Full aircraft. Optimise CG for efficiency."))
        if cruise_alt<33000:              recs.append(("warning","📉 Suboptimal altitude",  "FL350+ saves 5-8% fuel."))
        if fd["efficiency_score"]>80:     recs.append(("ok",     "✅ Optimal conditions",  "AI confirms efficient routing."))
        recs.append(("info","🔁 Step climb profile",  f"FL{cruise_alt//1000:02d}0→FL{(cruise_alt+2000)//1000:02d}0 at midpoint."))
        recs.append(("info","⚡ Power setting",       "LRC mode recommended for current load."))
        for lvl, title, detail in recs[:6]:
            st.markdown(f'<div class="alert-{lvl}" style="margin:6px 0"><div style="font-weight:700;margin-bottom:3px">{title}</div><div style="font-size:11px;opacity:0.8">{detail}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sec-head">ENVIRONMENTAL IMPACT</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="glass-card">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;text-align:center">
            <div><div style="font-family:'Orbitron',monospace;font-size:20px;font-weight:700;color:#ef4444">{fd['co2_tonnes']}</div><div style="font-size:11px;color:#475569;margin-top:3px">tonnes CO₂</div></div>
            <div><div style="font-family:'Orbitron',monospace;font-size:20px;font-weight:700;color:#22c55e">{round(fd['co2_tonnes']*45):,}</div><div style="font-size:11px;color:#475569;margin-top:3px">trees to offset</div></div>
            <div><div style="font-family:'Orbitron',monospace;font-size:20px;font-weight:700;color:#38bdf8">{fd['fuel_per_pax_kg']}</div><div style="font-size:11px;color:#475569;margin-top:3px">kg / pax</div></div>
            <div><div style="font-family:'Orbitron',monospace;font-size:20px;font-weight:700;color:#fbbf24">{fd['total_fuel_kg']:,}</div><div style="font-size:11px;color:#475569;margin-top:3px">total kg</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-head">EFFICIENCY ALONG ROUTE</div>', unsafe_allow_html=True)
        eff_scores = []
        for w in wp_weather:
            e = 100
            ws_ = w["wind_speed"]; c_ = w["weather_code"]
            if ws_>60: e-=15
            elif ws_>40: e-=8
            elif ws_>25: e-=3
            if c_>=95: e-=20
            elif c_>=80: e-=10
            elif c_>=61: e-=5
            eff_scores.append(max(40,e))
        wp_labels = ["ORIG"]+[f"WP{i}" for i in range(1,len(wp_weather)-1)]+["DEST"]
        fig_eff = go.Figure(go.Scatter(x=wp_labels, y=eff_scores, mode="lines+markers",
            line=dict(color="#22c55e",width=2),
            marker=dict(color=["#22c55e" if v>=80 else "#f59e0b" if v>=60 else "#ef4444" for v in eff_scores],size=10),
            fill="tozeroy", fillcolor="rgba(34,197,94,0.07)"))
        fig_eff.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(5,15,30,0.6)",
            margin=dict(l=0,r=0,t=0,b=0), height=160, showlegend=False,
            xaxis=dict(showgrid=False,color="#1e3a5f",tickfont=dict(size=9)),
            yaxis=dict(range=[0,110],showgrid=True,gridcolor="rgba(30,58,95,0.5)",color="#1e3a5f"),
            font=dict(color="#64748b",size=11))
        st.plotly_chart(fig_eff, use_container_width=True, config={"displayModeBar":False})

# ╔═══════════════════════════════════════════════════════════════
#  TAB 3 — ROUTE OPTIMIZATION
# ╚═══════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f"""
    <div style="background:rgba(10,22,40,0.8);border:1px solid rgba(56,189,248,0.1);border-radius:12px;padding:16px 20px;margin-bottom:16px">
      <div style="font-family:'Orbitron',monospace;font-size:10px;color:#1e6b8a;letter-spacing:3px;margin-bottom:8px">AI ROUTE ANALYSIS · {now_utc.strftime('%d %b %Y %H:%M')} UTC</div>
      <div style="font-size:13px;color:#64748b">
        Analysing <span style="color:#38bdf8">{len(routes)}</span> routes from
        <span style="color:#38bdf8">{icao_orig}</span> to <span style="color:#a78bfa">{icao_dest}</span> ·
        AI scoring: <span style="color:#fbbf24">Weather 40% · Fuel 35% · Time 25%</span>
      </div>
    </div>""", unsafe_allow_html=True)

    rc1, rc2 = st.columns([3,2])

    with rc1:
        fig_rmap = go.Figure()
        sorted_routes_r = [r for r in routes if not r.get("is_best")] + [r for r in routes if r.get("is_best")]
        for r in sorted_routes_r:
            wpts = r["waypoints"]
            rlats = [p[0] for p in wpts]; rlons = [p[1] for p in wpts]
            is_best = r.get("is_best",False)
            fig_rmap.add_trace(go.Scattermapbox(lat=rlats, lon=rlons, mode="lines",
                line=dict(color=r["color"],width=5 if is_best else 2),
                opacity=1.0 if is_best else 0.5,
                name=f"{'★ ' if is_best else ''}{r['name']} ({r['ai_score']}pts)",
                hovertemplate=f"{r['name']}<br>Score: {r['ai_score']}<br>{r['dist_km']:,} km · {r['time_h']}h<extra></extra>"))
            mid = wpts[len(wpts)//2]
            fig_rmap.add_trace(go.Scattermapbox(lat=[mid[0]], lon=[mid[1]], mode="text",
                text=[f"{'★' if is_best else r['id']}"], textfont=dict(size=16 if is_best else 13,color=r["color"]),
                showlegend=False, hovertemplate=f"{r['name']}<extra></extra>"))
        fig_rmap.add_trace(go.Scattermapbox(lat=[orig_lat], lon=[orig_lon], mode="markers+text",
            marker=dict(size=14,color="#38bdf8"), text=[icao_orig], textposition="top right",
            showlegend=False, hovertemplate=f"{icao_orig}<extra></extra>"))
        fig_rmap.add_trace(go.Scattermapbox(lat=[dest_lat], lon=[dest_lon], mode="markers+text",
            marker=dict(size=14,color="#a78bfa"), text=[icao_dest], textposition="top right",
            showlegend=False, hovertemplate=f"{icao_dest}<extra></extra>"))
        fig_rmap.update_layout(
            mapbox=dict(style="carto-darkmatter",center=dict(lat=center_lat,lon=center_lon),zoom=auto_zoom),
            paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0,r=0,t=0,b=0), height=480,
            legend=dict(bgcolor="rgba(5,15,30,0.9)",bordercolor="rgba(56,189,248,0.2)",
                        borderwidth=1,font=dict(color="#64748b",size=11),x=0.01,y=0.99))
        st.plotly_chart(fig_rmap, use_container_width=True, config={"displayModeBar":True,"scrollZoom":True,"modeBarButtonsToRemove":["toImage","resetViewMapbox"]})

        st.markdown('<div class="sec-head">ROUTE SCORE COMPARISON</div>', unsafe_allow_html=True)
        categories_r = ["Weather","Fuel","Time","Safety","AI Score"]
        fig_radar = go.Figure()
        for r in routes:
            safety = max(0, 100 - r["storm_count"]*15 - r["avg_wind"]*0.5)
            hx = r["color"].lstrip("#")
            rr,gg,bb = int(hx[0:2],16),int(hx[2:4],16),int(hx[4:6],16)
            fill_rgba = f"rgba({rr},{gg},{bb},0.13)"
            fig_radar.add_trace(go.Scatterpolar(
                r=[r["wx_score"],r["fuel_score"],r["time_score"],safety,r["ai_score"]],
                theta=categories_r, fill="toself", fillcolor=fill_rgba,
                line=dict(color=r["color"],width=2 if r.get("is_best") else 1),
                opacity=0.9 if r.get("is_best") else 0.5, name=r["name"]))
        fig_radar.update_layout(
            polar=dict(bgcolor="rgba(5,15,30,0.8)",
                radialaxis=dict(visible=True,range=[0,100],color="#1e3a5f",gridcolor="rgba(30,58,95,0.5)"),
                angularaxis=dict(color="#64748b",gridcolor="rgba(30,58,95,0.3)")),
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#64748b",size=11),
            margin=dict(l=40,r=40,t=20,b=20), height=300,
            legend=dict(bgcolor="rgba(5,15,30,0.8)",bordercolor="rgba(56,189,248,0.1)",font=dict(color="#64748b",size=11)))
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar":False})

    with rc2:
        st.markdown('<div class="sec-head">ROUTE DETAILS</div>', unsafe_allow_html=True)
        for r in routes:
            is_best   = r.get("is_best",False)
            card_cls  = "route-card best" if is_best else "route-card"
            eta_h2    = int(r["time_h"]); eta_m2 = int((r["time_h"]-eta_h2)*60)
            wx_color  = "#22c55e" if r["wx_score"]>=80   else "#f59e0b" if r["wx_score"]>=60  else "#ef4444"
            fc_color  = "#22c55e" if r["fuel_score"]>=80  else "#f59e0b" if r["fuel_score"]>=60 else "#ef4444"
            tc_color  = "#22c55e" if r["time_score"]>=80  else "#f59e0b" if r["time_score"]>=60 else "#ef4444"
            ai_color  = "#22c55e" if r["ai_score"]>=80   else "#f59e0b" if r["ai_score"]>=70  else "#ef4444"
            st.markdown(f"""
            <div class="{card_cls}" style="border-top:3px solid {r['color']}">
              <div class="route-name" style="color:{r['color']}">{r['id']}. {r['name']}</div>
              <div style="font-size:11px;color:#475569;margin-bottom:10px">{r['desc']}</div>
              <div class="route-stats">
                <div class="route-stat"><div class="route-stat-label">Distance</div><div class="route-stat-val" style="color:#94a3b8">{r['dist_km']:,}<span style="font-size:9px"> km</span></div></div>
                <div class="route-stat"><div class="route-stat-label">ETA</div><div class="route-stat-val" style="color:#94a3b8">{eta_h2}h{eta_m2:02d}m</div></div>
                <div class="route-stat"><div class="route-stat-label">Fuel</div><div class="route-stat-val" style="color:#f59e0b">{r['fuel_kg']//1000}K<span style="font-size:9px"> kg</span></div></div>
                <div class="route-stat"><div class="route-stat-label">AI Score</div><div class="route-stat-val" style="color:{ai_color}">{r['ai_score']}</div></div>
              </div>
              <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:10px">
                <div style="text-align:center"><div style="font-size:9px;color:#334d6b;letter-spacing:1px">WEATHER</div><div style="font-family:'Orbitron',monospace;font-size:16px;font-weight:700;color:{wx_color}">{r['wx_score']}</div></div>
                <div style="text-align:center"><div style="font-size:9px;color:#334d6b;letter-spacing:1px">FUEL</div><div style="font-family:'Orbitron',monospace;font-size:16px;font-weight:700;color:{fc_color}">{r['fuel_score']}</div></div>
                <div style="text-align:center"><div style="font-size:9px;color:#334d6b;letter-spacing:1px">TIME</div><div style="font-family:'Orbitron',monospace;font-size:16px;font-weight:700;color:{tc_color}">{r['time_score']}</div></div>
              </div>
              {"<div style='margin-top:10px;padding:6px 10px;background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);border-radius:6px;font-family:Orbitron,monospace;font-size:9px;color:#22c55e;letter-spacing:2px;text-align:center'>★ AI RECOMMENDED ROUTE</div>" if is_best else ""}
            </div>""", unsafe_allow_html=True)

        # ─ FIX: plain dataframe, no background_gradient (avoids matplotlib dependency) ─
        st.markdown('<div class="sec-head">QUICK COMPARISON</div>', unsafe_allow_html=True)
        df_routes = pd.DataFrame([{
            "Route":    r["name"],
            "Dist km":  r["dist_km"],
            "Time":     f"{int(r['time_h'])}h{int((r['time_h']%1)*60):02d}m",
            "Fuel kg":  r["fuel_kg"],
            "Wx":       r["wx_score"],
            "AI ★":    r["ai_score"],
        } for r in routes])
        st.dataframe(df_routes, use_container_width=True, hide_index=True)

# ─ FOOTER ─────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:16px 0 8px;font-family:'Orbitron',monospace;font-size:9px;color:#0f2744;letter-spacing:3px;border-top:1px solid rgba(56,189,248,0.06);margin-top:16px">
  AERONAV PRO · FLIGHT INTELLIGENCE · {now_utc.strftime('%d %b %Y %H:%M:%S')} UTC · DATA: OPEN-METEO / NOAA AWC
</div>""", unsafe_allow_html=True)
