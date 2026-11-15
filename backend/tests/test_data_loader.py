import os
import pytest
import numpy as np
from data_loader import DataLoader, MISSING_VALUE_FLAGS

@pytest.fixture
def data_loader_instance():
    return DataLoader()

def test_dynamic_scan_and_classify(data_loader_instance):
    """Verifies that all 4 Earth System data pillars are detected."""
    report = data_loader_instance.scan_and_classify()
    assert report["status"] == "ready"
    assert report["total_files"] >= 5

    pillars = data_loader_instance.pillars
    assert len(pillars["catalog_json"]) >= 1, "Catalog JSON pillar missing"
    assert len(pillars["precipitation_csv"]) >= 2, "Precipitation CSV pillar missing"
    assert len(pillars["modis_lst_ndvi_csv"]) >= 2, "MODIS LST/NDVI pillar missing"
    assert len(pillars["hydrology_benchmark_csv"]) >= 1, "Hydrology benchmark pillar missing"

def test_detect_header_row_giovanni(data_loader_instance):
    """Verifies Giovanni multi-line metadata header is skipped dynamically."""
    gpm_files = data_loader_instance.pillars["precipitation_csv"]
    assert len(gpm_files) > 0
    fpath = os.path.join(data_loader_instance.data_dir, gpm_files[0])
    header_idx, cols = data_loader_instance.detect_header_row(fpath)
    # Giovanni metadata typically has 8 lines before the header row
    assert header_idx > 0
    assert any("time" in c.lower() for c in cols)
    assert any("precipitation" in c.lower() or "gpm" in c.lower() for c in cols)

def test_detect_header_row_appeears(data_loader_instance):
    """Verifies AppEEARS header is at line 0."""
    modis_files = data_loader_instance.pillars["modis_lst_ndvi_csv"]
    assert len(modis_files) > 0
    fpath = os.path.join(data_loader_instance.data_dir, modis_files[0])
    header_idx, cols = data_loader_instance.detect_header_row(fpath)
    assert header_idx == 0
    assert "Category" in cols or "ID" in cols

def test_extract_modis_ndvi(data_loader_instance):
    """Verifies NDVI extraction for Amazon and Punjab."""
    dates_az, vals_az, meta_az = data_loader_instance.extract_modis_timeseries("NDVI", "RondoniaAmazonArc")
    assert len(vals_az) >= 200
    assert all(-0.2 <= v <= 1.0 for v in vals_az)
    assert meta_az["latitude"] == -10.875

    dates_pj, vals_pj, meta_pj = data_loader_instance.extract_modis_timeseries("NDVI", "PunjabIrrigatedBelt")
    assert len(vals_pj) >= 200
    assert all(-0.2 <= v <= 1.0 for v in vals_pj)

def test_extract_modis_lst_cloud_cleaning(data_loader_instance):
    """Verifies MODIS LST 0.0 cloud values are cleansed and values are in Kelvin (>200K)."""
    dates, vals, meta = data_loader_instance.extract_modis_timeseries("LST", "RondoniaAmazonArc")
    assert len(vals) >= 200
    assert all(v > 200.0 for v in vals), "Cloud 0.0 values must be filtered"

def test_extract_giovanni_gpm_precipitation(data_loader_instance):
    """Verifies GPM IMERG monthly precipitation extraction."""
    dates, vals, meta = data_loader_instance.extract_giovanni_gpm_timeseries("central")
    assert len(vals) >= 200
    assert all(v >= 0.0 for v in vals)

def test_extract_gldas_hydrology(data_loader_instance):
    """Verifies GLDAS soil moisture extraction."""
    dates, vals, meta = data_loader_instance.extract_gldas_timeseries("PunjabIrrigatedBelt")
    assert len(vals) >= 200
    assert all(v > 0.0 for v in vals)

def test_parse_uploaded_csv_giovanni_bbox_extraction():
    """Verifies that Giovanni coordinate bounding box in filename is extracted as region_label with location name."""
    csv_content = """time,GPM_3IMERGM_07_precipitation
2001-01-01,12.5
2001-02-01,15.8
2001-03-01,22.1
"""
    filename = "g4.areaAvgTimeSeries.GPM_3IMERGM_07_precipitation.20010101-20241231.75E_18N_77E_20N.csv"
    df = DataLoader.parse_uploaded_csv(csv_content, filename=filename)
    assert df["region_label"].iloc[0] == "Uploaded: Marathwada, India"
    assert df["region_id"].iloc[0] == "Uploaded: Marathwada, India"
    assert df["lat"].iloc[0] == 19.0
    assert df["lon"].iloc[0] == 76.0
    assert len(df) == 3

def test_parse_uploaded_csv_header_metadata_extraction():
    """Verifies that Title/Region header metadata in CSV is extracted as region_label with location name."""
    csv_content = """# Giovanni - The Bridge Between Data and Science
# Title: Area-Averaged Time Series (Marathwada)
# Units: mm/month
time,GPM_3IMERGM_07_precipitation
2001-01-01,12.5
2001-02-01,15.8
"""
    df = DataLoader.parse_uploaded_csv(csv_content, filename="random_upload.csv")
    assert df["region_label"].iloc[0] == "Uploaded: Marathwada, India"
    assert df["lat"].iloc[0] == 19.25
    assert df["lon"].iloc[0] == 76.25

def test_parse_uploaded_csv_clean_fallback():
    """Verifies that when no geo-data exists, clean fallback label is used instead of raw filename."""
    csv_content = """time,temperature
2001-01-01,25.4
2001-02-01,26.1
"""
    df_a = DataLoader.parse_uploaded_csv(csv_content, filename="raw_ugly_long_file_name_12345.csv", default_label="Uploaded Dataset A")
    assert df_a["region_label"].iloc[0] == "Uploaded Dataset A"

    df_b = DataLoader.parse_uploaded_csv(csv_content, filename="raw_ugly_long_file_name_67890.csv", default_label="Uploaded Dataset B")
    assert df_b["region_label"].iloc[0] == "Uploaded Dataset B"

