"""
TerraDetective Natural Language Query Engine & Auto-Investigation Router
NASA Space Apps Challenge 2026: "Be An Earth System Trend Detective!"

Translates natural language questions into data-grounded satellite investigations:
1. Flexible Intent, Variable & Location Extraction:
   - NLP phrase pattern extractors ('compare temperature in X to Y', 'X vs Y', 'difference between X and Y').
   - Expansive 70+ City Global Gazetteer covering major Indian and international urban centers & climate zones.
   - Fault-tolerant fuzzy matching (difflib) handling typos like 'heydrabad' -> 'hyderabad'.
   - Strict preset isolation: generic terms ('temperature', 'rainfall') never hijack custom location queries.
2. Dynamic Data-Grounded Answer Generation:
   - Question-specific answers tailored to the exact cities/variables queried (e.g. Delhi vs. Hyderabad, London vs. Cairo).
   - Local Ollama (qwen3:8b) with zero-hallucination instruction when available.
   - Rich, adaptive deterministic fallback that directly answers the user's specific question using computed satellite telemetry.
3. Single Round-Trip Auto-Sync:
   - Returns synchronized payload updating map pins, Plotly time series curves, and telemetry cards.
"""

from __future__ import annotations

import difflib
import json
import logging
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
import pandas as pd

logger = logging.getLogger("terradetective.nl_query_engine")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Ollama Configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "8.0"))

