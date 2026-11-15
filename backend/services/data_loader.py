"""
TerraDetective Data Loader Service Re-export
Provides backward-compatible and modular service-level import for DataLoader.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend directory to sys.path if not present
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import data_loader
from data_loader import (
    DataLoader,
    extract_smart_geolocation_label,
    enrich_variable_dict,
    MISSING_VALUE_FLAGS,
    CATALOG_METADATA_ENRICHMENT,
)

__all__ = [
    "DataLoader",
    "extract_smart_geolocation_label",
    "enrich_variable_dict",
    "MISSING_VALUE_FLAGS",
    "CATALOG_METADATA_ENRICHMENT",
]
