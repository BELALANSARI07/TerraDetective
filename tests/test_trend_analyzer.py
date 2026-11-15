"""
TerraDetective Automated Unit & Statistical Validation Tests: Trend Analyzer
NASA Space Apps Challenge: 'Be An Earth System Trend Detective!'

Tests verify:
1. Synthetic ground-truth recovery:
   - Monotonic upward trend + 12-month sinusoidal seasonality
   - Asserts is_significant == True
   - Asserts trend_direction == 'increasing'
   - Asserts recovered slope matches ground truth within 5% error
2. Pure random white noise null hypothesis:
   - Asserts is_significant == False
3. STL decomposition identity:
   - Asserts observed == trend + seasonal + residual
   - Asserts deseasonalized == observed - seasonal
4. OLS regression confidence intervals:
   - Asserts slope_ci_95_low <= ols_slope <= slope_ci_95_high
   - Asserts ci_band_lower <= trend_line <= ci_band_upper
5. Twin-region divergence detector:
   - Asserts divergence_detected == True for opposite-trend paradox pairs
6. Real NASA benchmark data execution:
   - Evaluates all 3 cases from terradetective_unified_monthly
   - Prints scientific summary audit table
   - Validates data/processed/case_studies_stats.json integrity
7. Robustness:
   - Handles series with < 24 months via fallback gracefully
"""

from __future__ import annotations

import json
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

import sys
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from services.trend_analyzer import (
    analyze_time_series,
    compare_regions,
    decompose_stl,
    compute_mann_kendall,
    compute_ols_regression,
    precompute_case_studies,
)

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# -------------------------------------------------------------------------
# Test Suite 1: Synthetic Ground-Truth Recovery
# -------------------------------------------------------------------------
def test_synthetic_monotonic_trend_with_seasonality():
    """
    Constructs a synthetic time series with known ground truth:
    - n = 240 months (20 years)
    - True annual slope = +0.60 units/year (+0.05 units/month)
    - True seasonality = 3.0 * sin(2 * pi * t / 12)
    - Gaussian noise = N(0, 0.05)

    Asserts:
    - Mann-Kendall is_significant == True
    - trend_direction == 'increasing'
    - Recovered Sen's slope matches ground truth within 5%
    - Recovered OLS slope matches ground truth within 5%
    """
    np.random.seed(42)
    n = 240
    t = np.arange(n)
    true_slope_per_month = 0.05
    true_slope_per_year = true_slope_per_month * 12.0  # 0.60

    seasonality = 3.0 * np.sin(2.0 * np.pi * t / 12.0)
    noise = np.random.normal(0.0, 0.05, n)
    observed = 15.0 + true_slope_per_month * t + seasonality + noise

    dates = [f"{2000 + i // 12:04d}-{(i % 12) + 1:02d}-01" for i in range(n)]
    df = pd.DataFrame({
        "date": dates,
        "value": observed,
        "region_id": "synthetic_region",
        "variable_name": "Synthetic Test Variable",
        "unit": "units",
    })

    result = analyze_time_series(df, alpha=0.05)

    # 1. Non-parametric Mann-Kendall checks
    mk_stats = result["mann_kendall"]
    assert mk_stats["is_significant"] is True, "Expected Mann-Kendall to be significant"
    assert mk_stats["trend_direction"] == "increasing", f"Expected 'increasing', got '{mk_stats['trend_direction']}'"
    assert mk_stats["confidence_pct"] >= 99.0, f"Expected confidence >= 99%, got {mk_stats['confidence_pct']}"

    recovered_sens_yr = mk_stats["sens_slope_per_year"]
    error_pct = abs(recovered_sens_yr - true_slope_per_year) / true_slope_per_year * 100.0
    assert error_pct <= 5.0, f"Sen's slope error ({error_pct:.2f}%) exceeds 5% threshold!"

    # 2. Parametric OLS checks
    ols_stats = result["ols_regression"]
    recovered_ols_yr = ols_stats["ols_slope_per_year"]
    ols_error_pct = abs(recovered_ols_yr - true_slope_per_year) / true_slope_per_year * 100.0
    assert ols_error_pct <= 5.0, f"OLS slope error ({ols_error_pct:.2f}%) exceeds 5% threshold!"

    # 3. Seasonal Mann-Kendall check
    smk_stats = result["seasonal_mann_kendall"]
    assert smk_stats["is_significant"] is True
    assert smk_stats["trend_direction"] == "increasing"


