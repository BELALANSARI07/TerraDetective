"""
TerraDetective Statistical Significance & Seasonal Decomposition Engine
NASA Space Apps Challenge: 'Be An Earth System Trend Detective!'

Provides rigorous climate statistical analysis:
1. STL Seasonal-Trend Decomposition (Loess, period=12, robust=True)
2. Non-Parametric Mann-Kendall & Seasonal Mann-Kendall Trend Tests
   (Sen's slope per month/year/decade, Kendall's tau, z-score, p-value, confidence %)
3. Parametric Ordinary Least Squares (OLS) Linear Regression with 95% Confidence Intervals
   and mean response CI bands (for Plotly shaded cones)
4. Twin-Region Divergence Comparator (detects statistical divergence across paradox pairs)
5. Pre-computes and exports case study baselines to data/processed/case_studies_stats.json
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import polars as pl
import pymannkendall as mk
from scipy import stats
from statsmodels.tsa.seasonal import STL

logger = logging.getLogger("terradetective.trend_analyzer")


def decompose_stl(
    observed: np.ndarray,
    period: int = 12,
    robust: bool = True,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Performs STL (Seasonal and Trend decomposition using Loess).

    Returns:
        (trend, seasonal, residual, deseasonalized) as numpy arrays.
    """
    n_obs = len(observed)

    # Clean any internal NaNs via linear interpolation
    s_obs = pd.Series(observed, dtype=float).interpolate(method="linear").bfill().ffill()
    clean_obs = s_obs.to_numpy()

    if n_obs < 2 * period:
        # Fallback for short time series (< 24 months)
        logger.warning(f"Time series length ({n_obs}) < 24 months. Using rolling mean fallback.")
        window = min(n_obs, max(3, period // 2))
        trend = (
            pd.Series(clean_obs)
            .rolling(window=window, center=True, min_periods=1)
            .mean()
            .bfill()
            .ffill()
            .to_numpy()
        )
        seasonal = np.zeros(n_obs, dtype=float)
        residual = clean_obs - trend
        deseasonalized = clean_obs.copy()
        return trend, seasonal, residual, deseasonalized

    try:
        stl_model = STL(clean_obs, period=period, robust=robust)
        res = stl_model.fit()
        trend = res.trend
        seasonal = res.seasonal
        residual = res.resid
        deseasonalized = clean_obs - seasonal
        return trend, seasonal, residual, deseasonalized
    except Exception as e:
        logger.warning(f"STL decomposition failed ({e}). Falling back to rolling mean.")
        trend = (
            pd.Series(clean_obs)
            .rolling(window=period, center=True, min_periods=1)
            .mean()
            .bfill()
            .ffill()
            .to_numpy()
        )
        seasonal = np.zeros(n_obs, dtype=float)
        residual = clean_obs - trend
        deseasonalized = clean_obs.copy()
        return trend, seasonal, residual, deseasonalized


def compute_mann_kendall(
    deseasonalized: np.ndarray,
    observed: np.ndarray,
    period: int = 12,
    alpha: float = 0.05,
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Executes both standard Mann-Kendall on deseasonalized values
    and Seasonal Mann-Kendall directly on raw seasonal observations.
    """
    # 1. Standard Mann-Kendall on Deseasonalized Series
    mk_orig = mk.original_test(deseasonalized, alpha=alpha)

    p_val = float(mk_orig.p)
    tau_val = float(mk_orig.Tau)
    z_score = float(mk_orig.z)
    trend_dir = str(mk_orig.trend)
    sens_slope_month = float(mk_orig.slope)
    sens_slope_year = float(sens_slope_month * 12.0)
    sens_slope_decade = float(sens_slope_month * 120.0)

    is_significant = bool(p_val < alpha)
    # Confidence percentage capped at 99.99% for student-friendly displays
    confidence_pct = min(99.99, max(0.0, round((1.0 - p_val) * 100.0, 2)))

    n_months = len(deseasonalized)
    total_years = max(1.0, (n_months - 1) / 12.0)
    total_estimated_change = round(sens_slope_year * total_years, 4)

    mk_metrics = {
        "trend_direction": trend_dir,
        "tau": round(tau_val, 4),
        "p_value": float(np.format_float_scientific(p_val, precision=5)) if p_val < 0.0001 else round(p_val, 5),
        "z_score": round(z_score, 4),
        "is_significant": is_significant,
        "confidence_pct": confidence_pct,
        "sens_slope_per_month": round(sens_slope_month, 6),
        "sens_slope_per_year": round(sens_slope_year, 5),
        "sens_slope_per_decade": round(sens_slope_decade, 4),
        "total_estimated_change": total_estimated_change,
        "total_change": total_estimated_change,
        "test_name": "Mann-Kendall Trend Test (Deseasonalized)",
    }

    # 2. Seasonal Mann-Kendall Test on Raw Observed Data
    if len(observed) >= 2 * period:
        try:
            smk_res = mk.seasonal_test(observed, period=period, alpha=alpha)
            smk_p = float(smk_res.p)
            seasonal_mk_metrics = {
                "trend_direction": str(smk_res.trend),
                "tau": round(float(smk_res.Tau), 4),
                "p_value": float(np.format_float_scientific(smk_p, precision=5)) if smk_p < 0.0001 else round(smk_p, 5),
                "z_score": round(float(smk_res.z), 4),
                "is_significant": bool(smk_p < alpha),
                "seasonal_slope_per_year": round(float(smk_res.slope), 5),
                "test_name": "Seasonal Mann-Kendall Test (Observed)",
            }
        except Exception as e:
            logger.warning(f"Seasonal Mann-Kendall computation failed ({e}).")
            seasonal_mk_metrics = {
                "trend_direction": trend_dir,
                "tau": round(tau_val, 4),
                "p_value": round(p_val, 5),
                "z_score": round(z_score, 4),
                "is_significant": is_significant,
                "seasonal_slope_per_year": round(sens_slope_year, 5),
                "test_name": "Seasonal Mann-Kendall Test (Fallback)",
            }
    else:
        seasonal_mk_metrics = {
            "trend_direction": trend_dir,
            "tau": round(tau_val, 4),
            "p_value": round(p_val, 5),
            "z_score": round(z_score, 4),
            "is_significant": is_significant,
            "seasonal_slope_per_year": round(sens_slope_year, 5),
            "test_name": "Seasonal Mann-Kendall Test (Insufficient Length)",
        }

    return mk_metrics, seasonal_mk_metrics


def compute_ols_regression(
    t_years: np.ndarray,
    deseasonalized: np.ndarray,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """
    Computes Ordinary Least Squares (OLS) linear regression against elapsed years.
    Derives 95% confidence intervals for annual rate of change and
    mean response confidence bounds (shaded ribbon cone).
    """
    n = len(t_years)
    reg = stats.linregress(t_years, deseasonalized)

    slope_yr = float(reg.slope)
    intercept = float(reg.intercept)
    r_squared = float(reg.rvalue ** 2)
    p_val = float(reg.pvalue)
    stderr_yr = float(reg.stderr)

    # Student's t critical value for two-sided (1 - alpha) CI
    df = max(1, n - 2)
    t_crit = float(stats.t.ppf(1.0 - alpha / 2.0, df=df))

    slope_ci_low = slope_yr - t_crit * stderr_yr
    slope_ci_high = slope_yr + t_crit * stderr_yr

    # Fitted trend line
    trend_line = intercept + slope_yr * t_years

    # Mean response confidence band across time
    residuals = deseasonalized - trend_line
    s_err = np.sqrt(np.sum(residuals ** 2) / df)
    mean_t = np.mean(t_years)
    ss_t = np.sum((t_years - mean_t) ** 2)

    if ss_t > 0:
        ci_band_half = t_crit * s_err * np.sqrt((1.0 / n) + ((t_years - mean_t) ** 2) / ss_t)
    else:
        ci_band_half = np.zeros(n)

    ci_upper = trend_line + ci_band_half
    ci_lower = trend_line - ci_band_half

    return {
        "ols_slope_per_year": round(slope_yr, 5),
        "ols_slope_per_decade": round(slope_yr * 10.0, 4),
        "ols_intercept": round(intercept, 4),
        "r_squared": round(r_squared, 4),
        "t_test_p_value": float(np.format_float_scientific(p_val, precision=5)) if p_val < 0.0001 else round(p_val, 5),
        "stderr_per_year": round(stderr_yr, 6),
        "slope_ci_95_low": round(slope_ci_low, 5),
        "slope_ci_95_high": round(slope_ci_high, 5),
        "trend_line": [round(float(v), 4) for v in trend_line],
        "ci_band_upper": [round(float(v), 4) for v in ci_upper],
        "ci_band_lower": [round(float(v), 4) for v in ci_lower],
    }


def analyze_time_series(
    df_region: pd.DataFrame,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """
    Primary statistical analysis pipeline for a single region's monthly time series.

    Input DataFrame must contain:
    - 'date': YYYY-MM-01 format string
    - 'value': float observation

    Optional columns:
    - 'case_id', 'region_id', 'region_label', 'variable_id', 'variable_name', 'unit'
    """
    if df_region.empty:
        raise ValueError("Cannot analyze empty time series DataFrame.")

    # Sort strictly by date
    df_sorted = df_region.sort_values("date").reset_index(drop=True).copy()

    dates = df_sorted["date"].astype(str).tolist()
    values = df_sorted["value"].astype(float).to_numpy()

    # Metadata extraction
    case_id = str(df_sorted["case_id"].iloc[0]) if "case_id" in df_sorted.columns else "custom_case"
    region_id = str(df_sorted["region_id"].iloc[0]) if "region_id" in df_sorted.columns else "region_a"
    region_label = str(df_sorted["region_label"].iloc[0]) if "region_label" in df_sorted.columns else region_id
    variable_id = str(df_sorted["variable_id"].iloc[0]) if "variable_id" in df_sorted.columns else "value"
    variable_name = str(df_sorted["variable_name"].iloc[0]) if "variable_name" in df_sorted.columns else variable_id
    unit = str(df_sorted["unit"].iloc[0]) if "unit" in df_sorted.columns else "units"
    lat = float(df_sorted["lat"].iloc[0]) if "lat" in df_sorted.columns else None
    lon = float(df_sorted["lon"].iloc[0]) if "lon" in df_sorted.columns else None

    # Step 1: STL Seasonal-Trend Decomposition
    trend, seasonal, residual, deseasonalized = decompose_stl(values, period=12, robust=True)

    # Step 2: Non-Parametric Mann-Kendall & Seasonal Mann-Kendall
    mk_stats, smk_stats = compute_mann_kendall(deseasonalized, values, period=12, alpha=alpha)

    # Step 3: Parametric OLS Regression with Confidence Intervals
    n = len(values)
    t_years = np.arange(n) / 12.0
    ols_stats = compute_ols_regression(t_years, deseasonalized, alpha=alpha)

    # Step 4: Summary Climatology
    climatology = {
        "mean": round(float(np.nanmean(values)), 3),
        "std": round(float(np.nanstd(values)), 3),
        "min": round(float(np.nanmin(values)), 3),
        "max": round(float(np.nanmax(values)), 3),
        "median": round(float(np.nanmedian(values)), 3),
        "seasonal_amplitude": round(float(np.max(seasonal) - np.min(seasonal)), 3),
    }

    # Total duration
    total_years = round((n - 1) / 12.0, 2)

    result = {
        "case_id": case_id,
        "region_id": region_id,
        "region_label": region_label,
        "variable_id": variable_id,
        "variable_name": variable_name,
        "unit": unit,
        "coordinates": {"lat": lat, "lon": lon},
        "total_records": n,
        "temporal_range": {
            "start": dates[0],
            "end": dates[-1],
            "total_years": total_years,
        },
        # Arrays for Plotly visualization
        "dates": dates,
        "observed": [round(float(v), 4) for v in values],
        "trend": [round(float(v), 4) for v in trend],
        "seasonal": [round(float(v), 4) for v in seasonal],
        "residual": [round(float(v), 4) for v in residual],
        "deseasonalized": [round(float(v), 4) for v in deseasonalized],
        "trend_line": ols_stats["trend_line"],
        "ci_band_upper": ols_stats["ci_band_upper"],
        "ci_band_lower": ols_stats["ci_band_lower"],
        # Statistical Metrics
        "mann_kendall": mk_stats,
        "seasonal_mann_kendall": smk_stats,
        "ols_regression": {
            "ols_slope_per_year": ols_stats["ols_slope_per_year"],
            "ols_slope_per_decade": ols_stats["ols_slope_per_decade"],
            "ols_intercept": ols_stats["ols_intercept"],
            "r_squared": ols_stats["r_squared"],
            "t_test_p_value": ols_stats["t_test_p_value"],
            "stderr_per_year": ols_stats["stderr_per_year"],
            "slope_ci_95_low": ols_stats["slope_ci_95_low"],
            "slope_ci_95_high": ols_stats["slope_ci_95_high"],
        },
        "climatology": climatology,
    }

    return result


def compare_regions(
    df_region_a: pd.DataFrame,
    df_region_b: pd.DataFrame,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """
    Twin-Region Divergence Comparator:
    Analyzes both regions in a paradox pair and determines whether
    their trajectories exhibit statistically significant divergence.
    """
    stats_a = analyze_time_series(df_region_a, alpha=alpha)
    stats_b = analyze_time_series(df_region_b, alpha=alpha)

    # Extract Sen's slopes
    sens_a_dec = stats_a["mann_kendall"]["sens_slope_per_decade"]
    sens_b_dec = stats_b["mann_kendall"]["sens_slope_per_decade"]
    sens_a_yr = stats_a["mann_kendall"]["sens_slope_per_year"]
    sens_b_yr = stats_b["mann_kendall"]["sens_slope_per_year"]

    # Extract OLS slopes & standard errors
    ols_a_yr = stats_a["ols_regression"]["ols_slope_per_year"]
    ols_b_yr = stats_b["ols_regression"]["ols_slope_per_year"]
    se_a = stats_a["ols_regression"]["stderr_per_year"]
    se_b = stats_b["ols_regression"]["stderr_per_year"]

    slope_diff_yr = round(sens_a_yr - sens_b_yr, 5)
    slope_diff_dec = round(sens_a_dec - sens_b_dec, 4)

    # 1. Opposite Signs Check
    opposite_signs = bool((sens_a_yr * sens_b_yr < 0) or (ols_a_yr * ols_b_yr < 0))

    # 2. Confidence Interval Non-Overlap Check
    ci_a_low = stats_a["ols_regression"]["slope_ci_95_low"]
    ci_a_high = stats_a["ols_regression"]["slope_ci_95_high"]
    ci_b_low = stats_b["ols_regression"]["slope_ci_95_low"]
    ci_b_high = stats_b["ols_regression"]["slope_ci_95_high"]

    ci_separated = bool((ci_a_high < ci_b_low) or (ci_b_high < ci_a_low))

    # 3. Two-Sample Z-Test for Slope Difference
    pooled_se = np.sqrt(se_a ** 2 + se_b ** 2)
    if pooled_se > 0:
        z_score_diff = (ols_a_yr - ols_b_yr) / pooled_se
        p_val_diff = float(2.0 * (1.0 - stats.norm.cdf(abs(z_score_diff))))
    else:
        z_score_diff = 0.0
        p_val_diff = 1.0

    statistically_separated = bool(p_val_diff < alpha)

    # Divergence Detected Verdict
    divergence_detected = bool(opposite_signs or ci_separated or statistically_separated)

    # Generate Detective Synthesis Narrative
    reg_a_name = stats_a["region_label"]
    reg_b_name = stats_b["region_label"]
    var_name = stats_a["variable_name"]
    unit_str = stats_a["unit"]

    if opposite_signs:
        verdict_title = "Strong Divergence: Trends Moving in Opposite Directions"
        narrative = (
            f"A sharp planetary paradox is detected. Over 2001–2025, {reg_a_name} shows a "
            f"{stats_a['mann_kendall']['trend_direction']} trend ({sens_a_dec:+.3f} {unit_str}/decade), "
            f"while {reg_b_name} exhibits an opposing {stats_b['mann_kendall']['trend_direction']} trend "
            f"({sens_b_dec:+.3f} {unit_str}/decade). Their trajectories are moving in opposite directions."
        )
    elif ci_separated or statistically_separated:
        verdict_title = "Statistically Significant Divergence: Distinct Trend Velocities"
        narrative = (
            f"Both regions trend in the same direction, but at dramatically separated rates. "
            f"{reg_a_name} changes at {sens_a_dec:+.3f} {unit_str}/decade versus "
            f"{sens_b_dec:+.3f} {unit_str}/decade for {reg_b_name} (difference: {slope_diff_dec:+.3f} {unit_str}/decade, p={p_val_diff:.4e})."
        )
    else:
        verdict_title = "Coupled Trajectory: Parallel Regional Trends"
        narrative = (
            f"Both regions follow statistically concordant paths for {var_name}. "
            f"The rate difference ({slope_diff_dec:+.3f} {unit_str}/decade) is within expected regional variance."
        )

    comparison = {
        "case_id": stats_a["case_id"],
        "variable_id": stats_a["variable_id"],
        "variable_name": var_name,
        "unit": unit_str,
        "region_a": stats_a,
        "region_b": stats_b,
        "divergence_analysis": {
            "divergence_detected": divergence_detected,
            "is_divergent": divergence_detected,
            "verdict_title": verdict_title,
            "narrative": narrative,
            "opposite_direction": opposite_signs,
            "ci_separated": ci_separated,
            "slope_difference_per_year": slope_diff_yr,
            "slope_difference_per_decade": slope_diff_dec,
            "z_score_divergence": round(float(z_score_diff), 3),
            "p_value_divergence": float(np.format_float_scientific(p_val_diff, precision=4)) if p_val_diff < 0.0001 else round(p_val_diff, 4),
            "region_a_summary": {
                "label": reg_a_name,
                "sens_slope_per_decade": sens_a_dec,
                "direction": stats_a["mann_kendall"]["trend_direction"],
                "p_value": stats_a["mann_kendall"]["p_value"],
                "is_significant": stats_a["mann_kendall"]["is_significant"],
            },
            "region_b_summary": {
                "label": reg_b_name,
                "sens_slope_per_decade": sens_b_dec,
                "direction": stats_b["mann_kendall"]["trend_direction"],
                "p_value": stats_b["mann_kendall"]["p_value"],
                "is_significant": stats_b["mann_kendall"]["is_significant"],
            },
        },
    }

    return comparison


def precompute_case_studies(
    processed_dir: Optional[Union[Path, str]] = None,
    output_json_path: Optional[Union[Path, str]] = None,
) -> Dict[str, Any]:
    """
    Ingests terradetective_unified_monthly, runs twin-region comparator across
    all 3 pre-bundled paradox cases, and saves data/processed/case_studies_stats.json.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    if processed_dir is None:
        processed_dir = base_dir / "data" / "processed"
    else:
        processed_dir = Path(processed_dir)

    if output_json_path is None:
        output_json_path = processed_dir / "case_studies_stats.json"
    else:
        output_json_path = Path(output_json_path)

    # Ingest data
    csv_path = processed_dir / "terradetective_unified_monthly.csv"
    parquet_path = processed_dir / "terradetective_unified_monthly.parquet"

    if csv_path.is_file():
        logger.info(f"Loading unified dataset from {csv_path.name}...")
        df = pd.read_csv(csv_path)
    elif parquet_path.is_file():
        logger.info(f"Loading unified dataset from {parquet_path.name}...")
        df = pd.DataFrame(pl.read_parquet(parquet_path).to_dicts())
    else:
        raise FileNotFoundError(f"Processed dataset not found in {processed_dir}")

    # Load manifest
    manifest_path = processed_dir / "case_studies_manifest.json"
    if manifest_path.is_file():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {"cases": []}

    case_order = [
        "case_1_monsoon_paradox",
        "case_2_land_thermal_paradox",
        "case_3_vegetation_paradox",
    ]

    all_cases_stats: Dict[str, Any] = {}

    print("\n" + "=" * 108)
    print("TERRADETECTIVE CLIMATE TREND SIGNIFICANCE & DIVERGENCE AUDIT")
    print("=" * 108)
    header = f"{'Case ID':<28} | {'Region':<22} | {'Variable':<10} | {'Sen/yr':<9} | {'Sen/dec':<9} | {'MK p-val':<10} | {'Seasonal p':<10} | {'Verdict'}"
    print(header)
    print("-" * 108)

    for cid in case_order:
        sub_df = df[df["case_id"] == cid]
        if sub_df.empty:
            logger.warning(f"No records found for case: {cid}")
            continue

        regions = sub_df["region_id"].unique().tolist()
        if len(regions) < 2:
            logger.warning(f"Case {cid} has fewer than 2 regions: {regions}")
            continue

        reg_a_df = sub_df[sub_df["region_id"] == regions[0]]
        reg_b_df = sub_df[sub_df["region_id"] == regions[1]]

        comparison = compare_regions(reg_a_df, reg_b_df, alpha=0.05)

        # Merge manifest title/subtitle
        manifest_meta = next((c for c in manifest.get("cases", []) if c["case_id"] == cid), {})
        comparison["title"] = manifest_meta.get("title", cid)
        comparison["subtitle"] = manifest_meta.get("subtitle", "")
        comparison["paradox_statement"] = manifest_meta.get("paradox_statement", "")

        all_cases_stats[cid] = comparison

        # Log table rows for each region
        for r_key in ["region_a", "region_b"]:
            r_data = comparison[r_key]
            rid = r_data["region_id"]
            var = r_data["variable_id"]
            sen_yr = f"{r_data['mann_kendall']['sens_slope_per_year']:+.4f}"
            sen_dec = f"{r_data['mann_kendall']['sens_slope_per_decade']:+.4f}"
            mk_p = f"{r_data['mann_kendall']['p_value']:.4e}" if isinstance(r_data['mann_kendall']['p_value'], float) and r_data['mann_kendall']['p_value'] < 0.001 else f"{r_data['mann_kendall']['p_value']:.4f}"
            smk_p = f"{r_data['seasonal_mann_kendall']['p_value']:.4e}" if isinstance(r_data['seasonal_mann_kendall']['p_value'], float) and r_data['seasonal_mann_kendall']['p_value'] < 0.001 else f"{r_data['seasonal_mann_kendall']['p_value']:.4f}"
            sig = "SIGNIFICANT" if r_data["mann_kendall"]["is_significant"] else "NOT SIG"
            print(f"{cid:<28} | {rid:<22} | {var:<10} | {sen_yr:<9} | {sen_dec:<9} | {mk_p:<10} | {smk_p:<10} | {sig}")

        print(f"  --> Divergence Verdict: {comparison['divergence_analysis']['verdict_title']}")
        print("-" * 108)

    print("=" * 108 + "\n")

    output_payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "workbench_name": "TerraDetective",
            "version": "1.0.0",
            "alpha": 0.05,
            "seasonal_period": 12,
            "total_precomputed_cases": len(all_cases_stats),
        },
        "cases": all_cases_stats,
    }

    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    logger.info(f"Pre-computed statistical baselines saved to: {output_json_path.name}")
    return output_payload


if __name__ == "__main__":
    precompute_case_studies()
