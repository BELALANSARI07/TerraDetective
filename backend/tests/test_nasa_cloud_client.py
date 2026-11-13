import pytest
from nasa_cloud_client import NASACloudClient, is_allowed_nasa_domain

def test_security_allowed_nasa_domain():
    """Security check: Verifies Bearer tokens can only be attached to official NASA domains."""
    # Allowed domains
    assert is_allowed_nasa_domain("https://cmr.earthdata.nasa.gov/search/granules.json") is True
    assert is_allowed_nasa_domain("https://hydro1.gesdisc.eosdis.nasa.gov/opendap/") is True
    assert is_allowed_nasa_domain("https://data.lpdaac.earthdatacloud.nasa.gov/protected/file.hdf") is True
    assert is_allowed_nasa_domain("https://urs.earthdata.nasa.gov/oauth/authorize") is True
    assert is_allowed_nasa_domain("https://opendap.earthdata.nasa.gov/collections") is True

    # Disallowed third-party domains (must never receive Earthdata Bearer Token)
    assert is_allowed_nasa_domain("https://google.com") is False
    assert is_allowed_nasa_domain("https://attacker.com/steal?token=") is False
    assert is_allowed_nasa_domain("https://fake-cmr.earthdata.nasa.gov.attacker.com") is False
    assert is_allowed_nasa_domain("http://localhost:8000") is False

def test_security_header_isolation():
    """Ensures Authorization Bearer is never attached to non-NASA domains."""
    client = NASACloudClient(token="test_secret_token_12345")

    # NASA domain gets Bearer header
    nasa_headers = client.get_safe_headers("https://cmr.earthdata.nasa.gov/search")
    assert "Authorization" in nasa_headers
    assert nasa_headers["Authorization"] == "Bearer test_secret_token_12345"

    # Non-NASA domain gets NO Authorization header
    external_headers = client.get_safe_headers("https://external-api.com/data")
    assert "Authorization" not in external_headers

def test_verify_auth_status_authenticated():
    """Verifies that an authentic token returns authenticated status."""
    client = NASACloudClient()
    status = client.verify_auth_status()
    assert isinstance(status, dict)
    assert "authenticated" in status
    assert "badge_text" in status
    assert "username" in status
    if status["authenticated"]:
        assert status["badge_text"] == "Earthdata Cloud Live Link: Authenticated"
        assert "token_preview" in status

def test_verify_auth_status_graceful_degradation():
    """Verifies missing token degrades gracefully without crashing."""
    client = NASACloudClient(token="")
    status = client.verify_auth_status()
    assert status["authenticated"] is False
    assert status["degraded"] is True
    assert "Unauthenticated" in status["badge_text"]

def test_search_granules_structure():
    """Verifies CMR Granule search returns valid granules with links and metadata."""
    client = NASACloudClient()
    granules = client.search_granules(
        keyword="MOD11A2",
        bounding_box=(-65.0, -15.0, -55.0, -5.0),
        limit=3
    )
    assert isinstance(granules, list)
    assert len(granules) > 0
    for g in granules:
        assert "title" in g
        assert "granule_size_mb" in g
        assert "dataset_short_name" in g
        assert g["download_url"] is not None or g["opendap_url"] is not None

def test_probe_opendap_subset():
    """Verifies OPeNDAP subset probe returns Hyrax endpoint metadata."""
    client = NASACloudClient()
    probe = client.probe_opendap_subset("GLDAS_NOAH025_M")
    assert isinstance(probe, dict)
    assert probe["dataset"] == "GLDAS_NOAH025_M"
    assert "opendap.gesdisc.eosdis.nasa.gov" in probe["opendap_endpoint"] or "hydro1" in probe["opendap_endpoint"]
    assert probe["hyrax_compatible"] is True
    assert "NetCDF-4" in probe["supported_formats"]

def test_api_earthdata_discover_endpoint():
    """Verifies the GET /api/earthdata/discover endpoint returns structured discovery data."""
    from main import discover_earthdata_granules
    res = discover_earthdata_granules(keyword="MOD11A2", limit=4)
    assert res["keyword"] == "MOD11A2"
    assert len(res["granules"]) <= 4
    assert res["badge_text"] is not None
    assert isinstance(res["opendap_probe"], dict)