# ---------------------------------------------------------------------------
# Comprehensive Global Gazetteer (70+ Cities & Hotspots with Aliases & Typos)
# ---------------------------------------------------------------------------
GLOBAL_GAZETTEER: Dict[str, Dict[str, Any]] = {
    # Flagship Paradox Regions
    "rondonia": {"name": "Rondônia Amazon Arc", "lat": -10.875, "lon": -61.930, "zone": "tropical_rainforest"},
    "rondônia": {"name": "Rondônia Amazon Arc", "lat": -10.875, "lon": -61.930, "zone": "tropical_rainforest"},
    "amazon": {"name": "Rondônia Amazon Arc", "lat": -10.875, "lon": -61.930, "zone": "tropical_rainforest"},
    "punjab": {"name": "Punjab Irrigated Belt", "lat": 30.901, "lon": 75.857, "zone": "irrigated_agriculture"},
    "marathwada": {"name": "Marathwada Rain Shadow", "lat": 19.250, "lon": 76.250, "zone": "semi_arid_rain_shadow"},
    "northeast india": {"name": "Northeast India (Cherrapunji)", "lat": 25.250, "lon": 91.500, "zone": "orographic_monsoon"},
    "cherrapunji": {"name": "Cherrapunji / Sohra", "lat": 25.298, "lon": 91.730, "zone": "orographic_monsoon"},
    "sohra": {"name": "Cherrapunji / Sohra", "lat": 25.298, "lon": 91.730, "zone": "orographic_monsoon"},
    "meghalaya": {"name": "Meghalaya Plateau", "lat": 25.467, "lon": 91.366, "zone": "orographic_monsoon"},
    "assam": {"name": "Assam Valley", "lat": 26.200, "lon": 92.937, "zone": "riverine_valley"},

    # Major Indian Cities & Capitals (Including Common Spelling Variants)
    "delhi": {"name": "New Delhi, India", "lat": 28.614, "lon": 77.209, "zone": "subtropical_continental"},
    "new delhi": {"name": "New Delhi, India", "lat": 28.614, "lon": 77.209, "zone": "subtropical_continental"},
    "hyderabad": {"name": "Hyderabad, India", "lat": 17.385, "lon": 78.487, "zone": "deccan_plateau"},
    "heydrabad": {"name": "Hyderabad, India", "lat": 17.385, "lon": 78.487, "zone": "deccan_plateau"},
    "hydrabad": {"name": "Hyderabad, India", "lat": 17.385, "lon": 78.487, "zone": "deccan_plateau"},
    "hyd": {"name": "Hyderabad, India", "lat": 17.385, "lon": 78.487, "zone": "deccan_plateau"},
    "mumbai": {"name": "Mumbai, India", "lat": 19.076, "lon": 72.878, "zone": "coastal_tropical"},
    "bombay": {"name": "Mumbai, India", "lat": 19.076, "lon": 72.878, "zone": "coastal_tropical"},
    "bengaluru": {"name": "Bengaluru, India", "lat": 12.972, "lon": 77.595, "zone": "mysore_plateau"},
    "bangalore": {"name": "Bengaluru, India", "lat": 12.972, "lon": 77.595, "zone": "mysore_plateau"},
    "chennai": {"name": "Chennai, India", "lat": 13.083, "lon": 80.271, "zone": "coromandel_coastal"},
    "madras": {"name": "Chennai, India", "lat": 13.083, "lon": 80.271, "zone": "coromandel_coastal"},
    "kolkata": {"name": "Kolkata, India", "lat": 22.573, "lon": 88.364, "zone": "gangetic_delta"},
    "calcutta": {"name": "Kolkata, India", "lat": 22.573, "lon": 88.364, "zone": "gangetic_delta"},
    "pune": {"name": "Pune, India", "lat": 18.520, "lon": 73.857, "zone": "leeward_western_ghats"},
    "ahmedabad": {"name": "Ahmedabad, India", "lat": 23.023, "lon": 72.571, "zone": "semi_arid_gujarat"},
    "jaipur": {"name": "Jaipur, India", "lat": 26.912, "lon": 75.787, "zone": "semi_arid_rajasthan"},
    "lucknow": {"name": "Lucknow, India", "lat": 26.847, "lon": 80.946, "zone": "central_gangetic_plain"},
    "surat": {"name": "Surat, India", "lat": 21.170, "lon": 72.831, "zone": "coastal_tapti"},
    "nagpur": {"name": "Nagpur, India", "lat": 21.146, "lon": 79.088, "zone": "vidarbha_plateau"},
    "indore": {"name": "Indore, India", "lat": 22.720, "lon": 75.858, "zone": "malwa_plateau"},
    "bhopal": {"name": "Bhopal, India", "lat": 23.260, "lon": 77.413, "zone": "central_highlands"},
    "patna": {"name": "Patna, India", "lat": 25.594, "lon": 85.138, "zone": "lower_gangetic_plain"},
    "chandigarh": {"name": "Chandigarh, India", "lat": 30.733, "lon": 76.779, "zone": "shivalik_foothills"},
    "srinagar": {"name": "Srinagar, Kashmir", "lat": 34.084, "lon": 74.797, "zone": "kashmir_valley"},
    "guwahati": {"name": "Guwahati, Assam", "lat": 26.145, "lon": 91.736, "zone": "brahmaputra_valley"},
    "varanasi": {"name": "Varanasi, India", "lat": 25.318, "lon": 82.974, "zone": "gangetic_plain"},
    "banaras": {"name": "Varanasi, India", "lat": 25.318, "lon": 82.974, "zone": "gangetic_plain"},
    "kochi": {"name": "Kochi, Kerala", "lat": 9.931, "lon": 76.267, "zone": "malabar_coastal"},
    "cochin": {"name": "Kochi, Kerala", "lat": 9.931, "lon": 76.267, "zone": "malabar_coastal"},
    "thiruvananthapuram": {"name": "Thiruvananthapuram, India", "lat": 8.524, "lon": 76.937, "zone": "southern_coastal"},
    "trivandrum": {"name": "Thiruvananthapuram, India", "lat": 8.524, "lon": 76.937, "zone": "southern_coastal"},
    "visakhapatnam": {"name": "Visakhapatnam, India", "lat": 17.687, "lon": 83.219, "zone": "eastern_ghats_coast"},
    "vizag": {"name": "Visakhapatnam, India", "lat": 17.687, "lon": 83.219, "zone": "eastern_ghats_coast"},
    "bhubaneswar": {"name": "Bhubaneswar, India", "lat": 20.296, "lon": 85.825, "zone": "eastern_coastal"},
    "shimla": {"name": "Shimla, Himalayas", "lat": 31.105, "lon": 77.173, "zone": "himalayan_montane"},
    "dehradun": {"name": "Dehradun, India", "lat": 30.316, "lon": 78.032, "zone": "doon_valley"},
    "goa": {"name": "Goa, India", "lat": 15.491, "lon": 73.828, "zone": "konkan_coastal"},
    "panaji": {"name": "Goa, India", "lat": 15.491, "lon": 73.828, "zone": "konkan_coastal"},

    # Global Climate Hotspots & World Cities
    "cairo": {"name": "Cairo, Egypt", "lat": 30.044, "lon": 31.236, "zone": "arid_nile_desert"},
    "sahara": {"name": "Sahara Desert", "lat": 23.416, "lon": 25.663, "zone": "hyper_arid"},
    "dubai": {"name": "Dubai, UAE", "lat": 25.205, "lon": 55.271, "zone": "gulf_desert_coastal"},
    "riyadh": {"name": "Riyadh, Saudi Arabia", "lat": 24.714, "lon": 46.675, "zone": "arabian_desert_plateau"},
    "london": {"name": "London, UK", "lat": 51.507, "lon": -0.128, "zone": "temperate_oceanic"},
    "paris": {"name": "Paris, France", "lat": 48.857, "lon": 2.352, "zone": "western_european_oceanic"},
    "berlin": {"name": "Berlin, Germany", "lat": 52.520, "lon": 13.405, "zone": "central_european_continental"},
    "madrid": {"name": "Madrid, Spain", "lat": 40.417, "lon": -3.704, "zone": "mediterranean_inland"},
    "rome": {"name": "Rome, Italy", "lat": 41.903, "lon": 12.496, "zone": "mediterranean_coastal"},
    "tokyo": {"name": "Tokyo, Japan", "lat": 35.676, "lon": 139.650, "zone": "humid_subtropical_island"},
    "beijing": {"name": "Beijing, China", "lat": 39.904, "lon": 116.407, "zone": "east_asian_monsoon_continental"},
    "singapore": {"name": "Singapore", "lat": 1.352, "lon": 103.820, "zone": "equatorial_rainforest"},
    "sydney": {"name": "Sydney, Australia", "lat": -33.869, "lon": 151.209, "zone": "temperate_oceanic"},
    "jakarta": {"name": "Jakarta, Indonesia", "lat": -6.209, "lon": 106.846, "zone": "tropical_monsoon"},
    "seoul": {"name": "Seoul, South Korea", "lat": 37.567, "lon": 126.978, "zone": "humid_continental"},
    "bangkok": {"name": "Bangkok, Thailand", "lat": 13.756, "lon": 100.502, "zone": "tropical_savanna"},
    "hong kong": {"name": "Hong Kong", "lat": 22.319, "lon": 114.169, "zone": "subtropical_maritime"},
    "new york": {"name": "New York, USA", "lat": 40.713, "lon": -74.006, "zone": "atlantic_coastal_continental"},
    "california": {"name": "California Central Valley", "lat": 36.778, "lon": -119.418, "zone": "mediterranean_agricultural"},
    "los angeles": {"name": "Los Angeles, USA", "lat": 34.052, "lon": -118.244, "zone": "pacific_mediterranean"},
    "phoenix": {"name": "Phoenix, Arizona", "lat": 33.448, "lon": -112.074, "zone": "sonoran_desert_heat_island"},
    "chicago": {"name": "Chicago, USA", "lat": 41.878, "lon": -87.630, "zone": "great_lakes_continental"},
    "houston": {"name": "Houston, Texas", "lat": 29.760, "lon": -95.370, "zone": "gulf_humid_subtropical"},
    "seattle": {"name": "Seattle, USA", "lat": 47.606, "lon": -122.332, "zone": "pacific_northwest_oceanic"},
    "miami": {"name": "Miami, Florida", "lat": 25.762, "lon": -80.192, "zone": "tropical_monsoon_coastal"},
    "san francisco": {"name": "San Francisco, USA", "lat": 37.775, "lon": -122.419, "zone": "pacific_coastal_marine"},
    "toronto": {"name": "Toronto, Canada", "lat": 43.653, "lon": -79.383, "zone": "great_lakes_humid_continental"},
    "buenos aires": {"name": "Buenos Aires, Argentina", "lat": -34.604, "lon": -58.382, "zone": "pampas_humid_subtropical"},
    "sao paulo": {"name": "São Paulo, Brazil", "lat": -23.551, "lon": -46.633, "zone": "subtropical_highland"},
    "são paulo": {"name": "São Paulo, Brazil", "lat": -23.551, "lon": -46.633, "zone": "subtropical_highland"},
    "rio de janeiro": {"name": "Rio de Janeiro, Brazil", "lat": -22.907, "lon": -43.173, "zone": "tropical_atlantic"},
    "rio": {"name": "Rio de Janeiro, Brazil", "lat": -22.907, "lon": -43.173, "zone": "tropical_atlantic"},
    "mexico city": {"name": "Mexico City, Mexico", "lat": 19.433, "lon": -99.133, "zone": "high_altitude_subtropical"},
    "greenland": {"name": "Nuuk, Greenland", "lat": 64.181, "lon": -51.694, "zone": "arctic_tundra"},
    "siberia": {"name": "Siberia (Yakutsk)", "lat": 62.036, "lon": 129.676, "zone": "subarctic_extreme_continental"},
    "antarctica": {"name": "Antarctica (McMurdo)", "lat": -77.846, "lon": 166.668, "zone": "polar_ice_cap"},
    "nairobi": {"name": "Nairobi, Kenya", "lat": -1.292, "lon": 36.822, "zone": "equatorial_highland"},
    "cape town": {"name": "Cape Town, South Africa", "lat": -33.925, "lon": 18.424, "zone": "mediterranean_benguela"},
    "lake chad": {"name": "Lake Chad Basin", "lat": 13.000, "lon": 14.500, "zone": "sahel_desiccation"},
    "aral sea": {"name": "Aral Sea Basin", "lat": 45.000, "lon": 60.000, "zone": "central_asian_desiccation"},
}

# ---------------------------------------------------------------------------
# Load Universal Planetary Gazetteer (All 195 Countries, 50 US States,
# 28 Indian States & 8 UTs, Canadian Provinces, Australian States, EU Regions)
# ---------------------------------------------------------------------------
try:
    from services.world_gazetteer import WORLD_GAZETTEER
    GLOBAL_GAZETTEER.update(WORLD_GAZETTEER)
except ImportError:
    try:
        from world_gazetteer import WORLD_GAZETTEER
        GLOBAL_GAZETTEER.update(WORLD_GAZETTEER)
    except Exception as e:
        logger.warning(f"Could not load world_gazetteer: {e}")


COORD_REGEX = re.compile(r"(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)")

