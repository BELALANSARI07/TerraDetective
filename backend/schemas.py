from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator

# --- Variable Catalog Schemas ---

class VariableMetadata(BaseModel):
    identifier: str = Field(..., description="Short code identifier, e.g. T2M, PRECTOTCORR, TS")
    name: str = Field(..., description="Full descriptive name")
    simple_label: Optional[str] = Field(default=None, description="Human-friendly plain-English label")
    category_icon: Optional[str] = Field(default="heat", description="Category icon: heat | rain | vegetation | water")
    units: str = Field(..., description="Measurement units (e.g. °C, mm/month, fraction)")
    category: str = Field(..., description="Physical domain category")
    description: str = Field(..., description="Scientific definition of the variable")
    detective_hint: str = Field(..., description="Climatological detective diagnostic hint")
    climatology_range: List[float] = Field(default_factory=lambda: [0.0, 100.0], description="[min, max] plausible physical range")
    primary_sat_model: str = Field(default="NASA Earth Observation Satellite System", description="Satellite sensor or assimilation model source")

class VariableCatalogResponse(BaseModel):
    mission: str
    version: str
    source: str
    total_variables: int
    variables: List[VariableMetadata]

# --- Statistical Engine Schemas ---

class ObservationPoint(BaseModel):
    date: str = Field(..., description="ISO date YYYY-MM or YYYY-MM-DD")
    value: float = Field(..., description="Measured or assimilated value")

class STLDecompositionData(BaseModel):
    trend: List[float] = Field(..., description="Low-frequency deseasonalized trend component")
    seasonal: List[float] = Field(..., description="Periodic 12-month seasonal cycle")
    residual: List[float] = Field(..., description="Irregular noise / anomaly residuals")
    seasonal_period: int = Field(default=12, description="Seasonality period length (12 for monthly)")

class TrendMetrics(BaseModel):
    sens_slope_per_month: float = Field(..., description="Sen's median slope per month")
    sens_slope_per_decade: float = Field(..., description="Sen's slope scaled to 10 years (slope_per_month * 120)")
    p_value: float = Field(..., description="Mann-Kendall p-value")
    z_score: float = Field(..., description="Mann-Kendall Z test statistic")
    kendall_tau: float = Field(..., description="Kendall tau rank correlation")
    is_significant: bool = Field(..., description="Statistically significant at alpha=0.05")
    trend_direction: str = Field(..., description="'increasing', 'decreasing', or 'no trend'")
    percent_shift: float = Field(..., description="Total percentage change over the period")
    mean_value: float = Field(..., description="Sample mean")
    std_value: float = Field(..., description="Sample standard deviation")
    observation_count: int = Field(..., description="Number of valid monthly points analyzed")

class AnalysisResponse(BaseModel):
    variable: str
    variable_name: str
    units: str
    latitude: float
    longitude: float
    location_label: Optional[str] = None
    data_source: str = Field(..., description="Dataset provenance (e.g. NASA AppEEARS MODIS, Giovanni GPM, NASA POWER)")
    dates: List[str]
    raw_values: List[float]
    stl: STLDecompositionData
    metrics: TrendMetrics
    headline: Optional[str] = Field(default=None, description="Plain-English human impact takeaway for Story Mode")
    plain_summary: Optional[str] = Field(default=None, description="2-sentence non-technical summary without jargon")
    scientific_briefing: Optional[str] = Field(default=None, description="3-sentence technical physical mechanism briefing")
    detective_briefing: str = Field(..., description="Backward-compatible AI scientific detective verdict")

# --- Regional Comparison Schemas ---

class RegionalCoordinate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180")
    label: str = Field(default="Target Region", description="Human-readable regional label")

class RegionalCompareRequest(BaseModel):
    region_a: RegionalCoordinate
    region_b: RegionalCoordinate
    variable: str = Field(default="T2M", description="Variable identifier to compare")
    start_year: int = Field(default=2001, ge=1980, le=2026)
    end_year: int = Field(default=2025, ge=1981, le=2026)

    @field_validator("end_year")
    @classmethod
    def validate_year_range(cls, v: int, info) -> int:
        start_year = info.data.get("start_year", 2001)
        if v <= start_year:
            raise ValueError("end_year must be greater than start_year")
        return v

class DivergenceMetrics(BaseModel):
    slope_difference_per_decade: float = Field(..., description="Sen slope A - Sen slope B per decade")
    divergence_ratio: float = Field(..., description="Relative divergence magnitude ratio")
    opposite_trends: bool = Field(..., description="True if one region trends positive and other trends negative")
    divergence_severity: str = Field(..., description="'Extreme Divergence', 'Moderate Divergence', or 'Synchronous'")
    headline: Optional[str] = Field(default=None, description="Plain-English regional contrast headline for Story Mode")
    plain_summary: Optional[str] = Field(default=None, description="2-sentence non-technical summary of regional divergence")
    scientific_briefing: Optional[str] = Field(default=None, description="3-sentence technical physical mechanism briefing")
    comparative_verdict: str = Field(..., description="Executive detective verdict explaining divergence")

class RegionalCompareResponse(BaseModel):
    variable: str
    variable_name: str
    units: str
    region_a: AnalysisResponse
    region_b: AnalysisResponse
    divergence: DivergenceMetrics

# --- Paradox Presets Schemas ---

class ParadoxPreset(BaseModel):
    id: str
    title: str
    subtitle: str
    description: str
    data_pillars_involved: List[str]
    region_a: RegionalCoordinate
    region_b: Optional[RegionalCoordinate] = None
    primary_variable: str
    secondary_variable: Optional[str] = None
    expected_divergence_summary: str
    key_physical_driver: str

class ParadoxPresetsResponse(BaseModel):
    presets: List[ParadoxPreset]

# --- AI Natural Language Query Schemas ---

class DetectiveQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500, description="Natural language scientific inquiry")

class RecommendedVariable(BaseModel):
    identifier: str
    name: str
    simple_label: Optional[str] = None
    category_icon: Optional[str] = None
    units: str
    category: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    why_selected: Optional[str] = None
    match_rationale: Optional[str] = None

class DetectiveQueryResponse(BaseModel):
    query: str
    top_recommendations: List[RecommendedVariable]
    detective_guidance: str

# --- Health & Discovery Schemas ---

class DataPillarStatus(BaseModel):
    pillar_name: str
    file_count: int
    files: List[str]
    status: str

class HealthResponse(BaseModel):
    status: str
    engine_version: str
    uptime_seconds: float
    data_pillars: Dict[str, DataPillarStatus]
    total_cached_points: int
    local_llm: Optional[Dict[str, Any]] = None
    earthdata: Optional[Dict[str, Any]] = None

# --- NASA Earthdata Cloud & CMR Discovery Schemas ---

class EarthdataGranuleItem(BaseModel):
    granule_id: Optional[str] = None
    title: str
    dataset_short_name: str
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    granule_size_mb: float = 0.0
    download_url: Optional[str] = None
    opendap_url: Optional[str] = None
    browse_url: Optional[str] = None
    cloud_hosted: bool = False

class EarthdataDiscoveryResponse(BaseModel):
    status: str
    authenticated: bool
    username: Optional[str] = None
    badge_text: str
    keyword: str
    bounding_box: List[float]
    total_granules_found: int
    granules: List[EarthdataGranuleItem]
    opendap_probe: Dict[str, Any]
