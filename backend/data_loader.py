import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger("terradetective.data_loader")

MISSING_VALUE_FLAGS = {-999, -999.0, -9999, -9999.0, -9999.9, -999.9}

CATALOG_METADATA_ENRICHMENT = {
    "T2M": {"simple_label": "Surface Air Temperature", "category_icon": "heat"},
    "T2M_MAX": {"simple_label": "Max Daytime Temperature", "category_icon": "heat"},
    "T2M_MIN": {"simple_label": "Nighttime Temperature", "category_icon": "heat"},
    "TS": {"simple_label": "Ground Skin Temperature", "category_icon": "heat"},
    "LST": {"simple_label": "Land Surface Temperature", "category_icon": "heat"},
    "LST_DAY": {"simple_label": "Daytime Land Temperature", "category_icon": "heat"},
    "ALLSKY_SFC_SW_DWN": {"simple_label": "Solar Energy Sunlight", "category_icon": "heat"},
    "CLRSKY_DAYS": {"simple_label": "Clear Sunny Days", "category_icon": "heat"},
    "PRECTOTCORR": {"simple_label": "Monthly Rainfall Total", "category_icon": "rain"},
    "GPM_PRECIP": {"simple_label": "Satellite Precipitation Rate", "category_icon": "rain"},
    "GPM_IMERG": {"simple_label": "Satellite Rainfall Rate", "category_icon": "rain"},
    "RH2M": {"simple_label": "Air Humidity Level", "category_icon": "rain"},
    "QV2M": {"simple_label": "Atmospheric Moisture", "category_icon": "rain"},
    "WS2M": {"simple_label": "Surface Wind Speed", "category_icon": "rain"},
    "WS10M": {"simple_label": "High Wind Speed", "category_icon": "rain"},
    "PS": {"simple_label": "Surface Air Pressure", "category_icon": "rain"},
    "NDVI": {"simple_label": "Plant Canopy Greenness", "category_icon": "vegetation"},
    "GWETTOP": {"simple_label": "Surface Soil Wetness", "category_icon": "water"},
    "GWETROOT": {"simple_label": "Root-Zone Soil Water", "category_icon": "water"},
    "GWETPROF": {"simple_label": "Deep Aquifer Moisture", "category_icon": "water"},
    "GLDAS_ROOTMOIST": {"simple_label": "Subsurface Soil Moisture", "category_icon": "water"},
    "SOILMOIST": {"simple_label": "Soil Moisture Storage", "category_icon": "water"},
    "GROUNDWATER": {"simple_label": "Groundwater Level", "category_icon": "water"},
    "T2MDEW": {"simple_label": "Dew Point Temperature", "category_icon": "water"},
    "EVLAND": {"simple_label": "Land Evaporation Rate", "category_icon": "water"},
    "DISCHARGE": {"simple_label": "River Water Runoff", "category_icon": "water"},
    "SNOWDP": {"simple_label": "Snowpack Depth", "category_icon": "water"},
    "SWOT": {"simple_label": "Surface Water Elevation", "category_icon": "water"}
}

def enrich_variable_dict(v: Dict[str, Any]) -> Dict[str, Any]:
    ident = v.get("identifier", "").upper().strip()
    enrich = CATALOG_METADATA_ENRICHMENT.get(ident, {})
    if "simple_label" not in v or not v["simple_label"]:
        v["simple_label"] = enrich.get("simple_label", v.get("name", ident))
    if "category_icon" not in v or not v["category_icon"]:
        cat = v.get("category", "").lower()
        if "therm" in cat or "temp" in cat or "solar" in cat:
            default_icon = "heat"
        elif "precip" in cat or "rain" in cat or "wind" in cat or "humid" in cat:
            default_icon = "rain"
        elif "bio" in cat or "veg" in cat or "canopy" in cat:
            default_icon = "vegetation"
        else:
            default_icon = "water"
        v["category_icon"] = enrich.get("category_icon", default_icon)
    return v