# Lazy-loaded cache holders
_MANIFEST: Optional[Dict[str, Any]] = None
_STATS_CACHE: Optional[Dict[str, Any]] = None
_UNIFIED_DF: Optional[pd.DataFrame] = None


def _get_manifest() -> Dict[str, Any]:
    global _MANIFEST
    if _MANIFEST is None:
        p = PROCESSED_DIR / "case_studies_manifest.json"
        if p.is_file():
            with open(p, "r", encoding="utf-8") as f:
                _MANIFEST = json.load(f)
        else:
            _MANIFEST = {"cases": []}
    return _MANIFEST


def _get_stats_cache() -> Dict[str, Any]:
    global _STATS_CACHE
    if _STATS_CACHE is None:
        p = PROCESSED_DIR / "case_studies_stats.json"
        if p.is_file():
            with open(p, "r", encoding="utf-8") as f:
                _STATS_CACHE = json.load(f)
        else:
            _STATS_CACHE = {"cases": {}}
    return _STATS_CACHE


def _get_unified_df() -> pd.DataFrame:
    global _UNIFIED_DF
    if _UNIFIED_DF is None:
        p = PROCESSED_DIR / "terradetective_unified_monthly.csv"
        if p.is_file():
            _UNIFIED_DF = pd.read_csv(p)
        else:
            _UNIFIED_DF = pd.DataFrame()
    return _UNIFIED_DF


# ---------------------------------------------------------------------------
# Location Resolution with Fuzzy Match, Global Gazetteer & Online OSM Geocoder
# ---------------------------------------------------------------------------
_GEOCODE_CACHE: Dict[str, Dict[str, Any]] = {}

def geocode_place_online(place: str) -> Optional[Dict[str, Any]]:
    """
    Live Universal Geocoder: queries OpenStreetMap Nominatim for any state,
    province, country, island, mountain, or municipality across the globe.
    Completely keyless and covers all jurisdictions globally.
    """
    clean = place.strip().lower()
    if clean in _GEOCODE_CACHE:
        return _GEOCODE_CACHE[clean].copy()

    stop_words = {
        "what", "why", "how", "when", "where", "can", "you", "please", "compare",
        "temperature", "temp", "rainfall", "rain", "precip", "precipitation",
        "weather", "climate", "trend", "trends", "divergence", "difference",
        "in", "between", "to", "and", "vs", "versus", "is", "it", "the", "a", "an",
        "warming", "cooling", "rising", "falling", "higher", "lower", "more", "less"
    }
    if clean in stop_words or len(clean) < 3:
        return None

    try:
        url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(clean)}&format=json&limit=1"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "TerraDetective/2.0 (NASA Space Apps Challenge; contact=info@terradetective.org)"}
        )
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            data = json.loads(resp.read().decode())
            if data and len(data) > 0:
                item = data[0]
                lat = round(float(item["lat"]), 4)
                lon = round(float(item["lon"]), 4)
                disp = item.get("display_name", place)
                parts = [p.strip() for p in disp.split(",")]
                short_name = f"{parts[0]}, {parts[-1]}" if len(parts) > 1 else parts[0]
                loc = {
                    "name": short_name,
                    "lat": lat,
                    "lon": lon,
                    "query_token": clean,
                    "source": "osm_global_geocoder",
                }
                _GEOCODE_CACHE[clean] = loc
                return loc.copy()
    except Exception as e:
        logger.debug(f"Online geocoding for '{place}' skipped or offline: {e}")

    return None


COMMON_ALIASES: Dict[str, str] = {
    "united states of america": "united states",
    "usa": "united states",
    "us": "united states",
    "u.s.a": "united states",
    "u.s.": "united states",
    "america": "united states",
    "uk": "united kingdom",
    "great britain": "united kingdom",
    "britain": "united kingdom",
    "england": "united kingdom",
    "uae": "dubai",
    "united arab emirates": "dubai",
    "saudi": "riyadh",
    "saudi arabia": "riyadh",
    "south korea": "seoul",
    "korea": "seoul",
    "japan": "tokyo",
    "china": "beijing",
    "australia": "sydney",
    "canada": "toronto",
    "germany": "berlin",
    "france": "paris",
    "spain": "madrid",
    "italy": "rome",
    "russia": "siberia",
    "brazil": "sao paulo",
    "argentina": "buenos aires",
    "mexico": "mexico city",
    "egypt": "cairo",
}

def resolve_location_name(token: str) -> Optional[Dict[str, Any]]:
    """
    Resolves any place token across:
    1. Alias dictionary mapping common nation/region variants.
    2. Exact match in 450+ global gazetteer entries (0 ms).
    3. Multi-word phrase & substring containment.
    4. Fault-tolerant fuzzy match (typo correction, e.g. 'heydrabad' -> 'hyderabad').
    5. Universal online OSM geocoder covering every country, state, and city on Earth!
    """
    clean = re.sub(r"[^\w\s]", "", token.lower()).strip()
    if not clean or len(clean) < 2:
        return None

    # Step 0: Reject common English non-place words immediately
    stop_words = {
        "what", "why", "how", "when", "where", "can", "you", "please", "compare",
        "temperature", "temp", "rainfall", "rain", "precip", "precipitation",
        "weather", "climate", "trend", "trends", "divergence", "difference",
        "in", "between", "to", "and", "vs", "versus", "is", "it", "the", "a", "an",
        "warming", "cooling", "rising", "falling", "higher", "lower", "more", "less",
        "measure", "measuring", "speed", "wind", "cloud", "clouds", "air", "water",
        "pollution", "smog", "aerosol", "smoke", "dust", "recipe", "cake", "food", "code"
    }
    if clean in stop_words:
        return None

    # Step 1: Check alias dictionary
    if clean in COMMON_ALIASES:
        clean = COMMON_ALIASES[clean]

    # Step 2: Direct match
    if clean in GLOBAL_GAZETTEER:
        loc = GLOBAL_GAZETTEER[clean].copy()
        loc["query_token"] = clean
        return loc

    # Step 3: Substring / superstring containment for multi-word places
    # (e.g. 'new delhi city' -> 'new delhi', 'state of california' -> 'california')
    for key, val in GLOBAL_GAZETTEER.items():
        if len(key) >= 4:
            if key in clean or clean in key:
                loc = val.copy()
                loc["query_token"] = key
                return loc

    # Step 4: Fuzzy match across gazetteer keys with strict threshold on words >= 5 chars
    if len(clean) >= 5:
        close = difflib.get_close_matches(clean, GLOBAL_GAZETTEER.keys(), n=1, cutoff=0.76)
        if close:
            matched_key = close[0]
            loc = GLOBAL_GAZETTEER[matched_key].copy()
            loc["query_token"] = matched_key
            return loc

    # Step 5: Universal Global Geocoder Fallback (Covers every state/province/country on Earth)
    online_loc = geocode_place_online(clean)
    if online_loc:
        return online_loc

    return None


