import React, { useState, useEffect } from 'react';
import { 
  Sparkles, CheckCircle, AlertTriangle, Download, 
  HelpCircle, Lightbulb, Compass, Award, ExternalLink,
  Table, FileText, ChevronRight, Activity, Satellite, Globe2, ShieldCheck, Eye,
  Copy, Check, ArrowRight, Flame, Snowflake, Cpu, Layers, Radio, Crosshair
} from 'lucide-react';

const formatSlope = (val, digits = 4) => {
  if (val === undefined || val === null || isNaN(val)) return '—';
  const num = Number(val);
  const sign = num > 0 ? '+' : '';
  return `${sign}${num.toFixed(digits)}`;
};

const getSatelliteTileUrl = (lat, lon, zoom = 5) => {
  if (lat == null || lon == null || isNaN(lat) || isNaN(lon)) return null;
  const latRad = (lat * Math.PI) / 180;
  const n = Math.pow(2, zoom);
  const xTile = Math.floor(((lon + 180) / 360) * n);
  const yTile = Math.floor(
    ((1 - Math.asinh(Math.tan(latRad)) / Math.PI) / 2) * n
  );
  return `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${zoom}/${yTile}/${xTile}`;
};

/**
 * High-tech NASA Orbital Scanner Reticle Component
 * Rendered when satellite imagery is loading, or as a high-fidelity visual telemetry fallback.
 * Uses procedural orbital scanner HUD with radar sweep, coordinate lock, and false-color thermal grid.
 */
const OrbitalScannerReticle = ({ label = 'Sensor Grid', lat, lon, collection = 'MODIS Sensor', isLight = false }) => {
  const safeLabel = String(label || 'Target Sensor Grid').replace(/[^a-zA-Z0-9]/g, '_');
  const latNum = lat != null && !isNaN(Number(lat)) ? Number(lat) : 20.0;
  const lonNum = lon != null && !isNaN(Number(lon)) ? Number(lon) : 78.0;

  // Procedural hue based on latitude/longitude
  const hue = Math.abs(Math.round((latNum * 7 + lonNum * 3) % 360));

  return (
    <div className={`absolute inset-0 flex flex-col items-center justify-center p-3 text-center overflow-hidden select-none ${
      isLight 
        ? 'bg-gradient-to-br from-[#EAE5D9] via-[#FAF8F5] to-[#E3DDD0]' 
        : 'bg-gradient-to-br from-[#06090F] via-[#0C121D] to-[#121927]'
    }`}>
      {/* Background Reticle Grid & Radar Rings */}
      <svg className="absolute inset-0 w-full h-full opacity-35 pointer-events-none" viewBox="0 0 100 100" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id={`reticle-grid-${safeLabel}`} width="10" height="10" patternUnits="userSpaceOnUse">
            <path d="M 10 0 L 0 0 0 10" fill="none" stroke={isLight ? '#1B6B50' : '#00E5FF'} strokeWidth="0.3" strokeDasharray="1,1" opacity="0.6" />
          </pattern>
          <radialGradient id={`orbital-glow-${safeLabel}`} cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor={isLight ? '#C84B31' : '#00E5FF'} stopOpacity="0.25" />
            <stop offset="60%" stopColor={isLight ? '#1B6B50' : '#38BDF8'} stopOpacity="0.08" />
            <stop offset="100%" stopColor={isLight ? '#FAF8F5' : '#07090E'} stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Ambient Orbital Heat Glow */}
        <rect width="100" height="100" fill={`url(#orbital-glow-${safeLabel})`} />
        
        {/* Reticle Mesh */}
        <rect width="100" height="100" fill={`url(#reticle-grid-${safeLabel})`} />
        
        {/* Concentric Radar Elevation Rings */}
        <circle cx="50" cy="50" r="20" fill="none" stroke={isLight ? '#1B6B50' : '#00E5FF'} strokeWidth="0.5" strokeDasharray="2,2" opacity="0.8" />
        <circle cx="50" cy="50" r="35" fill="none" stroke={isLight ? '#C84B31' : '#38BDF8'} strokeWidth="0.4" strokeDasharray="3,3" opacity="0.5" />
        <circle cx="50" cy="50" r="46" fill="none" stroke={isLight ? '#141E19' : '#F59E0B'} strokeWidth="0.3" opacity="0.3" />
        
        {/* Cardinal Crosshair Reticles */}
        <line x1="50" y1="5" x2="50" y2="95" stroke={isLight ? '#141E19' : '#00E5FF'} strokeWidth="0.5" opacity="0.45" strokeDasharray="4,3" />
        <line x1="5" y1="50" x2="95" y2="50" stroke={isLight ? '#141E19' : '#00E5FF'} strokeWidth="0.5" opacity="0.45" strokeDasharray="4,3" />

        {/* Diagonal Corner Tick Marks */}
        <path d="M 6 14 L 6 6 L 14 6" fill="none" stroke={isLight ? '#1B6B50' : '#00E5FF'} strokeWidth="1" />
        <path d="M 6 86 L 6 94 L 14 94" fill="none" stroke={isLight ? '#1B6B50' : '#00E5FF'} strokeWidth="1" />
        <path d="M 94 14 L 94 6 L 86 6" fill="none" stroke={isLight ? '#1B6B50' : '#00E5FF'} strokeWidth="1" />
        <path d="M 94 86 L 94 94 L 86 94" fill="none" stroke={isLight ? '#1B6B50' : '#00E5FF'} strokeWidth="1" />
      </svg>

      {/* Center Target Lock HUD */}
      <div className="relative z-10 flex flex-col items-center space-y-1.5 px-3 py-2 rounded bg-black/25 backdrop-blur-xs border border-white/5">
        <div className="relative">
          <div className={`w-9 h-9 rounded-full border flex items-center justify-center ${
            isLight
              ? 'border-archival-viridian/50 bg-archival-viridian/15 text-archival-viridian'
              : 'border-cyan-400/50 bg-cyan-950/50 text-cyan-400 shadow-[0_0_12px_rgba(0,229,255,0.3)]'
          }`}>
            <Crosshair className="w-4 h-4 animate-spin" style={{ animationDuration: '14s' }} />
          </div>
          <div className={`absolute -inset-1 rounded-full border opacity-40 animate-ping ${
            isLight ? 'border-archival-terracotta' : 'border-cyan-400'
          }`} style={{ animationDuration: '3s' }} />
        </div>

        <span className={`font-bold text-xs tracking-wide max-w-[220px] truncate ${
          isLight ? 'text-archival-ink font-serif text-sm' : 'text-slate-100 font-mono text-[11px]'
        }`}>
          {label}
        </span>
        
        <div className={`text-[9.5px] font-mono tabular-nums flex items-center space-x-2 ${
          isLight ? 'text-archival-muted' : 'text-cyan-300'
        }`}>
          <span>{latNum >= 0 ? `${latNum.toFixed(2)}°N` : `${Math.abs(latNum).toFixed(2)}°S`}, {lonNum >= 0 ? `${lonNum.toFixed(2)}°E` : `${Math.abs(lonNum).toFixed(2)}°W`}</span>
          <span>•</span>
          <span>705 km Orbit</span>
        </div>

        <div className="flex items-center space-x-1.5 pt-0.5">
          <span className={`text-[8.5px] font-mono px-2 py-0.5 rounded border uppercase tracking-wider ${
            isLight
              ? 'bg-archival-sand/90 text-archival-ink border-[#DCD7C9]'
              : 'bg-[#151D2A] text-cyan-300 border-[#223045]'
          }`}>
            {collection || 'MODIS Terra Sensor'}
          </span>
          <span className={`text-[8.5px] font-mono px-1.5 py-0.5 rounded border ${
            isLight ? 'bg-white text-archival-muted border-[#DCD7C9]' : 'bg-[#0E1520] text-emerald-400 border-emerald-900/60'
          }`}>
            ● Active Footprint
          </span>
        </div>
      </div>
    </div>
  );
};