# -------------------------------------------------------------------------
# Test Suite 2: Null Hypothesis / Pure Random Noise
# -------------------------------------------------------------------------
def test_pure_random_white_noise():
    """
    Tests trend analyzer against pure uncorrelated Gaussian white noise:
    - n = 240 months
    - Asserts that no statistically significant trend is detected (is_significant == False).
    """
    np.random.seed(12345)
    n = 240
    noise = np.random.normal(0.0, 1.0, n)
    dates = [f"{2000 + i // 12:04d}-{(i % 12) + 1:02d}-01" for i in range(n)]

    df = pd.DataFrame({
        "date": dates,
        "value": noise,
        "region_id": "white_noise_region",
        "variable_name": "White Noise",
        "unit": "units",
    })

    result = analyze_time_series(df, alpha=0.05)
    mk_stats = result["mann_kendall"]

    assert mk_stats["is_significant"] is False, f"Expected insignificant result on white noise, got p={mk_stats['p_value']}"
    assert mk_stats["trend_direction"] == "no trend", f"Expected 'no trend', got '{mk_stats['trend_direction']}'"


# -------------------------------------------------------------------------
# Test Suite 3: STL Decomposition & Geometric Consistency
# -------------------------------------------------------------------------
def test_stl_decomposition_identity():
    """
    Verifies that STL decomposition satisfies exact additive identities:
    observed == trend + seasonal + residual
    deseasonalized == observed - seasonal
    """
    np.random.seed(99)
    n = 120
    t = np.arange(n)
    y = 20.0 + 0.1 * t + 5.0 * np.cos(2.0 * np.pi * t / 12.0) + np.random.normal(0.0, 0.2, n)

    trend, seasonal, residual, deseasonalized = decompose_stl(y, period=12, robust=True)

    reconstructed = trend + seasonal + residual
    np.testing.assert_allclose(y, reconstructed, rtol=1e-5, atol=1e-5, err_msg="STL reconstructed sum must match observed")

    expected_deseasonalized = y - seasonal
    np.testing.assert_allclose(deseasonalized, expected_deseasonalized, rtol=1e-5, atol=1e-5)


def test_ols_confidence_bounds():
    """
    Verifies that OLS regression confidence intervals and mean response bands
    are geometrically consistent.
    """
    np.random.seed(77)
    n = 120
    t_years = np.arange(n) / 12.0
    y = 5.0 + 0.4 * t_years + np.random.normal(0.0, 0.5, n)

    ols = compute_ols_regression(t_years, y, alpha=0.05)

    # Slope CI bounds the estimated slope
    assert ols["slope_ci_95_low"] <= ols["ols_slope_per_year"] <= ols["slope_ci_95_high"]

    # Mean response CI bounds upper and lower envelop the trend line
    trend_line = np.array(ols["trend_line"])
    ci_upper = np.array(ols["ci_band_upper"])
    ci_lower = np.array(ols["ci_band_lower"])

    assert np.all(ci_lower <= trend_line + 1e-6)
    assert np.all(trend_line <= ci_upper + 1e-6)


# -------------------------------------------------------------------------
# Test Suite 4: Twin-Region Divergence Comparator
# -------------------------------------------------------------------------
def test_twin_region_divergence_comparator():
    """
    Tests compare_regions() with synthetic opposing trajectories:
    Region A warms by +1.0/year, Region B cools by -1.0/year.
    Asserts divergence_detected == True and opposite_direction == True.
    """
    n = 120
    dates = [f"{2000 + i // 12:04d}-{(i % 12) + 1:02d}-01" for i in range(n)]

    df_a = pd.DataFrame({
        "date": dates,
        "value": 10.0 + 0.1 * np.arange(n),
        "region_id": "warming_zone",
        "region_label": "Warming Zone",
        "variable_name": "Skin Temperature",
        "unit": "°C",
    })

    df_b = pd.DataFrame({
        "date": dates,
        "value": 30.0 - 0.1 * np.arange(n),
        "region_id": "cooling_zone",
        "region_label": "Cooling Zone",
        "variable_name": "Skin Temperature",
        "unit": "°C",
    })

    comp = compare_regions(df_a, df_b, alpha=0.05)
    div = comp["divergence_analysis"]

    assert div["divergence_detected"] is True
    assert div["opposite_direction"] is True
    assert div["slope_difference_per_decade"] > 0


