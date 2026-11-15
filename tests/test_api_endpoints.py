"""
TerraDetective API Endpoint & Service Integration Tests
NASA Space Apps Challenge: 'Be An Earth System Trend Detective!'

Tests all core backend endpoints:
- GET /api/health
- GET /api/cases
- GET /api/cases/{case_id}
- POST /api/recommend
- GET /api/recommend/options
- POST /api/explore/custom
- GET /api/export/{case_id}/csv
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest
from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

import main
from main import RecommendRequest, CustomExploreRequest


def test_health_endpoint():
    data = main.health_check()
    assert data["status"] in ("healthy", "degraded")
    assert data["processed_archive_ready"] is True
    assert "earthdata_token_present" in data
    assert data["total_precomputed_cases"] == 3
    assert data["engine_version"] == "2.0.0"


def test_list_cases():
    data = main.list_cases()
    assert "cases" in data
    assert len(data["cases"]) == 3
    case_ids = {c["case_id"] for c in data["cases"]}
    expected = {"case_1_monsoon_paradox", "case_2_land_thermal_paradox", "case_3_vegetation_paradox"}
    assert case_ids == expected


def test_get_case_detail_thermal():
    data = main.get_case_detail("case_2_land_thermal_paradox")
    assert data["case_id"] == "case_2_land_thermal_paradox"
    assert "manifest" in data
    assert "regions_data" in data
    assert "statistics" in data
    assert "narratives" in data

    regions = data["regions_data"]
    assert "RondoniaAmazonArc" in regions
    assert "PunjabIrrigatedBelt" in regions
    assert regions["RondoniaAmazonArc"]["record_count"] == 300
    assert len(regions["RondoniaAmazonArc"]["dates"]) == 300
    assert len(regions["RondoniaAmazonArc"]["values"]) == 300

    stats = data["statistics"]
    assert stats["divergence_analysis"]["divergence_detected"] is True

    narr = data["narratives"]
    assert "student_story_mode" in narr
    assert "scientist_research_mode" in narr
    assert len(narr["student_story_mode"]["headline"]) > 10
    assert len(narr["scientist_research_mode"]["technical_abstract"]) > 20


def test_get_case_detail_monsoon():
    data = main.get_case_detail("case_1_monsoon_paradox")
    assert data["case_id"] == "case_1_monsoon_paradox"
    regions = data["regions_data"]
    assert "Marathwada" in regions
    assert "NortheastIndia" in regions
    assert regions["Marathwada"]["record_count"] == 297


def test_get_case_detail_not_found():
    with pytest.raises(HTTPException) as excinfo:
        main.get_case_detail("case_nonexistent_99")
    assert excinfo.value.status_code == 404


def test_recommend_endpoint():
    req = RecommendRequest(
        environment="Forest / Deforestation",
        symptom="Rising Surface Heat",
        timeframe_years=25,
    )
    data = main.recommend(req)
    assert data["matched_mystery_case"]["has_match"] is True
    assert data["matched_mystery_case"]["case_id"] == "case_2_land_thermal_paradox"
    assert data["recommended_variable"]["variable_id"] == "MOD11A2"
    assert "°C" in data["recommended_variable"]["unit"]
    assert "forest canopy" in data["recommended_variable"]["plain_english_definition"].lower()


def test_recommend_endpoint_arid_context():
    req = RecommendRequest(
        environment="Arid / Rain Shadow",
        symptom="Rising Surface Heat",
        timeframe_years=25,
    )
    data = main.recommend(req)
    assert data["recommended_variable"]["variable_id"] == "MOD11A2"
    definition = data["recommended_variable"]["plain_english_definition"]
    assert "drought" in definition.lower() or "soil moisture loss" in definition.lower()
    assert "deforestation" not in definition.lower()
    assert "forest canopy" not in definition.lower()


def test_recommend_options():
    data = main.recommend_options()
    assert len(data["environments"]) >= 5
    assert len(data["symptoms"]) >= 5


def test_export_csv():
    resp = main.export_case_csv("case_2_land_thermal_paradox")
    assert resp.media_type == "text/csv"
    assert "case_2_land_thermal_paradox.csv" in resp.headers.get("content-disposition", "")

    # Read body
    content = resp.body.decode("utf-8") if hasattr(resp, "body") else ""
    lines = content.strip().split("\n")
    assert len(lines) >= 601  # header + 600 data rows
    assert "case_id" in lines[0]
    assert "case_2_land_thermal_paradox" in lines[1]


def test_export_csv_not_found():
    with pytest.raises(HTTPException) as excinfo:
        main.export_case_csv("case_nonexistent")
    assert excinfo.value.status_code == 404


def test_explore_custom_offline_fallback():
    req = CustomExploreRequest(
        lat=19.25,
        lon=76.25,
        region_label="Marathwada Offline Test",
        variable_id="precipitation",
        start_year=2001,
        end_year=2024,
    )
    result = main.explore_custom(req)
    assert result["total_records"] >= 200
    assert "mann_kendall" in result
    assert "trend" in result
    assert "deseasonalized" in result
    assert result["data_mode"] in ("live_nasa_power", "verified_offline_archive")
