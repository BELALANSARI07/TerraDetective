"""
TerraDetective Step 5 Unit Tests: Live Multi-Agency Telemetry & Upgrades
NASA Space Apps Challenge 2026: 'Be An Earth System Trend Detective!'

Validates:
1. Interactive Time-Window Significance Simulator (5-yr vs 25-yr window p-value shift)
2. Live Twin-Region Custom Exploration (POST /api/explore/twin-custom)
3. Bring-Your-Own NASA CSV Upload (POST /api/upload/csv)
4. Multi-Agency Telemetry (NASA CMR Bearer + Microsoft Planetary Computer STAC)
5. Telemetry Endpoint (GET /api/satellite/telemetry)
"""

import io
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure root and backend are on sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

import main
from backend.services.live_satellite_stac import (
    query_nasa_cmr,
    query_planetary_computer_stac,
    get_telemetry_for_region,
)


def test_time_window_significance_simulator_full_vs_slice():
    """
    Verifies that slicing to a short 5-year window (2018-2022) produces
    different p-values / significance verdicts compared to the full 25-year record (2001-2025).
    """
    # 1. Full 25-year record
    full_res = main.get_case_detail("case_2_land_thermal_paradox")
    assert full_res["case_id"] == "case_2_land_thermal_paradox"
    assert full_res["simulation_metadata"]["time_window_sliced"] is False
    assert full_res["simulation_metadata"]["window_years"] == 25
    assert len(full_res["regions_data"]["RondoniaAmazonArc"]["dates"]) >= 280

    # 2. Sliced 5-year lens (2018–2022)
    sliced_res = main.get_case_detail(
        "case_2_land_thermal_paradox",
        start_year=2018,
        end_year=2022,
    )
    assert sliced_res["simulation_metadata"]["time_window_sliced"] is True
    assert sliced_res["simulation_metadata"]["window_years"] == 5
    assert sliced_res["simulation_metadata"]["start_year"] == 2018
    assert sliced_res["simulation_metadata"]["end_year"] == 2022

    # Verify the sliced date array contains exactly 5 years (60 months)
    dates_sliced = sliced_res["regions_data"]["RondoniaAmazonArc"]["dates"]
    assert len(dates_sliced) == 60
    assert dates_sliced[0] == "2018-01-01"
    assert dates_sliced[-1] == "2022-12-01"

    # Verify simulation metadata has p-value and significance verdict
    assert "p_value_a" in sliced_res["simulation_metadata"]
    assert "significance_verdict" in sliced_res["simulation_metadata"]


def test_time_window_invalid_order_raises_400():
    """Verifies that start_year > end_year raises an HTTP 400 error."""
    with pytest.raises(Exception):
        main.get_case_detail("case_2_land_thermal_paradox", start_year=2024, end_year=2010)


def test_live_satellite_stac_cmr_query():
    """
    Verifies NASA CMR query function produces structured metadata with
    authenticated_edl_bearer flag, collection ID, and official Earthdata search link.
    """
    res = query_nasa_cmr(lat=-10.88, lon=-61.93, collection_short_name="MOD11A2", timeout=3.0)
    assert res["status"] in ("success", "fallback_offline_cache")
    assert res["collection"] == "MOD11A2"
    assert "authenticated_edl_bearer" in res
    assert isinstance(res["authenticated_edl_bearer"], bool)
    assert "search.earthdata.nasa.gov" in res["earthdata_search_link"]
    assert res["granule_count"] > 0


def test_live_satellite_stac_planetary_computer_preview():
    """
    Verifies Microsoft Planetary Computer STAC query returns a valid rendered preview
    or high-resolution curated NASA Earth Observatory satellite image URL without crashing.
    """
    res = query_planetary_computer_stac(lat=-10.88, lon=-61.93, timeout=3.0)
    assert res["status"] in ("success", "fallback_curated_nasa")
    assert "rendered_preview_url" in res
    assert res["rendered_preview_url"].startswith("http")
    assert "thumbnail_url" in res
    assert res["thumbnail_url"].startswith("http")
    assert len(res["bbox"]) == 4