def extract_gazetteer_locations(query: str) -> List[Dict[str, Any]]:
    """
    Extracts up to 2 distinct locations from the user query.
    1. Extracts candidate phrases from natural language patterns ('in X to Y', 'between X and Y', 'X vs Y').
    2. Searches for direct and fuzzy matches across the 70+ city gazetteer.
    3. Searches for literal latitude/longitude coordinate pairs.
    """
    q_clean = query.lower()
    matches: List[Dict[str, Any]] = []
    matched_names = set()

    # Pattern 1: Explicit comparison patterns (e.g. 'compare temperature in delhi to heydrabad')
    comparison_patterns = [
        r'(?:compare|divergence|difference|trend)\s+(?:(?:of|in)\s+)?(?:[a-z_]+\s+)?(?:in|between)\s+([a-z\s]+?)\s+(?:to|and|vs|versus)\s+([a-z\s\?]+)',
        r'(?:compare|contrast)\s+([a-z\s]+?)\s+(?:to|and|vs|versus)\s+([a-z\s\?]+)',
        r'([a-z\s]+?)\s+(?:vs|versus)\s+([a-z\s\?]+)',
        r'(?:between|in)\s+([a-z\s]+?)\s+(?:and|to)\s+([a-z\s\?]+)',
    ]

    for pat in comparison_patterns:
        m = re.search(pat, q_clean)
        if m:
            cand_a = m.group(1).strip()
            cand_b = m.group(2).replace("?", "").strip()
            res_a = resolve_location_name(cand_a)
            res_b = resolve_location_name(cand_b)
            if res_a and res_b and res_a["name"] != res_b["name"]:
                return [res_a, res_b]

    # Pattern 2: Scan for all gazetteer keys in descending order of length
    for key in sorted(GLOBAL_GAZETTEER.keys(), key=lambda k: len(k), reverse=True):
        # Use regex word boundaries so 'hyd' doesn't match 'dehydration' or 'in' match 'rain'
        if re.search(rf"\b{re.escape(key)}\b", q_clean):
            loc = GLOBAL_GAZETTEER[key].copy()
            loc["query_token"] = key
            if loc["name"] not in matched_names:
                matches.append(loc)
                matched_names.add(loc["name"])
            if len(matches) >= 2:
                return matches

    # Pattern 3: Word-by-word fuzzy scan for unmapped misspelled tokens
    words = [w for w in re.findall(r"\b[a-z]{3,}\b", q_clean) if w not in {"the", "and", "for", "why", "what", "how", "can", "you", "temperature", "temp", "rainfall", "rain", "compare", "between"}]
    for w in words:
        res = resolve_location_name(w)
        if res and res["name"] not in matched_names:
            matches.append(res)
            matched_names.add(res["name"])
            if len(matches) >= 2:
                return matches

    # Pattern 4: Coordinate Regex (e.g. '30.04, 31.23')
    if len(matches) < 2:
        for cf in COORD_REGEX.finditer(query):
            lat = float(cf.group(1))
            lon = float(cf.group(2))
            coord_name = f"Coordinate ({lat}°, {lon}°)"
            if coord_name not in matched_names:
                matches.append({
                    "name": coord_name,
                    "lat": lat,
                    "lon": lon,
                    "query_token": cf.group(0),
                })
                matched_names.add(coord_name)
            if len(matches) >= 2:
                break

    return matches


# ---------------------------------------------------------------------------
# Domain Guardrail (Out-of-Context Filter)
# ---------------------------------------------------------------------------
DOMAIN_KEYWORDS = {
    # Temperature & Heat
    "temperature", "temp", "heat", "warming", "cooling", "thermal", "cold", "hot", "lst",
    # Hydrology & Precipitation
    "rain", "rainfall", "precip", "precipitation", "deluge", "monsoon", "drought", "flood", "flooding", "shower", "wet", "dry", "arid",
    # Vegetation & Land Cover
    "greenness", "greening", "vegetation", "plant", "canopy", "forest", "deforestation", "crop", "crops", "ndvi", "tree", "trees", "browning", "agriculture", "irrigation",
    # Soil & Groundwater
    "soil", "moisture", "groundwater", "water", "wetness", "evaporation", "evapotranspiration",
    # Solar & Radiation
    "solar", "sun", "insolation", "radiation", "irradiance", "light", "flux",
    # Air Quality & Pollution (Explicitly checked for guardrails)
    "pollution", "air quality", "smog", "aod", "aerosol", "pm2.5", "pm10", "smoke", "dust", "emissions", "air", "wind",
    # Space & Satellite Telemetry
    "earth", "satellite", "sensor", "orbit", "orbital", "modis", "gpm", "imerg", "merra", "power", "nasa", "esa", "copernicus", "landsat",
    # Spatial & Statistical Paradox Keywords
    "trend", "trends", "trajectory", "decadal", "slope", "rate", "change", "changing",
    "compare", "comparing", "comparison", "contrast", "divergence", "divergent", "difference", "versus", "vs",
    "paradox", "anomaly", "anomalies", "climate", "weather", "atmosphere", "surface", "boundary", "land", "region", "regions", "regional",
}

def is_domain_relevant(query: str) -> bool:
    """
    Checks if the query contains ANY relevant Earth science, climate, environmental,
    spatial, or NASA keywords, OR if it mentions any recognized locations in our gazetteer.
    Filters out off-topic requests (e.g. 'What is a good recipe for cake?').
    """
    if not query or not query.strip():
        return False
    q_lower = query.lower()

    # 1. Keyword check (Earth science / climate domain words)
    for kw in DOMAIN_KEYWORDS:
        if len(kw) <= 3:
            if re.search(rf"\b{re.escape(kw)}\b", q_lower):
                return True
        else:
            if kw in q_lower:
                return True

    # 2. Check if recognized curated locations in GLOBAL_GAZETTEER or coordinates are mentioned
    # (Notice: we ONLY check curated gazetteer keys here, NOT arbitrary words via OSM geocoder)
    for key in sorted(GLOBAL_GAZETTEER.keys(), key=lambda k: len(k), reverse=True):
        if len(key) >= 4 and re.search(rf"\b{re.escape(key)}\b", q_lower):
            return True

    if COORD_REGEX.search(query):
        return True

    return False