# -------------------------------------------------------------------------
# Test Suite 5: Real NASA Paradox Benchmark Verification
# -------------------------------------------------------------------------
def test_real_nasa_paradox_cases_and_stats_json():
    """
    Ingests terradetective_unified_monthly.csv, runs trend analyzer on all 3 cases,
    validates scientific findings, prints summary audit table, and verifies case_studies_stats.json.
    """
    csv_path = PROCESSED_DIR / "terradetective_unified_monthly.csv"
    assert csv_path.is_file(), f"Unified CSV missing at: {csv_path}"
    df = pd.read_csv(csv_path)

    json_path = PROCESSED_DIR / "case_studies_stats.json"
    if not json_path.is_file():
        precompute_case_studies(processed_dir=PROCESSED_DIR, output_json_path=json_path)

    assert json_path.is_file()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "cases" in data
    cases = data["cases"]
    assert len(cases) == 3

    # Case 2: Land Thermal Paradox
    case2 = cases["case_2_land_thermal_paradox"]
    assert case2["divergence_analysis"]["divergence_detected"] is True
    assert case2["region_a"]["mann_kendall"]["trend_direction"] == "increasing"   # Rondonia warming
    assert case2["region_b"]["mann_kendall"]["trend_direction"] == "decreasing"   # Punjab cooling

    # Case 3: Vegetation Paradox
    case3 = cases["case_3_vegetation_paradox"]
    assert case3["divergence_analysis"]["divergence_detected"] is True
    assert case3["region_a"]["mann_kendall"]["trend_direction"] == "decreasing"   # Rondonia browning
    assert case3["region_b"]["mann_kendall"]["trend_direction"] == "increasing"   # Punjab greening

    # Case 1: Monsoon Disparity
    case1 = cases["case_1_monsoon_paradox"]
    assert case1["region_a"]["total_records"] == 297
    assert case1["region_b"]["total_records"] == 297

    # Print summary table as requested in prompt
    print("\n" + "=" * 105)
    print("REAL NASA CASE AUDIT SUMMARY TABLE (tests/test_trend_analyzer.py)")
    print("=" * 105)
    print(f"{'Case ID':<28} | {'Region':<22} | {'Variable':<12} | {'Sen/yr':<9} | {'Sen/dec':<9} | {'MK p-val':<10} | {'95% CI':<15} | {'Verdict'}")
    print("-" * 105)

    for cid, c_data in cases.items():
        for r_key in ["region_a", "region_b"]:
            r = c_data[r_key]
            rid = r["region_id"]
            var = r["variable_id"]
            sen_yr = f"{r['mann_kendall']['sens_slope_per_year']:+.4f}"
            sen_dec = f"{r['mann_kendall']['sens_slope_per_decade']:+.4f}"
            mk_p = f"{r['mann_kendall']['p_value']:.4e}" if isinstance(r['mann_kendall']['p_value'], float) and r['mann_kendall']['p_value'] < 0.001 else f"{r['mann_kendall']['p_value']:.4f}"
            ci = f"[{r['ols_regression']['slope_ci_95_low']:+.3f}, {r['ols_regression']['slope_ci_95_high']:+.3f}]"
            verdict = "SIGNIFICANT" if r["mann_kendall"]["is_significant"] else "NOT SIG"
            print(f"{cid:<28} | {rid:<22} | {var:<12} | {sen_yr:<9} | {sen_dec:<9} | {mk_p:<10} | {ci:<15} | {verdict}")

    print("=" * 105 + "\n")


# -------------------------------------------------------------------------
# Test Suite 6: Short Series Fallback
# -------------------------------------------------------------------------
def test_short_series_fallback():
    """
    Verifies that analyze_time_series handles series with fewer than 24 months
    using rolling mean fallback without raising exceptions.
    """
    n = 18
    dates = [f"2020-{i+1:02d}-01" if i < 12 else f"2021-{i-11:02d}-01" for i in range(n)]
    df = pd.DataFrame({
        "date": dates,
        "value": np.linspace(10.0, 20.0, n),
        "region_id": "short_region",
    })

    result = analyze_time_series(df)
    assert result["total_records"] == 18
    assert len(result["trend"]) == 18
    assert len(result["deseasonalized"]) == 18
    assert "mann_kendall" in result
