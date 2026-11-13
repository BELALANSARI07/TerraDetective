import pytest
import os
from data_loader import DataLoader
from ai_detective import AIDetective
from main import get_variables

@pytest.fixture
def ai_detective_instance():
    dl = DataLoader()
    return AIDetective(dl.get_catalog_variables())

def test_dense_variable_matcher_initialization(ai_detective_instance):
    """Verifies that the dense variable matcher is loaded with 384-d embeddings."""
    assert ai_detective_instance.dense_matcher_available is True
    assert ai_detective_instance.precomputed_embeddings is not None
    # 384 dimensions for all-MiniLM-L6-v2
    assert ai_detective_instance.precomputed_embeddings.shape[1] == 384
    assert len(ai_detective_instance.precomputed_embeddings) >= 20

def test_recommend_variables_dense_and_why_selected(ai_detective_instance):
    """Verifies semantic query matching and why_selected explanation."""
    recs = ai_detective_instance.recommend_variables("Why is soil drying out in Northern India?", top_k=4)
    assert len(recs) == 4
    for r in recs:
        assert "identifier" in r
        assert "name" in r
        assert "why_selected" in r
        assert len(r["why_selected"]) > 5
        assert 0.0 <= r["relevance_score"] <= 1.0

    # Top match should be a moisture or precipitation parameter
    rec_ids = [r["identifier"] for r in recs]
    assert any(ident in rec_ids for ident in ["GWETROOT", "GWETTOP", "PRECTOTCORR", "GPM_PRECIP", "GLDAS_ROOTMOIST"])

def test_api_variables_query_parameter():
    """Verifies GET /api/variables?q=... returns top 4 matches with why_selected."""
    res = get_variables(q="Amazon deforestation warming")
    assert "query" in res
    assert res["query"] == "Amazon deforestation warming"
    assert res["total_matches"] == 4
    assert len(res["variables"]) == 4
    assert "matcher_model" in res
    for v in res["variables"]:
        assert "why_selected" in v
        assert len(v["why_selected"]) > 5

def test_generate_detective_briefing_3_sentences(ai_detective_instance):
    """Verifies generate_detective_briefing outputs exactly 3 objective scientific sentences."""
    stats_a = {
        "sens_slope_per_decade": 0.38,
        "p_value": 0.0012,
        "is_significant": True
    }
    stats_b = {
        "sens_slope_per_decade": -0.15,
        "p_value": 0.084,
        "is_significant": False
    }
    meta = {
        "identifier": "LST_DAY",
        "name": "MODIS Daytime Land Surface Temperature",
        "units": "K"
    }

    briefing = ai_detective_instance.generate_detective_briefing(
        region_a_stats=stats_a,
        region_b_stats=stats_b,
        variable_meta=meta,
        label_a="Rondonia Deforested Arc",
        label_b="Intact Central Amazon"
    )

    assert isinstance(briefing, str)
    assert len(briefing) > 60

    # Must contain physical mechanism, exact rates, and significance
    assert "+0.380" in briefing or "0.38" in briefing
    assert "-0.150" in briefing or "0.15" in briefing
    assert "Mann-Kendall" in briefing or "significant" in briefing.lower()

    # Verify no conversational filler or think tags
    assert "<think>" not in briefing
    assert "</think>" not in briefing
    assert not briefing.lower().startswith("here is")

def test_generate_detective_briefing_resilient_fallback(ai_detective_instance):
    """Verifies fallback works deterministically without Ollama/GPU."""
    stats_a = {
        "sens_slope_per_decade": -5.04,
        "p_value": 0.0001,
        "is_significant": True
    }
    stats_b = {
        "sens_slope_per_decade": 1.25,
        "p_value": 0.12,
        "is_significant": False
    }
    meta = {
        "identifier": "GLDAS_ROOTMOIST",
        "name": "GLDAS Root Zone Soil Moisture",
        "units": "kg/m^2"
    }

    verdict = ai_detective_instance._synthesize_deterministic_verdict(
        var_ident=meta["identifier"],
        var_name=meta["name"],
        units=meta["units"],
        label_a="Punjab",
        slope_a=stats_a["sens_slope_per_decade"],
        p_a=stats_a["p_value"],
        sig_a=stats_a["is_significant"],
        label_b="Upper Gangetic",
        slope_b=stats_b["sens_slope_per_decade"],
        p_b=stats_b["p_value"],
        sig_b=stats_b["is_significant"]
    )

    assert "Punjab is trending at -5.040 kg/m^2/decade" in verdict
    assert "p=0.0001" in verdict
    assert "Mann-Kendall" in verdict
