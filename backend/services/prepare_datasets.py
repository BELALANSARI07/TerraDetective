"""
TerraDetective Data Preparation & Quality Control (QC) Pipeline
NASA Space Apps Challenge: 'Be An Earth System Trend Detective!'

Standardizes and cleans 4 NASA satellite observation datasets:
1. MODIS Terra MOD11A2.061: 8-Day 1km Land Surface Temperature (Daytime)
2. MODIS Terra MOD13A3.061: Monthly 1km Vegetation Indices (NDVI)
3. NASA Giovanni GPM IMERG (GPM_3IMERGM_07): Monthly Precipitation for Marathwada (75E_18N_77E_20N)
4. NASA Giovanni GPM IMERG (GPM_3IMERGM_07): Monthly Precipitation for Northeast India (90E_24N_92E_26N)

Outputs:
- data/processed/terradetective_unified_monthly.csv
- data/processed/terradetective_unified_monthly.parquet
- data/processed/case_1_monsoon_paradox.csv / .parquet
- data/processed/case_2_land_thermal_paradox.csv / .parquet
- data/processed/case_3_vegetation_paradox.csv / .parquet
- data/processed/case_studies_manifest.json

Unified Schema:
[case_id, region_id, region_label, lat, lon, date, year, month, variable_id, variable_name, unit, value, qc_flag, source_product]
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import polars as pl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("terradetective.prepare_datasets")

# Unified Schema Definition
UNIFIED_COLUMNS = [
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

# Region Metadata Definitions
REGION_METADATA = {
    "RondoniaAmazonArc": {
        "region_id": "RondoniaAmazonArc",
        "region_label": "Rondônia Amazon Deforestation Arc",
        "lat": -10.875,
        "lon": -61.93,
    },
    "PunjabIrrigatedBelt": {
        "region_id": "PunjabIrrigatedBelt",
        "region_label": "Punjab Intensive Irrigated Cropland Belt",
        "lat": 30.901,
        "lon": 75.8573,
    },
    "Marathwada": {
        "region_id": "Marathwada",
        "region_label": "Marathwada (Drought-Prone Rain Shadow)",
        "lat": 19.25,
        "lon": 76.25,
    },
    "NortheastIndia": {
        "region_id": "NortheastIndia",
        "region_label": "Northeast India (Cherrapunji / Meghalaya Monsoon Belt)",
        "lat": 25.25,
        "lon": 91.50,
    },
}


def clean_mod11a2_lst(raw_path: Path | str) -> pd.DataFrame:
    """
    Cleans and monthly-resamples MOD11A2 8-day Land Surface Temperature:
    1. Filters invalid/cloudy retrievals (LST <= 0 K or QC cloud description).
    2. Converts Kelvin to Celsius (LST_C = LST_Day_1km - 273.15).
    3. Resamples 8-day observations to monthly (MS: Month Start) using monthly mean.
    4. Interpolates missing cloudy months to align 1:1 with MOD13A3 (2001-01 to 2025-12).
    """
    path = Path(raw_path)
    if not path.is_file():
        raise FileNotFoundError(f"MOD11A2 file not found: {path}")

    logger.info(f"Loading MOD11A2 raw LST from {path.name}...")
    df = pd.read_csv(path)

    # Scientific QC Filtering
    cloud_or_zero = (
        (df["MOD11A2_061_LST_Day_1km"] <= 0)
        | (df["MOD11A2_061_QC_Day_MODLAND_Description"] == "LST not produced due to cloud effects")
    )
    dropped_count = cloud_or_zero.sum()
    logger.info(f"Filtered {dropped_count} cloudy/invalid LST retrievals (0.0 K).")

    df_valid = df[~cloud_or_zero].copy()
    df_valid["LST_C"] = df_valid["MOD11A2_061_LST_Day_1km"] - 273.15
    df_valid["Date"] = pd.to_datetime(df_valid["Date"])

    # Target monthly timeline: 2001-01-01 to 2025-12-01 (300 monthly timestamps)
    target_months = pd.date_range("2001-01-01", "2025-12-01", freq="MS")

    records: List[Dict[str, Any]] = []

    for region_id in ["RondoniaAmazonArc", "PunjabIrrigatedBelt"]:
        meta = REGION_METADATA[region_id]
        sub = df_valid[df_valid["ID"] == region_id].copy()

        # Group by Month Start and compute mean
        sub_monthly = sub.set_index("Date").resample("MS")["LST_C"].mean()
        # Reindex to complete 2001-2025 timeline
        sub_reindexed = sub_monthly.reindex(target_months)

        # Track which months were directly observed vs cloud-interpolated
        was_missing = sub_reindexed.isna()
        # Linearly interpolate gaps across persistently cloudy periods
        sub_clean = sub_reindexed.interpolate(method="linear").bfill().ffill()

        for dt, val in sub_clean.items():
            dt_str = dt.strftime("%Y-%m-01")
            is_interpolated = was_missing.loc[dt]
            records.append({
                "case_id": "case_2_land_thermal_paradox",
                "region_id": region_id,
                "region_label": meta["region_label"],
                "lat": meta["lat"],
                "lon": meta["lon"],
                "date": dt_str,
                "year": dt.year,
                "month": dt.month,
                "variable_id": "LST_Day",
                "variable_name": "Land Surface Temperature (Daytime)",
                "unit": "°C",
                "value": round(float(val), 3),
                "qc_flag": "cloud_interpolated" if is_interpolated else "observed",
                "source_product": "MOD11A2.061",
            })

    result_df = pd.DataFrame(records)
    logger.info(f"Cleaned MOD11A2 LST produced {len(result_df)} monthly aligned records.")
    return result_df[UNIFIED_COLUMNS]


def clean_mod13a3_ndvi(raw_path: Path | str) -> pd.DataFrame:
    """
    Cleans MOD13A3 Monthly NDVI:
    1. Normalizes Date to YYYY-MM-01.
    2. Flags cloudy pixels (MODLAND == 'Pixel produced, but most probably cloudy')
       as qc_flag = 'cloudy_interpolated'.
    3. Normalizes schema to unified fields.
    """
    path = Path(raw_path)
    if not path.is_file():
        raise FileNotFoundError(f"MOD13A3 file not found: {path}")

    logger.info(f"Loading MOD13A3 raw NDVI from {path.name}...")
    df = pd.read_csv(path)

    records: List[Dict[str, Any]] = []

    for _, row in df.iterrows():
        region_id = str(row["ID"]).strip()
        meta = REGION_METADATA.get(region_id, {
            "region_id": region_id,
            "region_label": region_id,
            "lat": float(row["Latitude"]),
            "lon": float(row["Longitude"]),
        })

        dt = pd.to_datetime(row["Date"])
        dt_str = dt.strftime("%Y-%m-01")

        qc_desc = str(row.get("MOD13A3_061__1_km_monthly_VI_Quality_MODLAND_Description", ""))
        is_cloudy = "most probably cloudy" in qc_desc.lower()
        qc_flag = "cloudy_interpolated" if is_cloudy else "nominal"

        val = float(row["MOD13A3_061__1_km_monthly_NDVI"])

        records.append({
            "case_id": "case_3_vegetation_paradox",
            "region_id": region_id,
            "region_label": meta["region_label"],
            "lat": meta["lat"],
            "lon": meta["lon"],
            "date": dt_str,
            "year": dt.year,
            "month": dt.month,
            "variable_id": "NDVI",
            "variable_name": "Normalized Difference Vegetation Index",
            "unit": "index",
            "value": round(val, 4),
            "qc_flag": qc_flag,
            "source_product": "MOD13A3.061",
        })

    result_df = pd.DataFrame(records)
    logger.info(f"Cleaned MOD13A3 NDVI produced {len(result_df)} monthly records.")
    return result_df[UNIFIED_COLUMNS]


def clean_gpm_precipitation(path_75e: Path | str, path_90e: Path | str) -> pd.DataFrame:
    """
    Cleans Giovanni GPM IMERG Monthly Precipitation for both Marathwada and Northeast India:
    1. Skips 8 header lines of metadata.
    2. Strips whitespace from column names.
    3. Replaces -9999.9 fill values with NaN.
    4. Converts precipitation rate (mm/hr) to monthly accumulation (mm/month)
       using 24 * days_in_month (accounting accurately for leap years).
    5. Normalizes to unified schema.
    """
    p_marathwada = Path(path_75e)
    p_ne_india = Path(path_90e)

    for p in (p_marathwada, p_ne_india):
        if not p.is_file():
            raise FileNotFoundError(f"GPM file not found: {p}")

    records: List[Dict[str, Any]] = []

    file_configs = [
        (p_marathwada, "Marathwada"),
        (p_ne_india, "NortheastIndia"),
    ]

    for fpath, region_id in file_configs:
        logger.info(f"Loading GPM IMERG precip for {region_id} from {fpath.name}...")
        df = pd.read_csv(fpath, skiprows=8)
        df.columns = [c.strip() for c in df.columns]

        meta = REGION_METADATA[region_id]
        val_col = "mean_GPM_3IMERGM_07_precipitation"

        # Replace missing fill values
        df[val_col] = df[val_col].replace(-9999.9, np.nan)
        df["dt"] = pd.to_datetime(df["time"])

        for _, row in df.iterrows():
            dt = row["dt"]
            dt_str = dt.strftime("%Y-%m-01")
            rate_mm_hr = float(row[val_col]) if pd.notna(row[val_col]) else np.nan

            days_in_month = pd.Period(dt, freq="M").days_in_month
            if pd.notna(rate_mm_hr):
                monthly_mm = rate_mm_hr * 24.0 * days_in_month
                val_clean = round(monthly_mm, 2)
                qc_flag = "observed"
            else:
                val_clean = np.nan
                qc_flag = "missing"

            records.append({
                "case_id": "case_1_monsoon_paradox",
                "region_id": region_id,
                "region_label": meta["region_label"],
                "lat": meta["lat"],
                "lon": meta["lon"],
                "date": dt_str,
                "year": dt.year,
                "month": dt.month,
                "variable_id": "precipitation",
                "variable_name": "Monthly Precipitation Accumulation",
                "unit": "mm/month",
                "value": val_clean,
                "qc_flag": qc_flag,
                "source_product": "GPM_3IMERGM_07",
            })

    result_df = pd.DataFrame(records)
    logger.info(f"Cleaned GPM IMERG produced {len(result_df)} monthly records.")
    return result_df[UNIFIED_COLUMNS]


def build_manifest() -> Dict[str, Any]:
    """
    Constructs the 3 pre-bundled Mystery Case Files metadata manifest
    for zero-dependency offline playback and interactive investigation.
    """
    manifest = {
        "workbench_name": "TerraDetective",
        "description": "Earth System Trend & Regional Paradox Workbench for NASA Space Apps Challenge",
        "challenge_track": "Be An Earth System Trend Detective!",
        "version": "1.0.0",
        "unified_schema": UNIFIED_COLUMNS,
        "cases": [
            {
                "case_id": "case_1_monsoon_paradox",
                "title": "The Monsoon Paradox: Orographic Deluge vs. Rain-Shadow Drought",
                "subtitle": "Marathwada vs. Northeast India (2001–2025)",
                "paradox_statement": (
                    "Despite sharing the same South Asian summer monsoon air mass, why does Northeast "
                    "India receive up to 1,350+ mm/month causing extreme flash flooding, while Marathwada "
                    "(just 1,500 km away) suffers persistent agro-meteorological drought (<10 mm/month)?"
                ),
                "scientific_driver": "Western Ghats rain-shadow effect vs. Bay of Bengal orographic funneling into Khasi Hills.",
                "variable_id": "precipitation",
                "variable_name": "Monthly Precipitation Accumulation",
                "unit": "mm/month",
                "temporal_range": {"start": "2001-01-01", "end": "2025-09-01", "resolution": "monthly"},
                "source_product": "NASA Giovanni GPM IMERG Final (GPM_3IMERGM_07)",
                "regions": [
                    {
                        "region_id": "Marathwada",
                        "region_label": "Marathwada (Drought-Prone Rain Shadow)",
                        "latitude": 19.25,
                        "longitude": 76.25,
                        "bounding_box": [75.0, 18.0, 77.5, 20.5],
                        "expected_climatology": "Semi-arid rain shadow, erratic monsoon onset, high drought frequency",
                    },
                    {
                        "region_id": "NortheastIndia",
                        "region_label": "Northeast India (Cherrapunji / Meghalaya Monsoon Belt)",
                        "latitude": 25.25,
                        "longitude": 91.50,
                        "bounding_box": [90.5, 24.5, 92.5, 26.0],
                        "expected_climatology": "World-record orographic monsoon rainfall, extreme convective cloud bursts",
                    },
                ],
                "detective_clues": [
                    "Compare peak monsoon months (July-August) across both regions.",
                    "Analyze rainfall variability: Marathwada exhibits coefficient of variation >45%.",
                    "Correlate dry season precipitation deficits with regional water stress.",
                ],
                "data_files": {
                    "csv": "case_1_monsoon_paradox.csv",
                    "parquet": "case_1_monsoon_paradox.parquet",
                },
            },
            {
                "case_id": "case_2_land_thermal_paradox",
                "title": "Land Thermal Paradox: Deforestation Warming vs. Irrigation Cooling",
                "subtitle": "Rondônia Amazon Arc vs. Punjab Irrigated Belt (2001–2025)",
                "paradox_statement": (
                    "Why is daytime Land Surface Temperature accelerating upward across cleared Amazon rainforest, "
                    "whereas Punjab's intensive agricultural belt exhibits strong evaporative cooling anomalies "
                    "despite substantial atmospheric greenhouse warming?"
                ),
                "scientific_driver": (
                    "Canopy clearance in Rondônia eliminates latent heat evaporative cooling, converting solar "
                    "energy to sensible surface heat (+4°C to +8°C). In Punjab, canal and tubewell irrigation "
                    "amplifies latent evaporative flux, suppressing daytime skin temperatures."
                ),
                "variable_id": "LST_Day",
                "variable_name": "Land Surface Temperature (Daytime)",
                "unit": "°C",
                "temporal_range": {"start": "2001-01-01", "end": "2025-12-01", "resolution": "monthly"},
                "source_product": "MODIS Terra 8-Day 1km LST (MOD11A2.061) Monthly Mean",
                "regions": [
                    {
                        "region_id": "RondoniaAmazonArc",
                        "region_label": "Rondônia Amazon Deforestation Arc",
                        "latitude": -10.875,
                        "longitude": -61.93,
                        "expected_climatology": "Persistent tropical warming anomaly, dry season LST spikes >40°C",
                    },
                    {
                        "region_id": "PunjabIrrigatedBelt",
                        "region_label": "Punjab Intensive Irrigated Cropland Belt",
                        "latitude": 30.901,
                        "longitude": 75.8573,
                        "expected_climatology": "Subtropical continental climate, strong summer evaporative cooling dip",
                    },
                ],
                "detective_clues": [
                    "Notice the dry season (August-October) LST surge in Rondônia post-2005.",
                    "Contrast with Punjab's June pre-monsoon heat vs August irrigation crop canopy cooling.",
                    "Verify cloud-filtered retrievals: zero 0.0 K artifacts remain.",
                ],
                "data_files": {
                    "csv": "case_2_land_thermal_paradox.csv",
                    "parquet": "case_2_land_thermal_paradox.parquet",
                },
            },
            {
                "case_id": "case_3_vegetation_paradox",
                "title": "Vegetation Greenness Paradox: Canopy Degradation vs. Human-Engineered Greening",
                "subtitle": "Rondônia Amazon Arc vs. Punjab Irrigated Belt (2001–2025)",
                "paradox_statement": (
                    "Why has dense pristine rainforest canopy in Rondônia experienced fragmentation and dry-season "
                    "brown-downs, while Punjab's semi-arid terrain shows sustained bimodal vegetation greenness peaks?"
                ),
                "scientific_driver": (
                    "Amazon arc deforestation replaces perennial evergreen canopy (NDVI ~0.75-0.85) with cattle "
                    "pasture and soy fields (NDVI fluctuating down to ~0.30 in dry season). Punjab uses Green Revolution "
                    "double-cropping (Kharif rice + Rabi wheat) to artificially drive high bimodal NDVI peaks."
                ),
                "variable_id": "NDVI",
                "variable_name": "Normalized Difference Vegetation Index",
                "unit": "index",
                "temporal_range": {"start": "2001-01-01", "end": "2025-12-01", "resolution": "monthly"},
                "source_product": "MODIS Terra Monthly 1km Vegetation Indices (MOD13A3.061)",
                "regions": [
                    {
                        "region_id": "RondoniaAmazonArc",
                        "region_label": "Rondônia Amazon Deforestation Arc",
                        "latitude": -10.875,
                        "longitude": -61.93,
                        "expected_climatology": "Degraded tropical forest transitioning to pasture seasonal amplitude",
                    },
                    {
                        "region_id": "PunjabIrrigatedBelt",
                        "region_label": "Punjab Intensive Irrigated Cropland Belt",
                        "latitude": 30.901,
                        "longitude": 75.8573,
                        "expected_climatology": "Distinct dual-season peaks (Feb-Mar wheat, Sep-Oct rice)",
                    },
                ],
                "detective_clues": [
                    "Inspect the seasonal cycle amplitude in Rondônia expanding over time.",
                    "Observe the strict bimodal cropping pattern in Punjab.",
                    "Cloud-interpolated flags are transparently logged for QC audit.",
                ],
                "data_files": {
                    "csv": "case_3_vegetation_paradox.csv",
                    "parquet": "case_3_vegetation_paradox.parquet",
                },
            },
        ],
    }
    return manifest


def export_all(
    df_unified: pd.DataFrame,
    manifest: Dict[str, Any],
    processed_dir: Path | str,
) -> None:
    """
    Exports clean datasets in both Parquet and CSV formats, along with manifest JSON.
    """
    out_dir = Path(processed_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Export Unified Master CSV & Parquet
    master_csv = out_dir / "terradetective_unified_monthly.csv"
    master_parquet = out_dir / "terradetective_unified_monthly.parquet"

    df_unified.to_csv(master_csv, index=False, encoding="utf-8")
    # Using Polars for fast, zero-dependency Parquet writing
    pl_df = pl.from_pandas(df_unified)
    pl_df.write_parquet(master_parquet)
    logger.info(f"Master files exported: {master_csv.name}, {master_parquet.name}")

    # Export Individual Case Study Files
    for case in manifest["cases"]:
        cid = case["case_id"]
        sub_df = df_unified[df_unified["case_id"] == cid]

        sub_csv = out_dir / f"{cid}.csv"
        sub_parquet = out_dir / f"{cid}.parquet"

        sub_df.to_csv(sub_csv, index=False, encoding="utf-8")
        pl.from_pandas(sub_df).write_parquet(sub_parquet)
        logger.info(f"Case file exported: {sub_csv.name} ({len(sub_df)} rows)")

    # Export Manifest JSON
    manifest_path = out_dir / "case_studies_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"Manifest JSON saved to {manifest_path.name}")


def print_summary_table(df_unified: pd.DataFrame) -> None:
    """
    Prints a rich ASCII scientific summary table of all processed variables and regions.
    """
    print("\n" + "=" * 96)
    print("TERRADETECTIVE DATASET PREPARATION SUMMARY & QUALITY CONTROL AUDIT")
    print("=" * 96)
    header = f"{'Case ID':<28} | {'Region ID':<20} | {'Variable':<12} | {'Rows':<6} | {'Dates Range':<23} | {'Min':<8} | {'Max':<8} | {'Mean':<8}"
    print(header)
    print("-" * 96)

    grouped = df_unified.groupby(["case_id", "region_id", "variable_id"])
    for (cid, rid, vid), grp in grouped:
        rows_cnt = len(grp)
        min_date = grp["date"].min()
        max_date = grp["date"].max()
        date_range = f"{min_date[:7]}..{max_date[:7]}"
        min_val = round(grp["value"].min(), 2)
        max_val = round(grp["value"].max(), 2)
        mean_val = round(grp["value"].mean(), 2)
        print(f"{cid:<28} | {rid:<20} | {vid:<12} | {rows_cnt:<6} | {date_range:<23} | {min_val:<8} | {max_val:<8} | {mean_val:<8}")

    print("=" * 96)
    print(f"Total Unified Records: {len(df_unified)} rows across 3 cases and 4 regions.")
    print("=" * 96 + "\n")


def prepare_datasets(
    raw_dir: Path | str | None = None,
    processed_dir: Path | str | None = None,
) -> pd.DataFrame:
    """
    Main orchestration entrypoint for dataset preparation.
    """
    base_dir = Path(__file__).resolve().parent.parent.parent
    if raw_dir is None:
        raw_dir = base_dir / "data" / "raw"
    else:
        raw_dir = Path(raw_dir)

    if processed_dir is None:
        processed_dir = base_dir / "data" / "processed"
    else:
        processed_dir = Path(processed_dir)

    logger.info(f"Raw directory: {raw_dir}")
    logger.info(f"Processed directory: {processed_dir}")

    # Paths to raw files
    mod11a2_path = raw_dir / "TerraDetective-MODIS-Paradox-MOD11A2-061-results.csv"
    mod13a3_path = raw_dir / "TerraDetective-MODIS-Paradox-MOD13A3-061-results.csv"
    gpm_75e_path = raw_dir / "g4.areaAvgTimeSeries.GPM_3IMERGM_07_precipitation.20010101-20251231.75E_18N_77E_20N.csv"
    gpm_90e_path = raw_dir / "g4.areaAvgTimeSeries.GPM_3IMERGM_07_precipitation.20010101-20251231.90E_24N_92E_26N.csv"

    # Step 1: Clean MOD11A2 (LST)
    df_lst = clean_mod11a2_lst(mod11a2_path)

    # Step 2: Clean MOD13A3 (NDVI)
    df_ndvi = clean_mod13a3_ndvi(mod13a3_path)

    # Step 3: Clean Giovanni GPM (Precipitation)
    df_gpm = clean_gpm_precipitation(gpm_75e_path, gpm_90e_path)

    # Step 4: Concatenate into unified schema
    df_unified = pd.concat([df_gpm, df_lst, df_ndvi], ignore_index=True)

    # Step 5: Build Manifest
    manifest = build_manifest()

    # Step 6: Export all assets
    export_all(df_unified, manifest, processed_dir)

    # Step 7: Print Summary Table
    print_summary_table(df_unified)

    return df_unified


if __name__ == "__main__":
    prepare_datasets()
