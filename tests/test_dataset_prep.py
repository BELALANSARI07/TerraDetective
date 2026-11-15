"""
TerraDetective Automated Unit & Regression Tests: Dataset Preparation & QC
NASA Space Apps Challenge: 'Be An Earth System Trend Detective!'

Tests verify:
1. All 4 raw NASA CSVs exist in data/raw/
2. Master and per-case CSV/Parquet files and manifest exist in data/processed/
3. Unified schema strict adherence (14 columns)
4. Scientific QC: Zero 0.0 K temperatures remain in LST; all values in realistic Celsius range
5. Temporal alignment: 100% of dates align to monthly start (YYYY-MM-01)
6. Hydrological conversion: GPM precipitation properly scaled to mm/month
7. QC flags: cloudy_interpolated flag properly assigned
8. Manifest schema and metadata completeness
9. 3-Tier Earthdata Connector resilient offline fallback
"""

from __future__ import annotations

import json
import re
from pathlib import Path
import pytest
import pandas as pd
import numpy as np

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

EXPECTED_UNIFIED_COLUMNS = [
    "case_id",
    "region_id",
    "region_label",
    "lat",
    "lon",
    "date",
    "year",
    "month",
    "variable_id",
    "variable_name",
    "unit",
    "value",
    "qc_flag",
    "source_product",
]

DATE_MONTH_START_REGEX = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-01$")


@pytest.fixture(scope="session")
def processed_df():
    csv_path = PROCESSED_DIR / "terradetective_unified_monthly.csv"
    assert csv_path.is_file(), f"Unified CSV not found at {csv_path}"
    return pd.read_csv(csv_path)


@pytest.fixture(scope="session")
def manifest_json():
    manifest_path = PROCESSED_DIR / "case_studies_manifest.json"
    assert manifest_path.is_file(), f"Manifest JSON not found at {manifest_path}"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------------------------------------------------
# Test Suite 1: File Existence & Pipeline Outputs
# -------------------------------------------------------------------------
def test_raw_files_exist():
    """Verify that all 4 raw NASA CSV files exist in data/raw/."""
    expected_files = [
        "TerraDetective-MODIS-Paradox-MOD13A3-061-results.csv",
        "TerraDetective-MODIS-Paradox-MOD11A2-061-results.csv",
        "g4.areaAvgTimeSeries.GPM_3IMERGM_07_precipitation.20010101-20251231.75E_18N_77E_20N.csv",
        "g4.areaAvgTimeSeries.GPM_3IMERGM_07_precipitation.20010101-20251231.90E_24N_92E_26N.csv",
    ]
    for fname in expected_files:
        fpath = RAW_DIR / fname
        assert fpath.is_file(), f"Raw file missing: {fname}"
        assert fpath.stat().st_size > 0, f"Raw file is empty: {fname}"


def test_processed_files_exist():
    """Verify that all processed Parquet, CSV, and JSON manifest assets exist."""
    expected_assets = [
        "terradetective_unified_monthly.csv",
        "terradetective_unified_monthly.parquet",
        "case_1_monsoon_paradox.csv",
        "case_1_monsoon_paradox.parquet",
        "case_2_land_thermal_paradox.csv",
        "case_2_land_thermal_paradox.parquet",
        "case_3_vegetation_paradox.csv",
        "case_3_vegetation_paradox.parquet",
        "case_studies_manifest.json",
    ]
    for asset in expected_assets:
        fpath = PROCESSED_DIR / asset
        assert fpath.is_file(), f"Processed asset missing: {asset}"
        assert fpath.stat().st_size > 0, f"Processed asset is empty: {asset}"


# -------------------------------------------------------------------------
# Test Suite 2: Unified Schema & Temporal Alignment
# -------------------------------------------------------------------------
def test_unified_schema_columns(processed_df):
    """Verify that the processed dataset contains exactly the required 14 schema columns."""
    assert list(processed_df.columns) == EXPECTED_UNIFIED_COLUMNS
    assert len(processed_df) >= 1700, f"Expected at least 1700 records, got {len(processed_df)}"


def test_all_dates_align_to_month_start(processed_df):
    """Verify that 100% of dates align to monthly 'YYYY-MM-01' timestamps."""
    dates = processed_df["date"].astype(str)
    invalid_dates = [d for d in dates if not DATE_MONTH_START_REGEX.match(d)]
    assert len(invalid_dates) == 0, f"Found non-month-start dates: {invalid_dates[:5]}"

    # Verify year and month columns strictly correspond to date string
    for _, row in processed_df.sample(n=min(100, len(processed_df)), random_state=42).iterrows():
        d_str = row["date"]
        assert int(d_str[:4]) == int(row["year"])
        assert int(d_str[5:7]) == int(row["month"])


# -------------------------------------------------------------------------
# Test Suite 3: Scientific QC (MOD11A2 LST)
# -------------------------------------------------------------------------
def test_no_zero_or_negative_temperatures(processed_df):
    """
    Verifies that zero 0.0 K (or <= -200°C) cloud artifacts remain in the LST data,
    and all LST values are in realistic Celsius degrees (10°C to 50°C).
    """
    lst_rows = processed_df[processed_df["variable_id"] == "LST_Day"]
    assert len(lst_rows) == 600, f"Expected 600 monthly LST records (300 per region), got {len(lst_rows)}"

    # Check for 0.0 K conversion artifacts: 0.0 K - 273.15 = -273.15 °C
    invalid_cold = lst_rows[lst_rows["value"] < 0.0]
    assert len(invalid_cold) == 0, f"Found {len(invalid_cold)} negative/zero-Kelvin temperature values!"

    # Earth surface temperatures in Punjab and Rondonia must fall within realistic ranges
    assert lst_rows["value"].min() >= 10.0, f"Unrealistically low LST: {lst_rows['value'].min()}°C"
    assert lst_rows["value"].max() <= 55.0, f"Unrealistically high LST: {lst_rows['value'].max()}°C"

    # Check that both regions have records
    regions = set(lst_rows["region_id"])
    assert "RondoniaAmazonArc" in regions
    assert "PunjabIrrigatedBelt" in regions


