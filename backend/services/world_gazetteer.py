# Universal Planetary Gazetteer: Global Countries, States, Provinces, and Hotspots
# Provides 100% offline, 0ms latency coordinate resolution for all sovereign nations,
# US states, Indian states, Canadian provinces, Australian states, European regions, and climate hotspots.
from typing import Dict, Any, Optional

WORLD_GAZETTEER: Dict[str, Dict[str, Any]] = {
    "alabama": {
        "name": "Alabama, USA",
        "lat": 32.8067,
        "lon": -86.7911,
        "zone": "humid_subtropical"
    },
    "alaska": {
        "name": "Alaska, USA",
        "lat": 61.3707,
        "lon": -152.4044,
        "zone": "subarctic_tundra"
    },
    "arizona": {
        "name": "Arizona, USA",
        "lat": 33.7298,
        "lon": -111.4312,
        "zone": "sonoran_desert"
    },
    "arkansas": {
        "name": "Arkansas, USA",
        "lat": 34.9697,
        "lon": -92.3731,
        "zone": "humid_subtropical"
    },
    "california": {
        "name": "California, USA",
        "lat": 36.1162,
        "lon": -119.6816,
        "zone": "mediterranean_pacific"
    },
    "colorado": {
        "name": "Colorado, USA",
        "lat": 39.0598,
        "lon": -105.3111,
        "zone": "rocky_mountain_semi_arid"
    },
    "connecticut": {
        "name": "Connecticut, USA",
        "lat": 41.5978,
        "lon": -72.7554,
        "zone": "humid_continental"
    },
    "delaware": {
        "name": "Delaware, USA",
        "lat": 39.3185,
        "lon": -75.5071,
        "zone": "humid_subtropical_atlantic"
    },
    "florida": {
        "name": "Florida, USA",
        "lat": 27.7663,
        "lon": -81.6868,
        "zone": "subtropical_gulf_atlantic"
    },
    "georgia": {
        "name": "Georgia (Country)",
        "lat": 42.3154,
        "lon": 43.3569,
        "zone": "caucasian_subtropical"
    },
    "hawaii": {
        "name": "Hawaii, USA",
        "lat": 21.0943,
        "lon": -157.4983,
        "zone": "tropical_pacific_island"
    },
    "idaho": {
        "name": "Idaho, USA",
        "lat": 44.2405,
        "lon": -114.4788,
        "zone": "semi_arid_montane"
    },
    "illinois": {
        "name": "Illinois, USA",
        "lat": 40.3495,
        "lon": -88.9861,
        "zone": "midwest_humid_continental"
    },
    "indiana": {
        "name": "Indiana, USA",
        "lat": 39.8494,
        "lon": -86.2583,
        "zone": "midwest_humid_continental"
    },
    "iowa": {
        "name": "Iowa, USA",
        "lat": 42.0115,
        "lon": -93.2105,
        "zone": "corn_belt_continental"
    },
    "kansas": {
        "name": "Kansas, USA",
        "lat": 38.5266,
        "lon": -96.7265,
        "zone": "great_plains_continental"
    },
    "kentucky": {
        "name": "Kentucky, USA",
        "lat": 37.6681,
        "lon": -84.6701,
        "zone": "humid_subtropical"
    },
    "louisiana": {
        "name": "Louisiana, USA",
        "lat": 31.1695,
        "lon": -91.8678,
        "zone": "gulf_coastal_subtropical"
    },
    "maine": {
        "name": "Maine, USA",
        "lat": 44.6939,
        "lon": -69.3819,
        "zone": "northern_humid_continental"
    },
    "maryland": {
        "name": "Maryland, USA",
        "lat": 39.0639,
        "lon": -76.8021,
        "zone": "humid_subtropical"
    },
    "massachusetts": {
        "name": "Massachusetts, USA",
        "lat": 42.2302,
        "lon": -71.5301,
        "zone": "humid_continental_coastal"
    },
    "michigan": {
        "name": "Michigan, USA",
        "lat": 43.3266,
        "lon": -84.5361,
        "zone": "great_lakes_continental"
    },
    "minnesota": {
        "name": "Minnesota, USA",
        "lat": 45.6945,
        "lon": -93.9002,
        "zone": "upper_midwest_continental"
    },
    "mississippi": {
        "name": "Mississippi, USA",
        "lat": 32.7416,
        "lon": -89.6787,
        "zone": "humid_subtropical"
    },
    "missouri": {
        "name": "Missouri, USA",
        "lat": 38.4561,
        "lon": -92.2884,
        "zone": "humid_continental"
    },
    "montana": {
        "name": "Montana, USA",
        "lat": 46.9219,
        "lon": -110.4544,
        "zone": "northern_plains_montane"
    },
    "nebraska": {
        "name": "Nebraska, USA",
        "lat": 41.1254,
        "lon": -98.2681,
        "zone": "great_plains_continental"
    },
    "nevada": {
        "name": "Nevada, USA",
        "lat": 38.3135,
        "lon": -117.0554,
        "zone": "great_basin_desert"
    },
    "new hampshire": {
        "name": "New Hampshire, USA",
        "lat": 43.4525,
        "lon": -71.5639,
        "zone": "northern_continental"
    },
    "new jersey": {
        "name": "New Jersey, USA",
        "lat": 40.2989,
        "lon": -74.521,
        "zone": "mid_atlantic_humid_continental"
    },
    "new mexico": {
        "name": "New Mexico, USA",
        "lat": 34.8405,
        "lon": -106.2485,
        "zone": "chihuahuan_desert_montane"
    },
    "new york": {
        "name": "New York, USA",
        "lat": 42.1657,
        "lon": -74.9481,
        "zone": "humid_continental"
    },
    "north carolina": {
        "name": "North Carolina, USA",
        "lat": 35.6301,
        "lon": -79.8064,
        "zone": "humid_subtropical"
    },
    "north dakota": {
        "name": "North Dakota, USA",
        "lat": 47.5289,
        "lon": -99.784,
        "zone": "northern_plains_continental"
    },
    "ohio": {
        "name": "Ohio, USA",
        "lat": 40.3888,
        "lon": -82.7649,
        "zone": "humid_continental"
    },
    "oklahoma": {
        "name": "Oklahoma, USA",
        "lat": 35.5653,
        "lon": -96.9289,
        "zone": "southern_plains_subtropical"
    },
    "oregon": {
        "name": "Oregon, USA",
        "lat": 44.572,
        "lon": -122.0709,
        "zone": "pacific_northwest_oceanic"
    },
    "pennsylvania": {
        "name": "Pennsylvania, USA",
        "lat": 40.5908,
        "lon": -77.2098,
        "zone": "humid_continental"
    },
    "rhode island": {
        "name": "Rhode Island, USA",
        "lat": 41.6809,
        "lon": -71.5118,
        "zone": "coastal_humid_continental"
    },
    "south carolina": {
        "name": "South Carolina, USA",
        "lat": 33.8569,
        "lon": -80.945,
        "zone": "humid_subtropical"
    },
    "south dakota": {
        "name": "South Dakota, USA",
        "lat": 44.2998,
        "lon": -99.4388,
        "zone": "great_plains_continental"
    },
    "tennessee": {
        "name": "Tennessee, USA",
        "lat": 35.7478,
        "lon": -86.6923,
        "zone": "humid_subtropical"
    },
    "texas": {
        "name": "Texas, USA",
        "lat": 31.0545,
        "lon": -97.5635,
        "zone": "gulf_plains_subtropical"
    },
    "utah": {
        "name": "Utah, USA",
        "lat": 40.15,
        "lon": -111.8624,
        "zone": "semi_arid_colorado_plateau"
    },
    "vermont": {
        "name": "Vermont, USA",
        "lat": 44.0459,
        "lon": -72.7107,
        "zone": "northern_continental"
    },
    "virginia": {
        "name": "Virginia, USA",
        "lat": 37.7693,
        "lon": -78.1699,
        "zone": "mid_atlantic_subtropical"
    },
    "washington": {
        "name": "Washington, USA",
        "lat": 47.4009,
        "lon": -121.4905,
        "zone": "pacific_northwest_oceanic"
    },
    "west virginia": {
        "name": "West Virginia, USA",
        "lat": 38.4912,
        "lon": -80.9545,
        "zone": "appalachian_humid_continental"
    },
    "wisconsin": {
        "name": "Wisconsin, USA",
        "lat": 44.2685,
        "lon": -89.6165,
        "zone": "upper_midwest_continental"
    },
    "wyoming": {
        "name": "Wyoming, USA",
        "lat": 42.756,
        "lon": -107.3025,
        "zone": "semi_arid_rocky_mountain"
    },
    "washington dc": {
        "name": "Washington D.C., USA",
        "lat": 38.9072,
        "lon": -77.0369,
        "zone": "mid_atlantic_subtropical"
    },
    "dc": {
        "name": "Washington D.C., USA",
        "lat": 38.9072,
        "lon": -77.0369,
        "zone": "mid_atlantic_subtropical"
    },
    "puerto rico": {
        "name": "Puerto Rico, USA",
        "lat": 18.2208,
        "lon": -66.5901,
        "zone": "caribbean_tropical"
    },
    "andhra pradesh": {
        "name": "Andhra Pradesh, India",
        "lat": 15.9129,
        "lon": 79.74,
        "zone": "coastal_deccan_tropical"
    },
    "arunachal pradesh": {
        "name": "Arunachal Pradesh, India",
        "lat": 28.218,
        "lon": 94.7278,
        "zone": "eastern_himalayan_montane"
    },
    "assam": {
        "name": "Assam, India",
        "lat": 26.2006,
        "lon": 92.9376,
        "zone": "brahmaputra_riverine_subtropical"
    },
    "bihar": {
        "name": "Bihar, India",
        "lat": 25.0961,
        "lon": 85.3131,
        "zone": "middle_gangetic_plain"
    },
    "chhattisgarh": {
        "name": "Chhattisgarh, India",
        "lat": 21.2787,
        "lon": 81.8661,
        "zone": "central_deccan_plateau"
    },
    "goa": {
        "name": "Goa, India",
        "lat": 15.2993,
        "lon": 74.124,
        "zone": "konkan_coastal_tropical"
    },
    "gujarat": {
        "name": "Gujarat, India",
        "lat": 22.2587,
        "lon": 71.1924,
        "zone": "semi_arid_kathiawar"
    },
    "haryana": {
        "name": "Haryana, India",
        "lat": 29.0588,
        "lon": 76.0856,
        "zone": "indo_gangetic_semi_arid"
    },
    "himachal pradesh": {
        "name": "Himachal Pradesh, India",
        "lat": 31.1048,
        "lon": 77.1734,
        "zone": "western_himalayan_temperate"
    },
    "jharkhand": {
        "name": "Jharkhand, India",
        "lat": 23.6102,
        "lon": 85.2799,
        "zone": "chota_nagpur_plateau"
    },
    "karnataka": {
        "name": "Karnataka, India",
        "lat": 15.3173,
        "lon": 75.7139,
        "zone": "deccan_western_ghats"
    },
    "kerala": {
        "name": "Kerala, India",
        "lat": 10.8505,
        "lon": 76.2711,
        "zone": "malabar_tropical_wet"
    },
    "madhya pradesh": {
        "name": "Madhya Pradesh, India",
        "lat": 22.9734,
        "lon": 78.6569,
        "zone": "central_indian_highlands"
    },
    "maharashtra": {
        "name": "Maharashtra, India",
        "lat": 19.7515,
        "lon": 75.7139,
        "zone": "deccan_plateau_rain_shadow"
    },
    "manipur": {
        "name": "Manipur, India",
        "lat": 24.6637,
        "lon": 93.9063,
        "zone": "purvanchal_subtropical_montane"
    },
    "meghalaya": {
        "name": "Meghalaya, India",
        "lat": 25.467,
        "lon": 91.3662,
        "zone": "shillong_plateau_monsoon"
    },
    "mizoram": {
        "name": "Mizoram, India",
        "lat": 23.1645,
        "lon": 92.9376,
        "zone": "lushei_hills_subtropical"
    },
    "nagaland": {
        "name": "Nagaland, India",
        "lat": 26.1584,
        "lon": 94.5624,
        "zone": "naga_hills_montane"
    },
    "odisha": {
        "name": "Odisha, India",
        "lat": 20.9517,
        "lon": 85.0985,
        "zone": "eastern_ghats_coastal_tropical"
    },
    "orissa": {
        "name": "Odisha, India",
        "lat": 20.9517,
        "lon": 85.0985,
        "zone": "eastern_ghats_coastal_tropical"
    },
    "punjab": {
        "name": "Punjab, India",
        "lat": 31.1471,
        "lon": 75.3412,
        "zone": "indo_gangetic_irrigated_plains"
    },
    "rajasthan": {
        "name": "Rajasthan, India",
        "lat": 27.0238,
        "lon": 74.2179,
        "zone": "thar_arid_desert"
    },
    "sikkim": {
        "name": "Sikkim, India",
        "lat": 27.533,
        "lon": 88.5122,
        "zone": "eastern_himalayan_alpine"
    },
    "tamil nadu": {
        "name": "Tamil Nadu, India",
        "lat": 11.1271,
        "lon": 78.6569,
        "zone": "coromandel_tropical_dry"
    },
    "telangana": {
        "name": "Telangana, India",
        "lat": 18.1124,
        "lon": 79.0193,
        "zone": "semi_arid_telangana_plateau"
    },
    "tripura": {
        "name": "Tripura, India",
        "lat": 23.9408,
        "lon": 91.9882,
        "zone": "northeast_subtropical_humid"
    },
    "uttar pradesh": {
        "name": "Uttar Pradesh, India",
        "lat": 26.8467,
        "lon": 80.9462,
        "zone": "gangetic_alluvial_plain"
    },
    "up": {
        "name": "Uttar Pradesh, India",
        "lat": 26.8467,
        "lon": 80.9462,
        "zone": "gangetic_alluvial_plain"
    },
    "uttarakhand": {
        "name": "Uttarakhand, India",
        "lat": 30.0668,
        "lon": 79.0193,
        "zone": "central_himalayan_montane"
    },
    "west bengal": {
        "name": "West Bengal, India",
        "lat": 22.9868,
        "lon": 87.855,
        "zone": "gangetic_delta_tropical"
    },
    "bengal": {
        "name": "West Bengal, India",
        "lat": 22.9868,
        "lon": 87.855,
        "zone": "gangetic_delta_tropical"
    },
    "andaman and nicobar": {
        "name": "Andaman & Nicobar Islands, India",
        "lat": 11.7401,
        "lon": 92.6586,
        "zone": "tropical_bay_of_bengal"
    },
    "chandigarh": {
        "name": "Chandigarh, India",
        "lat": 30.7333,
        "lon": 76.7794,
        "zone": "sub_himalayan_shivalik"
    },
    "dadra and nagar haveli": {
        "name": "Dadra & Nagar Haveli, India",
        "lat": 20.1809,
        "lon": 73.0169,
        "zone": "western_coastal_tropical"
    },
    "daman and diu": {
        "name": "Daman & Diu, India",
        "lat": 20.4283,
        "lon": 72.8397,
        "zone": "western_coastal_tropical"
    },
    "delhi": {
        "name": "New Delhi, India",
        "lat": 28.614,
        "lon": 77.209,
        "zone": "subtropical_continental"
    },
    "jammu and kashmir": {
        "name": "Jammu and Kashmir, India",
        "lat": 33.7782,
        "lon": 76.5762,
        "zone": "pir_panjal_himalayan_temperate"
    },
    "kashmir": {
        "name": "Jammu and Kashmir, India",
        "lat": 33.7782,
        "lon": 76.5762,
        "zone": "pir_panjal_himalayan_temperate"
    },
    "ladakh": {
        "name": "Ladakh, India",
        "lat": 34.1526,
        "lon": 77.5771,
        "zone": "high_altitude_cold_desert"
    },
    "lakshadweep": {
        "name": "Lakshadweep, India",
        "lat": 10.5667,
        "lon": 72.6417,
        "zone": "tropical_coral_atoll"
    },
    "puducherry": {
        "name": "Puducherry, India",
        "lat": 11.9416,
        "lon": 79.8083,
        "zone": "coromandel_coastal_tropical"
    },
    "pondicherry": {
        "name": "Puducherry, India",
        "lat": 11.9416,
        "lon": 79.8083,
        "zone": "coromandel_coastal_tropical"
    },
    "ontario": {
        "name": "Ontario, Canada",
        "lat": 51.2538,
        "lon": -85.3232,
        "zone": "great_lakes_boreal"
    },
    "quebec": {
        "name": "Quebec, Canada",
        "lat": 52.9399,
        "lon": -73.5491,
        "zone": "laurentian_boreal"
    },
    "british columbia": {
        "name": "British Columbia, Canada",
        "lat": 53.7267,
        "lon": -127.6476,
        "zone": "pacific_coastal_montane"
    },
    "bc": {
        "name": "British Columbia, Canada",
        "lat": 53.7267,
        "lon": -127.6476,
        "zone": "pacific_coastal_montane"
    },
    "alberta": {
        "name": "Alberta, Canada",
        "lat": 53.9333,
        "lon": -116.5765,
        "zone": "canadian_prairies_montane"
    },
    "manitoba": {
        "name": "Manitoba, Canada",
        "lat": 53.7609,
        "lon": -98.8139,
        "zone": "prairies_subarctic"
    },
    "saskatchewan": {
        "name": "Saskatchewan, Canada",
        "lat": 52.9399,
        "lon": -106.4509,
        "zone": "central_plains_continental"
    },
    "nova scotia": {
        "name": "Nova Scotia, Canada",
        "lat": 44.682,
        "lon": -63.7443,
        "zone": "atlantic_maritime"
    },
    "new brunswick": {
        "name": "New Brunswick, Canada",
        "lat": 46.5653,
        "lon": -66.4619,
        "zone": "atlantic_humid_continental"
    },
    "newfoundland": {
        "name": "Newfoundland, Canada",
        "lat": 53.1355,
        "lon": -57.6604,
        "zone": "subarctic_maritime"
    },
    "prince edward island": {
        "name": "Prince Edward Island, Canada",
        "lat": 46.5107,
        "lon": -63.4168,
        "zone": "maritime_temperate"
    },
    "pei": {
        "name": "Prince Edward Island, Canada",
        "lat": 46.5107,
        "lon": -63.4168,
        "zone": "maritime_temperate"
    },
    "yukon": {
        "name": "Yukon, Canada",
        "lat": 64.2823,
        "lon": -135.0,
        "zone": "subarctic_alpine"
    },
    "northwest territories": {
        "name": "Northwest Territories, Canada",
        "lat": 64.8255,
        "lon": -124.8457,
        "zone": "arctic_tundra"
    },
    "nunavut": {
        "name": "Nunavut, Canada",
        "lat": 70.2998,
        "lon": -83.1076,
        "zone": "polar_tundra"
    },
    "new south wales": {
        "name": "New South Wales, Australia",
        "lat": -31.8402,
        "lon": 145.6128,
        "zone": "temperate_semi_arid"
    },
    "nsw": {
        "name": "New South Wales, Australia",
        "lat": -31.8402,
        "lon": 145.6128,
        "zone": "temperate_semi_arid"
    },
    "victoria": {
        "name": "Victoria, Australia",
        "lat": -37.4713,
        "lon": 144.7852,
        "zone": "temperate_oceanic"
    },
    "queensland": {
        "name": "Queensland, Australia",
        "lat": -20.9176,
        "lon": 142.7028,
        "zone": "subtropical_tropical_savanna"
    },
    "western australia": {
        "name": "Western Australia",
        "lat": -27.6728,
        "lon": 121.6283,
        "zone": "arid_outback_desert"
    },
    "south australia": {
        "name": "South Australia",
        "lat": -30.0002,
        "lon": 136.2092,
        "zone": "mediterranean_arid_steppe"
    },
    "tasmania": {
        "name": "Tasmania, Australia",
        "lat": -42.0409,
        "lon": 146.8087,
        "zone": "cool_temperate_oceanic"
    },
    "northern territory": {
        "name": "Northern Territory, Australia",
        "lat": -19.4914,
        "lon": 132.551,
        "zone": "tropical_monsoon_savanna"
    },
    "act": {
        "name": "Australian Capital Territory",
        "lat": -35.2809,
        "lon": 149.13,
        "zone": "temperate_highland"
    },
    "bavaria": {
        "name": "Bavaria, Germany",
        "lat": 48.7904,
        "lon": 11.4979,
        "zone": "alpine_central_european"
    },
    "saxony": {
        "name": "Saxony, Germany",
        "lat": 51.1045,
        "lon": 13.2017,
        "zone": "central_european_temperate"
    },
    "tuscany": {
        "name": "Tuscany, Italy",
        "lat": 43.7711,
        "lon": 11.2486,
        "zone": "mediterranean_hilly"
    },
    "lombardy": {
        "name": "Lombardy, Italy",
        "lat": 45.4654,
        "lon": 9.1859,
        "zone": "po_valley_humid_subtropical"
    },
    "sicily": {
        "name": "Sicily, Italy",
        "lat": 37.599,
        "lon": 14.0154,
        "zone": "mediterranean_island"
    },
    "andalusia": {
        "name": "Andalusia, Spain",
        "lat": 37.5443,
        "lon": -4.7278,
        "zone": "mediterranean_hot_summer"
    },
    "catalonia": {
        "name": "Catalonia, Spain",
        "lat": 41.5912,
        "lon": 1.5209,
        "zone": "mediterranean_coastal"
    },
    "scotland": {
        "name": "Scotland, UK",
        "lat": 56.4907,
        "lon": -4.2026,
        "zone": "temperate_maritime_highlands"
    },
    "wales": {
        "name": "Wales, UK",
        "lat": 52.1307,
        "lon": -3.7837,
        "zone": "temperate_maritime"
    },
    "england": {
        "name": "England, UK",
        "lat": 52.3555,
        "lon": -1.1743,
        "zone": "temperate_oceanic"
    },
    "northern ireland": {
        "name": "Northern Ireland, UK",
        "lat": 54.7877,
        "lon": -6.4923,
        "zone": "temperate_maritime"
    },
    "afghanistan": {
        "name": "Afghanistan",
        "lat": 33.9391,
        "lon": 67.71,
        "zone": "arid_continental"
    },
    "albania": {
        "name": "Albania",
        "lat": 41.1533,
        "lon": 20.1683,
        "zone": "mediterranean"
    },
    "algeria": {
        "name": "Algeria",
        "lat": 28.0339,
        "lon": 1.6596,
        "zone": "saharan_arid"
    },
    "andorra": {
        "name": "Andorra",
        "lat": 42.5063,
        "lon": 1.5218,
        "zone": "pyrenean_alpine"
    },
    "angola": {
        "name": "Angola",
        "lat": -11.2027,
        "lon": 17.8739,
        "zone": "tropical_savanna"
    },
    "antigua and barbuda": {
        "name": "Antigua and Barbuda",
        "lat": 17.0608,
        "lon": -61.7964,
        "zone": "tropical_caribbean"
    },
    "argentina": {
        "name": "Argentina",
        "lat": -38.4161,
        "lon": -63.6167,
        "zone": "pampas_temperate_patagonia"
    },
    "armenia": {
        "name": "Armenia",
        "lat": 40.0691,
        "lon": 45.0382,
        "zone": "highland_continental"
    },
    "australia": {
        "name": "Australia",
        "lat": -25.2744,
        "lon": 133.7751,
        "zone": "arid_desert_interior"
    },
    "austria": {
        "name": "Austria",
        "lat": 47.5162,
        "lon": 14.5501,
        "zone": "alpine_temperate"
    },
    "azerbaijan": {
        "name": "Azerbaijan",
        "lat": 40.1431,
        "lon": 47.5769,
        "zone": "semi_arid_steppe"
    },
    "bahamas": {
        "name": "Bahamas",
        "lat": 25.0343,
        "lon": -77.3963,
        "zone": "tropical_marine"
    },
    "bahrain": {
        "name": "Bahrain",
        "lat": 26.0667,
        "lon": 50.5577,
        "zone": "arid_gulf_island"
    },
    "bangladesh": {
        "name": "Bangladesh",
        "lat": 23.685,
        "lon": 90.3563,
        "zone": "tropical_monsoon_delta"
    },
    "barbados": {
        "name": "Barbados",
        "lat": 13.1939,
        "lon": -59.5432,
        "zone": "tropical_atlantic"
    },
    "belarus": {
        "name": "Belarus",
        "lat": 53.7098,
        "lon": 27.9534,
        "zone": "humid_continental"
    },
    "belgium": {
        "name": "Belgium",
        "lat": 50.5039,
        "lon": 4.4699,
        "zone": "temperate_maritime"
    },
    "belize": {
        "name": "Belize",
        "lat": 17.1899,
        "lon": -88.4976,
        "zone": "tropical_coastal"
    },
    "benin": {
        "name": "Benin",
        "lat": 9.3077,
        "lon": 2.3158,
        "zone": "tropical_guinean"
    },
    "bhutan": {
        "name": "Bhutan",
        "lat": 27.5142,
        "lon": 90.4336,
        "zone": "eastern_himalayan_montane"
    },
    "bolivia": {
        "name": "Bolivia",
        "lat": -16.2902,
        "lon": -63.5887,
        "zone": "altiplano_amazonian"
    },
    "bosnia and herzegovina": {
        "name": "Bosnia and Herzegovina",
        "lat": 43.9159,
        "lon": 17.6791,
        "zone": "mediterranean_balkan"
    },
    "bosnia": {
        "name": "Bosnia and Herzegovina",
        "lat": 43.9159,
        "lon": 17.6791,
        "zone": "mediterranean_balkan"
    },
    "botswana": {
        "name": "Botswana",
        "lat": -22.3285,
        "lon": 24.6849,
        "zone": "kalahari_semi_arid"
    },
    "brazil": {
        "name": "Brazil",
        "lat": -14.235,
        "lon": -51.9253,
        "zone": "tropical_amazon_cerrado"
    },
    "brunei": {
        "name": "Brunei",
        "lat": 4.5353,
        "lon": 114.7277,
        "zone": "equatorial_borneo"
    },
    "bulgaria": {
        "name": "Bulgaria",
        "lat": 42.7339,
        "lon": 25.4858,
        "zone": "temperate_continental"
    },
    "burkina faso": {
        "name": "Burkina Faso",
        "lat": 12.2383,
        "lon": -1.5616,
        "zone": "sahel_tropical_savanna"
    },
    "burundi": {
        "name": "Burundi",
        "lat": -3.3731,
        "lon": 29.9189,
        "zone": "equatorial_highland"
    },
    "cambodia": {
        "name": "Cambodia",
        "lat": 12.5657,
        "lon": 104.991,
        "zone": "tropical_monsoon_mekong"
    },
    "cameroon": {
        "name": "Cameroon",
        "lat": 7.3697,
        "lon": 12.3547,
        "zone": "tropical_rainforest_savanna"
    },
    "canada": {
        "name": "Canada",
        "lat": 56.1304,
        "lon": -106.3468,
        "zone": "boreal_arctic_temperate"
    },
    "cape verde": {
        "name": "Cabo Verde",
        "lat": 16.0022,
        "lon": -24.0132,
        "zone": "tropical_sahel_atlantic"
    },
    "central african republic": {
        "name": "Central African Republic",
        "lat": 6.6111,
        "lon": 20.9394,
        "zone": "tropical_savanna"
    },
    "chad": {
        "name": "Chad",
        "lat": 15.4542,
        "lon": 18.7322,
        "zone": "sahel_saharan"
    },
    "chile": {
        "name": "Chile",
        "lat": -35.6751,
        "lon": -71.543,
        "zone": "atacama_mediterranean_patagonia"
    },
    "china": {
        "name": "China",
        "lat": 35.8617,
        "lon": 104.1954,
        "zone": "monsoon_continental_tibetan"
    },
    "colombia": {
        "name": "Colombia",
        "lat": 4.5709,
        "lon": -74.2973,
        "zone": "tropical_andean_equatorial"
    },
    "comoros": {
        "name": "Comoros",
        "lat": -11.8753,
        "lon": 43.8722,
        "zone": "tropical_island"
    },
    "congo": {
        "name": "Congo (Brazzaville)",
        "lat": -0.228,
        "lon": 15.8277,
        "zone": "equatorial_congo_basin"
    },
    "costa rica": {
        "name": "Costa Rica",
        "lat": 9.7489,
        "lon": -83.7534,
        "zone": "tropical_neotropical"
    },
    "croatia": {
        "name": "Croatia",
        "lat": 45.1,
        "lon": 15.2,
        "zone": "mediterranean_adriatic"
    },
    "cuba": {
        "name": "Cuba",
        "lat": 21.5218,
        "lon": -77.7812,
        "zone": "tropical_caribbean"
    },
    "cyprus": {
        "name": "Cyprus",
        "lat": 35.1264,
        "lon": 33.4299,
        "zone": "mediterranean_eastern"
    },
    "czech republic": {
        "name": "Czech Republic",
        "lat": 49.8175,
        "lon": 15.473,
        "zone": "central_european_temperate"
    },
    "czechia": {
        "name": "Czech Republic",
        "lat": 49.8175,
        "lon": 15.473,
        "zone": "central_european_temperate"
    },
    "denmark": {
        "name": "Denmark",
        "lat": 56.2639,
        "lon": 9.5018,
        "zone": "temperate_nordic_maritime"
    },
    "djibouti": {
        "name": "Djibouti",
        "lat": 11.8251,
        "lon": 42.5903,
        "zone": "arid_horn_of_africa"
    },
    "dominica": {
        "name": "Dominica",
        "lat": 15.415,
        "lon": -61.371,
        "zone": "caribbean_tropical"
    },
    "dominican republic": {
        "name": "Dominican Republic",
        "lat": 18.7357,
        "lon": -70.1627,
        "zone": "caribbean_tropical"
    },
    "dr congo": {
        "name": "Democratic Republic of the Congo",
        "lat": -4.0383,
        "lon": 21.7587,
        "zone": "congo_rainforest"
    },
    "congo drc": {
        "name": "Democratic Republic of the Congo",
        "lat": -4.0383,
        "lon": 21.7587,
        "zone": "congo_rainforest"
    },
    "ecuador": {
        "name": "Ecuador",
        "lat": -1.8312,
        "lon": -78.1834,
        "zone": "equatorial_andean"
    },
    "egypt": {
        "name": "Egypt",
        "lat": 26.8206,
        "lon": 30.8025,
        "zone": "saharan_nile_arid"
    },
    "el salvador": {
        "name": "El Salvador",
        "lat": 13.7942,
        "lon": -88.8965,
        "zone": "tropical_pacific"
    },
    "equatorial guinea": {
        "name": "Equatorial Guinea",
        "lat": 1.6508,
        "lon": 10.2679,
        "zone": "equatorial_rainforest"
    },
    "eritrea": {
        "name": "Eritrea",
        "lat": 15.1794,
        "lon": 39.7823,
        "zone": "red_sea_semi_arid"
    },
    "estonia": {
        "name": "Estonia",
        "lat": 58.5953,
        "lon": 25.0136,
        "zone": "baltic_humid_continental"
    },
    "eswatini": {
        "name": "Eswatini",
        "lat": -26.5225,
        "lon": 31.4659,
        "zone": "subtropical_highland"
    },
    "ethiopia": {
        "name": "Ethiopia",
        "lat": 9.145,
        "lon": 40.4897,
        "zone": "ethiopian_highlands"
    },
    "fiji": {
        "name": "Fiji",
        "lat": -17.7134,
        "lon": 178.065,
        "zone": "tropical_pacific_archipelago"
    },
    "finland": {
        "name": "Finland",
        "lat": 61.9241,
        "lon": 25.7482,
        "zone": "boreal_subarctic"
    },
    "france": {
        "name": "France",
        "lat": 46.2276,
        "lon": 2.2137,
        "zone": "western_european_temperate"
    },
    "gabon": {
        "name": "Gabon",
        "lat": -0.8037,
        "lon": 11.6094,
        "zone": "equatorial_rainforest"
    },
    "gambia": {
        "name": "Gambia",
        "lat": 13.4432,
        "lon": -15.3101,
        "zone": "tropical_riverine_savanna"
    },
    "germany": {
        "name": "Germany",
        "lat": 51.1657,
        "lon": 10.4515,
        "zone": "central_european_temperate"
    },
    "ghana": {
        "name": "Ghana",
        "lat": 7.9465,
        "lon": -1.0232,
        "zone": "tropical_guinea_savanna"
    },
    "greece": {
        "name": "Greece",
        "lat": 39.0742,
        "lon": 21.8243,
        "zone": "mediterranean_aegean"
    },
    "grenada": {
        "name": "Grenada",
        "lat": 12.1165,
        "lon": -61.679,
        "zone": "caribbean_tropical"
    },
    "guatemala": {
        "name": "Guatemala",
        "lat": 15.7835,
        "lon": -90.2308,
        "zone": "central_american_tropical"
    },
    "guinea": {
        "name": "Guinea",
        "lat": 9.9456,
        "lon": -9.6966,
        "zone": "west_african_tropical"
    },
    "guinea-bissau": {
        "name": "Guinea-Bissau",
        "lat": 11.8037,
        "lon": -15.1804,
        "zone": "tropical_savanna"
    },
    "guyana": {
        "name": "Guyana",
        "lat": 4.8604,
        "lon": -58.9302,
        "zone": "amazonian_coastal_tropical"
    },
    "haiti": {
        "name": "Haiti",
        "lat": 18.9712,
        "lon": -72.2852,
        "zone": "caribbean_tropical"
    },
    "honduras": {
        "name": "Honduras",
        "lat": 15.2,
        "lon": -86.2419,
        "zone": "central_american_tropical"
    },
    "hungary": {
        "name": "Hungary",
        "lat": 47.1625,
        "lon": 19.5033,
        "zone": "pannonian_continental"
    },
    "iceland": {
        "name": "Iceland",
        "lat": 64.9631,
        "lon": -19.0208,
        "zone": "subpolar_oceanic"
    },
    "india": {
        "name": "India",
        "lat": 20.5937,
        "lon": 78.9629,
        "zone": "tropical_monsoon_peninsular"
    },
    "indonesia": {
        "name": "Indonesia",
        "lat": -0.7893,
        "lon": 113.9213,
        "zone": "equatorial_archipelago"
    },
    "iran": {
        "name": "Iran",
        "lat": 32.4279,
        "lon": 53.688,
        "zone": "iranian_plateau_arid"
    },
    "iraq": {
        "name": "Iraq",
        "lat": 33.2232,
        "lon": 43.6793,
        "zone": "mesopotamian_arid_desert"
    },
    "ireland": {
        "name": "Ireland",
        "lat": 53.1424,
        "lon": -7.6921,
        "zone": "temperate_maritime"
    },
    "israel": {
        "name": "Israel",
        "lat": 31.0461,
        "lon": 34.8516,
        "zone": "mediterranean_desert"
    },
    "italy": {
        "name": "Italy",
        "lat": 41.8719,
        "lon": 12.5674,
        "zone": "mediterranean_peninsular"
    },
    "ivory coast": {
        "name": "Ivory Coast",
        "lat": 7.54,
        "lon": -5.5471,
        "zone": "tropical_savanna"
    },
    "jamaica": {
        "name": "Jamaica",
        "lat": 18.1096,
        "lon": -77.2975,
        "zone": "caribbean_tropical"
    },
    "japan": {
        "name": "Japan",
        "lat": 36.2048,
        "lon": 138.2529,
        "zone": "temperate_pacific_island"
    },
    "jordan": {
        "name": "Jordan",
        "lat": 30.5852,
        "lon": 36.2384,
        "zone": "arid_arabian_desert"
    },
    "kazakhstan": {
        "name": "Kazakhstan",
        "lat": 48.0196,
        "lon": 66.9237,
        "zone": "eurasian_steppe_continental"
    },
    "kenya": {
        "name": "Kenya",
        "lat": -0.0236,
        "lon": 37.9062,
        "zone": "equatorial_east_african_rift"
    },
    "kiribati": {
        "name": "Kiribati",
        "lat": -3.3704,
        "lon": -168.734,
        "zone": "pacific_equatorial_atolls"
    },
    "kuwait": {
        "name": "Kuwait",
        "lat": 29.3117,
        "lon": 47.4818,
        "zone": "hyper_arid_gulf"
    },
    "kyrgyzstan": {
        "name": "Kyrgyzstan",
        "lat": 41.2044,
        "lon": 74.7661,
        "zone": "tian_shan_alpine_continental"
    },
    "laos": {
        "name": "Laos",
        "lat": 19.8563,
        "lon": 102.4955,
        "zone": "tropical_monsoon_mekong"
    },
    "latvia": {
        "name": "Latvia",
        "lat": 56.8796,
        "lon": 24.6032,
        "zone": "baltic_humid_continental"
    },
    "lebanon": {
        "name": "Lebanon",
        "lat": 33.8547,
        "lon": 35.8623,
        "zone": "eastern_mediterranean_montane"
    },
    "lesotho": {
        "name": "Lesotho",
        "lat": -29.6099,
        "lon": 28.2336,
        "zone": "drakensberg_alpine"
    },
    "liberia": {
        "name": "Liberia",
        "lat": 6.4281,
        "lon": -9.4295,
        "zone": "west_african_rainforest"
    },
    "libya": {
        "name": "Libya",
        "lat": 26.3351,
        "lon": 17.2283,
        "zone": "saharan_hyper_arid"
    },
    "liechtenstein": {
        "name": "Liechtenstein",
        "lat": 47.166,
        "lon": 9.5554,
        "zone": "alpine_rhine_valley"
    },
    "lithuania": {
        "name": "Lithuania",
        "lat": 55.1694,
        "lon": 23.8813,
        "zone": "baltic_humid_continental"
    },
    "luxembourg": {
        "name": "Luxembourg",
        "lat": 49.8153,
        "lon": 6.1296,
        "zone": "western_european_temperate"
    },
    "madagascar": {
        "name": "Madagascar",
        "lat": -18.7669,
        "lon": 46.8691,
        "zone": "tropical_island_endemic"
    },
    "malawi": {
        "name": "Malawi",
        "lat": -13.2543,
        "lon": 34.3015,
        "zone": "east_african_rift_savanna"
    },
    "malaysia": {
        "name": "Malaysia",
        "lat": 4.2105,
        "lon": 101.9758,
        "zone": "equatorial_rainforest"
    },
    "maldives": {
        "name": "Maldives",
        "lat": 3.2028,
        "lon": 73.2207,
        "zone": "equatorial_indian_ocean_atolls"
    },
    "mali": {
        "name": "Mali",
        "lat": 17.5707,
        "lon": -3.9962,
        "zone": "sahel_saharan_desert"
    },
    "malta": {
        "name": "Malta",
        "lat": 35.9375,
        "lon": 14.3754,
        "zone": "mediterranean_archipelago"
    },
    "marshall islands": {
        "name": "Marshall Islands",
        "lat": 7.1315,
        "lon": 171.1845,
        "zone": "micronesian_atolls"
    },
    "mauritania": {
        "name": "Mauritania",
        "lat": 21.0079,
        "lon": -10.9408,
        "zone": "saharan_atlantic_desert"
    },
    "mauritius": {
        "name": "Mauritius",
        "lat": -20.3484,
        "lon": 57.5522,
        "zone": "tropical_mascarene_island"
    },
    "mexico": {
        "name": "Mexico",
        "lat": 23.6345,
        "lon": -102.5528,
        "zone": "mesoamerican_arid_tropical"
    },
    "micronesia": {
        "name": "Micronesia",
        "lat": 7.4256,
        "lon": 150.5508,
        "zone": "tropical_oceanic"
    },
    "moldova": {
        "name": "Moldova",
        "lat": 47.4116,
        "lon": 28.3699,
        "zone": "eastern_european_continental"
    },
    "monaco": {
        "name": "Monaco",
        "lat": 43.7384,
        "lon": 7.4246,
        "zone": "mediterranean_riviera"
    },
    "mongolia": {
        "name": "Mongolia",
        "lat": 46.8625,
        "lon": 103.8467,
        "zone": "gobi_central_asian_steppe"
    },
    "montenegro": {
        "name": "Montenegro",
        "lat": 42.7087,
        "lon": 19.3744,
        "zone": "dinaric_mediterranean"
    },
    "morocco": {
        "name": "Morocco",
        "lat": 31.7917,
        "lon": -7.0926,
        "zone": "atlas_mediterranean_saharan"
    },
    "mozambique": {
        "name": "Mozambique",
        "lat": -18.6657,
        "lon": 35.5296,
        "zone": "tropical_savanna_coastal"
    },
    "myanmar": {
        "name": "Myanmar (Burma)",
        "lat": 21.9162,
        "lon": 95.956,
        "zone": "tropical_monsoon_irrawaddy"
    },
    "burma": {
        "name": "Myanmar (Burma)",
        "lat": 21.9162,
        "lon": 95.956,
        "zone": "tropical_monsoon_irrawaddy"
    },
    "namibia": {
        "name": "Namibia",
        "lat": -22.9576,
        "lon": 18.4904,
        "zone": "namib_kalahari_hyper_arid"
    },
    "nauru": {
        "name": "Nauru",
        "lat": -0.5228,
        "lon": 166.9315,
        "zone": "equatorial_pacific_island"
    },
    "nepal": {
        "name": "Nepal",
        "lat": 28.3949,
        "lon": 84.124,
        "zone": "himalayan_montane_terai"
    },
    "netherlands": {
        "name": "Netherlands",
        "lat": 52.1326,
        "lon": 5.2913,
        "zone": "lowlands_temperate_maritime"
    },
    "holland": {
        "name": "Netherlands",
        "lat": 52.1326,
        "lon": 5.2913,
        "zone": "lowlands_temperate_maritime"
    },
    "new zealand": {
        "name": "New Zealand",
        "lat": -40.9006,
        "lon": 174.886,
        "zone": "temperate_maritime_oceanic"
    },
    "nicaragua": {
        "name": "Nicaragua",
        "lat": 12.8654,
        "lon": -85.2072,
        "zone": "tropical_central_american"
    },
    "niger": {
        "name": "Niger",
        "lat": 17.6078,
        "lon": 8.0817,
        "zone": "sahel_tenere_desert"
    },
    "nigeria": {
        "name": "Nigeria",
        "lat": 9.082,
        "lon": 8.6753,
        "zone": "tropical_guinean_savanna"
    },
    "north korea": {
        "name": "North Korea",
        "lat": 40.3399,
        "lon": 127.5101,
        "zone": "humid_continental_monsoon"
    },
    "north macedonia": {
        "name": "North Macedonia",
        "lat": 41.6086,
        "lon": 21.7453,
        "zone": "balkan_continental"
    },
    "norway": {
        "name": "Norway",
        "lat": 60.472,
        "lon": 8.4689,
        "zone": "scandinavian_fjord_subpolar"
    },
    "oman": {
        "name": "Oman",
        "lat": 21.5126,
        "lon": 55.9233,
        "zone": "arabian_desert_monsoon"
    },
    "pakistan": {
        "name": "Pakistan",
        "lat": 30.3753,
        "lon": 69.3451,
        "zone": "indus_basin_arid_montane"
    },
    "palau": {
        "name": "Palau",
        "lat": 7.515,
        "lon": 134.5825,
        "zone": "tropical_pacific_archipelago"
    },
    "palestine": {
        "name": "Palestine",
        "lat": 31.9522,
        "lon": 35.2332,
        "zone": "mediterranean_desert"
    },
    "panama": {
        "name": "Panama",
        "lat": 8.5379,
        "lon": -80.7821,
        "zone": "tropical_isthmus"
    },
    "papua new guinea": {
        "name": "Papua New Guinea",
        "lat": -6.315,
        "lon": 143.9555,
        "zone": "equatorial_highlands_oceanic"
    },
    "paraguay": {
        "name": "Paraguay",
        "lat": -23.4425,
        "lon": -58.4438,
        "zone": "gran_chaco_subtropical"
    },
    "peru": {
        "name": "Peru",
        "lat": -9.1899,
        "lon": -75.0152,
        "zone": "andean_pacific_amazonian"
    },
    "philippines": {
        "name": "Philippines",
        "lat": 12.8797,
        "lon": 121.774,
        "zone": "tropical_maritime_archipelago"
    },
    "poland": {
        "name": "Poland",
        "lat": 51.9194,
        "lon": 19.1451,
        "zone": "central_european_continental"
    },
    "portugal": {
        "name": "Portugal",
        "lat": 39.3999,
        "lon": -8.2245,
        "zone": "mediterranean_atlantic"
    },
    "qatar": {
        "name": "Qatar",
        "lat": 25.3548,
        "lon": 51.1839,
        "zone": "hyper_arid_gulf_peninsula"
    },
    "romania": {
        "name": "Romania",
        "lat": 45.9432,
        "lon": 24.9668,
        "zone": "carpathian_temperate_continental"
    },
    "russia": {
        "name": "Russia",
        "lat": 61.524,
        "lon": 105.3188,
        "zone": "subarctic_boreal_eurasian"
    },
    "rwanda": {
        "name": "Rwanda",
        "lat": -1.9403,
        "lon": 29.8739,
        "zone": "equatorial_albertine_rift"
    },
    "saint kitts and nevis": {
        "name": "Saint Kitts and Nevis",
        "lat": 17.3578,
        "lon": -62.783,
        "zone": "caribbean_tropical"
    },
    "saint lucia": {
        "name": "Saint Lucia",
        "lat": 13.9094,
        "lon": -60.9789,
        "zone": "caribbean_tropical"
    },
    "saint vincent": {
        "name": "Saint Vincent & Grenadines",
        "lat": 13.2528,
        "lon": -61.1971,
        "zone": "caribbean_tropical"
    },
    "samoa": {
        "name": "Samoa",
        "lat": -13.759,
        "lon": -172.1046,
        "zone": "polynesian_tropical"
    },
    "san marino": {
        "name": "San Marino",
        "lat": 43.9424,
        "lon": 12.4578,
        "zone": "apennine_mediterranean"
    },
    "sao tome and principe": {
        "name": "Sao Tome and Principe",
        "lat": 0.1864,
        "lon": 6.6131,
        "zone": "equatorial_atlantic"
    },
    "saudi arabia": {
        "name": "Saudi Arabia",
        "lat": 23.8859,
        "lon": 45.0792,
        "zone": "arabian_desert_hyper_arid"
    },
    "senegal": {
        "name": "Senegal",
        "lat": 14.4974,
        "lon": -14.4524,
        "zone": "sahel_coastal_savanna"
    },
    "serbia": {
        "name": "Serbia",
        "lat": 44.0165,
        "lon": 21.0059,
        "zone": "danube_balkan_continental"
    },
    "seychelles": {
        "name": "Seychelles",
        "lat": -4.6796,
        "lon": 55.492,
        "zone": "granitic_tropical_indian_ocean"
    },
    "sierra leone": {
        "name": "Sierra Leone",
        "lat": 8.4606,
        "lon": -11.7799,
        "zone": "west_african_tropical_monsoon"
    },
    "singapore": {
        "name": "Singapore",
        "lat": 1.3521,
        "lon": 103.8198,
        "zone": "equatorial_rainforest_urban"
    },
    "slovakia": {
        "name": "Slovakia",
        "lat": 48.669,
        "lon": 19.699,
        "zone": "carpathian_continental"
    },
    "slovenia": {
        "name": "Slovenia",
        "lat": 46.1512,
        "lon": 14.9955,
        "zone": "alpine_sub_mediterranean"
    },
    "solomon islands": {
        "name": "Solomon Islands",
        "lat": -9.6457,
        "lon": 160.1562,
        "zone": "tropical_oceanic_rainforest"
    },
    "somalia": {
        "name": "Somalia",
        "lat": 5.1521,
        "lon": 46.1996,
        "zone": "arid_horn_of_africa"
    },
    "south africa": {
        "name": "South Africa",
        "lat": -30.5595,
        "lon": 22.9375,
        "zone": "subtropical_veldt_karoo"
    },
    "south korea": {
        "name": "South Korea",
        "lat": 35.9078,
        "lon": 127.7669,
        "zone": "east_asian_humid_continental"
    },
    "south sudan": {
        "name": "South Sudan",
        "lat": 6.877,
        "lon": 31.307,
        "zone": "sudd_tropical_savanna"
    },
    "spain": {
        "name": "Spain",
        "lat": 40.4637,
        "lon": -3.7492,
        "zone": "iberian_mediterranean_semi_arid"
    },
    "sri lanka": {
        "name": "Sri Lanka",
        "lat": 7.8731,
        "lon": 80.7718,
        "zone": "tropical_monsoon_island"
    },
    "sudan": {
        "name": "Sudan",
        "lat": 12.8628,
        "lon": 30.2176,
        "zone": "sahel_saharan_savanna"
    },
    "suriname": {
        "name": "Suriname",
        "lat": 3.9193,
        "lon": -56.0278,
        "zone": "amazonian_guiana_shield"
    },
    "sweden": {
        "name": "Sweden",
        "lat": 60.1282,
        "lon": 18.6435,
        "zone": "boreal_nordic_temperate"
    },
    "switzerland": {
        "name": "Switzerland",
        "lat": 46.8182,
        "lon": 8.2275,
        "zone": "central_alpine"
    },
    "syria": {
        "name": "Syria",
        "lat": 34.8021,
        "lon": 38.9968,
        "zone": "levantine_semi_arid"
    },
    "taiwan": {
        "name": "Taiwan",
        "lat": 23.6978,
        "lon": 120.9605,
        "zone": "subtropical_island_typhoon"
    },
    "tajikistan": {
        "name": "Tajikistan",
        "lat": 38.861,
        "lon": 71.2761,
        "zone": "pamir_highland_alpine"
    },
    "tanzania": {
        "name": "Tanzania",
        "lat": -6.369,
        "lon": 34.8888,
        "zone": "serengeti_rift_savanna"
    },
    "thailand": {
        "name": "Thailand",
        "lat": 15.87,
        "lon": 100.9925,
        "zone": "tropical_monsoon_chao_phraya"
    },
    "timor-leste": {
        "name": "Timor-Leste",
        "lat": -8.8742,
        "lon": 125.7275,
        "zone": "tropical_savanna_island"
    },
    "togo": {
        "name": "Togo",
        "lat": 8.6195,
        "lon": 0.8248,
        "zone": "dahomey_gap_savanna"
    },
    "tonga": {
        "name": "Tonga",
        "lat": -21.1789,
        "lon": -175.1982,
        "zone": "polynesian_tropical"
    },
    "trinidad and tobago": {
        "name": "Trinidad and Tobago",
        "lat": 10.6918,
        "lon": -61.2225,
        "zone": "caribbean_tropical"
    },
    "tunisia": {
        "name": "Tunisia",
        "lat": 33.8869,
        "lon": 9.5375,
        "zone": "mediterranean_saharan"
    },
    "turkey": {
        "name": "Turkey",
        "lat": 38.9637,
        "lon": 35.2433,
        "zone": "anatolian_plateau_mediterranean"
    },
    "turkmenistan": {
        "name": "Turkmenistan",
        "lat": 38.9697,
        "lon": 59.5563,
        "zone": "karakum_hyper_arid"
    },
    "tuvalu": {
        "name": "Tuvalu",
        "lat": -7.1095,
        "lon": 177.6493,
        "zone": "equatorial_atolls"
    },
    "uganda": {
        "name": "Uganda",
        "lat": 1.3733,
        "lon": 32.2903,
        "zone": "lake_victoria_equatorial"
    },
    "ukraine": {
        "name": "Ukraine",
        "lat": 48.3794,
        "lon": 31.1656,
        "zone": "pontic_steppe_continental"
    },
    "united arab emirates": {
        "name": "United Arab Emirates",
        "lat": 23.4241,
        "lon": 53.8478,
        "zone": "hyper_arid_gulf_desert"
    },
    "uae": {
        "name": "United Arab Emirates",
        "lat": 23.4241,
        "lon": 53.8478,
        "zone": "hyper_arid_gulf_desert"
    },
    "united kingdom": {
        "name": "United Kingdom",
        "lat": 55.3781,
        "lon": -3.436,
        "zone": "temperate_maritime_oceanic"
    },
    "uk": {
        "name": "United Kingdom",
        "lat": 55.3781,
        "lon": -3.436,
        "zone": "temperate_maritime_oceanic"
    },
    "britain": {
        "name": "United Kingdom",
        "lat": 55.3781,
        "lon": -3.436,
        "zone": "temperate_maritime_oceanic"
    },
    "united states": {
        "name": "United States of America",
        "lat": 37.0902,
        "lon": -95.7129,
        "zone": "temperate_continental"
    },
    "usa": {
        "name": "United States of America",
        "lat": 37.0902,
        "lon": -95.7129,
        "zone": "temperate_continental"
    },
    "america": {
        "name": "United States of America",
        "lat": 37.0902,
        "lon": -95.7129,
        "zone": "temperate_continental"
    },
    "uruguay": {
        "name": "Uruguay",
        "lat": -32.5228,
        "lon": -55.7658,
        "zone": "pampas_temperate_subtropical"
    },
    "uzbekistan": {
        "name": "Uzbekistan",
        "lat": 41.3775,
        "lon": 64.5853,
        "zone": "kyzylkum_continental_arid"
    },
    "vanuatu": {
        "name": "Vanuatu",
        "lat": -15.3767,
        "lon": 166.9592,
        "zone": "tropical_oceanic"
    },
    "vatican city": {
        "name": "Vatican City",
        "lat": 41.9029,
        "lon": 12.4534,
        "zone": "mediterranean_urban"
    },
    "venezuela": {
        "name": "Venezuela",
        "lat": 6.4238,
        "lon": -66.5897,
        "zone": "llanos_orinoco_tropical"
    },
    "vietnam": {
        "name": "Vietnam",
        "lat": 14.0583,
        "lon": 108.2772,
        "zone": "tropical_monsoon_coastal"
    },
    "yemen": {
        "name": "Yemen",
        "lat": 15.5527,
        "lon": 48.5164,
        "zone": "arid_arabian_highlands"
    },
    "zambia": {
        "name": "Zambia",
        "lat": -13.1339,
        "lon": 27.8493,
        "zone": "miombo_savanna_plateau"
    },
    "zimbabwe": {
        "name": "Zimbabwe",
        "lat": -19.0154,
        "lon": 29.1549,
        "zone": "highveld_subtropical_savanna"
    },
    "greenland": {
        "name": "Greenland",
        "lat": 71.7069,
        "lon": -42.6043,
        "zone": "polar_ice_sheet"
    },
    "antarctica": {
        "name": "Antarctica",
        "lat": -82.8628,
        "lon": 135.0,
        "zone": "polar_ice_cap"
    },
    "siberia": {
        "name": "Siberia, Russia",
        "lat": 60.0,
        "lon": 100.0,
        "zone": "subarctic_taiga"
    },
    "sahara": {
        "name": "Sahara Desert",
        "lat": 23.4162,
        "lon": 25.6628,
        "zone": "hyper_arid_desert"
    },
    "sahel": {
        "name": "Sahel Belt, Africa",
        "lat": 14.5,
        "lon": 1.5,
        "zone": "semi_arid_transition"
    },
    "amazon": {
        "name": "Amazon Basin, South America",
        "lat": -3.4653,
        "lon": -62.2159,
        "zone": "equatorial_rainforest"
    },
    "atacama": {
        "name": "Atacama Desert, Chile",
        "lat": -23.8634,
        "lon": -69.1328,
        "zone": "hyper_arid_rain_shadow"
    },
    "death valley": {
        "name": "Death Valley, California",
        "lat": 36.5323,
        "lon": -116.9325,
        "zone": "extreme_arid_basin"
    },
    "hokkaido": {
        "name": "Hokkaido, Japan",
        "lat": 43.2203,
        "lon": 142.8635,
        "zone": "subarctic_temperate"
    },
    "okinawa": {
        "name": "Okinawa, Japan",
        "lat": 26.2124,
        "lon": 127.6809,
        "zone": "subtropical_island"
    },
    "sichuan": {
        "name": "Sichuan Basin, China",
        "lat": 30.6517,
        "lon": 104.0764,
        "zone": "subtropical_humid_basin"
    },
    "xinjiang": {
        "name": "Xinjiang, China",
        "lat": 41.1129,
        "lon": 85.2401,
        "zone": "continental_arid_tarim_basin"
    },
    "tibet": {
        "name": "Tibetan Plateau",
        "lat": 31.6927,
        "lon": 88.0924,
        "zone": "alpine_high_plateau"
    },
    "bahia": {
        "name": "Bahia, Brazil",
        "lat": -12.5797,
        "lon": -41.7007,
        "zone": "caatinga_semi_arid_tropical"
    },
    "minas gerais": {
        "name": "Minas Gerais, Brazil",
        "lat": -18.5122,
        "lon": -44.555,
        "zone": "cerrado_tropical_highland"
    },
    "patagonia": {
        "name": "Patagonia, South America",
        "lat": -47.0,
        "lon": -70.0,
        "zone": "subpolar_steppe"
    },
    "marathwada": {
        "name": "Marathwada, India",
        "lat": 19.25,
        "lon": 76.25,
        "zone": "deccan_plateau_rain_shadow"
    },
    "rondonia": {
        "name": "Rondônia, Brazil",
        "lat": -10.88,
        "lon": -61.93,
        "zone": "amazon_deforestation_arc"
    },
    "northeast india": {
        "name": "Northeast India",
        "lat": 25.57,
        "lon": 91.89,
        "zone": "monsoon_floodplain"
    },
    "cherrapunji": {
        "name": "Cherrapunji, Meghalaya, India",
        "lat": 25.27,
        "lon": 91.73,
        "zone": "orographic_monsoon"
    },
    "mumbai": {
        "name": "Mumbai, Maharashtra, India",
        "lat": 19.076,
        "lon": 72.8777,
        "zone": "coastal_monsoon"
    },
    "pune": {
        "name": "Pune, Maharashtra, India",
        "lat": 18.5204,
        "lon": 73.8567,
        "zone": "leeward_western_ghats"
    },
    "aurangabad": {
        "name": "Chhatrapati Sambhajinagar (Aurangabad), India",
        "lat": 19.8762,
        "lon": 75.3433,
        "zone": "marathwada_semi_arid"
    },
    "nagpur": {
        "name": "Nagpur, Maharashtra, India",
        "lat": 21.1458,
        "lon": 79.0882,
        "zone": "central_india_plateau"
    }
}

import math

def get_world_location(query_token: str) -> Optional[Dict[str, Any]]:
    clean = query_token.strip().lower()
    if clean in WORLD_GAZETTEER:
        loc = WORLD_GAZETTEER[clean].copy()
        loc["query_token"] = clean
        return loc
    return None

def reverse_geocode(lat: float, lon: float, max_degrees: float = 6.0) -> Optional[Dict[str, Any]]:
    """
    Finds the closest geographic entity in WORLD_GAZETTEER within max_degrees.
    Uses equirectangular approximation for fast local distance calculation.
    """
    best_loc = None
    min_dist = float('inf')
    for token, entry in WORLD_GAZETTEER.items():
        e_lat = entry.get('lat')
        e_lon = entry.get('lon')
        if e_lat is None or e_lon is None:
            continue
        lat_diff = lat - e_lat
        lon_diff = (lon - e_lon) * math.cos(math.radians((lat + e_lat) / 2.0))
        dist = math.hypot(lat_diff, lon_diff)
        if dist < min_dist:
            min_dist = dist
            best_loc = entry.copy()
            best_loc["distance_deg"] = round(dist, 4)
            best_loc["query_token"] = token
            
    if best_loc and min_dist <= max_degrees:
        return best_loc
    return None
