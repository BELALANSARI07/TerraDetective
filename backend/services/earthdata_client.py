"""
TerraDetective 3-Tier Earthdata Connector
NASA Space Apps Challenge: 'Be An Earth System Trend Detective!'

Implements resilient 3-Tier NASA data retrieval architecture:
- Tier 1 (Live NASA POWER API): Keyless monthly point time-series fetcher
  (https://power.larc.nasa.gov/api/temporal/monthly/point) for custom map clicks
  (T2M, PRECTOTCORR, ALLSKY_SFC_SW_DWN, GWETROOT).
- Tier 2 (Live NASA AppEEARS / CMR API): Authenticated requests using
  Authorization: Bearer {EARTHDATA_BEARER_TOKEN} against
  https://appeears.earthdatacloud.nasa.gov/api/ with /product health-check and strict timeout.
- Tier 3 (Automatic Local Archive Fallback): If token is missing, expired (401/403),
  unreachable, or times out, seamlessly serves from data/processed/ and returns
  {"data_mode": "verified_offline_archive"} so the application never fails.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from dotenv import load_dotenv
import pandas as pd
import polars as pl

logger = logging.getLogger("terradetective.earthdata_connector")

# Endpoints
NASA_POWER_MONTHLY_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
APPEEARS_API_URL = "https://appeears.earthdatacloud.nasa.gov/api"
CMR_SEARCH_URL = "https://cmr.earthdata.nasa.gov/search"

# Supported live NASA POWER default parameters
DEFAULT_POWER_PARAMS = ["T2M", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN", "GWETROOT"]


class ThreeTierEarthDataConnector:
    """
    Resilient 3-Tier Earthdata Client supporting live NASA APIs with
    graceful offline fallback to verified local archive assets.
    """

    def __init__(
        self,
        token: Optional[str] = None,
        env_file: Optional[Path | str] = None,
        processed_dir: Optional[Path | str] = None,
        timeout: float = 4.0,
    ):
        base_dir = Path(__file__).resolve().parent.parent.parent
        env_path = Path(env_file) if env_file else base_dir / ".env"
        if env_path.is_file():
            load_dotenv(env_path)

        # Read EARTHDATA_BEARER_TOKEN with fallback to EARTHDATA_TOKEN
        self.token = (
            token
            or os.getenv("EARTHDATA_BEARER_TOKEN")
            or os.getenv("EARTHDATA_TOKEN", "")
        ).strip().strip('"').strip("'")

        self.username = os.getenv("EARTHDATA_USER", "NASA Earthdata User").strip().strip('"')
        self.timeout = timeout

        if processed_dir is None:
            self.processed_dir = base_dir / "data" / "processed"
        else:
            self.processed_dir = Path(processed_dir)

        self._cached_manifest: Optional[Dict[str, Any]] = None
        self._cached_unified_df: Optional[pd.DataFrame] = None

    def get_auth_headers(self) -> Dict[str, str]:
        """Returns standard NASA Bearer authentication header."""
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    # -------------------------------------------------------------------------
    # Tier 2: NASA AppEEARS Token Health Check & Product Inspection
    # -------------------------------------------------------------------------
    def check_appeears_token_health(self) -> Dict[str, Any]:
        """
        Tier 2 Health Check: Tests EARTHDATA_BEARER_TOKEN against NASA AppEEARS API.
        Enforces strict timeout. If missing, expired (401/403), or offline,
        reports status and designates Tier 3 fallback.
        """
        if not self.token:
            return {
                "authenticated": False,
                "tier": 3,
                "status": "Token missing (EARTHDATA_BEARER_TOKEN not set)",
                "data_mode": "verified_offline_archive",
                "recommended_action": "Set EARTHDATA_BEARER_TOKEN in .env or rely on local verified archive",
            }

        headers = self.get_auth_headers()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{APPEEARS_API_URL}/product", headers=headers)
                if res.status_code == 200:
                    products = res.json()
                    return {
                        "authenticated": True,
                        "tier": 2,
                        "status": "active",
                        "username": self.username,
                        "total_products_available": len(products) if isinstance(products, list) else 1,
                        "data_mode": "live_appeears",
                        "token_preview": f"{self.token[:12]}...{self.token[-8:]}",
                    }
                elif res.status_code in (401, 403):
                    logger.warning(f"NASA AppEEARS token rejected (HTTP {res.status_code}). Falling back to Tier 3.")
                    return {
                        "authenticated": False,
                        "tier": 3,
                        "status": f"expired_or_invalid (HTTP {res.status_code})",
                        "data_mode": "verified_offline_archive",
                        "token_preview": f"{self.token[:12]}...{self.token[-8:]}",
                    }
                else:
                    return {
                        "authenticated": False,
                        "tier": 3,
                        "status": f"appeears_http_error_{res.status_code}",
                        "data_mode": "verified_offline_archive",
                    }
        except (httpx.TimeoutException, httpx.NetworkError, Exception) as err:
            logger.info(f"NASA AppEEARS probe timed out or unreachable ({type(err).__name__}). Using Tier 3 fallback.")
            return {
                "authenticated": False,
                "tier": 3,
                "status": "unreachable_or_offline",
                "reason": str(err),
                "data_mode": "verified_offline_archive",
            }

    def fetch_appeears_product_metadata(self, product_id: str = "MOD11A2.061") -> Dict[str, Any]:
        """
        Tier 2 Product Inspection: Queries AppEEARS for product information.
        Falls back to local manifest metadata if offline or unauthorized.
        """
        health = self.check_appeears_token_health()
        if health.get("authenticated"):
            try:
                headers = self.get_auth_headers()
                with httpx.Client(timeout=self.timeout) as client:
                    res = client.get(f"{APPEEARS_API_URL}/product/{product_id}", headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        return {
                            "status": "success",
                            "tier": 2,
                            "data_mode": "live_appeears",
                            "product": data,
                        }
            except Exception as e:
                logger.warning(f"AppEEARS fetch failed ({e}). Falling back to local manifest.")

        # Tier 3 Fallback: Return cached manifest info for this product
        manifest = self.load_manifest()
        matching_case = None
        for c in manifest.get("cases", []):
            if product_id.lower() in c.get("source_product", "").lower():
                matching_case = c
                break

        return {
            "status": "success",
            "tier": 3,
            "data_mode": "verified_offline_archive",
            "fallback_reason": health.get("status", "offline"),
            "product_id": product_id,
            "associated_case": matching_case,
        }

    # -------------------------------------------------------------------------
    # Tier 1: Keyless Live NASA POWER API (Monthly Point Time-Series)
    # -------------------------------------------------------------------------
    def fetch_nasa_power_point(
        self,
        lat: float,
        lon: float,
        start_year: int = 2001,
        end_year: int = 2024,
        parameters: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Tier 1: Keyless monthly point time-series fetcher for custom user map clicks.
        Queries NASA POWER API for parameters like T2M, PRECTOTCORR, ALLSKY_SFC_SW_DWN, GWETROOT.
        If offline, timed out, or uncontactable, automatically executes Tier 3 archive fallback.
        """
        if parameters is None:
            parameters = DEFAULT_POWER_PARAMS

        param_str = ",".join(parameters)
        query_params = {
            "parameters": param_str,
            "community": "AG",
            "longitude": round(lon, 4),
            "latitude": round(lat, 4),
            "start": str(start_year),
            "end": str(end_year),
            "format": "JSON",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(NASA_POWER_MONTHLY_URL, params=query_params)
                if res.status_code == 200:
                    data = res.json()
                    properties = data.get("properties", {})
                    param_dict = properties.get("parameter", {})

                    # Format into standardized monthly time-series
                    time_series: List[Dict[str, Any]] = []
                    sample_param = parameters[0] if parameters else "T2M"
                    keys = sorted(param_dict.get(sample_param, {}).keys())

                    for k in keys:
                        # Exclude 13th month entry (annual average '13' in POWER)
                        if k.endswith("13"):
                            continue
                        yr = int(k[:4])
                        mo = int(k[4:6])
                        dt_str = f"{yr:04d}-{mo:02d}-01"
                        entry = {"date": dt_str, "year": yr, "month": mo}
                        for p in parameters:
                            raw_val = param_dict.get(p, {}).get(k, None)
                            entry[p] = raw_val if (raw_val is not None and raw_val != -999.0) else None
                        time_series.append(entry)

                    return {
                        "status": "success",
                        "tier": 1,
                        "data_mode": "live_nasa_power",
                        "latitude": lat,
                        "longitude": lon,
                        "parameters": parameters,
                        "total_monthly_records": len(time_series),
                        "data": time_series,
                    }
                else:
                    logger.warning(f"NASA POWER API returned HTTP {res.status_code}. Initiating Tier 3 fallback.")
        except (httpx.TimeoutException, httpx.NetworkError, Exception) as e:
            logger.info(f"NASA POWER API unreachable ({type(e).__name__}: {e}). Serving from Tier 3 local archive.")

        # Tier 3 Fallback
        return self._fallback_to_nearest_offline_case(lat, lon)

    # -------------------------------------------------------------------------
    # Tier 3: Verified Local Archive Loader (Zero-API Dependency)
    # -------------------------------------------------------------------------
    def load_manifest(self) -> Dict[str, Any]:
        """Loads and caches case_studies_manifest.json from data/processed/."""
        if self._cached_manifest is not None:
            return self._cached_manifest

        manifest_path = self.processed_dir / "case_studies_manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(f"Case studies manifest not found at: {manifest_path}")

        with open(manifest_path, "r", encoding="utf-8") as f:
            self._cached_manifest = json.load(f)
        return self._cached_manifest

    def load_unified_archive(self) -> pd.DataFrame:
        """Loads and caches terradetective_unified_monthly from data/processed/."""
        if self._cached_unified_df is not None:
            return self._cached_unified_df

        csv_path = self.processed_dir / "terradetective_unified_monthly.csv"
        parquet_path = self.processed_dir / "terradetective_unified_monthly.parquet"

        if csv_path.is_file():
            self._cached_unified_df = pd.read_csv(csv_path)
        elif parquet_path.is_file():
            pl_df = pl.read_parquet(parquet_path)
            self._cached_unified_df = pd.DataFrame(pl_df.to_dicts())
        else:
            raise FileNotFoundError(f"Processed archive not found in {self.processed_dir}")

        return self._cached_unified_df

    def fetch_case_study(
        self,
        case_id: str,
        region_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Tier 3 Direct Service: Returns verified pre-bundled case study time-series
        and metadata for instant playback.
        """
        manifest = self.load_manifest()
        case_meta = None
        for c in manifest.get("cases", []):
            if c["case_id"] == case_id:
                case_meta = c
                break

        if case_meta is None:
            available_cases = [c["case_id"] for c in manifest.get("cases", [])]
            return {
                "status": "error",
                "message": f"Case ID '{case_id}' not found. Available: {available_cases}",
                "data_mode": "verified_offline_archive",
                "tier": 3,
            }

        df = self.load_unified_archive()
        filtered = df[df["case_id"] == case_id]

        if region_id:
            filtered = filtered[filtered["region_id"] == region_id]

        records = filtered.to_dict(orient="records")

        return {
            "status": "success",
            "tier": 3,
            "data_mode": "verified_offline_archive",
            "case_id": case_id,
            "case_metadata": case_meta,
            "filter_region": region_id,
            "total_records": len(records),
            "records": records,
        }

    def fetch_all_cases_summary(self) -> Dict[str, Any]:
        """Returns summary of all 3 pre-bundled case studies for workbench UI."""
        manifest = self.load_manifest()
        df = self.load_unified_archive()

        summary_cases = []
        for c in manifest.get("cases", []):
            cid = c["case_id"]
            sub = df[df["case_id"] == cid]
            summary_cases.append({
                "case_id": cid,
                "title": c["title"],
                "subtitle": c["subtitle"],
                "variable_id": c["variable_id"],
                "variable_name": c["variable_name"],
                "unit": c["unit"],
                "regions": [r["region_id"] for r in c.get("regions", [])],
                "record_count": len(sub),
                "date_min": sub["date"].min() if not sub.empty else None,
                "date_max": sub["date"].max() if not sub.empty else None,
            })

        return {
            "status": "success",
            "tier": 3,
            "data_mode": "verified_offline_archive",
            "cases_count": len(summary_cases),
            "cases": summary_cases,
        }

    def _fallback_to_nearest_offline_case(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Helper that maps user coordinates to the closest pre-bundled case study
        and returns verified offline archive data with transparent metadata.
        """
        coords_map = {
            "RondoniaAmazonArc": (-10.875, -61.93, "case_2_land_thermal_paradox"),
            "PunjabIrrigatedBelt": (30.901, 75.8573, "case_2_land_thermal_paradox"),
            "Marathwada": (19.25, 76.25, "case_1_monsoon_paradox"),
            "NortheastIndia": (25.25, 91.50, "case_1_monsoon_paradox"),
        }

        closest_region = None
        min_dist = float("inf")
        target_case = "case_1_monsoon_paradox"

        for r_id, (r_lat, r_lon, cid) in coords_map.items():
            dist = (lat - r_lat) ** 2 + (lon - r_lon) ** 2
            if dist < min_dist:
                min_dist = dist
                closest_region = r_id
                target_case = cid

        res = self.fetch_case_study(case_id=target_case, region_id=closest_region)
        res["fallback_reason"] = "live_network_unavailable_using_nearest_study_region"
        res["requested_coordinates"] = {"lat": lat, "lon": lon}
        res["nearest_region"] = closest_region
        return res


# Backward-compatible alias
EarthdataClient = ThreeTierEarthDataConnector
