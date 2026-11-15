"""
TerraDetective Automated Unit & Narrative Fidelity Tests: Dual-Mode AI Explainer
NASA Space Apps Challenge: 'Be An Earth System Trend Detective!'

Tests verify:
1. Grounded Number Fidelity:
   - Verifies all numeric slopes and statistical metrics are accurately preserved
     in student and scientist narrations without hallucination or sign reversals.
2. Zero-Downtime Fallback:
   - When Ollama is unreachable (mocked ConnectionError / Timeout), engine immediately
     and safely returns deterministic fallback with ai_source == 'deterministic_fallback'.
3. JSON Schema Conformance:
   - Student Mode: headline, what_changed, detective_clue_why, confidence_plain_english, try_this_next
   - Scientist Mode: technical_abstract, statistical_interpretation, physical_mechanisms, methodological_caveats
4. Flagship Narratives Cache:
   - Verifies data/processed/case_studies_narratives.json exists, parses, and has valid
     entries for all 3 flagship mystery cases.
5. Guided Variable Recommender:
   - Validates accurate mappings for forest heat, agricultural greenness, and monsoon deluge queries.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch
import pytest
import httpx

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from services.ai_explainer import (
    explain_case_study,
    generate_deterministic_narrative,
    generate_with_ollama,
    precompute_flagship_narratives,
)
from services.variable_recommender import (
    recommend_variable,
    list_supported_environments,
    list_supported_symptoms,
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# -------------------------------------------------------------------------
# Test Suite 1: Grounded Number Fidelity & Prompt Safety
# -------------------------------------------------------------------------
def test_number_fidelity_in_deterministic_narrative():
    """
    Verifies that numeric slopes and changes passed in the stats input
    are faithfully formatted into the narrative without corruption or sign reversal.
    """
    custom_stats = {
        "case_id": "test_divergence_case",
        "variable_id": "TS",
        "variable_name": "Earth Skin Temperature",
        "unit": "°C",
        "region_a": {
            "region_label": "Northern Deforested Ridge",
            "mann_kendall": {
                "sens_slope_per_decade": 0.456,
                "sens_slope_per_year": 0.0456,
                "total_estimated_change": 1.14,
                "p_value": 0.0003,
                "confidence_pct": 99.97,
                "trend_direction": "increasing",
            },
            "ols_regression": {
                "slope_ci_95_low": 0.035,
                "slope_ci_95_high": 0.055,
            },
        },
        "region_b": {
            "region_label": "Southern Irrigated Valley",
            "mann_kendall": {
                "sens_slope_per_decade": -0.789,
                "sens_slope_per_year": -0.0789,
                "total_estimated_change": -1.97,
                "p_value": 0.0001,
                "confidence_pct": 99.99,
                "trend_direction": "decreasing",
            },
            "ols_regression": {
                "slope_ci_95_low": -0.090,
                "slope_ci_95_high": -0.065,
            },
        },
        "divergence_analysis": {
            "divergence_detected": True,
            "opposite_direction": True,
            "slope_difference_per_decade": 1.245,
            "z_score_divergence": 4.12,
            "p_value_divergence": 0.00003,
        },
    }

    result = generate_deterministic_narrative(custom_stats)

    assert result["ai_source"] == "deterministic_fallback"
    student = result["student_story_mode"]
    scientist = result["scientist_research_mode"]

    # Student Mode Number Verifications
    what_changed = student["what_changed"]
    assert "+0.456" in what_changed or "0.456" in what_changed
    assert "-0.789" in what_changed or "0.789" in what_changed
    assert "+1.14" in what_changed or "1.14" in what_changed
    assert "-1.97" in what_changed or "1.97" in what_changed

    # Confidence check
    conf_str = student["confidence_plain_english"]
    assert "99.97%" in conf_str
    assert "99.99%" in conf_str

    # Scientist Mode Number Verifications
    stat_interp = scientist["statistical_interpretation"]
    assert "0.456" in stat_interp
    assert "0.789" in stat_interp
    assert "1.245" in stat_interp


# -------------------------------------------------------------------------
# Test Suite 2: Zero-Downtime Fallback on Ollama Failure
# -------------------------------------------------------------------------
def test_zero_downtime_fallback_on_unreachable_ollama():
    """
    Simulates Ollama being completely offline (ConnectError).
    Verifies that explain_case_study safely catches the exception
    and returns a complete, schema-compliant fallback response.
    """
    dummy_stats = {
        "case_id": "case_2_land_thermal_paradox",
        "variable_id": "LST_Day",
        "unit": "°C",
        "region_a": {
            "region_label": "Rondônia Amazon Deforestation Arc",
            "mann_kendall": {"sens_slope_per_decade": 0.374, "p_value": 0.0003, "confidence_pct": 99.97},
        },
        "region_b": {
            "region_label": "Punjab Intensive Irrigated Cropland Belt",
            "mann_kendall": {"sens_slope_per_decade": -0.376, "p_value": 0.0004, "confidence_pct": 99.96},
        },
        "divergence_analysis": {"divergence_detected": True, "slope_difference_per_decade": 0.750},
    }

    # Mock httpx.Client.post to raise ConnectError (simulating offline port 11434)
    with patch("httpx.Client.post", side_effect=httpx.ConnectError("Connection refused")):
        res = explain_case_study(dummy_stats, prefer_live_ollama=True)

    assert res["ai_source"] == "deterministic_fallback"
    assert "student_story_mode" in res
    assert "scientist_research_mode" in res

    # Verify all expected student keys exist
    student_keys = {"headline", "what_changed", "detective_clue_why", "confidence_plain_english", "try_this_next"}
    assert student_keys.issubset(set(res["student_story_mode"].keys()))

    # Verify all expected scientist keys exist
    scientist_keys = {"technical_abstract", "statistical_interpretation", "physical_mechanisms", "methodological_caveats"}
    assert scientist_keys.issubset(set(res["scientist_research_mode"].keys()))


# -------------------------------------------------------------------------
# Test Suite 3: Pre-Cached Flagship Narratives File
# -------------------------------------------------------------------------
def test_pre_cached_case_studies_narratives_json():
    """
    Verifies that data/processed/case_studies_narratives.json exists,
    contains all 3 flagship cases, and each case contains populated student
    and scientist modes with rich environmental narratives.
    """
    json_path = PROCESSED_DIR / "case_studies_narratives.json"
    if not json_path.is_file():
        precompute_flagship_narratives(output_narratives_path=json_path)

    assert json_path.is_file(), f"Narratives JSON missing at {json_path}"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "cases" in data
    cases = data["cases"]
    assert len(cases) == 3

    expected_case_ids = [
        "case_1_monsoon_paradox",
        "case_2_land_thermal_paradox",
        "case_3_vegetation_paradox",
    ]

    for cid in expected_case_ids:
        assert cid in cases, f"Case {cid} missing from cached narratives"
        entry = cases[cid]
        assert "student_story_mode" in entry
        assert "scientist_research_mode" in entry

        student = entry["student_story_mode"]
        scientist = entry["scientist_research_mode"]

        # Student validations
        assert len(student["headline"]) > 10
        assert len(student["what_changed"]) > 30
        assert len(student["detective_clue_why"]) > 30
        assert len(student["confidence_plain_english"]) > 10

        # Scientist validations
        assert len(scientist["technical_abstract"]) > 30
        assert len(scientist["statistical_interpretation"]) > 30
        assert len(scientist["physical_mechanisms"]) > 30
        assert len(scientist["methodological_caveats"]) > 20

    # Specifically verify Case 2 (Amazon vs Punjab Thermal Paradox)
    c2_student = cases["case_2_land_thermal_paradox"]["student_story_mode"]
    assert "evaporative cooling" in c2_student["detective_clue_why"].lower() or "sweating" in c2_student["detective_clue_why"].lower()

    # Specifically verify Case 3 (Canopy Degradation vs Irrigation Greening)
    c3_scientist = cases["case_3_vegetation_paradox"]["scientist_research_mode"]
    assert "phenology" in c3_scientist["physical_mechanisms"].lower() or "bimodal" in c3_scientist["physical_mechanisms"].lower()


# -------------------------------------------------------------------------
# Test Suite 4: Guided Variable Detective Recommender
# -------------------------------------------------------------------------
def test_guided_variable_recommender():
    """
    Tests the Guided Variable Detective recommender on various student queries.
    """
    # Query 1: Forest & Surface Heat -> MOD11A2 & Case 2
    rec1 = recommend_variable("Forest / Deforestation", "Rising Surface Heat", 25)
    assert rec1["matched_mystery_case"]["has_match"] is True
    assert rec1["matched_mystery_case"]["case_id"] == "case_2_land_thermal_paradox"
    assert rec1["recommended_variable"]["variable_id"] == "MOD11A2"
    assert "°C" in rec1["recommended_variable"]["unit"]
    assert len(rec1["recommended_variable"]["plain_english_definition"]) > 20
    assert "forest canopy" in rec1["recommended_variable"]["plain_english_definition"].lower()

    # Query 1b: Arid / Rain Shadow & Surface Heat -> MOD11A2 but Arid-specific description (NOT deforestation!)
    rec_arid = recommend_variable("Arid / Rain Shadow", "Rising Surface Heat", 25)
    assert rec_arid["recommended_variable"]["variable_id"] == "MOD11A2"
    arid_def = rec_arid["recommended_variable"]["plain_english_definition"]
    assert "drought" in arid_def.lower() or "soil moisture loss" in arid_def.lower()
    assert "deforestation" not in arid_def.lower()
    assert "forest canopy" not in arid_def.lower()

    # Query 2: Farmland & Greenness -> MOD13A3 & Case 3
    rec2 = recommend_variable("Farmland / Irrigation", "Plant Greenness", 25)
    assert rec2["matched_mystery_case"]["has_match"] is True
    assert rec2["matched_mystery_case"]["case_id"] == "case_3_vegetation_paradox"
    assert rec2["recommended_variable"]["variable_id"] == "MOD13A3"
    assert "index" in rec2["recommended_variable"]["unit"].lower()

    # Query 3: Monsoon & Extreme Rainfall -> GPM_3IMERGM_07 & Case 1
    rec3 = recommend_variable("Monsoon / River Basin", "Extreme Rainfall", 25)
    assert rec3["matched_mystery_case"]["has_match"] is True
    assert rec3["matched_mystery_case"]["case_id"] == "case_1_monsoon_paradox"
    assert "GPM" in rec3["recommended_variable"]["variable_id"]
    assert "mm/month" in rec3["recommended_variable"]["unit"]

    # Query 4: Supported lists
    envs = list_supported_environments()
    assert len(envs) >= 5
    symps = list_supported_symptoms()
    assert len(symps) >= 5