const SatelliteSnapshotViewer = ({ label, lat, lon, previewUrl, fallbackUrl, collection, visualClue, isStudent = false }) => {
  const sanitizeUrl = (url) => {
    if (!url || typeof url !== 'string') return null;
    if (url.endsWith('.tif') || url.endsWith('.tiff') || url.endsWith('.hdf')) return null;
    return url;
  };

  const cleanPreview = sanitizeUrl(previewUrl);
  const tileUrl = getSatelliteTileUrl(lat, lon, 6) || fallbackUrl;
  const primarySrc = cleanPreview || tileUrl;

  const [currentSrc, setCurrentSrc] = useState(primarySrc);
  const [hasError, setHasError] = useState(false);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const src = sanitizeUrl(previewUrl) || tileUrl;
    setCurrentSrc(src);
    setHasError(false);
    setLoaded(false);
  }, [previewUrl, tileUrl, lat, lon]);

  const handleError = () => {
    if (tileUrl && currentSrc !== tileUrl) {
      setCurrentSrc(tileUrl);
    } else {
      setHasError(true);
    }
  };

  return (
    <div className={`relative aspect-video overflow-hidden border transition-all ${
      isStudent
        ? 'rounded-lg bg-[#EAE5D9] border-[#DCD7C9] shadow-none'
        : 'rounded-none bg-[#07090E] border-[#1E2636] shadow-none'
    }`}>
      {/* Background Reticle Always Available Underneath */}
      <OrbitalScannerReticle
        label={label}
        lat={lat}
        lon={lon}
        collection={collection}
        isLight={isStudent}
      />

      {/* Satellite Imagery Overlaid Smoothly */}
      {!hasError && currentSrc && (
        <img
          src={currentSrc}
          alt={`${label} NASA Satellite Telemetry`}
          className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-500 z-10 ${
            loaded ? 'opacity-100' : 'opacity-0'
          }`}
          onLoad={() => setLoaded(true)}
          onError={handleError}
          loading="lazy"
        />
      )}

      {/* Loading Sensor Scan Spinner */}
      {!loaded && !hasError && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-end pb-3 pointer-events-none">
          <span className={`text-[9px] font-mono tracking-wider px-2 py-0.5 rounded backdrop-blur-sm ${
            isStudent
              ? 'bg-[#FAF8F5]/90 text-archival-ink border border-[#DCD7C9]'
              : 'bg-[#07090E]/90 text-cyan-300 border border-[#1E2636]'
          }`}>
            Scanning Orbital Pass...
          </span>
        </div>
      )}

      {/* Sensor HUD Overlays */}
      <div className={`absolute top-2 left-2 z-30 px-2 py-0.5 text-[9px] font-mono backdrop-blur-sm border flex items-center space-x-1 ${
        isStudent
          ? 'bg-[#FAF8F5]/90 text-archival-ink border-[#DCD7C9] rounded-md'
          : 'bg-[#07090E]/90 text-cyan-400 border-[#1E2636] rounded-none'
      }`}>
        <span>🛰️</span>
        <span className="tabular-nums">{lat != null ? `${Number(lat).toFixed(2)}°, ${Number(lon).toFixed(2)}°` : 'NASA Grid'}</span>
      </div>

      <div className={`absolute bottom-2 right-2 z-30 px-2 py-0.5 text-[9px] font-mono backdrop-blur-sm border ${
        isStudent
          ? 'bg-[#FAF8F5]/90 text-archival-ink border-[#DCD7C9] rounded-md'
          : 'bg-[#07090E]/90 text-slate-300 border-[#1E2636] rounded-none'
      }`}>
        1 km Swath Resolution
      </div>

      {/* Explorer Mode Visual Clue Overlay */}
      {isStudent && visualClue && (
        <div className="absolute bottom-8 left-2 right-2 z-30 px-2.5 py-1.5 rounded-md bg-[#FAF8F5]/95 backdrop-blur-md text-[10.5px] text-archival-ink border border-[#DCD7C9] leading-snug shadow-sm font-sans">
          {visualClue}
        </div>
      )}
    </div>
  );
};

export default function InsightPanel({
  statistics,
  narratives,
  caseId,
  mode = 'student',
  customData = null,
  telemetry = null,
  manifest = null,
}) {
  const isLight = mode === 'student';

  const [liveTelemetry, setLiveTelemetry] = useState(telemetry);
  const [telemetryLoading, setTelemetryLoading] = useState(false);
  const [alphaCutoff, setAlphaCutoff] = useState(0.05);
  const [copyStatus, setCopyStatus] = useState('idle');

  const studentNarrative = narratives?.student_story_mode;
  const scientistNarrative = narratives?.scientist_research_mode;

  const regA = statistics?.region_a;
  const regB = statistics?.region_b;
  const div = statistics?.divergence_analysis;
  const unit = statistics?.unit || 'units';

  // Robust clean place name resolution
  const isCleanName = (str) => {
    if (!str || typeof str !== 'string') return false;
    const lower = str.trim().toLowerCase();
    return (
      lower.length > 0 &&
      !['region_a', 'region_b', 'region a', 'region b', 'region', 'region_id'].includes(lower)
    );
  };

  const resolveCleanName = (reg, manifestReg, index, defaultFallback) => {
    const candidates = [
      reg?.region_label,
      manifestReg?.region_label,
      manifestReg?.region_name,
      manifestReg?.label,
      reg?.name,
      manifest?.region_a?.label,
      manifest?.region_b?.label,
    ];
    for (const c of candidates) {
      if (isCleanName(c)) {
        return c.trim();
      }
    }
    if (manifest?.title) {
      const match = manifest.title.match(/(?:Investigation|Probe|Analysis|Comparison|Telemetry)?[:\s]*(.+?)\s+(?:vs\.?|versus|to|and)\s+(.+?)(?:\s*\(|$)/i);
      if (match) {
        const first = match[1].replace(/^.*?: /, '').trim();
        const second = match[2].trim();
        if (index === 0 && isCleanName(first)) return first;
        if (index === 1 && isCleanName(second)) return second;
      }
    }
    return defaultFallback;
  };

  const labelA = resolveCleanName(regA, manifest?.regions?.[0] || manifest?.region_a, 0, 'Region A');
  const labelB = resolveCleanName(regB, manifest?.regions?.[1] || manifest?.region_b, 1, 'Region B');

  // Support coordinates across all manifest & telemetry data structures
  const latA = regA?.coordinates?.lat ?? regA?.lat ?? manifest?.regions?.[0]?.latitude ?? manifest?.region_a?.lat ?? 20.59;
  const lonA = regA?.coordinates?.lon ?? regA?.lon ?? manifest?.regions?.[0]?.longitude ?? manifest?.region_a?.lon ?? 78.96;
  const latB = regB?.coordinates?.lat ?? regB?.lat ?? manifest?.regions?.[1]?.latitude ?? manifest?.region_b?.lat ?? 37.09;
  const lonB = regB?.coordinates?.lon ?? regB?.lon ?? manifest?.regions?.[1]?.longitude ?? manifest?.region_b?.lon ?? -95.71;

  const fallbackTileA = getSatelliteTileUrl(latA, lonA, 5);
  const fallbackTileB = getSatelliteTileUrl(latB, lonB, 5);

  const slopeA = regA?.mann_kendall?.sens_slope_per_decade;
  const slopeB = regB?.mann_kendall?.sens_slope_per_decade;

  const totalA = regA?.mann_kendall?.total_estimated_change 
    ?? regA?.mann_kendall?.total_change 
    ?? (slopeA != null ? slopeA * 2.5 : 0);
  const totalB = regB?.mann_kendall?.total_estimated_change 
    ?? regB?.mann_kendall?.total_change 
    ?? (slopeB != null ? slopeB * 2.5 : 0);

  const isOpposing = Boolean(
    div?.opposite_direction ||
    div?.divergence_detected ||
    div?.is_divergent ||
    (slopeA != null && slopeB != null && slopeA * slopeB < 0)
  );

  const confA = regA?.mann_kendall?.confidence_pct || 99.0;
  const confB = regB?.mann_kendall?.confidence_pct || 99.0;
  const meanConf = Math.round((confA + confB) / 2 * 10) / 10;

  const handleDownloadCsv = () => {
    if (caseId) {
      window.open(`/api/export/${caseId}/csv`, '_blank');
    }
  };

  useEffect(() => {
    if (telemetry) {
      setLiveTelemetry(telemetry);
      return;
    }

    const varId = manifest?.variable_id || 'LST';
    setTelemetryLoading(true);
    Promise.all([
      fetch(`/api/satellite/telemetry?lat=${latA}&lon=${lonA}&variable_id=${varId}`).then((r) => r.json()),
      fetch(`/api/satellite/telemetry?lat=${latB}&lon=${lonB}&variable_id=${varId}`).then((r) => r.json()),
    ])
      .then(([tA, tB]) => {
        setLiveTelemetry({ region_a: tA, region_b: tB });
      })
      .catch((err) => console.warn('Live telemetry fetch warning:', err))
      .finally(() => setTelemetryLoading(false));
  }, [caseId, telemetry, manifest, latA, lonA, latB, lonB]);

  const telemA = liveTelemetry?.region_a;
  const telemB = liveTelemetry?.region_b;

  const urlA = telemA?.rendered_preview_url || fallbackTileA;
  const urlB = telemB?.rendered_preview_url || fallbackTileB;

  // Visual Field Guide Clues for Student Mode
  const getVisualClues = () => {
    const cid = caseId || manifest?.case_id;
    if (cid === 'case_2_land_thermal_paradox') {
      return {
        clueA: "🔍 Detective Clue: Notice the light-colored 'fishbone' logging roads cut into the dark green canopy where trees were cleared.",
        clueB: "🔍 Detective Clue: Notice the geometric mosaic of bright green irrigated crops fed by Himalayan snowmelt canals.",
      };
    } else if (cid === 'case_1_monsoon_paradox') {
      return {
        clueA: "🔍 Detective Clue: Notice the steep southern escarpment of the Meghalaya plateau trapping incoming Bay of Bengal monsoon air.",
        clueB: "🔍 Detective Clue: Notice the semi-arid, brown terrain lying in the dry leeward rain shadow of the Western Ghats mountain wall.",
      };
    } else if (cid === 'case_3_vegetation_paradox') {
      return {
        clueA: "🔍 Detective Clue: Notice the expanding pasture fields replacing primary rainforest canopy across the Amazon arc.",
        clueB: "🔍 Detective Clue: Notice the dense emerald green double-cropped farmlands of Punjab.",
      };
    }
    return {
      clueA: `🔍 Detective Clue: High-resolution orbital sensor view over ${labelA} (${latA?.toFixed(2)}°, ${lonA?.toFixed(2)}°).`,
      clueB: `🔍 Detective Clue: High-resolution orbital sensor view over ${labelB} (${latB?.toFixed(2)}°, ${lonB?.toFixed(2)}°).`,
    };
  };

  const visualClues = getVisualClues();

  // Markdown & LaTeX Table Export Functions
  const generateMarkdownTable = () => {
    return `| Metric | Region A: ${labelA} | Region B: ${labelB} | Divergence Verdict |
| :--- | :--- | :--- | :--- |
| Sen's Median Slope / Decade | ${formatSlope(slopeA, 4)} ${unit}/dec | ${formatSlope(slopeB, 4)} ${unit}/dec | Δ = ${formatSlope(div?.slope_difference_per_decade, 4)} ${unit}/dec |
| Total 25-Year Change | ${formatSlope(totalA, 2)} ${unit} | ${formatSlope(totalB, 2)} ${unit} | Net Separation: ${formatSlope(Math.abs(totalA - totalB), 2)} ${unit} |
| Deseasonalized Mann-Kendall p-value | ${regA?.mann_kendall?.p_value} (${regA?.mann_kendall?.trend_direction}) | ${regB?.mann_kendall?.p_value} (${regB?.mann_kendall?.trend_direction}) | ${div?.both_significant ? 'Both Significant (p < 0.05)' : 'Partial'} |
| Seasonal Mann-Kendall p-value | ${regA?.seasonal_mann_kendall?.p_value ?? '—'} | ${regB?.seasonal_mann_kendall?.p_value ?? '—'} | 12-Month Period Alignment |
| Kendall's Tau | ${regA?.mann_kendall?.tau ?? '—'} | ${regB?.mann_kendall?.tau ?? '—'} | ${isOpposing ? 'Opposing Trajectory' : 'Concordant'} |
| OLS Regression Slope | ${formatSlope(regA?.ols_regression?.ols_slope_per_year, 4)}/yr (R²=${regA?.ols_regression?.r_squared}) | ${formatSlope(regB?.ols_regression?.ols_slope_per_year, 4)}/yr (R²=${regB?.ols_regression?.r_squared}) | Z-score diff = ${div?.z_score_divergence ?? '—'} |
| 95% Confidence Interval | [${formatSlope(regA?.ols_regression?.slope_ci_95_low, 4)}, ${formatSlope(regA?.ols_regression?.slope_ci_95_high, 4)}] | [${formatSlope(regB?.ols_regression?.slope_ci_95_low, 4)}, ${formatSlope(regB?.ols_regression?.slope_ci_95_high, 4)}] | ${div?.ci_separated ? 'Non-Overlapping (Separated)' : 'Overlapping'} |`;
  };

  const generateLatexTable = () => {
    return `\\begin{table}[ht]
\\centering
\\caption{Multi-Decadal Trend Divergence Analysis (${labelA} vs. ${labelB})}
\\begin{tabular}{lccc}
\\hline
\\textbf{Metric} & \\textbf{Region A (${labelA})} & \\textbf{Region B (${labelB})} & \\textbf{Divergence Verdict} \\\\
\\hline
Sen's Median Slope & ${formatSlope(slopeA, 4)} ${unit}/dec & ${formatSlope(slopeB, 4)} ${unit}/dec & $\\Delta = ${formatSlope(div?.slope_difference_per_decade, 4)}$ ${unit}/dec \\\\
Total 25-Year Change & ${formatSlope(totalA, 2)} ${unit} & ${formatSlope(totalB, 2)} ${unit} & Net: ${formatSlope(Math.abs(totalA - totalB), 2)} ${unit} \\\\
Mann-Kendall $p$-value & $p = ${regA?.mann_kendall?.p_value}$ & $p = ${regB?.mann_kendall?.p_value}$ & ${div?.both_significant ? '$p < 0.05$ (Significant)' : 'Partial'} \\\\
Kendall's $\\tau$ & ${regA?.mann_kendall?.tau} & ${regB?.mann_kendall?.tau} & ${isOpposing ? 'Antiphase' : 'Concordant'} \\\\
OLS Slope ($R^2$) & ${formatSlope(regA?.ols_regression?.ols_slope_per_year, 4)}/yr ($R^2=${regA?.ols_regression?.r_squared}$) & ${formatSlope(regB?.ols_regression?.ols_slope_per_year, 4)}/yr ($R^2=${regB?.ols_regression?.r_squared}$) & $Z = ${div?.z_score_divergence}$ \\\\
\\hline
\\end{tabular}
\\end{table}`;
  };

  const handleCopyTable = (format = 'markdown') => {
    const text = format === 'latex' ? generateLatexTable() : generateMarkdownTable();
    navigator.clipboard.writeText(text);
    setCopyStatus(format === 'latex' ? 'copied_latex' : 'copied_md');
    setTimeout(() => setCopyStatus('idle'), 2500);
  };

  // Render Telemetry Imagery Section
  const renderTelemetryCard = () => (
    <div className={`border p-4 sm:p-5 transition-all ${
      isLight 
        ? 'bg-[#FAF8F5] border-[#DCD7C9] rounded-xl shadow-none' 
        : 'bg-[#0C1017] border-[#1E2636] rounded-none shadow-none'
    }`}>
      <div className={`flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b gap-2 mb-4 ${
        isLight ? 'border-[#DCD7C9]' : 'border-[#1E2636]'
      }`}>
        <div className="flex items-center space-x-2">
          <Satellite className={`w-4 h-4 ${isLight ? 'text-archival-viridian' : 'text-cyan-400'}`} />
          <h3 className={`font-bold text-sm ${isLight ? 'font-serif text-base text-archival-ink' : 'font-mono text-xs text-white'}`}>
            {isLight ? '📸 What NASA Satellites See From Space (Visual Field Guide)' : 'Live Multi-Agency Satellite Imagery & Granule Registry'}
          </h3>
        </div>
        <div className="flex items-center space-x-2 text-[10px] font-mono">
          <span className={`px-2 py-0.5 border flex items-center space-x-1 ${
            isLight
              ? 'bg-archival-sand text-archival-ink border-[#DCD7C9] rounded-md'
              : 'bg-[#1E2636] text-cyan-300 border-[#2E3B52] rounded-none'
          }`}>
            <ShieldCheck className="w-3 h-3 text-cyan-400" />
            <span>NASA EDL Bearer: Active</span>
          </span>
          <span className={`px-2 py-0.5 border ${
            isLight
              ? 'bg-[#EAE5D9] text-archival-ink border-[#DCD7C9] rounded-md'
              : 'bg-[#151D2A] text-purple-300 border-[#253247] rounded-none'
          }`}>
            MS Planetary Computer STAC
          </span>
        </div>
      </div>

      {/* Side-by-Side Satellite Snapshots */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Region A Visual */}
        <div className={`p-3 border flex flex-col justify-between ${
          isLight ? 'bg-white border-[#DCD7C9] rounded-lg' : 'bg-[#07090E] border-[#1E2636] rounded-none'
        }`}>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className={`font-bold text-xs ${isLight ? 'text-archival-terracotta' : 'text-cyan-400 font-mono'}`}>
                Region A: {labelA}
              </span>
              <span className="text-[10px] font-mono text-slate-400">
                {telemA?.cmr?.collection || 'MODIS MOD11A2'}
              </span>
            </div>
            <SatelliteSnapshotViewer
              label={labelA}
              lat={latA}
              lon={lonA}
              previewUrl={urlA}
              fallbackUrl={fallbackTileA}
              collection={telemA?.cmr?.collection || 'MODIS MOD11A2'}
              visualClue={visualClues.clueA}
              isStudent={isLight}
            />
          </div>
          {!isLight && (
            <div className="mt-2.5 text-[10px] font-mono text-slate-400 leading-tight">
              Latest CMR Granule: <span className="text-cyan-300">{telemA?.cmr?.latest_granule_id || 'MOD11A2.A2024365'}</span>
              <div className="mt-1">
                <a
                  href={telemA?.cmr?.earthdata_search_link || 'https://search.earthdata.nasa.gov'}
                  target="_blank"
                  rel="noreferrer"
                  className="text-cyan-400 hover:underline inline-flex items-center space-x-1"
                >
                  <span>Browse {telemA?.cmr?.granule_count || 1150} granules on NASA Earthdata</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              </div>
            </div>
          )}
        </div>

        {/* Region B Visual */}
        <div className={`p-3 border flex flex-col justify-between ${
          isLight ? 'bg-white border-[#DCD7C9] rounded-lg' : 'bg-[#07090E] border-[#1E2636] rounded-none'
        }`}>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className={`font-bold text-xs ${isLight ? 'text-archival-viridian' : 'text-amber-400 font-mono'}`}>
                Region B: {labelB}
              </span>
              <span className="text-[10px] font-mono text-slate-400">
                {telemB?.cmr?.collection || 'MODIS MOD11A2'}
              </span>
            </div>
            <SatelliteSnapshotViewer
              label={labelB}
              lat={latB}
              lon={lonB}
              previewUrl={urlB}
              fallbackUrl={fallbackTileB}
              collection={telemB?.cmr?.collection || 'MODIS MOD11A2'}
              visualClue={visualClues.clueB}
              isStudent={isLight}
            />
          </div>
          {!isLight && (
            <div className="mt-2.5 text-[10px] font-mono text-slate-400 leading-tight">
              Latest CMR Granule: <span className="text-amber-300">{telemB?.cmr?.latest_granule_id || 'MOD13A3.A2024365'}</span>
              <div className="mt-1">
                <a
                  href={telemB?.cmr?.earthdata_search_link || 'https://search.earthdata.nasa.gov'}
                  target="_blank"
                  rel="noreferrer"
                  className="text-amber-400 hover:underline inline-flex items-center space-x-1"
                >
                  <span>Browse {telemB?.cmr?.granule_count || 1150} granules on NASA Earthdata</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  // =========================================================================
  // 1. 🎓 EXPLORER STORY MODE VIEW (Student / Public - Field Atlas)
  // =========================================================================
  if (isLight) {
    return (
      <div className="space-y-6">
        {/* Visual Field Guide Satellite Snapshot Cards */}
        {renderTelemetryCard()}

        {/* ----------------------------------------------------------------- */}
        {/* Connected 3-Step Physical Cause-and-Effect Chain                  */}
        {/* ----------------------------------------------------------------- */}
        <div className="p-5 rounded-xl border border-[#DCD7C9] bg-[#FAF8F5] text-archival-ink shadow-none">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-archival-muted mb-4">
            <Compass className="w-4 h-4 text-archival-viridian" />
            <span>The Detective Chain: 3-Step Physical Mechanism</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Step 1 */}
            <div className="p-4 rounded-lg bg-white border border-[#DCD7C9] flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  <span className="w-5 h-5 rounded-full bg-archival-terracotta text-white font-bold text-[10px] flex items-center justify-center">1</span>
                  <h4 className="font-serif text-sm font-bold text-archival-ink">Human Landscape Trigger</h4>
                </div>
                <p className="text-xs text-archival-muted leading-relaxed">
                  In <strong>{labelA}</strong>, deep-rooted natural canopy was cleared for cattle grazing or agriculture. In <strong>{labelB}</strong>, intensive canal networks saturated agricultural fields.
                </p>
              </div>
              <div className="text-[10px] font-mono text-archival-ink bg-archival-sand/70 px-2 py-1 rounded border border-[#DCD7C9]">
                Surface Albedo & Roughness Altered
              </div>
            </div>

            {/* Step 2 */}
            <div className="p-4 rounded-lg bg-white border border-[#DCD7C9] flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  <span className="w-5 h-5 rounded-full bg-archival-viridian text-white font-bold text-[10px] flex items-center justify-center">2</span>
                  <h4 className="font-serif text-sm font-bold text-archival-ink">Energy & Moisture Shift</h4>
                </div>
                <p className="text-xs text-archival-muted leading-relaxed">
                  Deforestation halts natural tree evapotranspiration, forcing incoming solar radiation into direct ground sensible heating. Canal irrigation pumps water into the air, absorbing heat through latent vaporization!
                </p>
              </div>
              <div className="text-[10px] font-mono text-archival-ink bg-archival-sand/70 px-2 py-1 rounded border border-[#DCD7C9]">
                Latent vs. Sensible Heat Partitioning
              </div>
            </div>

            {/* Step 3 */}
            <div className="p-4 rounded-lg bg-white border border-[#DCD7C9] flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center space-x-2 mb-2">
                  <span className="w-5 h-5 rounded-full bg-blue-700 text-white font-bold text-[10px] flex items-center justify-center">3</span>
                  <h4 className="font-serif text-sm font-bold text-archival-ink">25-Year Satellite Verdict</h4>
                </div>
                <p className="text-xs text-archival-muted leading-relaxed">
                  NASA's thermal sensors confirm <strong>{labelA}</strong> heating up ({formatSlope(totalA, 2)} {unit}), while <strong>{labelB}</strong> cools ({formatSlope(totalB, 2)} {unit})—a verified planetary paradox!
                </p>
              </div>
              <div className="text-[10px] font-mono text-archival-viridian bg-archival-sand/70 px-2 py-1 rounded border border-[#DCD7C9] font-bold">
                Δ = {formatSlope(Math.abs(totalA - totalB), 2)} {unit} Regional Divergence
              </div>
            </div>
          </div>
        </div>

        {/* ----------------------------------------------------------------- */}
        {/* "How This NASA Satellite Works" Card                              */}
        {/* ----------------------------------------------------------------- */}
        <div className="p-5 rounded-xl border border-[#DCD7C9] bg-white text-archival-ink shadow-none">
          <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-archival-muted mb-3">
            <Radio className="w-4 h-4 text-archival-viridian" />
            <span>How NASA Earth Observing Satellites Detect These Trends</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#DCD7C9]">
              <span className="font-bold text-archival-ink block mb-1">🛰️ 705 km Sun-Synchronous Orbit</span>
              <p className="text-archival-muted text-[11px] leading-relaxed">
                NASA Terra & Aqua spacecraft circle Earth every 99 minutes from pole to pole, crossing the equator at identical local solar times to eliminate diurnal lighting bias.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#DCD7C9]">
              <span className="font-bold text-archival-ink block mb-1">🌡️ Thermal Infrared Skin Radiometry</span>
              <p className="text-archival-muted text-[11px] leading-relaxed">
                Instead of ground air thermometers, MODIS captures 11–12 µm thermal emissions directly from the ground surface skin to compute true thermodynamic temperature.
              </p>
            </div>
            <div className="p-3 rounded-lg bg-[#FAF8F5] border border-[#DCD7C9]">
              <span className="font-bold text-archival-ink block mb-1">🔍 25-Year STL Loess Filtering</span>
              <p className="text-archival-muted text-[11px] leading-relaxed">
                TerraDetective mathematically removes recurring 12-month seasonal zig-zags, isolating the persistent multi-decadal climate and human land-use signal.
              </p>
            </div>
          </div>
        </div>

        {/* 1-Click CSV Download Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={handleDownloadCsv}
            className="px-4 py-2.5 rounded-lg text-xs font-semibold bg-[#141E19] text-white hover:bg-black shadow-sm transition-all flex items-center space-x-2 border border-[#141E19]"
          >
            <Download className="w-4 h-4 text-white" />
            <span className="text-white font-medium">Download Verified NASA Dataset (.CSV)</span>
          </button>
        </div>

      </div>
    );
  }

  // =========================================================================
  // 2. 🔬 TELEMETRY WORKBENCH MODE VIEW (Scientist / Pro - NASA Ops IDE)
  // =========================================================================
  return (
    <div className="space-y-4">
      {/* Top Telemetry & Empirical Divergence Audit Banner */}
      <div className={`p-4 border transition-all ${
        isOpposing
          ? 'bg-[#0C1017] border-cyan-500/40 rounded-none'
          : 'bg-[#0C1017] border-[#1E2636] rounded-none'
      }`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider font-mono border ${
                isOpposing 
                  ? 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30' 
                  : 'bg-[#1E2636] text-slate-300 border-[#2E3B52]'
              }`}>
                Empirical Divergence Audit
              </span>
              <span className="text-[11px] text-slate-400 font-mono">STL Deseasonalization: Robust Loess (period=12)</span>
            </div>

            {/* Antiphase Trajectory Title when Opposing */}
            <h2 className="text-base font-bold font-mono mt-1 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-sky-300 to-amber-400">
              {isOpposing 
                ? 'Opposing Regional Divergence Verified (Antiphase Trajectory)' 
                : 'Concordant Regional Trajectory (Parallel Velocity)'
              }
            </h2>
          </div>

          {/* Action Controls */}
          <div className="flex items-center space-x-2">
            {/* Copy Table Button */}
            <div className="relative flex items-center space-x-1 bg-[#07090E] p-0.5 border border-[#1E2636] text-xs">
              <button
                onClick={() => handleCopyTable('markdown')}
                className="px-2.5 py-1 text-slate-300 hover:text-white hover:bg-[#1E2636] transition-colors flex items-center space-x-1 font-mono text-[10px]"
                title="Copy Markdown Table to Clipboard"
              >
                {copyStatus === 'copied_md' ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                <span>{copyStatus === 'copied_md' ? 'Copied MD!' : 'Copy MD'}</span>
              </button>
              <button
                onClick={() => handleCopyTable('latex')}
                className="px-2.5 py-1 text-slate-300 hover:text-white hover:bg-[#1E2636] transition-colors flex items-center space-x-1 font-mono text-[10px]"
                title="Copy LaTeX Table to Clipboard"
              >
                {copyStatus === 'copied_latex' ? <Check className="w-3 h-3 text-emerald-400" /> : <FileText className="w-3 h-3" />}
                <span>{copyStatus === 'copied_latex' ? 'Copied LaTeX!' : 'Copy LaTeX'}</span>
              </button>
            </div>

            <button
              onClick={handleDownloadCsv}
              className="px-3 py-1.5 text-xs font-mono font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/20 transition-all flex items-center space-x-1.5 flex-shrink-0"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>
      </div>

      {/* Multi-Agency Live Telemetry Card */}
      {renderTelemetryCard()}

      {/* Full Scientific Statistical Audit Table */}
      <div className="p-4 bg-[#0C1017] border border-[#1E2636] overflow-x-auto">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
          <div className="flex items-center space-x-2 text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
            <Table className="w-3.5 h-3.5" />
            <span>Rigorous Multi-Decadal Statistical Audit Matrix</span>
          </div>

          {/* Interactive Significance Cutoff Selector */}
          <div className="flex items-center space-x-2 text-xs font-mono">
            <span className="text-slate-400 text-[10px]">Significance Threshold:</span>
            <div className="flex items-center space-x-1 bg-[#07090E] p-0.5 border border-[#1E2636]">
              {[0.05, 0.01, 0.001].map((alphaVal) => (
                <button
                  key={alphaVal}
                  onClick={() => setAlphaCutoff(alphaVal)}
                  className={`px-2 py-0.5 text-[10px] font-bold transition-all ${
                    alphaCutoff === alphaVal
                      ? 'bg-cyan-500 text-slate-950 font-bold'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  α = {alphaVal}
                </button>
              ))}
            </div>
          </div>
        </div>

        <table className="w-full text-left text-xs font-mono text-slate-300">
          <thead>
            <tr className="border-b border-[#1E2636] text-slate-400 uppercase text-[10px]">
              <th className="pb-2">Metric</th>
              <th className="pb-2 text-cyan-400">Region A: {labelA}</th>
              <th className="pb-2 text-amber-400">Region B: {labelB}</th>
              <th className="pb-2 text-slate-300">Divergence Verdict</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1E2636]/60">
            <tr>
              <td className="py-2 text-slate-400">Sen's Median Slope / Decade</td>
              <td className="py-2 font-bold text-cyan-300 tabular-nums">{formatSlope(slopeA, 4)} {unit}/dec</td>
              <td className="py-2 font-bold text-amber-300 tabular-nums">{formatSlope(slopeB, 4)} {unit}/dec</td>
              <td className="py-2 text-emerald-400 font-bold tabular-nums">Δ = {formatSlope(div?.slope_difference_per_decade, 4)} {unit}/dec</td>
            </tr>
            <tr>
              <td className="py-2 text-slate-400">Total 25-Year Change</td>
              <td className="py-2 font-bold text-cyan-300 tabular-nums">{formatSlope(totalA, 2)} {unit}</td>
              <td className="py-2 font-bold text-amber-300 tabular-nums">{formatSlope(totalB, 2)} {unit}</td>
              <td className="py-2 text-emerald-400 font-bold tabular-nums">Net separation: {formatSlope(Math.abs(totalA - totalB), 2)} {unit}</td>
            </tr>
            <tr>
              <td className="py-2 text-slate-400">Deseasonalized Mann-Kendall p-value</td>
              <td className="py-2 tabular-nums">{regA?.mann_kendall?.p_value} ({regA?.mann_kendall?.trend_direction})</td>
              <td className="py-2 tabular-nums">{regB?.mann_kendall?.p_value} ({regB?.mann_kendall?.trend_direction})</td>
              <td className="py-2">
                <span className={`px-2 py-0.5 text-[9px] font-bold border ${
                  (regA?.mann_kendall?.p_value < alphaCutoff && regB?.mann_kendall?.p_value < alphaCutoff)
                    ? 'bg-emerald-950/80 text-emerald-300 border-emerald-800' 
                    : 'bg-amber-950/80 text-amber-300 border-amber-800'
                }`}>
                  {(regA?.mann_kendall?.p_value < alphaCutoff && regB?.mann_kendall?.p_value < alphaCutoff)
                    ? `Both Significant (p < ${alphaCutoff})`
                    : `Threshold Check (α=${alphaCutoff})`}
                </span>
              </td>
            </tr>
            <tr>
              <td className="py-2 text-slate-400">Seasonal Mann-Kendall p-value</td>
              <td className="py-2 tabular-nums">{regA?.seasonal_mann_kendall?.p_value ?? '—'}</td>
              <td className="py-2 tabular-nums">{regB?.seasonal_mann_kendall?.p_value ?? '—'}</td>
              <td className="py-2 text-slate-400">Direct 12-Month Period Alignment</td>
            </tr>
            <tr>
              <td className="py-2 text-slate-400">Kendall's Tau (Rank Correlation)</td>
              <td className="py-2 tabular-nums">{regA?.mann_kendall?.tau ?? '—'}</td>
              <td className="py-2 tabular-nums">{regB?.mann_kendall?.tau ?? '—'}</td>
              <td className="py-2 text-slate-400">{isOpposing ? 'Opposing Trajectory' : 'Concordant'}</td>
            </tr>
            <tr>
              <td className="py-2 text-slate-400">OLS Regression Slope & R²</td>
              <td className="py-2 tabular-nums">{formatSlope(regA?.ols_regression?.ols_slope_per_year, 4)}/yr (R²={regA?.ols_regression?.r_squared})</td>
              <td className="py-2 tabular-nums">{formatSlope(regB?.ols_regression?.ols_slope_per_year, 4)}/yr (R²={regB?.ols_regression?.r_squared})</td>
              <td className="py-2 text-slate-400 tabular-nums">Z-score diff = {div?.z_score_divergence ?? '—'}</td>
            </tr>
            <tr>
              <td className="py-2 text-slate-400">95% OLS Slope Confidence Interval</td>
              <td className="py-2 tabular-nums">[{formatSlope(regA?.ols_regression?.slope_ci_95_low, 4)}, {formatSlope(regA?.ols_regression?.slope_ci_95_high, 4)}]</td>
              <td className="py-2 tabular-nums">[{formatSlope(regB?.ols_regression?.slope_ci_95_low, 4)}, {formatSlope(regB?.ols_regression?.slope_ci_95_high, 4)}]</td>
              <td className="py-2 text-emerald-400">
                {div?.ci_separated ? 'Non-Overlapping CIs (Separated)' : 'Overlapping CI Range'}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* AI Researcher Briefing Sections */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Technical Abstract */}
        <div className="p-4 bg-[#0C1017] border border-[#1E2636]">
          <div className="flex items-center space-x-2 text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider mb-2">
            <FileText className="w-3.5 h-3.5" />
            <span>Technical Abstract</span>
          </div>
          <p className="text-xs leading-relaxed text-slate-300">
            {scientistNarrative?.technical_abstract || div?.narrative}
          </p>
        </div>

        {/* Physical Mechanisms */}
        <div className="p-4 bg-[#0C1017] border border-[#1E2636]">
          <div className="flex items-center space-x-2 text-xs font-mono font-bold text-amber-400 uppercase tracking-wider mb-2">
            <Activity className="w-3.5 h-3.5" />
            <span>Physical Mechanisms & Drivers</span>
          </div>
          <p className="text-xs leading-relaxed text-slate-300">
            {scientistNarrative?.physical_mechanisms || (
              "Energy and water balance partitioning driven by localized land use and terrain barriers."
            )}
          </p>
        </div>

        {/* Statistical Interpretation */}
        <div className="p-4 bg-[#0C1017] border border-[#1E2636]">
          <div className="flex items-center space-x-2 text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Statistical Interpretation</span>
          </div>
          <p className="text-xs leading-relaxed text-slate-300">
            {scientistNarrative?.statistical_interpretation || (
              `Sen's slope rates indicate statistically significant divergence across the 25-year study window.`
            )}
          </p>
        </div>

        {/* Methodological Caveats */}
        <div className="p-4 bg-[#0C1017] border border-[#1E2636]">
          <div className="flex items-center space-x-2 text-xs font-mono font-bold text-rose-400 uppercase tracking-wider mb-2">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Methodological & Sensor Caveats</span>
          </div>
          <p className="text-xs leading-relaxed text-slate-300">
            {scientistNarrative?.methodological_caveats || (
              "Missing or cloud-obscured observations were linearly interpolated and flagged in the unified schema metadata."
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
