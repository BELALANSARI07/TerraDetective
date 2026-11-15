"""
Tests for Step 6: The 'Ask TerraDetective' Natural Language Data-Grounded Query Bar
& Auto-Investigation Router.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pytest

# Setup sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import main
from main import AskDetectiveRequest
from services.nl_query_engine import (
    process_natural_language_query,
    detect_preset_case,
    extract_gazetteer_locations,
    detect_variable,
    GLOBAL_GAZETTEER,
)


def test_gazetteer_coverage():
    """Verify global gazetteer has 25+ climate hotspots and world regions."""
    assert len(GLOBAL_GAZETTEER) >= 25
    assert "cairo" in GLOBAL_GAZETTEER
    assert "delhi" in GLOBAL_GAZETTEER
    assert "mumbai" in GLOBAL_GAZETTEER
    assert "cherrapunji" in GLOBAL_GAZETTEER
    assert "amazon" in GLOBAL_GAZETTEER
    assert "punjab" in GLOBAL_GAZETTEER
    assert "london" in GLOBAL_GAZETTEER
    assert "greenland" in GLOBAL_GAZETTEER


def test_preset_intent_detection():
    """Verify natural language queries correctly map to preset case IDs."""
    # Thermal paradox
    assert detect_preset_case("Why is deforestation heating the Amazon while Punjab cools?") == "case_2_land_thermal_paradox"
    assert detect_preset_case("Explain the MOD11A2 land surface temperature paradox") == "case_2_land_thermal_paradox"

    # Monsoon paradox
    assert detect_preset_case("Why is there a deluge in Northeast India while Marathwada faces drought?") == "case_1_monsoon_paradox"
    assert detect_preset_case("Show me the GPM IMERG rainfall trend in Meghalaya vs rain shadow") == "case_1_monsoon_paradox"

    # Vegetation paradox
    assert detect_preset_case("Why is NDVI greenness surging in Punjab while Amazon forest thins?") == "case_3_vegetation_paradox"
    assert detect_preset_case("Analyze MOD13A3 canopy browning vs crop greening") == "case_3_vegetation_paradox"


def test_preset_thermal_query_processing():
    """Test full processing of the Amazon vs Punjab thermal query."""
    res = process_natural_language_query(
        "Why is deforestation heating the Amazon while Punjab cools?",
        mode="student",
        skip_ollama=True,
    )
    assert res["action_type"] == "load_preset_case"
    assert res["matched_case_id"] == "case_2_land_thermal_paradox"
    assert len(res["key_evidence_badges"]) >= 3

    # Check that exact slope numbers (+0.37 and -0.38) appear in badges
    badges_str = " ".join(res["key_evidence_badges"])
    assert "+0.37" in badges_str or "+0.374" in badges_str
    assert "-0.38" in badges_str or "-0.376" in badges_str
    assert "MOD11A2" in badges_str

    # Check payload integrity
    payload = res["case_payload"]
    assert payload["case_id"] == "case_2_land_thermal_paradox"
    assert "manifest" in payload
    assert "regions_data" in payload
    assert "statistics" in payload
    assert len(payload["regions_data"]) == 2


def test_preset_monsoon_query_scientist_mode():
    """Test monsoon query in scientist mode for rigor and technical terminology."""
    res = process_natural_language_query(
        "Is rainfall changing in Marathwada vs Northeast India?",
        mode="scientist",
        skip_ollama=True,
    )
    assert res["action_type"] == "load_preset_case"
    assert res["matched_case_id"] == "case_1_monsoon_paradox"
    assert "GPM" in " ".join(res["key_evidence_badges"])
    assert "Mann-Kendall" in res["answer"] or "trajectory" in res["answer"]


def test_custom_city_comparison():
    """Test custom city comparison (Delhi vs Mumbai) triggers live telemetry pipeline."""
    res = process_natural_language_query("Compare temperature in Delhi vs Mumbai", mode="student", skip_ollama=True)
    assert res["action_type"] == "load_custom_comparison"
    assert res["matched_case_id"] is None
    payload = res["case_payload"]
    assert "manifest" in payload
    assert "regions_data" in payload
    assert len(payload["regions_data"]) == 2
    assert "statistics" in payload
    assert "telemetry" in payload
    assert "region_a" in payload["regions_data"]
    assert "region_b" in payload["regions_data"]


def test_user_delhi_heydrabad_query():
    """Verify exact user query with typo ('heydrabad') resolves to Delhi vs Hyderabad comparison."""
    req = AskDetectiveRequest(
        query="can you compare temperature in delhi to heydrabad",
        mode="student",
    )
    data = main.ask_detective(req)
    assert data["action_type"] == "load_custom_comparison"
    assert data["matched_case_id"] is None
    payload = data["case_payload"]
    assert "New Delhi" in payload["regions_data"]["region_a"]["region_label"]
    assert "Hyderabad" in payload["regions_data"]["region_b"]["region_label"]
    assert "New Delhi" in data["answer"]
    assert "Hyderabad" in data["answer"]
    assert "Rondônia" not in data["answer"]


def test_api_ask_endpoint_student():
    """Test FastAPI /api/ask endpoint handler in student mode."""
    req = AskDetectiveRequest(
        query="Why is deforestation heating the Amazon while Punjab cools?",
        mode="student",
    )
    data = main.ask_detective(req)
    assert data["action_type"] == "load_preset_case"
    assert data["matched_case_id"] == "case_2_land_thermal_paradox"
    assert len(data["key_evidence_badges"]) >= 3
    assert len(data["suggested_followups"]) == 3
    assert data["ai_source"] in ["ollama_qwen3_8b", "deterministic_fallback"]


def test_api_ask_endpoint_scientist():
    """Test FastAPI /api/ask endpoint handler in scientist mode."""
    req = AskDetectiveRequest(
        query="Evaluate GPM precipitation anomaly and orographic divergence between Cherrapunji and Marathwada",
        mode="scientist",
    )
    data = main.ask_detective(req)
    assert data["action_type"] == "load_preset_case"
    assert data["matched_case_id"] == "case_1_monsoon_paradox"
    assert "GPM" in " ".join(data["key_evidence_badges"]) or "IMERG" in " ".join(data["key_evidence_badges"])


def test_api_ask_endpoint_custom_twin():
    """Test FastAPI /api/ask endpoint handler with custom cities."""
    req = AskDetectiveRequest(
        query="Compare rainfall in London vs Cairo",
        mode="student",
    )
    data = main.ask_detective(req)
    assert data["action_type"] == "load_custom_comparison"
    assert data["case_payload"]["manifest"]["variable_id"] == "PRECTOTCORR"
    assert len(data["case_payload"]["regions_data"]) == 2


def test_api_ask_fallback_resilience():
    """Verify that even with an empty query, /api/ask returns cleanly without error."""
    req = AskDetectiveRequest(
        query="",
        mode="student",
    )
    data = main.ask_detective(req)
    assert "answer" in data
    assert "case_payload" in data


def test_worldwide_states_and_countries_query():
    """Verify that all global states, provinces, and countries resolve instantly."""
    req1 = AskDetectiveRequest(
        query="compare temperature in Alaska to Texas",
        mode="student",
    )
    data1 = main.ask_detective(req1)
    assert data1["action_type"] == "load_custom_comparison"
    assert "Alaska" in data1["answer"]
    assert "Texas" in data1["answer"]

    req2 = AskDetectiveRequest(
        query="compare rainfall in Bavaria to Tuscany",
        mode="student",
    )
    data2 = main.ask_detective(req2)
    assert data2["action_type"] == "load_custom_comparison"
    assert "Bavaria" in data2["answer"]
    assert "Tuscany" in data2["answer"]

    req3 = AskDetectiveRequest(
        query="compare temperature between Kerala and Punjab",
        mode="student",
    )
    data3 = main.ask_detective(req3)
    assert data3["action_type"] == "load_custom_comparison"
    assert "Kerala" in data3["answer"]
    assert "Punjab" in data3["answer"]


def test_out_of_context_guardrail():
    """Verify that off-topic queries are intercepted with a friendly Earth science AI notice."""
    req = AskDetectiveRequest(
        query="What is a good recipe for cake?",
        mode="student",
    )
    data = main.ask_detective(req)
    assert data["action_type"] == "info"
    assert data["case_payload"] is None
    assert "I am TerraDetective, an Earth science AI!" in data["answer"]


def test_unsupported_pollution_guardrail():
    """Verify that pollution/air quality queries return an honest, helpful response rather than falling back to temperature."""
    req = AskDetectiveRequest(
        query="Compare pollution in Delhi vs Mumbai",
        mode="student",
    )
    data = main.ask_detective(req)
    assert data["action_type"] == "info"
    assert data["case_payload"] is None
    assert "air quality or pollution" in data["answer"]
    assert "Surface Temperature" in data["answer"]


def test_unknown_variable_guardrail():
    """Verify that unsupported variables (like wind speed) return unknown variable guidance."""
    req = AskDetectiveRequest(
        query="Measure wind speed in London",
        mode="student",
    )
    data = main.ask_detective(req)
    assert data["action_type"] == "info"
    assert data["case_payload"] is None
    assert "couldn't detect which environmental variable" in data["answer"]

