import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple, Optional
from statsmodels.tsa.seasonal import STL
import pymannkendall as mk
import logging

logger = logging.getLogger("terradetective.stats_engine")

MISSING_FLAGS = {-999, -999.0, -9999, -9999.0, -9999.9, -999.9}

class StatsEngine:
    def __init__(self, seasonal_period: int = 12):
        self.seasonal_period = seasonal_period

    def sanitize_series(
        self,
        dates: List[str],
        values: List[float]
    ) -> Tuple[pd.Series, List[str]]:
        """
        Sanitizes a time series:
        - Filters out NASA POWER 'YYYY13' annual summary entries.
        - Replaces missing value flags (-999, -999.0, etc.) with NaN.
        - Reindexes to a regular monthly period frequency, interpolating small missing spans.
        """
        clean_dates = []
        clean_vals = []

        for d, v in zip(dates, values):
            # Check for NASA POWER YYYY13 key
            d_str = str(d).strip()
            if "13" in d_str and len(d_str) == 6 and d_str.endswith("13"):
                continue
            if "-13" in d_str or d_str.endswith("/13"):
                continue

            if v in MISSING_FLAGS or (isinstance(v, float) and np.isnan(v)):
                val = np.nan
            else:
                val = float(v)

            clean_dates.append(d_str)
            clean_vals.append(val)

        # Build pandas series with monthly datetime index
        dt_idx = pd.to_datetime(clean_dates)
        s = pd.Series(clean_vals, index=dt_idx).sort_index()

        # Handle duplicates if any by taking monthly mean
        s = s.groupby(s.index.to_period("M")).mean()
        # Create full contiguous monthly index
        if not s.empty:
            full_idx = pd.period_range(start=s.index.min(), end=s.index.max(), freq="M")
            s = s.reindex(full_idx)
            # Interpolate missing values linearly (up to 3 consecutive months) then forward/back fill
            s = s.interpolate(method="linear", limit=3).ffill().bfill()

        # Convert index back to YYYY-MM-01 format string
        formatted_dates = [f"{p.year:04d}-{p.month:02d}-01" for p in s.index]
        return s, formatted_dates

    def run_stl_decomposition(
        self,
        series: pd.Series
    ) -> Dict[str, List[float]]:
        """
        Executes STL (Seasonal and Trend decomposition using Loess)
        with period=12 and robust=True.
        """
        n_obs = len(series)
        if n_obs < 2 * self.seasonal_period:
            # Fallback if series is shorter than 24 months
            trend = series.rolling(window=min(n_obs, 5), min_periods=1, center=True).mean().tolist()
            seasonal = [0.0] * n_obs
            residual = [float(v - t) for v, t in zip(series.values, trend)]
            return {
                "trend": [round(float(x), 4) for x in trend],
                "seasonal": seasonal,
                "residual": [round(float(x), 4) for x in residual],
                "seasonal_period": self.seasonal_period
            }

        try:
            stl = STL(series.values, period=self.seasonal_period, robust=True)
            res = stl.fit()
            return {
                "trend": [round(float(x), 4) for x in res.trend],
                "seasonal": [round(float(x), 4) for x in res.seasonal],
                "residual": [round(float(x), 4) for x in res.resid],
                "seasonal_period": self.seasonal_period
            }
        except Exception as e:
            logger.warning(f"STL decomposition failed, falling back to moving average: {e}")
            trend = series.rolling(window=12, min_periods=1, center=True).mean().bfill().ffill().values
            seasonal = [0.0] * n_obs
            residual = [float(v - t) for v, t in zip(series.values, trend)]
            return {
                "trend": [round(float(x), 4) for x in trend],
                "seasonal": seasonal,
                "residual": [round(float(x), 4) for x in residual],
                "seasonal_period": self.seasonal_period
            }

    def run_mann_kendall(
        self,
        series: pd.Series,
        deseasonalized_trend: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Executes Seasonal Mann-Kendall or Original Mann-Kendall test.
        Computes Sen's slope per month and per decade (slope * 120),
        p-value, significance flag, and total percentage shift.
        """
        vals = series.values
        n_obs = len(vals)
        if n_obs < 4:
            return {
                "sens_slope_per_month": 0.0,
                "sens_slope_per_decade": 0.0,
                "p_value": 1.0,
                "z_score": 0.0,
                "kendall_tau": 0.0,
                "is_significant": False,
                "trend_direction": "no trend",
                "percent_shift": 0.0,
                "mean_value": float(np.mean(vals)) if n_obs > 0 else 0.0,
                "std_value": 0.0,
                "observation_count": n_obs
            }

        # Attempt seasonal Mann-Kendall if length >= 24
        is_seasonal_run = False
        try:
            if n_obs >= 24:
                mk_res = mk.seasonal_test(vals, period=self.seasonal_period)
                is_seasonal_run = True
            else:
                mk_res = mk.original_test(vals)
        except Exception as e:
            logger.warning(f"Seasonal MK test encountered error ({e}), running original MK: {e}")
            mk_res = mk.original_test(vals)

        if is_seasonal_run:
            # In pymannkendall seasonal_test, slope is computed per seasonal cycle (i.e. per year)
            slope_per_month = float(mk_res.slope) / float(self.seasonal_period)
            slope_per_decade = round(float(mk_res.slope) * 10.0, 4)
        else:
            slope_per_month = float(mk_res.slope)
            slope_per_decade = round(slope_per_month * 120.0, 4)
        p_val = round(float(mk_res.p), 5)
        z_val = round(float(getattr(mk_res, "z", 0.0)), 4)
        tau_val = round(float(getattr(mk_res, "Tau", 0.0)), 4)
        is_sig = bool(p_val < 0.05)

        # Determine trend direction
        if is_sig:
            if slope_per_month > 0:
                direction = "increasing"
            elif slope_per_month < 0:
                direction = "decreasing"
            else:
                direction = "no trend"
        else:
            direction = "no trend"

        # Compute percentage shift across time series
        mean_val = float(np.mean(vals))
        std_val = float(np.std(vals))

        if deseasonalized_trend and len(deseasonalized_trend) >= 2:
            start_t = deseasonalized_trend[0]
            end_t = deseasonalized_trend[-1]
            ref_val = abs(mean_val) if abs(mean_val) > 1e-6 else 1.0
            percent_shift = round(((end_t - start_t) / ref_val) * 100.0, 2)
        else:
            total_change = slope_per_month * n_obs
            ref_val = abs(mean_val) if abs(mean_val) > 1e-6 else 1.0
            percent_shift = round((total_change / ref_val) * 100.0, 2)

        return {
            "sens_slope_per_month": round(slope_per_month, 6),
            "sens_slope_per_decade": slope_per_decade,
            "p_value": p_val,
            "z_score": z_val,
            "kendall_tau": tau_val,
            "is_significant": is_sig,
            "trend_direction": direction,
            "percent_shift": percent_shift,
            "mean_value": round(mean_val, 4),
            "std_value": round(std_val, 4),
            "observation_count": n_obs
        }

    def analyze_timeseries(
        self,
        dates: List[str],
        values: List[float]
    ) -> Tuple[List[str], List[float], Dict[str, Any], Dict[str, Any]]:
        """
        Full analytical pipeline:
        1. Sanitize & align to regular monthly index.
        2. STL 12-month decomposition (trend, seasonal, resid).
        3. Mann-Kendall trend testing & Sen's slope calculation.
        """
        clean_series, formatted_dates = self.sanitize_series(dates, values)
        stl_data = self.run_stl_decomposition(clean_series)
        metrics = self.run_mann_kendall(clean_series, stl_data["trend"])
        raw_vals = [round(float(x), 4) for x in clean_series.values]
        return formatted_dates, raw_vals, stl_data, metrics

    def compute_regional_divergence(
        self,
        metrics_a: Dict[str, Any],
        metrics_b: Dict[str, Any],
        label_a: str = "Region A",
        label_b: str = "Region B"
    ) -> Dict[str, Any]:
        """
        Calculates mathematical divergence between two regional time series.
        Evaluates slope difference, sign opposition, and severity.
        """
        slope_a = metrics_a["sens_slope_per_decade"]
        slope_b = metrics_b["sens_slope_per_decade"]
        slope_diff = round(slope_a - slope_b, 4)

        # Opposite trends check
        opposite = bool((slope_a * slope_b < 0) and (metrics_a["is_significant"] or metrics_b["is_significant"]))

        # Divergence magnitude ratio
        max_abs = max(abs(slope_a), abs(slope_b), 1e-5)
        ratio = round(abs(slope_diff) / max_abs, 2)

        if opposite:
            severity = "Extreme Divergence"
            verdict = (
                f"{label_a} and {label_b} display diametrically opposing Earth system trends. "
                f"{label_a} is trending at {slope_a:+.3f}/decade ({metrics_a['trend_direction']}) "
                f"while {label_b} is shifting at {slope_b:+.3f}/decade ({metrics_b['trend_direction']}), "
                f"indicating sharp regional bioclimatic divergence."
            )
        elif abs(slope_diff) > 0.5 * max_abs and (metrics_a["is_significant"] or metrics_b["is_significant"]):
            severity = "Moderate Divergence"
            verdict = (
                f"Statistically significant divergence observed between {label_a} and {label_b}. "
                f"Net differential rate is {slope_diff:+.3f}/decade, demonstrating unequal climate velocity."
            )
        else:
            severity = "Synchronous"
            verdict = (
                f"{label_a} and {label_b} exhibit broadly synchronized trajectories "
                f"(differential: {slope_diff:+.3f}/decade)."
            )

        return {
            "slope_difference_per_decade": slope_diff,
            "divergence_ratio": ratio,
            "opposite_trends": opposite,
            "divergence_severity": severity,
            "comparative_verdict": verdict
        }