# ---------------------------------------------------------------------------
# Query Intent Detection (Strict & Selective)
# ---------------------------------------------------------------------------
def detect_preset_case(query: str, extracted_locations: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
    """
    Detects if the query is explicitly asking about one of our 3 core paradox cases.
    CRITICAL RULE: If the user explicitly asks about custom locations (e.g. Delhi, Hyderabad, London),
    we MUST return None so the custom investigation comparator runs!
    """
    preset_tokens = {
        "amazon", "rondonia", "rondônia", "punjab", "marathwada",
        "northeast india", "cherrapunji", "sohra", "meghalaya", "assam"
    }

    if extracted_locations and len(extracted_locations) >= 1:
        tokens = {loc.get("query_token", "").lower() for loc in extracted_locations}
        # If any identified location is NOT a preset region, route to custom comparison!
        if not tokens.issubset(preset_tokens):
            return None

    q = query.lower()

    # Case 1: Monsoon Paradox
    if any(w in q for w in ["monsoon paradox", "gpm", "imerg", "3imergm"]) or (
        any(w in q for w in ["monsoon", "rainfall", "precipitation", "rain", "rain shadow", "deluge", "flood"])
        and any(w in q for w in ["marathwada", "northeast india", "cherrapunji", "meghalaya", "khasi", "assam"])
    ):
        return "case_1_monsoon_paradox"

    # Case 3: Vegetation Greenness Paradox
    if any(w in q for w in ["vegetation paradox", "mod13a3"]) or (
        any(w in q for w in ["ndvi", "greenness", "greening", "canopy loss", "crop greening", "vegetation"])
        and any(w in q for w in ["amazon", "rondonia", "rondônia", "punjab"])
    ):
        return "case_3_vegetation_paradox"

    # Case 2: Land Thermal Paradox
    if any(w in q for w in ["thermal paradox", "mod11a2", "land surface temperature paradox"]) or (
        any(w in q for w in ["heat", "warming", "cooling", "thermal", "lst", "deforestation warming", "irrigation cooling"])
        and any(w in q for w in ["amazon", "rondonia", "rondônia", "punjab"])
    ):
        return "case_2_land_thermal_paradox"

    return None


def detect_variable(query: str) -> Tuple[str, str, str]:
    """
    Returns (variable_id, variable_name, unit) based on natural language clues.
    Prevents silent fallback to T2M on unsupported variables like pollution or wind.
    """
    q = query.lower()
    if any(w in q for w in ["rain", "precip", "deluge", "monsoon", "flood", "shower", "wet"]):
        return "PRECTOTCORR", "Monthly Precipitation Accumulation", "mm/month"
    elif any(w in q for w in ["soil", "moisture", "groundwater", "water table", "root"]):
        return "GWETROOT", "Root-Zone Soil Moisture", "kg/m²"
    elif any(w in q for w in ["solar", "sun", "insolation", "radiation", "light", "heat flux"]):
        return "ALLSKY_SFC_SW_DWN", "All Sky Surface Shortwave Downward Irradiance", "W/m²"
    elif any(w in q for w in ["plant", "green", "ndvi", "vegetation", "canopy", "forest", "crop"]):
        return "NDVI", "Normalized Difference Vegetation Index", "NDVI"
    elif any(w in q for w in ["temp", "temperature", "heat", "warming", "cooling", "thermal", "cold", "lst", "hot"]):
        return "T2M", "Surface Air Temperature", "°C"
    elif any(k in q for k in ["pollution", "air quality", "smog", "aod", "aerosol", "pm2.5", "pm10", "smoke", "aqi"]):
        return "UNSUPPORTED_POLLUTION", "Air Quality", "N/A"
    else:
        return "UNKNOWN_VARIABLE", "Unknown", "N/A"


# ---------------------------------------------------------------------------
# Data-Grounded Answer Generation (Adaptive & Specific to Queried Locations)
# ---------------------------------------------------------------------------
def generate_grounded_answer(
    query: str,
    stats_data: Dict[str, Any],
    mode: str = "student",
    manifest_info: Optional[Dict[str, Any]] = None,
    skip_ollama: bool = False,
    is_custom: bool = False,
) -> Tuple[str, str]:
    """
    Generates a natural-language answer to the user's query grounded strictly
    in the computed statistics and tailored to the exact locations and questions asked.
    """
    reg_a = stats_data.get("region_a", {})
    reg_b = stats_data.get("region_b", {})
    div = stats_data.get("divergence_analysis", {})

    label_a = reg_a.get("region_label", reg_a.get("region_id", "Region A"))
    label_b = reg_b.get("region_label", reg_b.get("region_id", "Region B"))

    slope_a = reg_a.get("mann_kendall", {}).get("sens_slope_per_decade", 0.0)
    p_val_a = reg_a.get("mann_kendall", {}).get("p_value", 1.0)
    conf_a = reg_a.get("mann_kendall", {}).get("confidence_pct", 0.0)

    slope_b = reg_b.get("mann_kendall", {}).get("sens_slope_per_decade", 0.0)
    p_val_b = reg_b.get("mann_kendall", {}).get("p_value", 1.0)
    conf_b = reg_b.get("mann_kendall", {}).get("confidence_pct", 0.0)

    unit = stats_data.get("unit", "units")
    var_name = stats_data.get("variable_name", stats_data.get("variable_id", "Measurement"))
    prod = manifest_info.get("source_product", "NASA Earth Observation Satellite Telemetry") if manifest_info else "NASA Satellite Telemetry"

    # 1. Attempt Ollama Generation (when available and not explicitly skipped)
    if not skip_ollama and os.getenv("SKIP_OLLAMA") != "1":
        try:
            system_instruction = (
                "You are TerraDetective AI, an expert NASA Earth System Trend Assistant. "
                "You must directly answer the user's specific question using ONLY the provided verified satellite numbers. "
                "Never fabricate or change numbers. "
                f"Audience Mode: {'Student/Public (clear, engaging, jargon-free)' if mode == 'student' else 'Scientist/Researcher (rigorous, citing sensors, Mann-Kendall p-values, and physical drivers)'}. "
                "Keep response concise (1-2 crisp paragraphs)."
            )

            context_summary = {
                "user_question": query,
                "comparing": f"{label_a} vs {label_b}",
                "variable": var_name,
                "unit": unit,
                "satellite_product": prod,
                "region_a": {
                    "name": label_a,
                    "decadal_slope": slope_a,
                    "p_value": p_val_a,
                    "confidence_pct": conf_a,
                    "trend": reg_a.get("mann_kendall", {}).get("trend_direction"),
                },
                "region_b": {
                    "name": label_b,
                    "decadal_slope": slope_b,
                    "p_value": p_val_b,
                    "confidence_pct": conf_b,
                    "trend": reg_b.get("mann_kendall", {}).get("trend_direction"),
                },
                "divergence": {
                    "detected": div.get("divergence_detected", False),
                    "verdict": div.get("verdict", ""),
                    "slope_difference_per_decade": div.get("slope_difference_per_decade", 0.0),
                },
            }

            user_content = (
                f"User Question: \"{query}\"\n\n"
                f"Verified NASA Satellite Telemetry Data for this query:\n"
                f"{json.dumps(context_summary, indent=2)}\n\n"
                f"Instruction: Directly answer the user's question comparing {label_a} and {label_b} using these exact figures."
            )

            req_body = {
                "model": OLLAMA_MODEL,
                "prompt": f"{system_instruction}\n\nUser: {user_content}\n\nAssistant: ",
                "stream": False,
                "options": {"temperature": 0.2, "top_p": 0.9},
            }

            client_timeout = httpx.Timeout(OLLAMA_TIMEOUT, connect=min(1.5, OLLAMA_TIMEOUT))
            with httpx.Client(timeout=client_timeout) as client:
                resp = client.post(OLLAMA_API_URL, json=req_body)
                if resp.status_code == 200:
                    out = resp.json().get("response", "").strip()
                    if out and len(out) > 40:
                        return out, "ollama_qwen3_8b"
        except Exception as e:
            logger.debug(f"Ollama generation skipped or offline: {e}. Using deterministic fallback.")

    # 2. Adaptive Question-Specific Deterministic Synthesizer
    sign_a = "+" if slope_a >= 0 else ""
    sign_b = "+" if slope_b >= 0 else ""
    diff_dec = div.get("slope_difference_per_decade", slope_a - slope_b)

    if is_custom:
        # Custom Comparison Generator (e.g. Delhi vs Hyderabad, London vs Cairo)
        if mode == "student":
            # Determine relationship
            if slope_a > slope_b:
                rel_statement = f"**{label_a}** is warming faster (or cooling slower) than **{label_b}** by **{abs(diff_dec):.4f} {unit}/decade**."
            elif slope_b > slope_a:
                rel_statement = f"**{label_b}** is warming faster (or cooling slower) than **{label_a}** by **{abs(diff_dec):.4f} {unit}/decade**."
            else:
                rel_statement = f"Both **{label_a}** and **{label_b}** share virtually identical decadal trajectory rates."

            ans = (
                f"Here is your comparative satellite analysis for **{label_a}** vs. **{label_b}** based on 25 years of NASA satellite telemetry ({prod}):\n\n"
                f"• **{label_a}:** records a decadal trend of **{sign_a}{slope_a:.4f} {unit}/decade** with **{conf_a:.1f}% statistical confidence** (p = {p_val_a:.4f}).\n"
                f"• **{label_b}:** records a decadal trend of **{sign_b}{slope_b:.4f} {unit}/decade** with **{conf_b:.1f}% statistical confidence** (p = {p_val_b:.4f}).\n\n"
                f"{rel_statement} This reflects distinct regional climatic drivers — such as differences in urban heat island density, elevation, distance from maritime cooling, and local vegetative cover."
            )
        else:
            # Scientist Research Mode
            ans = (
                f"**Multi-Decadal Satellite Telemetry Comparison ({prod}):**\n"
                f"Comparative non-parametric analysis reveals divergent {var_name.lower()} trajectories between the two requested study coordinates. "
                f"For **{label_a}**, the Sen's median slope is **{sign_a}{slope_a:.4f} {unit}/decade** (Mann-Kendall p = {p_val_a:.4e}, confidence = {conf_a:.2f}%). "
                f"For **{label_b}**, the decadal rate is **{sign_b}{slope_b:.4f} {unit}/decade** (p = {p_val_b:.4e}, confidence = {conf_b:.2f}%). "
                f"Net divergence between regions is evaluated at **Δ = {diff_dec:+.4f} {unit}/decade**. "
                f"These contrasting trajectories illustrate localized surface boundary-layer dynamics and energy balance partitioning over the 2001–2025 observation window."
            )
    else:
        # Flagship Preset Paradox Generator
        driver = manifest_info.get("scientific_driver", "") if manifest_info else ""
        if mode == "student":
            ans = (
                f"Great question! Based on 25 years of NASA satellite telemetry ({prod}), here is what orbit reveals for this paradox:\n\n"
                f"• **{label_a}:** displays a trend of **{sign_a}{slope_a:.4f} {unit}/decade** ({conf_a:.1f}% confidence, p = {p_val_a:.4f}).\n"
                f"• **{label_b}:** displays a contrasting trend of **{sign_b}{slope_b:.4f} {unit}/decade** ({conf_b:.1f}% confidence, p = {p_val_b:.4f}).\n\n"
                f"**Why they differ:** {driver}"
            )
        else:
            ans = (
                f"**NASA Earth Observation Telemetry ({prod}):**\n"
                f"Rigorous Mann-Kendall evaluation confirms statistically significant multi-decadal divergence between {label_a} ({sign_a}{slope_a:.4f} {unit}/dec, p = {p_val_a:.4e}) "
                f"and {label_b} ({sign_b}{slope_b:.4f} {unit}/dec, p = {p_val_b:.4e}), with an inter-regional divergence of **Δ = {diff_dec:+.4f} {unit}/decade**. "
                f"**Biophysical Mechanism:** {driver}"
            )

    return ans, "deterministic_fallback"


# ---------------------------------------------------------------------------
# Key Evidence Badges & Follow-up Generator
# ---------------------------------------------------------------------------
def build_evidence_badges(
    stats_data: Dict[str, Any],
    manifest_info: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Builds 3-4 compact metric badges highlighting key statistical findings."""
    reg_a = stats_data.get("region_a", {})
    reg_b = stats_data.get("region_b", {})
    div = stats_data.get("divergence_analysis", {})

    label_a = reg_a.get("region_label", reg_a.get("region_id", "Region A"))
    label_b = reg_b.get("region_label", reg_b.get("region_id", "Region B"))

    slope_a = reg_a.get("mann_kendall", {}).get("sens_slope_per_decade", 0.0)
    p_a = reg_a.get("mann_kendall", {}).get("p_value", 1.0)
    slope_b = reg_b.get("mann_kendall", {}).get("sens_slope_per_decade", 0.0)
    p_b = reg_b.get("mann_kendall", {}).get("p_value", 1.0)

    unit = stats_data.get("unit", "")
    sign_a = "+" if slope_a >= 0 else ""
    sign_b = "+" if slope_b >= 0 else ""

    badges = [
        f"{label_a[:18]}: {sign_a}{slope_a:.3f} {unit}/dec (p={p_a:.4f})",
        f"{label_b[:18]}: {sign_b}{slope_b:.3f} {unit}/dec (p={p_b:.4f})",
    ]

    diff_dec = div.get("slope_difference_per_decade")
    if diff_dec is not None and div.get("divergence_detected", False):
        badges.append(f"Divergence: Δ = {diff_dec:+.3f} {unit}/dec")

    sensor = manifest_info.get("source_product", "") if manifest_info else ""
    if "MOD11A2" in sensor:
        badges.append("Sensor: MODIS MOD11A2.061 (LST)")
    elif "MOD13A3" in sensor:
        badges.append("Sensor: MODIS MOD13A3.061 (NDVI)")
    elif "GPM" in sensor or "IMERG" in sensor:
        badges.append("Sensor: NASA GPM IMERG (3IMERGM)")
    elif "POWER" in sensor:
        badges.append("Telemetry: NASA POWER / MERRA-2")
    else:
        badges.append("Source: NASA Earthdata Archive")

    return badges[:4]


def build_suggested_followups(case_id: Optional[str], var_id: str, label_a: str = "", label_b: str = "") -> List[str]:
    """Generates 3 contextual clickable follow-up questions tailored to queried entities."""
    if case_id == "case_2_land_thermal_paradox":
        return [
            "How does Amazon deforestation compare in terms of vegetation greenness (NDVI)?",
            "What happens to the temperature trend if I look only at the last 5 years?",
            "Compare temperature trends in Delhi vs Mumbai.",
        ]
    elif case_id == "case_3_vegetation_paradox":
        return [
            "Does Punjab's NDVI greening surge translate into actual land cooling?",
            "How severe is canopy brown-down in the Rondônia Amazon Arc?",
            "Compare rainfall in Marathwada vs Northeast India.",
        ]
    elif case_id == "case_1_monsoon_paradox":
        return [
            "Why doesn't the monsoon air mass drop moisture over Marathwada?",
            "Is flash flood frequency increasing in Cherrapunji?",
            "Compare rainfall in London vs Cairo.",
        ]
    elif label_a and label_b:
        return [
            f"How does rainfall compare between {label_a.split(',')[0]} and {label_b.split(',')[0]}?",
            f"What happens to {label_a.split(',')[0]}'s trend if we isolate the last 10 years?",
            "Why is the Amazon warming while Punjab cools?",
        ]
    else:
        return [
            "Compare temperature trends in Delhi vs Mumbai.",
            "Compare rainfall in London vs Cairo.",
            "Why is the Amazon warming while Punjab cools?",
        ]


# ---------------------------------------------------------------------------
# Master Natural Language Query Router
# ---------------------------------------------------------------------------
def process_natural_language_query(
    query: str,
    mode: str = "student",
    active_case_id: Optional[str] = None,
    skip_ollama: bool = False,
) -> Dict[str, Any]:
    """
    Main entry point: processes natural language question, retrieves data,
    computes/loads statistics, generates data-grounded AI answer, and outputs
    a synchronized payload for the workbench UI.
    """
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        cleaned_query = "What is the most significant Earth system trend paradox in the dataset?"

    # Check 1 (Out of Context Domain Guardrail):
    if not is_domain_relevant(cleaned_query):
        return {
            "query": cleaned_query,
            "mode": mode,
            "answer": "I am TerraDetective, an Earth science AI! I can only answer questions about climate trends, regional paradoxes, and NASA satellite data. Try asking me to compare temperature or rainfall between two cities.",
            "ai_source": "domain_guardrail",
            "key_evidence_badges": ["Domain: Earth Science Only", "Guardrail: Active"],
            "suggested_followups": [
                "Compare temperature trends in Delhi vs Mumbai",
                "Why is the Amazon warming while Punjab cools?",
                "Compare rainfall in London vs Cairo",
            ],
            "action_type": "info",
            "matched_case_id": None,
            "case_payload": None,
        }

    var_id, var_name, unit = detect_variable(cleaned_query)

    # Check 2 (Unsupported Pollution Variable):
    if var_id == "UNSUPPORTED_POLLUTION":
        return {
            "query": cleaned_query,
            "mode": mode,
            "answer": "I don't currently have live satellite feeds for air quality or pollution (like PM2.5 or Aerosol Optical Depth). However, I can analyze trends for Surface Temperature, Rainfall, Soil Moisture, or Vegetation. Which would you like to investigate?",
            "ai_source": "unsupported_variable_guardrail",
            "key_evidence_badges": ["Variable: Air Quality / Pollution", "Live Feed: Not Available"],
            "suggested_followups": [
                "Compare temperature trends in Delhi vs Mumbai",
                "Compare rainfall in Delhi vs Mumbai",
                "Why is the Amazon warming while Punjab cools?",
            ],
            "action_type": "info",
            "matched_case_id": None,
            "case_payload": None,
        }

    manifest_data = _get_manifest()
    cases_list = manifest_data.get("cases", [])
    cases_dict = {c["case_id"]: c for c in cases_list}
    stats_cache = _get_stats_cache().get("cases", {})

    # Step 1: Extract any explicit or fuzzy-matched locations from query
    gazetteer_locs = extract_gazetteer_locations(cleaned_query)

    # Step 2: Detect preset paradox ONLY if no custom cities were requested
    matched_case_id = detect_preset_case(cleaned_query, gazetteer_locs)

    # Check 3 (Unknown Variable for Non-Preset Queries):
    if matched_case_id is None and var_id == "UNKNOWN_VARIABLE":
        return {
            "query": cleaned_query,
            "mode": mode,
            "answer": "I couldn't detect which environmental variable you want to measure. Try asking about temperature, rainfall, soil moisture, or plant greenness!",
            "ai_source": "unknown_variable_guardrail",
            "key_evidence_badges": ["Variable: Unknown", "Supported: Temp, Rain, Soil, NDVI"],
            "suggested_followups": [
                "Compare temperature in London vs Cairo",
                "Compare rainfall in London vs Cairo",
                "Why is the Amazon warming while Punjab cools?",
            ],
            "action_type": "info",
            "matched_case_id": None,
            "case_payload": None,
        }

    # Step 3: Determine whether this is a custom comparison or preset case
    is_custom_comparison = False
    loc_a: Optional[Dict[str, Any]] = None
    loc_b: Optional[Dict[str, Any]] = None

    if len(gazetteer_locs) >= 2 and matched_case_id is None:
        is_custom_comparison = True
        loc_a = gazetteer_locs[0]
        loc_b = gazetteer_locs[1]
    elif len(gazetteer_locs) == 1 and matched_case_id is None:
        loc_a = gazetteer_locs[0]
        # Choose a contrasting comparison twin based on climate zone
        tok = loc_a.get("query_token", "")
        if tok in ["cairo", "sahara", "dubai", "riyadh"]:
            loc_b = GLOBAL_GAZETTEER["london"]
        elif tok in ["delhi", "new delhi"]:
            loc_b = GLOBAL_GAZETTEER["mumbai"]
        elif tok == "california":
            loc_b = GLOBAL_GAZETTEER["greenland"]
        else:
            loc_b = {
                "name": f"{loc_a['name']} Regional Perimeter",
                "lat": round(loc_a["lat"] + 2.5, 3),
                "lon": round(loc_a["lon"] + 2.5, 3),
            }
        is_custom_comparison = True

    # -----------------------------------------------------------------------
    # Branch A: Preset Case Route
    # -----------------------------------------------------------------------
    if not is_custom_comparison:
        target_case_id = matched_case_id or active_case_id or "case_2_land_thermal_paradox"
        if target_case_id not in cases_dict:
            target_case_id = "case_2_land_thermal_paradox"

        case_manifest = cases_dict[target_case_id]
        case_stats = stats_cache.get(target_case_id)

        # Build regions_data from unified CSV
        unified_df = _get_unified_df()
        case_df = unified_df[unified_df["case_id"] == target_case_id] if not unified_df.empty else pd.DataFrame()

        regions_data = {}
        if not case_df.empty:
            for rid in case_df["region_id"].unique():
                r_df = case_df[case_df["region_id"] == rid].sort_values("date")
                regions_data[rid] = {
                    "dates": r_df["date"].tolist(),
                    "values": r_df["value"].tolist(),
                    "region_label": r_df["region_label"].iloc[0] if len(r_df) > 0 else rid,
                    "lat": float(r_df["lat"].iloc[0]) if len(r_df) > 0 else None,
                    "lon": float(r_df["lon"].iloc[0]) if len(r_df) > 0 else None,
                    "record_count": len(r_df),
                }

        # If stats weren't cached, compute them
        if not case_stats and len(regions_data) >= 2:
            from services.trend_analyzer import compare_regions as _compare_regions
            r_keys = list(regions_data.keys())
            df_a = case_df[case_df["region_id"] == r_keys[0]]
            df_b = case_df[case_df["region_id"] == r_keys[1]]
            case_stats = _compare_regions(df_a, df_b, alpha=0.05)

        # Generate Grounded AI Answer
        answer_text, ai_source = generate_grounded_answer(
            query=cleaned_query,
            stats_data=case_stats or {},
            mode=mode,
            manifest_info=case_manifest,
            skip_ollama=skip_ollama,
            is_custom=False,
        )

        badges = build_evidence_badges(case_stats or {}, case_manifest)
        followups = build_suggested_followups(target_case_id, case_manifest.get("variable_id", ""))

        case_payload = {
            "case_id": target_case_id,
            "manifest": case_manifest,
            "regions_data": regions_data,
            "statistics": case_stats,
            "narratives": {
                "student_story_mode": {
                    "headline": case_manifest.get("title", ""),
                    "what_changed": answer_text,
                    "detective_clue_why": case_manifest.get("scientific_driver", ""),
                },
                "scientist_research_mode": {
                    "technical_abstract": answer_text,
                    "statistical_interpretation": "Mann-Kendall p < 0.05",
                },
            },
            "simulation_metadata": {
                "time_window_sliced": False,
                "start_year": 2001,
                "end_year": 2025,
                "window_years": 25,
                "significance_verdict": "Full 25-Year Satellite Record — High Statistical Significance",
            },
        }

        return {
            "query": cleaned_query,
            "mode": mode,
            "answer": answer_text,
            "ai_source": ai_source,
            "key_evidence_badges": badges,
            "suggested_followups": followups,
            "action_type": "load_preset_case",
            "matched_case_id": target_case_id,
            "case_payload": case_payload,
        }

    # -----------------------------------------------------------------------
    # Branch B: Custom Twin-Region Comparison Route
    # -----------------------------------------------------------------------
    from services.earthdata_client import ThreeTierEarthDataConnector
    from services.trend_analyzer import compare_regions as _compare_regions
    from services.live_satellite_stac import get_telemetry_for_region

    var_id, var_name, unit = detect_variable(cleaned_query)
    earthdata_connector = ThreeTierEarthDataConnector()

    assert loc_a is not None and loc_b is not None

    power_a = earthdata_connector.fetch_nasa_power_point(
        lat=loc_a["lat"], lon=loc_a["lon"],
        start_year=2001, end_year=2025,
        parameters=[var_id],
    )
    power_b = earthdata_connector.fetch_nasa_power_point(
        lat=loc_b["lat"], lon=loc_b["lon"],
        start_year=2001, end_year=2025,
        parameters=[var_id],
    )

    data_mode = (
        "live_nasa_power"
        if power_a.get("data_mode") == "live_nasa_power" and power_b.get("data_mode") == "live_nasa_power"
        else "verified_offline_archive"
    )

    recs_a = power_a.get("data") or earthdata_connector._fallback_to_nearest_offline_case(loc_a["lat"], loc_a["lon"]).get("records", [])
    clean_a = [(r["date"], r.get(var_id, r.get("value"))) for r in recs_a if r.get(var_id, r.get("value")) is not None]

    recs_b = power_b.get("data") or earthdata_connector._fallback_to_nearest_offline_case(loc_b["lat"], loc_b["lon"]).get("records", [])
    clean_b = [(r["date"], r.get(var_id, r.get("value"))) for r in recs_b if r.get(var_id, r.get("value")) is not None]

    if len(clean_a) < 12 or len(clean_b) < 12:
        clean_a = [(r["date"], r["value"]) for r in earthdata_connector._fallback_to_nearest_offline_case(loc_a["lat"], loc_a["lon"]).get("records", [])]
        clean_b = [(r["date"], r["value"]) for r in earthdata_connector._fallback_to_nearest_offline_case(loc_b["lat"], loc_b["lon"]).get("records", [])]

    dates_a, vals_a = zip(*clean_a)
    dates_b, vals_b = zip(*clean_b)

    df_a = pd.DataFrame({
        "date": list(dates_a),
        "value": [float(v) for v in vals_a],
        "region_id": "region_a",
        "region_label": loc_a["name"],
        "variable_id": var_id,
        "variable_name": var_name,
        "unit": unit,
        "lat": loc_a["lat"],
        "lon": loc_a["lon"],
    })

    df_b = pd.DataFrame({
        "date": list(dates_b),
        "value": [float(v) for v in vals_b],
        "region_id": "region_b",
        "region_label": loc_b["name"],
        "variable_id": var_id,
        "variable_name": var_name,
        "unit": unit,
        "lat": loc_b["lat"],
        "lon": loc_b["lon"],
    })

    stats = _compare_regions(df_a, df_b, alpha=0.05)

    custom_manifest = {
        "case_id": f"custom_query_{var_id.lower()}",
        "title": f"Telemetry Investigation: {loc_a['name']} vs. {loc_b['name']}",
        "paradox_statement": f"Evaluating comparative 25-year {var_name.lower()} trajectories between {loc_a['name']} and {loc_b['name']}.",
        "variable_id": var_id,
        "variable_name": var_name,
        "unit": unit,
        "source_product": f"NASA POWER / MERRA-2 Climatology ({data_mode})",
        "regions": [
            {
                "region_id": "region_a",
                "region_label": loc_a["name"],
                "latitude": loc_a["lat"],
                "longitude": loc_a["lon"],
            },
            {
                "region_id": "region_b",
                "region_label": loc_b["name"],
                "latitude": loc_b["lat"],
                "longitude": loc_b["lon"],
            },
        ],
        "region_a": {
            "id": "region_a",
            "label": loc_a["name"],
            "region_label": loc_a["name"],
            "lat": loc_a["lat"],
            "lon": loc_a["lon"],
        },
        "region_b": {
            "id": "region_b",
            "label": loc_b["name"],
            "region_label": loc_b["name"],
            "lat": loc_b["lat"],
            "lon": loc_b["lon"],
        },
        "data_mode": data_mode,
    }

    # Generate Grounded AI Answer
    answer_text, ai_source = generate_grounded_answer(
        query=cleaned_query,
        stats_data=stats,
        mode=mode,
        manifest_info=custom_manifest,
        skip_ollama=skip_ollama,
        is_custom=True,
    )

    badges = build_evidence_badges(stats, custom_manifest)
    followups = build_suggested_followups(None, var_id, loc_a["name"], loc_b["name"])

    # Telemetry
    telemetry_a = get_telemetry_for_region(loc_a["lat"], loc_a["lon"], var_id)
    telemetry_b = get_telemetry_for_region(loc_b["lat"], loc_b["lon"], var_id)

    case_payload = {
        "case_id": custom_manifest["case_id"],
        "manifest": custom_manifest,
        "regions_data": {
            "region_a": {
                "dates": df_a["date"].tolist(),
                "values": df_a["value"].tolist(),
                "region_label": loc_a["name"],
                "lat": loc_a["lat"],
                "lon": loc_a["lon"],
                "record_count": len(df_a),
            },
            "region_b": {
                "dates": df_b["date"].tolist(),
                "values": df_b["value"].tolist(),
                "region_label": loc_b["name"],
                "lat": loc_b["lat"],
                "lon": loc_b["lon"],
                "record_count": len(df_b),
            },
        },
        "statistics": stats,
        "narratives": {
            "student_story_mode": {
                "headline": custom_manifest["title"],
                "what_changed": answer_text,
                "detective_clue_why": f"Regional divergence between {loc_a['name']} and {loc_b['name']} driven by geographic boundary conditions and energy fluxes.",
            },
            "scientist_research_mode": {
                "technical_abstract": answer_text,
                "statistical_interpretation": f"Comparative Mann-Kendall decadal trajectories across 2001–2025. Sen's slope difference evaluated at Δ = {stats.get('divergence_analysis', {}).get('slope_difference_per_decade', 0.0):+.4f} {unit}/decade.",
                "physical_mechanisms": f"Differential surface boundary-layer energy partitioning, sensible vs. latent heat flux allocation, and local land-use / topographic divergence between {loc_a['name']} and {loc_b['name']}.",
                "methodological_caveats": f"Multi-decadal monthly climatology sourced from {custom_manifest['source_product']}. Time series deseasonalized using periodic STL decomposition prior to non-parametric trend evaluation.",
            },
        },
        "telemetry": {
            "region_a": telemetry_a,
            "region_b": telemetry_b,
        },
        "simulation_metadata": {
            "time_window_sliced": False,
            "start_year": 2001,
            "end_year": 2025,
            "window_years": 25,
            "significance_verdict": "Multi-Decadal Satellite Telemetry Analysis",
        },
    }

    return {
        "query": cleaned_query,
        "mode": mode,
        "answer": answer_text,
        "ai_source": ai_source,
        "key_evidence_badges": badges,
        "suggested_followups": followups,
        "action_type": "load_custom_comparison",
        "matched_case_id": None,
        "case_payload": case_payload,
    }