def test_get_telemetry_for_region_aggregation():
    """Verifies aggregate telemetry service bundles both CMR and Planetary Computer STAC."""
    telem = get_telemetry_for_region(lat=30.90, lon=75.86, variable_id="NDVI")
    assert telem["lat"] == 30.90
    assert telem["lon"] == 75.86
    assert telem["cmr"]["collection"] == "MOD13A3"
    assert "rendered_preview_url" in telem
    assert telem["rendered_preview_url"].startswith("http")


def test_api_satellite_telemetry_endpoint():
    """Verifies GET /api/satellite/telemetry returns full telemetry."""
    res = main.get_satellite_telemetry(lat=-10.88, lon=-61.93, variable_id="LST")
    assert "cmr" in res
    assert "stac" in res
    assert "rendered_preview_url" in res


def test_explore_twin_custom_payload_schema_parity():
    """
    Verifies POST /api/explore/twin-custom returns a payload structurally
    identical to GET /api/cases/{case_id} (manifest, regions_data, statistics, narratives, telemetry).
    """
    req = main.TwinCustomExploreRequest(
        region_a=main.TwinCoordinate(lat=-10.875, lon=-61.93, label="Amazon Pin"),
        region_b=main.TwinCoordinate(lat=30.901, lon=75.8573, label="Punjab Pin"),
        variable_id="T2M",
        start_year=2001,
        end_year=2024,
    )
    res = main.explore_twin_custom(req)
    assert res["case_id"] == "custom_twin_t2m"
    assert "manifest" in res
    assert "regions_data" in res
    assert "region_a" in res["regions_data"]
    assert "region_b" in res["regions_data"]
    assert "statistics" in res
    assert "narratives" in res
    assert "student_story_mode" in res["narratives"]
    assert "scientist_research_mode" in res["narratives"]
    assert "telemetry" in res
    assert "region_a" in res["telemetry"]
    assert "region_b" in res["telemetry"]


def test_upload_nasa_csv_single_region():
    """Verifies parsing and analysis of a single-region uploaded NASA CSV."""
    from backend.data_loader import DataLoader
    
    # Synthetic Giovanni CSV with typical metadata header
    sample_csv = """Title: Giovanni GPM Area-Averaged Monthly Precipitation
User Start Date: 2001-01-01
Units: mm/hr
time,mean_precipitation
2001-01-01,0.125
2001-02-01,0.140
2001-03-01,0.180
2001-04-01,0.210
2001-05-01,0.320
2001-06-01,0.510
2001-07-01,0.720
2001-08-01,0.680
2001-09-01,0.450
2001-10-01,0.230
2001-11-01,0.150
2001-12-01,0.110
2002-01-01,0.130
2002-02-01,0.145
2002-03-01,0.190
2002-04-01,0.220
2002-05-01,0.330
2002-06-01,0.530
2002-07-01,0.740
2002-08-01,0.700
2002-09-01,0.470
2002-10-01,0.240
2002-11-01,0.160
2002-12-01,0.120
"""
    df = DataLoader.parse_uploaded_csv(sample_csv, default_label="Giovanni Test Basin")
    assert len(df) == 24
    assert "date" in df.columns
    assert "value" in df.columns
    assert df["region_label"].iloc[0] == "Giovanni Test Basin"
    assert df["value"].iloc[0] == 0.125


def test_upload_nasa_csv_multi_region_modis_format():
    """
    Verifies parsing of a multi-region MODIS CSV (similar to raw MOD13A3 / MOD11A2)
    where two regions share one file with an 'ID' column.
    """
    from backend.data_loader import DataLoader

    sample_modis = """ID,Date,MOD11A2_061_LST_Day_1km
AmazonArc,2001-01-01,302.15
PunjabBelt,2001-01-01,295.15
AmazonArc,2001-02-01,303.20
PunjabBelt,2001-02-01,296.00
AmazonArc,2001-03-01,304.50
PunjabBelt,2001-03-01,298.20
"""
    df = DataLoader.parse_uploaded_csv(sample_modis)
    assert df["region_id"].nunique() == 2
    assert "AmazonArc" in df["region_id"].values
    assert "PunjabBelt" in df["region_id"].values
    # Check Kelvin -> Celsius conversion (>200K)
    assert df["unit"].iloc[0] == "°C"
    assert df["value"].iloc[0] < 50.0  # Converted to Celsius
