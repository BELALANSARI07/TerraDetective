import pytest
import numpy as np
import pandas as pd
from stats_engine import StatsEngine

@pytest.fixture
def stats_engine_instance():
    return StatsEngine(seasonal_period=12)

def test_sanitize_series_filters_yyyy13(stats_engine_instance):
    """Verifies that NASA POWER YYYY13 annual summary keys are stripped."""
    dates = ["2020-01", "2020-02", "2020-03", "202013", "2020-04", "202113"]
    values = [10.0, 12.0, 14.0, 999.0, 16.0, 888.0]
    s, clean_dates = stats_engine_instance.sanitize_series(dates, values)

    assert not any("13" in d and len(d) == 6 for d in clean_dates)
    assert not any(d.endswith("-13-01") for d in clean_dates)

def test_sanitize_series_cleans_missing_flags(stats_engine_instance):
    """Verifies that -999 and -9999.0 flags are converted to valid interpolated values."""
    dates = [f"2020-{m:02d}-01" for m in range(1, 13)]
    values = [20.0, 22.0, -999.0, 26.0, 28.0, -9999.0, 32.0, 30.0, 28.0, 26.0, 24.0, 22.0]
    s, clean_dates = stats_engine_instance.sanitize_series(dates, values)

    assert len(s) == 12
    assert not any(np.isnan(s.values))
    assert not any(v in {-999, -9999.0} for v in s.values)

def test_stl_decomposition(stats_engine_instance):
    """Verifies STL decomposition returns trend, seasonal, residual with matching lengths."""
    # 5 years of synthetic monthly data
    t = np.arange(60)
    seasonal = 10.0 * np.sin(2 * np.pi * t / 12.0)
    trend = 0.5 * t
    noise = np.random.normal(0, 0.5, 60)
    series = pd.Series(trend + seasonal + noise)

    res = stats_engine_instance.run_stl_decomposition(series)
    assert len(res["trend"]) == 60
    assert len(res["seasonal"]) == 60
    assert len(res["residual"]) == 60
    assert res["seasonal_period"] == 12

def test_mann_kendall_significance_and_decadal_slope(stats_engine_instance):
    """Verifies Sen's slope scaling to decade (120 * monthly slope) and p-value."""
    # Strong upward trend
    t = np.arange(120) # 10 years
    seasonal = 5.0 * np.sin(2 * np.pi * t / 12.0)
    trend = 0.05 * t # 0.05 per month -> 6.0 per decade
    series = pd.Series(trend + seasonal)

    metrics = stats_engine_instance.run_mann_kendall(series)
    assert metrics["is_significant"] is True
    assert metrics["trend_direction"] == "increasing"
    assert metrics["p_value"] < 0.05
    # Sen's slope per decade should be close to 6.0
    assert abs(metrics["sens_slope_per_decade"] - 6.0) < 1.0

def test_compute_regional_divergence_extreme(stats_engine_instance):
    """Verifies detection of opposite trends as Extreme Divergence."""
    metrics_a = {
        "sens_slope_per_decade": 0.45,
        "is_significant": True,
        "trend_direction": "increasing"
    }
    metrics_b = {
        "sens_slope_per_decade": -0.35,
        "is_significant": True,
        "trend_direction": "decreasing"
    }

    div = stats_engine_instance.compute_regional_divergence(metrics_a, metrics_b, "Amazon", "Punjab")
    assert div["opposite_trends"] is True
    assert div["divergence_severity"] == "Extreme Divergence"
    assert div["slope_difference_per_decade"] == 0.8
    assert "opposing" in div["comparative_verdict"].lower()
