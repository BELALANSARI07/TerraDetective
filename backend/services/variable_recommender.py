"""
TerraDetective Guided 'Variable Detective' Recommender
NASA Space Apps Challenge: 'Be An Earth System Trend Detective!'

Assists students, educators, and citizen scientists in identifying
the right NASA Earth Observation variables and preset Mystery Cases based on:
1. Environment type (e.g. 'Forest / Deforestation', 'Farmland / Irrigation', 'Monsoon / River Basin')
2. Environmental symptom (e.g. 'Rising Surface Heat', 'Plant Greenness', 'Extreme Rainfall')
3. Observation timeframe (e.g. 10, 20, 25 years)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("terradetective.variable_recommender")

SUPPORTED_ENVIRONMENTS = [
    "Forest / Deforestation",
    "Farmland / Irrigation",
    "Monsoon / River Basin",
    "Arid / Rain Shadow",
    "Urban / Built Environment",
    "Global / Macro Climate",
]

SUPPORTED_SYMPTOMS = [
    "Rising Surface Heat (Ground Skin Temperature)",
    "Plant Greenness & Canopy Health (Vegetation Loss or Greening)",
    "Extreme Rainfall & Monsoon Disparity (Flooding vs. Rain Shadow)",
    "Soil Moisture & Root-Zone Water Stress",
    "Atmospheric Warming (2-Meter Air Temperature)",
    "Solar Radiation & Surface Sunlight",
]

# ---------------------------------------------------------------------------
# Variable Master Catalog Definitions
# ---------------------------------------------------------------------------
VARIABLE_METADATA = {
    "MOD11A2": {
        "variable_id": "MOD11A2",
        "variable_code": "MOD11A2_061_LST_Day_1km",
        "common_name": "Daytime Land Surface Temperature (LST)",
        "satellite_platform": "NASA Terra Satellite / MODIS Spectroradiometer (1 km resolution)",
        "unit": "°C (Degrees Celsius)",
        "alternatives": [
            {"variable_id": "T2M", "name": "NASA POWER 2m Air Temperature", "unit": "°C"},
            {"variable_id": "GWETROOT", "name": "NASA GLDAS Root-Zone Soil Moisture", "unit": "fraction"},
        ],
    },
    "MOD13A3": {
        "variable_id": "MOD13A3",
        "variable_code": "MOD13A3_061__1_km_monthly_NDVI",
        "common_name": "Normalized Difference Vegetation Index (NDVI)",
        "satellite_platform": "NASA Terra Satellite / MODIS Spectroradiometer (1 km monthly)",
        "unit": "index (0.0 to 1.0)",
        "alternatives": [
            {"variable_id": "MOD11A2", "name": "MODIS Daytime Land Surface Temperature", "unit": "°C"},
            {"variable_id": "GWETROOT", "name": "NASA GLDAS Root-Zone Soil Moisture", "unit": "fraction"},
        ],
    },
    "GPM_3IMERGM_07": {
        "variable_id": "GPM_3IMERGM_07",
        "variable_code": "mean_GPM_3IMERGM_07_precipitation",
        "common_name": "Monthly Precipitation Accumulation",
        "satellite_platform": "NASA Global Precipitation Measurement (GPM) Core Observatory & Satellite Constellation",
        "unit": "mm/month",
        "alternatives": [
            {"variable_id": "PRECTOTCORR", "name": "NASA POWER Bias-Corrected Precipitation", "unit": "mm/month"},
            {"variable_id": "GWETTOP", "name": "NASA GLDAS Surface Soil Wetness (0-5cm)", "unit": "fraction"},
        ],
    },
    "GWETROOT": {
        "variable_id": "GWETROOT",
        "variable_code": "GWETROOT",
        "common_name": "Root-Zone Soil Wetness (0-100cm)",
        "satellite_platform": "NASA GLDAS / MERRA-2 Catchment Land Surface Model",
        "unit": "fraction (0.0 to 1.0)",
        "alternatives": [
            {"variable_id": "GWETPROF", "name": "Profile Groundwater Wetness", "unit": "fraction"},
            {"variable_id": "PRECTOTCORR", "name": "NASA POWER Precipitation", "unit": "mm/month"},
        ],
    },
    "T2M": {
        "variable_id": "T2M",
        "variable_code": "T2M",
        "common_name": "2-Meter Ambient Air Temperature",
        "satellite_platform": "NASA MERRA-2 Atmospheric Reanalysis (NASA POWER)",
        "unit": "°C (Degrees Celsius)",
        "alternatives": [
            {"variable_id": "T2M_MAX", "name": "Daily Maximum Air Temperature", "unit": "°C"},
            {"variable_id": "ALLSKY_SFC_SW_DWN", "name": "Solar Downward Irradiance", "unit": "MJ/m^2/day"},
        ],
    },
    "ALLSKY_SFC_SW_DWN": {
        "variable_id": "ALLSKY_SFC_SW_DWN",
        "variable_code": "ALLSKY_SFC_SW_DWN",
        "common_name": "Solar Downward Surface Irradiance",
        "satellite_platform": "NASA CERES / MERRA-2 Solar Radiative Flux",
        "unit": "MJ/m^2/day",
        "alternatives": [
            {"variable_id": "T2M", "name": "NASA POWER 2m Air Temperature", "unit": "°C"},
            {"variable_id": "MOD11A2", "name": "MODIS Daytime Land Surface Temperature", "unit": "°C"},
        ],
    },
}

# ---------------------------------------------------------------------------
# Dynamic Contextual Mapping for (Environment, Symptom) Pairs
# ---------------------------------------------------------------------------
PAIR_RECOMMENDATION_MAP: Dict[Tuple[str, str], Dict[str, Any]] = {
    # 1. Forest / Deforestation
    ("forest", "surface_heat"): {
        "variable_id": "MOD11A2",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures radiant skin temperature, exposing how removing forest canopy eliminates natural evaporative cooling.",
        "detective_prompt_tip": "Compare the dry season months (August–October) in Rondônia to observe how deforestation turns solar radiation into blistering sensible ground heat.",
    },
    ("forest", "plant_greenness"): {
        "variable_id": "MOD13A3",
        "matched_case_id": "case_3_vegetation_paradox",
        "case_title": "Vegetation Greenness Paradox: Fragile Forests vs. Human-Engineered Greening",
        "plain_english_definition": "Measures photosynthetic canopy density, quantifying the structural loss of primary tropical rainforest from logging and clearing.",
        "detective_prompt_tip": "Observe multi-decadal canopy degradation along deforestation frontiers.",
    },
    ("forest", "extreme_rainfall"): {
        "variable_id": "GPM_3IMERGM_07",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures monthly rainfall totals, evaluating whether large-scale forest loss is reducing biogenic moisture recycling and convective downpours.",
        "detective_prompt_tip": "Look for shifts in wet-season onset and overall monthly rain accumulation over cleared forest tracts.",
    },
    ("forest", "soil_moisture"): {
        "variable_id": "GWETROOT",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures root-zone moisture reserves, tracking how forest clearance desiccates upper soil strata through direct solar exposure.",
        "detective_prompt_tip": "Track moisture loss in root-zone strata following logging events.",
    },
    ("forest", "atmospheric_warming"): {
        "variable_id": "T2M",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures 2-meter ambient air temperature, detecting broader tropospheric heating above clear-cut forest landscapes.",
        "detective_prompt_tip": "Compare air temperature against surface skin temperature to measure boundary-layer heat divergence.",
    },
    ("forest", "solar_radiation"): {
        "variable_id": "ALLSKY_SFC_SW_DWN",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures downward surface solar radiation reaching stripped ground, tracking radiative flux changes once protective forest foliage is cleared.",
        "detective_prompt_tip": "Examine how stripped ground absorbs maximum incoming solar irradiance compared to adjacent intact canopy.",
    },

    # 2. Farmland / Irrigation
    ("farmland", "surface_heat"): {
        "variable_id": "MOD11A2",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures radiant skin temperature, demonstrating how intensive canal flooding and crop transpiration create cooling thermal anomalies.",
        "detective_prompt_tip": "Notice the strong evaporative cooling signature over Punjab during peak irrigation cycles compared to adjacent desert terrain.",
    },
    ("farmland", "plant_greenness"): {
        "variable_id": "MOD13A3",
        "matched_case_id": "case_3_vegetation_paradox",
        "case_title": "Vegetation Greenness Paradox: Fragile Forests vs. Human-Engineered Greening",
        "plain_english_definition": "Measures photosynthetic capacity, tracking how human-engineered irrigation and fertilizers create artificial greening peaks.",
        "detective_prompt_tip": "Look for the two annual greenness peaks in Punjab (wheat in March, rice in September) contrasting with natural ecosystems.",
    },
    ("farmland", "extreme_rainfall"): {
        "variable_id": "GPM_3IMERGM_07",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures precipitation totals across agricultural breadbaskets, contrasting natural monsoon inputs against irrigation dependency.",
        "detective_prompt_tip": "Assess whether crop water demand is met by natural precipitation or groundwater pumping.",
    },
    ("farmland", "soil_moisture"): {
        "variable_id": "GWETROOT",
        "matched_case_id": "case_3_vegetation_paradox",
        "case_title": "Vegetation Greenness Paradox: Fragile Forests vs. Human-Engineered Greening",
        "plain_english_definition": "Measures root-zone moisture saturation, quantifying agricultural aquifer drawdown and irrigation recharge dynamics.",
        "detective_prompt_tip": "Analyze root-zone moisture peaks during winter and monsoon irrigation intervals.",
    },
    ("farmland", "atmospheric_warming"): {
        "variable_id": "T2M",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures 2-meter air temperature, showing how regional irrigation cools boundary-layer air compared to uncultivated surroundings.",
        "detective_prompt_tip": "Inspect decadal air temperature trends over heavily irrigated river basins.",
    },
    ("farmland", "solar_radiation"): {
        "variable_id": "ALLSKY_SFC_SW_DWN",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures solar irradiance reaching irrigated crop canopies, analyzing radiative energy converted into evaporative latent cooling flux.",
        "detective_prompt_tip": "Track seasonal solar incoming energy over cultivated crop belts compared to adjacent arid land.",
    },

    # 3. Monsoon / River Basin
    ("monsoon", "surface_heat"): {
        "variable_id": "MOD11A2",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures radiant skin temperature during monsoon breaks, capturing extreme ground heating when cloud cover clears over rain-shadow regions.",
        "detective_prompt_tip": "Observe dramatic ground skin temperature spikes during dry spell breaks within the summer monsoon.",
    },
    ("monsoon", "solar_radiation"): {
        "variable_id": "ALLSKY_SFC_SW_DWN",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures surface solar irradiance and radiative forcing, showing how heavy monsoon cloud decks physically block sunlight and depress daytime temperatures.",
        "detective_prompt_tip": "Inspect dry spell intervals in the summer monsoon when solar radiation rapidly drives up ground skin heat.",
    },
    ("monsoon", "plant_greenness"): {
        "variable_id": "MOD13A3",
        "matched_case_id": "case_3_vegetation_paradox",
        "case_title": "Vegetation Greenness Paradox: Fragile Forests vs. Human-Engineered Greening",
        "plain_english_definition": "Measures seasonal vegetation response, capturing the rapid surge in green biomass following the arrival of monsoon rains.",
        "detective_prompt_tip": "Watch how vegetation surges from brown dormancy to vivid green within 30 days of monsoon onset.",
    },
    ("monsoon", "extreme_rainfall"): {
        "variable_id": "GPM_3IMERGM_07",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures monthly precipitation accumulation, tracking extreme orographic deluge and regional rain-shadow deficits.",
        "detective_prompt_tip": "Inspect July and August rainfall records to see Northeast India spike above 1,300 mm/month while Marathwada remains trapped under drought conditions.",
    },
    ("monsoon", "soil_moisture"): {
        "variable_id": "GWETROOT",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures soil water content across river catchments, tracking ground saturation preceding floods and depletion during monsoon dry spells.",
        "detective_prompt_tip": "Compare soil saturation levels between windward floodplains and rain-shadow basins.",
    },
    ("monsoon", "atmospheric_warming"): {
        "variable_id": "T2M",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures air temperature across river basins, tracking temperature dampening by monsoon cloud cover and moisture advection.",
        "detective_prompt_tip": "Evaluate whether cloud shading masks underlying long-term atmospheric warming.",
    },

    # 4. Arid / Rain Shadow
    ("arid", "surface_heat"): {
        "variable_id": "MOD11A2",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures radiant skin temperature, revealing how drought and soil moisture loss cause bare ground to rapidly heat up under incoming solar radiation.",
        "detective_prompt_tip": "Look at how low vegetation and bare dry soils exhibit extreme diurnal and seasonal thermal amplitude under high solar irradiance.",
    },
    ("arid", "solar_radiation"): {
        "variable_id": "ALLSKY_SFC_SW_DWN",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures downward surface solar radiation, tracking how persistent cloudless skies in rain-shadow basins drive extreme radiative energy heating.",
        "detective_prompt_tip": "Inspect continuous high solar radiative flux over rain-shadow terrain where descending adiabatic air prevents cloud formation.",
    },
    ("arid", "plant_greenness"): {
        "variable_id": "MOD13A3",
        "matched_case_id": "case_3_vegetation_paradox",
        "case_title": "Vegetation Greenness Paradox: Fragile Forests vs. Human-Engineered Greening",
        "plain_english_definition": "Measures vegetation health in semi-arid zones, tracking prolonged canopy browning and drought-induced desertification.",
        "detective_prompt_tip": "Track how prolonged precipitation droughts suppress sparse shrub and steppe greening.",
    },
    ("arid", "extreme_rainfall"): {
        "variable_id": "GPM_3IMERGM_07",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures monthly rainfall, capturing chronic precipitation deficits on leeward slopes blocked by mountain ranges.",
        "detective_prompt_tip": "Check the rain shadow deficit where air masses descend and heat up adiabatically without releasing moisture.",
    },
    ("arid", "soil_moisture"): {
        "variable_id": "GWETROOT",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures root-zone soil wetness, diagnosing severe moisture exhaustion in rain-shadow basins where rainfall fails to penetrate.",
        "detective_prompt_tip": "Correlate consecutive multi-month root-zone water deficits with historical drought declarations.",
    },
    ("arid", "atmospheric_warming"): {
        "variable_id": "T2M",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures air temperatures in arid basins, tracking heightened sensible heat flux under clear, cloudless skies.",
        "detective_prompt_tip": "Compare air temperature rise against ground surface heating in moisture-depleted desert biomes.",
    },

    # 5. Urban / Built Environment
    ("urban", "surface_heat"): {
        "variable_id": "MOD11A2",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures surface skin temperature, mapping the Urban Heat Island (UHI) effect where concrete, asphalt, and rooftops store and re-radiate intense heat.",
        "detective_prompt_tip": "Contrast dense downtown concrete cores with surrounding rural vegetative baselines.",
    },
    ("urban", "solar_radiation"): {
        "variable_id": "ALLSKY_SFC_SW_DWN",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures solar irradiance reaching urban surfaces, examining how low-albedo asphalt and dark rooftops absorb and store solar energy.",
        "detective_prompt_tip": "Examine the correlation between incoming daytime solar radiation and subsequent nocturnal heat trapping.",
    },
    ("urban", "plant_greenness"): {
        "variable_id": "MOD13A3",
        "matched_case_id": "case_3_vegetation_paradox",
        "case_title": "Vegetation Greenness Paradox: Fragile Forests vs. Human-Engineered Greening",
        "plain_english_definition": "Measures urban tree canopy and park coverage, evaluating municipal greenspace mitigation against impervious concrete sprawl.",
        "detective_prompt_tip": "Identify green corridors that mitigate extreme thermal hotspots within metropolitan perimeters.",
    },
    ("urban", "extreme_rainfall"): {
        "variable_id": "GPM_3IMERGM_07",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures precipitation over metropolitan areas, tracking urban flash flood risks and convective storms amplified by city heat.",
        "detective_prompt_tip": "Examine storm intensity peaks over cities caused by thermal updrafts and aerosol pollution.",
    },
    ("urban", "soil_moisture"): {
        "variable_id": "GWETROOT",
        "matched_case_id": "case_1_monsoon_paradox",
        "case_title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
        "plain_english_definition": "Measures root-zone moisture, quantifying how urban impermeable surfaces prevent precipitation from recharging underlying groundwater.",
        "detective_prompt_tip": "Assess ground moisture depletion underneath expanding metropolitan concrete networks.",
    },
    ("urban", "atmospheric_warming"): {
        "variable_id": "T2M",
        "matched_case_id": "case_2_land_thermal_paradox",
        "case_title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
        "plain_english_definition": "Measures 2-meter air temperature, capturing urban atmospheric heating and nighttime trapped warmth relative to rural baselines.",
        "detective_prompt_tip": "Track nocturnal cooling deficits where urban canyon geometry traps heat until dawn.",
    },
}


BIOME_SYMPTOMS_MAP: Dict[str, List[str]] = {
    "Forest / Deforestation": [
        "Canopy Clearance & Extreme Surface Heat",
        "Vegetation Browning & Biomass Loss",
        "Forest Microclimate Moisture Loss",
        "Regional Rainfall Decline & Deforestation Drought",
        "Boundary-Layer Tropospheric Warming",
        "Direct Solar Radiation Exposure",
    ],
    "Farmland / Irrigation": [
        "Intense Evaporative Surface Cooling",
        "Artificial Crop Greening Surges",
        "Aquifer & Root-Zone Groundwater Depletion",
        "Agricultural Air Temperature Dampening",
        "Precipitation vs Irrigation Disparity",
        "Canopy Solar Irradiance Conversion",
    ],
    "Monsoon / River Basin": [
        "Extreme Orographic Deluge & Flooding",
        "Monsoon Cloud Shading & Solar Blockage",
        "River Catchment Soil Water Saturation",
        "Monsoon Break Ground Skin Heating",
        "Post-Monsoon Vegetation Flush",
        "Atmospheric Moisture Advection & Cooling",
    ],
    "Arid / Rain Shadow": [
        "Chronic Rain-Shadow Precipitation Deficit",
        "Severe Root-Zone Soil Moisture Exhaustion",
        "Bare Ground Radiant Heat & Thermal Amplitude",
        "Cloud-Free Surface Solar Radiative Forcing",
        "Drought Canopy Browning & Desertification",
        "Sensible Heat Tropospheric Warming",
    ],
    "Urban / Built Environment": [
        "Urban Heat Island (Asphalt Thermal Storage)",
        "Urban Canopy & Greenspace Mitigation",
        "Impervious Surface Runoff & Infiltration Loss",
        "Nocturnal Heat Trapping (2-Meter Air)",
        "Urban Convective Thunderstorm Deluge",
        "Low-Albedo Solar Absorption",
    ],
}


def get_biome_symptoms_map() -> Dict[str, List[str]]:
    """Returns mapping of environment types to their signature observable symptoms."""
    return {k: list(v) for k, v in BIOME_SYMPTOMS_MAP.items()}


def _normalize_environment(env: str) -> str:
    """Normalizes environment string to a standard classification key."""
    e = (env or "").lower()
    if any(k in e for k in ["forest", "deforestation", "amazon", "rainforest", "jungle", "trees"]):
        return "forest"
    if any(k in e for k in ["farm", "cropland", "agriculture", "crop", "irrigation", "punjab"]):
        return "farmland"
    if any(k in e for k in ["monsoon", "river", "basin", "flood", "deluge", "cherrapunji"]):
        return "monsoon"
    if any(k in e for k in ["arid", "shadow", "rain shadow", "desert", "drought", "dry"]):
        return "arid"
    if any(k in e for k in ["urban", "city", "cities", "built", "metropolitan", "asphalt"]):
        return "urban"
    return "global"


def _normalize_symptom(symp: str) -> str:
    """Normalizes symptom string to a standard classification key."""
    s = (symp or "").lower()
    if any(k in s for k in ["solar", "sun", "sunlight", "radiation", "irradiance", "blockage", "shading", "flux"]):
        return "solar_radiation"
    if any(k in s for k in ["skin", "surface heat", "ground", "lst", "thermal", "cooling", "heat", "hot", "evaporative", "amplitude"]):
        return "surface_heat"
    if any(k in s for k in ["green", "ndvi", "vegetation", "canopy", "leaf", "greening", "browning", "biomass", "flush"]):
        return "plant_greenness"
    if any(k in s for k in ["rain", "precipitation", "deluge", "orographic", "monsoon", "flood", "flooding", "deficit", "drought", "storm"]):
        return "extreme_rainfall"
    if any(k in s for k in ["soil", "moisture", "root", "aquifer", "water stress", "exhaustion", "desiccation", "groundwater", "depletion", "saturation", "infiltration"]):
        return "soil_moisture"
    if any(k in s for k in ["air", "atmosphere", "atmospheric", "2-meter", "t2m", "trapping", "warmth", "dampening", "nocturnal", "tropospheric"]):
        return "atmospheric_warming"
    return "surface_heat"


def list_supported_environments() -> List[str]:
    """Returns list of student-friendly environment categories."""
    return SUPPORTED_ENVIRONMENTS.copy()


def list_supported_symptoms() -> List[str]:
    """Returns list of observable Earth system symptoms."""
    return SUPPORTED_SYMPTOMS.copy()


def recommend_variable(
    environment_type: str,
    symptom_type: str,
    timeframe_years: int = 25,
) -> Dict[str, Any]:
    """
    Given an environment type and observed symptom, dynamically recommends:
    1. Best matching preset Mystery Case File (if applicable)
    2. Best NASA Earthdata variable (MODIS, GPM, or NASA POWER)
    3. Plain-English contextual definition directly mapped to the (environment, symptom) pair,
       guaranteeing no mismatched context (e.g., arid selections never receive deforestation text).
    """
    env_key = _normalize_environment(environment_type)
    symp_key = _normalize_symptom(symptom_type)

    pair_key = (env_key, symp_key)

    if pair_key in PAIR_RECOMMENDATION_MAP:
        rec_data = PAIR_RECOMMENDATION_MAP[pair_key]
        var_id = rec_data["variable_id"]
        meta = VARIABLE_METADATA.get(var_id, VARIABLE_METADATA["MOD11A2"])

        matched_case_id = rec_data.get("matched_case_id")
        case_title = rec_data.get("case_title") or ("Custom Investigation" if matched_case_id is None else "")
        plain_def = rec_data["plain_english_definition"]
        tip = rec_data["detective_prompt_tip"]
    else:
        # Generalized dynamic fallback for novel combinations
        if symp_key == "solar_radiation":
            var_id = "ALLSKY_SFC_SW_DWN"
        elif symp_key == "plant_greenness":
            var_id = "MOD13A3"
        elif symp_key == "extreme_rainfall":
            var_id = "GPM_3IMERGM_07"
        elif symp_key == "soil_moisture":
            var_id = "GWETROOT"
        elif symp_key == "atmospheric_warming":
            var_id = "T2M"
        else:
            var_id = "MOD11A2"

        meta = VARIABLE_METADATA[var_id]
        matched_case_id = None
        case_title = f"Custom Investigation: {environment_type} {symptom_type} Telemetry"
        plain_def = (
            f"Measures {meta['common_name'].lower()} across {environment_type.lower()} terrain, "
            f"tracking how {symptom_type.lower()} evolves over decadal satellite records."
        )
        tip = f"Examine long-term multi-decadal trends to detect persistent anthropogenic or climatic shifts in {environment_type.lower()}."

    return {
        "query": {
            "environment_type": environment_type,
            "symptom_type": symptom_type,
            "timeframe_years": timeframe_years,
        },
        "matched_mystery_case": {
            "has_match": bool(matched_case_id is not None),
            "case_id": matched_case_id,
            "case_title": case_title,
        },
        "recommended_variable": {
            "variable_id": meta["variable_id"],
            "variable_code": meta["variable_code"],
            "common_name": meta["common_name"],
            "satellite_platform": meta["satellite_platform"],
            "unit": meta["unit"],
            "plain_english_definition": plain_def,
        },
        "detective_prompt_tip": tip,
        "alternatives": meta.get("alternatives", []),
        "available_filters": {
            "environments": SUPPORTED_ENVIRONMENTS,
            "symptoms": SUPPORTED_SYMPTOMS,
        },
    }