class DataLoader:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            # Default to ../data relative to backend/
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.data_dir = os.path.abspath(os.path.join(base_dir, "..", "data"))
        else:
            self.data_dir = os.path.abspath(data_dir)
            
        self.catalog: Dict[str, Any] = {}
        self.pillars: Dict[str, List[str]] = {
            "catalog_json": [],
            "precipitation_csv": [],
            "modis_lst_ndvi_csv": [],
            "hydrology_benchmark_csv": []
        }
        self.cached_dfs: Dict[str, pd.DataFrame] = {}
        self.scan_and_classify()

    def scan_and_classify(self) -> Dict[str, Any]:
        """
        Dynamically scans data_dir, inspects first 20 lines of CSVs,
        and classifies files into the 4 Earth System data pillars.
        """
        self.pillars = {
            "catalog_json": [],
            "precipitation_csv": [],
            "modis_lst_ndvi_csv": [],
            "hydrology_benchmark_csv": []
        }

        if not os.path.isdir(self.data_dir):
            logger.warning(f"Data directory does not exist: {self.data_dir}")
            return {"status": "empty", "files_found": 0}

        files = [f for f in os.listdir(self.data_dir) if os.path.isfile(os.path.join(self.data_dir, f))]
        
        for fname in sorted(files):
            fpath = os.path.join(self.data_dir, fname)
            lower = fname.lower()

            if lower.endswith(".json"):
                self.pillars["catalog_json"].append(fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as jf:
                        self.catalog = json.load(jf)
                except Exception as e:
                    logger.error(f"Failed to load catalog JSON {fname}: {e}")
            elif lower.endswith(".csv"):
                # Inspect file to determine pillar
                pillar = self._classify_csv(fpath, fname)
                self.pillars[pillar].append(fname)

        report = {
            "status": "ready",
            "data_dir": self.data_dir,
            "total_files": len(files),
            "pillars": {k: len(v) for k, v in self.pillars.items()},
            "details": self.pillars
        }
        return report

    def _classify_csv(self, fpath: str, fname: str) -> str:
        lower = fname.lower()
        if "gpm" in lower or "imerg" in lower or "precipitation" in lower:
            return "precipitation_csv"
        if "mod11a2" in lower or "mod13a3" in lower or "ndvi" in lower or "lst" in lower or "modis" in lower:
            return "modis_lst_ndvi_csv"
        if "gldas" in lower or "hydrology" in lower or "soilmoist" in lower or "knmi" in lower:
            return "hydrology_benchmark_csv"

        # Inspect header content if filename is generic
        header_idx, cols = self.detect_header_row(fpath)
        col_str = " ".join(cols).lower()
        if "precipitation" in col_str or "rain" in col_str:
            return "precipitation_csv"
        if "ndvi" in col_str or "lst" in col_str or "vi_quality" in col_str:
            return "modis_lst_ndvi_csv"
        if "soil" in col_str or "moist" in col_str or "water" in col_str or "runoff" in col_str:
            return "hydrology_benchmark_csv"

        return "hydrology_benchmark_csv"

    def detect_header_row(self, fpath: str, max_inspect: int = 30) -> Tuple[int, List[str]]:
        """
        Inspects first max_inspect lines of CSV to dynamically find
        the actual table header row (skipping metadata key-value lines).
        """
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            lines = [f.readline() for _ in range(max_inspect)]

        for idx, line in enumerate(lines):
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue

            parts = [p.strip().strip('"').strip("'") for p in line_str.split(",")]
            # Metadata lines in Giovanni / GLDAS typically have first token ending in colon (e.g. 'Title:', 'User Start Date:')
            if len(parts) >= 2 and not parts[0].endswith(":"):
                # Verify that elements look like column identifiers
                first_col = parts[0].lower()
                if first_col in {"time", "date", "datetime", "category", "id", "latitude", "lat", "region", "year"}:
                    return idx, parts
                # If the line contains at least 2 non-empty tokens without ':'
                if all(":" not in p for p in parts[:2]):
                    return idx, parts

        return 0, []

    def load_smart_dataframe(self, fname: str) -> pd.DataFrame:
        """Loads and caches DataFrame with automatic metadata header skipping."""
        if fname in self.cached_dfs:
            return self.cached_dfs[fname]

        fpath = os.path.join(self.data_dir, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"File not found: {fpath}")

        header_idx, cols = self.detect_header_row(fpath)
        df = pd.read_csv(fpath, skiprows=header_idx)

        # Standardize column names (strip whitespace and quotes)
        df.columns = [c.strip().strip('"').strip("'") for c in df.columns]

        # Clean null flags (-999, -9999.0, etc.)
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col] = df[col].replace(list(MISSING_VALUE_FLAGS), np.nan)

        self.cached_dfs[fname] = df
        return df

    def get_catalog_variables(self) -> List[Dict[str, Any]]:
        """Returns the list of 20 NASA POWER variables from the catalog with Story Mode metadata."""
        vars_list = self.catalog.get("variables", [])
        return [enrich_variable_dict(dict(v)) for v in vars_list]

    def get_variable_metadata(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Finds metadata for a specific variable by identifier (e.g. 'T2M', 'TS', 'NDVI')."""
        ident_clean = identifier.upper().strip()
        # Check standard NASA POWER catalog
        for var in self.catalog.get("variables", []):
            if var.get("identifier", "").upper() == ident_clean:
                return enrich_variable_dict(dict(var))

        # Local datasets metadata overrides
        local_meta = {
            "NDVI": {
                "identifier": "NDVI",
                "name": "MODIS Normalized Difference Vegetation Index (1km)",
                "simple_label": "Plant Canopy Greenness",
                "category_icon": "vegetation",
                "units": "index (-0.2 to 1.0)",
                "category": "Biosphere / Vegetation",
                "description": "MODIS MOD13A3 1km Monthly Normalized Difference Vegetation Index measuring canopy greenness and photosynthetic activity.",
                "detective_hint": "Declining NDVI tracks forest clearance, logging, or desertification; rising NDVI in agricultural zones tracks irrigation intensification.",
                "climatology_range": [-0.2, 1.0],
                "primary_sat_model": "Terra MODIS (MOD13A3.061)"
            },
            "LST_DAY": {
                "identifier": "LST_DAY",
                "name": "MODIS Land Surface Temperature Day (1km)",
                "simple_label": "Daytime Land Temperature",
                "category_icon": "heat",
                "units": "K",
                "category": "Thermal / Surface",
                "description": "MODIS MOD11A2 8-day 1km Daytime Land Surface Temperature aggregated to monthly mean.",
                "detective_hint": "Surface skin warming directly reflects loss of canopy evaporative cooling from deforestation.",
                "climatology_range": [260.0, 335.0],
                "primary_sat_model": "Terra MODIS (MOD11A2.061)"
            },
            "GPM_PRECIP": {
                "identifier": "GPM_PRECIP",
                "name": "GPM IMERG Final Run Monthly Precipitation",
                "simple_label": "Satellite Precipitation Rate",
                "category_icon": "rain",
                "units": "mm/hr",
                "category": "Hydrology / Precipitation",
                "description": "Global Precipitation Measurement (GPM) IMERG Final Precipitation L3 1 month 0.1 degree x 0.1 degree area-averaged time series.",
                "detective_hint": "Validates regional monsoon shifts and precipitation divergence between arid basins and orographic belts.",
                "climatology_range": [0.0, 2.5],
                "primary_sat_model": "NASA / JAXA GPM IMERGM v07"
            },
            "GLDAS_ROOTMOIST": {
                "identifier": "GLDAS_ROOTMOIST",
                "name": "GLDAS Noah Root Zone Soil Moisture (0-100cm)",
                "simple_label": "Subsurface Soil Moisture",
                "category_icon": "water",
                "units": "kg/m^2",
                "category": "Hydrology / Soil Moisture",
                "description": "GLDAS Noah Land Surface Model 0.25 degree monthly root-zone soil water storage (0-100cm).",
                "detective_hint": "Crucial ground-truth metric proving agricultural water drawdown behind greening paradoxes.",
                "climatology_range": [50.0, 600.0],
                "primary_sat_model": "NASA GES DISC GLDAS Noah v2.1"
            }
        }
        res = local_meta.get(ident_clean)
        return enrich_variable_dict(dict(res)) if res else None

    def extract_modis_timeseries(self, product: str, location_id: str) -> Tuple[List[str], List[float], Dict[str, Any]]:
        """
        Extracts monthly time series for MODIS MOD13A3 (NDVI) or MOD11A2 (LST).
        Cleans cloud flags, aggregates 8-day LST to monthly, returns sorted dates & values.
        """
        if product.upper() == "NDVI":
            files = [f for f in self.pillars["modis_lst_ndvi_csv"] if "13a3" in f.lower() or "ndvi" in f.lower()]
            val_col = "MOD13A3_061__1_km_monthly_NDVI"
        else:
            files = [f for f in self.pillars["modis_lst_ndvi_csv"] if "11a2" in f.lower() or "lst" in f.lower()]
            val_col = "MOD11A2_061_LST_Day_1km"

        if not files:
            raise FileNotFoundError(f"No MODIS {product} CSV file found in data directory.")

        df = self.load_smart_dataframe(files[0])
        sub_df = df[df["ID"].astype(str).str.lower() == location_id.lower()].copy()
        if sub_df.empty:
            # Fallback to coordinate matching if ID didn't match directly
            raise ValueError(f"Location ID '{location_id}' not found in {files[0]}. Available: {list(df['ID'].unique())}")

        sub_df["Date"] = pd.to_datetime(sub_df["Date"])

        # Filter out invalid values
        if product.upper() == "NDVI":
            # NDVI range is -1 to 1; values <= -0.3 are missing or water
            sub_df = sub_df[(sub_df[val_col] >= -0.2) & (sub_df[val_col] <= 1.0)]
        else:
            # For MOD11A2 LST: 0.0 means cloud cover
            sub_df = sub_df[sub_df[val_col] > 200.0]  # Valid Kelvin range > 200K

        # Aggregate by Year-Month
        sub_df["YearMonth"] = sub_df["Date"].dt.to_period("M")
        monthly = sub_df.groupby("YearMonth")[val_col].mean().reset_index()
        monthly = monthly.sort_values("YearMonth")

        dates = [str(ym) + "-01" for ym in monthly["YearMonth"]]
        values = [round(float(v), 4) for v in monthly[val_col]]

        meta = {
            "source": f"NASA AppEEARS ({product})",
            "location_id": location_id,
            "latitude": float(sub_df["Latitude"].iloc[0]),
            "longitude": float(sub_df["Longitude"].iloc[0]),
            "category": str(sub_df["Category"].iloc[0]) if "Category" in sub_df.columns else "Target"
        }
        return dates, values, meta

    def extract_giovanni_gpm_timeseries(self, box_hint: str) -> Tuple[List[str], List[float], Dict[str, Any]]:
        """
        Extracts monthly GPM IMERG precipitation from Giovanni exports.
        box_hint can be 'central_india' (75E) or 'ne_india' (90E).
        """
        files = self.pillars["precipitation_csv"]
        target_file = None
        for f in files:
            if "75e" in f.lower() and ("central" in box_hint.lower() or "75" in box_hint):
                target_file = f
                break
            elif "90e" in f.lower() and ("ne" in box_hint.lower() or "meghalaya" in box_hint.lower() or "90" in box_hint):
                target_file = f
                break

        if not target_file and files:
            target_file = files[0]
        if not target_file:
            raise FileNotFoundError("No Giovanni GPM precipitation CSV found in data directory.")

        df = self.load_smart_dataframe(target_file)
        # Find time column and value column
        time_col = [c for c in df.columns if "time" in c.lower() or "date" in c.lower()][0]
        val_col = [c for c in df.columns if c != time_col and "gpm" in c.lower() or "precip" in c.lower()][0]

        df["Date"] = pd.to_datetime(df[time_col])
        df = df.dropna(subset=[val_col]).sort_values("Date")
        df["YearMonth"] = df["Date"].dt.to_period("M")
        monthly = df.groupby("YearMonth")[val_col].mean().reset_index()

        dates = [str(ym) + "-01" for ym in monthly["YearMonth"]]
        values = [round(float(v), 5) for v in monthly[val_col]]

        meta = {
            "source": "NASA Giovanni GPM IMERG v07",
            "file": target_file,
            "units": "mm/hr",
            "box": "75E_18N to 77.5E_20.5N" if "75e" in target_file.lower() else "90.5E_24.5N to 92.5E_26N"
        }
        return dates, values, meta

    def extract_gldas_timeseries(self, region_id: str) -> Tuple[List[str], List[float], Dict[str, Any]]:
        """Extracts monthly GLDAS root-zone soil moisture for a given region."""
        files = self.pillars["hydrology_benchmark_csv"]
        if not files:
            raise FileNotFoundError("No GLDAS Hydrology benchmark CSV found in data directory.")

        df = self.load_smart_dataframe(files[0])
        sub_df = df[df["Region"].astype(str).str.lower() == region_id.lower()].copy()
        if sub_df.empty:
            raise ValueError(f"Region '{region_id}' not found in GLDAS benchmark. Available: {list(df['Region'].unique())}")

        sub_df["Date"] = pd.to_datetime(sub_df["time"])
        sub_df = sub_df.sort_values("Date")

        val_col = "RootMoist_inst_kg_m2" if "RootMoist_inst_kg_m2" in sub_df.columns else sub_df.columns[4]
        dates = [d.strftime("%Y-%m-%d") for d in sub_df["Date"]]
        values = [round(float(v), 3) for v in sub_df[val_col]]

        meta = {
            "source": "NASA GES DISC GLDAS Noah v2.1",
            "region": region_id,
            "latitude": float(sub_df["Latitude"].iloc[0]),
            "longitude": float(sub_df["Longitude"].iloc[0]),
            "units": "kg/m^2"
        }
        return dates, values, meta