# -------------------------------------------------------------------------
# Test Suite 4: Hydrological Conversion & Validation (GPM IMERG)
# -------------------------------------------------------------------------
def test_gpm_precipitation_transformation(processed_df):
    """
    Verifies Giovanni GPM IMERG monthly precipitation:
    - Rate converted from mm/hr to mm/month (value >= 0.0)
    - Marathwada and NortheastIndia regions properly populated
    - Orographic deluge paradox: Northeast India precipitation mean > Marathwada mean
    """
    precip_rows = processed_df[processed_df["variable_id"] == "precipitation"]
    assert len(precip_rows) >= 590, f"Expected ~594 GPM records, got {len(precip_rows)}"

    # No negative precipitation
    assert (precip_rows["value"] >= 0.0).all(), "Negative precipitation values detected!"

    # Check units
    assert (precip_rows["unit"] == "mm/month").all()

    # Compare regional means to verify scientific paradox
    marathwada_mean = precip_rows[precip_rows["region_id"] == "Marathwada"]["value"].mean()
    ne_india_mean = precip_rows[precip_rows["region_id"] == "NortheastIndia"]["value"].mean()

    assert ne_india_mean > 200.0, f"Expected high mean precipitation for NE India, got {ne_india_mean}"
    assert marathwada_mean < 120.0, f"Expected rain-shadow mean precipitation for Marathwada, got {marathwada_mean}"
    assert ne_india_mean > marathwada_mean * 2.5, "Northeast India monsoon rainfall should vastly exceed Marathwada"


# -------------------------------------------------------------------------
# Test Suite 5: Vegetation Indices QC (MOD13A3 NDVI)
# -------------------------------------------------------------------------
def test_mod13a3_ndvi_qc_flags(processed_df):
    """
    Verifies MOD13A3 NDVI:
    - Values bounded in [0.0, 1.0]
    - Cloudy pixels flagged with 'cloudy_interpolated'
    - Nominal pixels flagged with 'nominal'
    """
    ndvi_rows = processed_df[processed_df["variable_id"] == "NDVI"]
    assert len(ndvi_rows) == 600, f"Expected 600 monthly NDVI records, got {len(ndvi_rows)}"

    assert ndvi_rows["value"].min() >= 0.0, f"Negative NDVI detected: {ndvi_rows['value'].min()}"
    assert ndvi_rows["value"].max() <= 1.0, f"NDVI > 1.0 detected: {ndvi_rows['value'].max()}"

    flags = set(ndvi_rows["qc_flag"])
    assert "cloudy_interpolated" in flags, "Expected 'cloudy_interpolated' flag in NDVI data"
    assert "nominal" in flags, "Expected 'nominal' flag in NDVI data"


# -------------------------------------------------------------------------
# Test Suite 6: Case Studies Manifest Completeness
# -------------------------------------------------------------------------
def test_case_studies_manifest(manifest_json):
    """
    Verifies that case_studies_manifest.json contains complete metadata for all 3 mystery cases.
    """
    assert "cases" in manifest_json
    cases = manifest_json["cases"]
    assert len(cases) == 3

    case_ids = {c["case_id"] for c in cases}
    expected_case_ids = {
        "case_1_monsoon_paradox",
        "case_2_land_thermal_paradox",
        "case_3_vegetation_paradox",
    }
    assert case_ids == expected_case_ids

    for case in cases:
        assert "title" in case and len(case["title"]) > 0
        assert "paradox_statement" in case and len(case["paradox_statement"]) > 10
        assert "regions" in case and len(case["regions"]) == 2
        assert "data_files" in case
        assert "csv" in case["data_files"]
        assert "parquet" in case["data_files"]


# -------------------------------------------------------------------------
# Test Suite 7: Resilient 3-Tier Earthdata Connector Fallback
# -------------------------------------------------------------------------
def test_three_tier_earthdata_client_fallback():
    """
    Verifies that the 3-Tier Earthdata Connector safely falls back to Tier 3 verified local archive:
    - Token health check reports offline/invalid gracefully without raising unhandled exceptions
    - fetch_case_study serves data with data_mode == 'verified_offline_archive'
    - fetch_nasa_power_point safely falls back if network is unreachable
    """
    import sys
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))
    from services.earthdata_client import ThreeTierEarthDataConnector

    # Instantiate connector with dummy invalid token to test resilience
    connector = ThreeTierEarthDataConnector(token="invalid_test_token_12345", timeout=1.0)

    # Test Tier 2 fallback on invalid token / offline
    health = connector.check_appeears_token_health()
    assert health["data_mode"] == "verified_offline_archive"
    assert health["tier"] == 3

    # Test Tier 3 offline case loading
    case_res = connector.fetch_case_study("case_2_land_thermal_paradox", region_id="RondoniaAmazonArc")
    assert case_res["status"] == "success"
    assert case_res["data_mode"] == "verified_offline_archive"
    assert case_res["total_records"] == 300
    assert len(case_res["records"]) == 300

    # Test Tier 1 offline fallback to nearest region
    power_res = connector.fetch_nasa_power_point(lat=-10.8, lon=-61.9)
    assert power_res["status"] == "success"
    assert power_res["data_mode"] == "verified_offline_archive"
    assert power_res.get("nearest_region") == "RondoniaAmazonArc"
