import pytest
import os
import re
from schemas import (
    RegionalCoordinate,
    RegionalCompareRequest,
    DetectiveQueryRequest,
    VariableCatalogResponse
)
from main import (
    get_health,
    get_variables,
    get_paradox_presets,
    query_detective,
    analyze_live,
    compare_regions,
    PARADOX_PRESETS
)

def test_api_health():
    """Verifies health response structure and data pillars status."""
    health = get_health()
    assert health.status == "healthy"
    assert "catalog_json" in health.data_pillars
    assert "precipitation_csv" in health.data_pillars
    assert "modis_lst_ndvi_csv" in health.data_pillars
    assert "hydrology_benchmark_csv" in health.data_pillars

def test_api_variables_catalog():
    """Verifies that 20 variables are listed with complete metadata."""
    res = get_variables()
    assert len(res.variables) == 20
    var_ids = {v.identifier for v in res.variables}
    assert "T2M" in var_ids
    assert "PRECTOTCORR" in var_ids
    assert "TS" in var_ids
    assert "GWETROOT" in var_ids
    assert "ALLSKY_SFC_SW_DWN" in var_ids

def test_api_paradox_presets():
    """Verifies the 4 verified Earth System Paradox Case Studies."""
    res = get_paradox_presets()
    assert len(res.presets) == 4
    preset_ids = {p.id for p in res.presets}
    assert "amazon_deforestation_warming" in preset_ids
    assert "punjab_greening_hydrology" in preset_ids
    assert "indian_monsoon_divergence" in preset_ids
    assert "sahel_greening_warming" in preset_ids

def test_api_detective_query():
    """Verifies TF-IDF recommendation maps query to relevant NASA parameters."""
    req = DetectiveQueryRequest(query="Why is soil drying out in Northern India?")
    res = query_detective(req)
    rec_ids = [r.identifier for r in res.top_recommendations]
    # Should match root zone soil moisture or precipitation
    assert any(var in rec_ids for var in ["GWETROOT", "GWETTOP", "PRECTOTCORR", "GPM_PRECIP", "GLDAS_ROOTMOIST"])
    assert len(res.detective_guidance) > 10

def test_api_analyze_live_modis_ndvi():
    """Verifies live analysis pipeline for MODIS NDVI."""
    res = analyze_live(variable="NDVI", latitude=30.901, longitude=75.8573)
    assert res.variable == "NDVI"
    assert len(res.raw_values) >= 200
    assert len(res.stl.trend) == len(res.raw_values)
    assert res.metrics.observation_count >= 200
    assert isinstance(res.metrics.is_significant, bool)
    assert len(res.detective_briefing) > 30

def test_api_region_compare():
    """Verifies dual regional comparison between Amazon and Punjab."""
    req = RegionalCompareRequest(
        region_a=RegionalCoordinate(latitude=-10.875, longitude=-61.93, label="Rondonia"),
        region_b=RegionalCoordinate(latitude=30.901, longitude=75.8573, label="Punjab"),
        variable="NDVI"
    )
    res = compare_regions(req)
    assert res.region_a.location_label == "Rondonia"
    assert res.region_b.location_label == "Punjab"
    assert res.divergence.divergence_severity in ["Extreme Divergence", "Moderate Divergence", "Synchronous"]
    assert res.divergence.slope_difference_per_decade != 0.0

def test_security_input_coordinates_validation():
    """Verifies Pydantic rejects invalid latitude and longitude."""
    with pytest.raises(Exception):
        RegionalCoordinate(latitude=95.0, longitude=0.0) # lat > 90

    with pytest.raises(Exception):
        RegionalCoordinate(latitude=-95.0, longitude=0.0) # lat < -90

    with pytest.raises(Exception):
        RegionalCoordinate(latitude=0.0, longitude=195.0) # lon > 180

def test_security_zero_hardcoded_secrets():
    """Scans backend python files for API keys, passwords, or tokens."""
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secret_patterns = [
        re.compile(r'(?:api[_-]?key|secret|password|auth[_-]?token)\s*=\s*["\'][A-Za-z0-9+/=]{16,}["\']', re.IGNORECASE),
        re.compile(r'ghp_[A-Za-z0-9]{36}'),
        re.compile(r'AIza[0-9A-Za-z-_]{35}')
    ]

    for root, _, files in os.walk(backend_dir):
        if "tests" in root or "__pycache__" in root:
            continue
        for fname in files:
            if fname.endswith(".py"):
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        match = pattern.search(content)
                        assert match is None, f"Potential secret found in {fname}: {match.group(0)}"
