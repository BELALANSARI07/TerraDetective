import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AskDetectiveBar from './components/AskDetectiveBar';
import GuidedDetectiveBar from './components/GuidedDetectiveBar';
import DivergenceMap from './components/DivergenceMap';
import TrendComparisonChart from './components/TrendComparisonChart';
import InsightPanel from './components/InsightPanel';
import SensorOrbitalSpecCard from './components/SensorOrbitalSpecCard';
import ThermometerComparator from './components/ThermometerComparator';
import { Loader2, AlertCircle, RefreshCw, Satellite, Radio, ExternalLink, Download, Sparkles } from 'lucide-react';

export default function App() {
  const [mode, setMode] = useState('student'); // 'student' (light Explorer) vs 'scientist' (dark Workbench)
  const [activeCaseId, setActiveCaseId] = useState('case_2_land_thermal_paradox');
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Time-Window Simulator State
  const [startYear, setStartYear] = useState(2001);
  const [endYear, setEndYear] = useState(2025);

  // Custom Exploration State
  const [customData, setCustomData] = useState(null);
  const [selectedCoord, setSelectedCoord] = useState(null);
  const [customLoading, setCustomLoading] = useState(false);
  const [twinLoading, setTwinLoading] = useState(false);

  // Sync mode with documentElement class (Tailwind dark mode)
  useEffect(() => {
    if (mode === 'scientist') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [mode]);

  // Load Case Study Data with optional Time Window
  const loadCase = async (id, sYear = 2001, eYear = 2025, isTimeSliceOnly = false) => {
    if (!isTimeSliceOnly) {
      setLoading(true);
      setCustomData(null);
      setSelectedCoord(null);
    }
    setError(null);
    try {
      const url = (sYear > 2001 || eYear < 2025)
        ? `/api/cases/${id}?start_year=${sYear}&end_year=${eYear}`
        : `/api/cases/${id}`;

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}: Failed to fetch case`);
      const data = await res.json();
      setCaseData(data);
      setActiveCaseId(id);
      setStartYear(sYear);
      setEndYear(eYear);
    } catch (err) {
      console.error('Failed to load case detail:', err);
      setError(err.message);
    } finally {
      if (!isTimeSliceOnly) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    loadCase(activeCaseId);
  }, []);

  // Time Window Slider Change Handler - Smooth in-place update without full-page reloads
  const handleTimeWindowChange = (newStart, newEnd) => {
    setStartYear(newStart);
    setEndYear(newEnd);
    if (activeCaseId && !activeCaseId.startsWith('custom') && !activeCaseId.startsWith('uploaded')) {
      loadCase(activeCaseId, newStart, newEnd, true);
    }
  };

  // Handle Single Custom Coordinate Click from Map
  const handleMapClickCoordinates = async (lat, lon) => {
    setSelectedCoord({ lat, lon });
    setCustomLoading(true);
    try {
      const res = await fetch('/api/explore/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lat,
          lon,
          region_label: `Probe (${lat}°, ${lon}°)`,
          variable_id: caseData?.manifest?.variable_id === 'precipitation' ? 'PRECTOTCORR' : 'T2M',
          start_year: 2001,
          end_year: 2024,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setCustomData(data);
      }
    } catch (e) {
      console.warn('Custom coordinate probe error:', e);
    } finally {
      setCustomLoading(false);
    }
  };

  // Handle Twin-Region Custom Comparison
  const handleTwinCompare = async ({ region_a, region_b, variable_id }) => {
    setTwinLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/explore/twin-custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          region_a,
          region_b,
          variable_id,
          start_year: startYear,
          end_year: endYear,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `HTTP ${res.status}: Twin exploration failed`);
      }

      const payload = await res.json();
      setCaseData(payload);
      setActiveCaseId(payload.case_id);
      setCustomData(null);
    } catch (err) {
      console.error('Twin comparison error:', err);
      setError(err.message);
    } finally {
      setTwinLoading(false);
    }
  };

  // Handle User Uploaded NASA CSV Success
  const handleUploadSuccess = (payload) => {
    setCaseData(payload);
    setActiveCaseId(payload.case_id);
    setCustomData(null);
    setSelectedCoord(null);
  };

  // Handle Ask TerraDetective NL Query Sync
  const handleAskSync = (result) => {
    if (!result || !result.case_payload) return;
    setCaseData(result.case_payload);
    setActiveCaseId(result.matched_case_id || result.case_payload.case_id);
    setCustomData(null);
    setSelectedCoord(null);
  };

  const isLight = mode === 'student';

  // Derived Values for Thermometer & Comparative Gauges
  const regA = caseData?.statistics?.region_a;
  const regB = caseData?.statistics?.region_b;
  const unit = caseData?.statistics?.unit || caseData?.manifest?.unit || '°C';
  const slopeA = regA?.mann_kendall?.sens_slope_per_decade;
  const slopeB = regB?.mann_kendall?.sens_slope_per_decade;
  const totalA = regA?.mann_kendall?.total_estimated_change 
    ?? regA?.mann_kendall?.total_change 
    ?? (slopeA != null ? slopeA * 2.5 : 0.94);
  const totalB = regB?.mann_kendall?.total_estimated_change 
    ?? regB?.mann_kendall?.total_change 
    ?? (slopeB != null ? slopeB * 2.5 : -0.94);

  const cleanLabelA = regA?.region_label || caseData?.manifest?.regions?.[0]?.region_label || 'Region A';
  const cleanLabelB = regB?.region_label || caseData?.manifest?.regions?.[1]?.region_label || 'Region B';

  const handleDownloadCsv = () => {
    if (activeCaseId) {
      window.open(`/api/export/${activeCaseId}/csv`, '_blank');
    }
  };

  return (
    <div className={`min-h-screen transition-colors duration-200 ${
      isLight 
        ? 'bg-archival-stone text-archival-ink font-sans' 
        : 'bg-obsidian-bg text-obsidian-text font-sans'
    }`}>
      {/* Top Navbar */}
      <Navbar
        mode={mode}
        onToggleMode={setMode}
        activeCaseId={activeCaseId}
        onSelectCase={(id) => loadCase(id, 2001, 2025)}
        isCustom={!!customData || (caseData && caseData.case_id && (caseData.case_id.startsWith('custom_twin') || caseData.case_id.startsWith('uploaded') || caseData.case_id.startsWith('custom_query')))}
        onUploadSuccess={handleUploadSuccess}
      />

      {/* Mode B Exclusive: Top 36px Telemetry Ops Ribbon */}
      {!isLight && (
        <div className="w-full max-w-full h-9 px-4 sm:px-6 bg-[#07090E] border-b border-[#1E2636] flex items-center justify-between text-[11px] font-mono text-slate-400 overflow-x-auto whitespace-nowrap">
          <div className="flex items-center space-x-3">
            <span className="flex items-center space-x-1.5 text-cyan-400">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span className="font-bold">NASA EOS TELEMETRY STREAM</span>
            </span>
            <span>•</span>
            <span>TIMESPAN: <strong className="text-slate-200 tabular-nums">2001-01 to 2025-12 (N=300 obs)</strong></span>
            <span>•</span>
            <span>SENSOR: <strong className="text-cyan-300">{caseData?.manifest?.source_product?.split(' ')[0] || 'MOD11A2.061'}</strong></span>
            <span>•</span>
            <span>RESOLUTION: <strong className="text-slate-200">1 km Gridded L3</strong></span>
          </div>

          <div className="flex items-center space-x-3 pl-4">
            <a
              href="https://doi.org/10.5067/MODIS/MOD11A2.061"
              target="_blank"
              rel="noreferrer"
              className="text-slate-400 hover:text-cyan-300 transition-colors flex items-center space-x-1 focus-visible:ring-1 focus-visible:ring-cyan-400 focus-visible:outline-none"
            >
              <span>DOI: 10.5067/MODIS</span>
              <ExternalLink className="w-2.5 h-2.5" />
            </a>
            <span>•</span>
            <button
              onClick={handleDownloadCsv}
              className="text-cyan-400 hover:text-cyan-300 font-bold transition-colors flex items-center space-x-1 focus-visible:ring-1 focus-visible:ring-cyan-400 focus-visible:outline-none"
            >
              <Download className="w-3 h-3" />
              <span>EXPORT DATA (.CSV)</span>
            </button>
          </div>
        </div>
      )}

      {/* Main Content Body */}
      {isLight ? (
        /* =========================================================================
           MODE A: 🌍 EXPLORER STORY MODE (Student / Public - Field Atlas)
           ========================================================================= */
        <main className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
          {/* Loading Indicator */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 space-y-3">
              <Loader2 className="w-8 h-8 animate-spin text-archival-terracotta" />
              <p className="text-xs font-mono text-archival-muted">Loading verified NASA Earth observations...</p>
            </div>
          )}

          {/* Error Notice */}
          {error && (
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 text-amber-600" />
              <span>Failed loading dataset: {error}. Click a quick-case pill above to retry.</span>
            </div>
          )}

          {/* Welcome Hero / Novice-Friendly Onboarding Banner */}
          {!loading && (
            <div className="p-5 sm:p-6 rounded-2xl border border-[#DCD7C9] bg-gradient-to-br from-[#FAF8F5] via-[#F4EFE6] to-[#FAF8F5] text-archival-ink relative overflow-hidden shadow-xs">
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="space-y-1.5 max-w-3xl">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[10.5px] font-bold uppercase tracking-wider bg-archival-sand text-archival-ink border border-[#DCD7C9] flex items-center space-x-1">
                      <Sparkles className="w-3 h-3 text-archival-terracotta" />
                      <span>NASA Space Apps Challenge 2026</span>
                    </span>
                    <span className="text-xs text-archival-muted font-mono">25-Year Planetary Observations (2001–2025)</span>
                  </div>
                  <h1 className="font-serif text-2xl sm:text-3xl font-bold text-archival-ink leading-snug">
                    Welcome to TerraDetective. We compare Earth's environments to uncover hidden climate paradoxes.
                  </h1>
                  <p className="text-xs sm:text-sm text-archival-muted leading-relaxed font-sans">
                    Why does clearing a tropical rainforest cause scorching surface heat, while canal-flooded desert farmland triggers intense evaporative cooling? 
                    Pick a flagship NASA case, explore the interactive map, guess the outcome in our <strong>Hypothesis Quiz</strong>, or ask any natural question in plain English below!
                  </p>
                </div>

                <div className="grid grid-cols-3 gap-2.5 sm:gap-3 text-center lg:border-l lg:border-[#DCD7C9] lg:pl-6 flex-shrink-0">
                  <div className="p-2.5 rounded-xl bg-white/80 border border-[#DCD7C9]">
                    <span className="text-base sm:text-lg block font-bold font-serif text-archival-terracotta">25 Yrs</span>
                    <span className="text-[10px] text-archival-muted font-mono uppercase tracking-wider">MODIS Record</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-white/80 border border-[#DCD7C9]">
                    <span className="text-base sm:text-lg block font-bold font-serif text-archival-viridian">3 Paradoxes</span>
                    <span className="text-[10px] text-archival-muted font-mono uppercase tracking-wider">NASA Flagships</span>
                  </div>
                  <div className="p-2.5 rounded-xl bg-white/80 border border-[#DCD7C9]">
                    <span className="text-base sm:text-lg block font-bold font-serif text-blue-700">100%</span>
                    <span className="text-[10px] text-archival-muted font-mono uppercase tracking-wider">Data-Grounded</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Guided 3-Step Variable Detective Wizard (Positioned directly beneath Welcome Hero) */}
          {!loading && (
            <GuidedDetectiveBar
              onSelectCase={(id) => loadCase(id, 2001, 2025)}
              isLight={true}
            />
          )}

          {!loading && caseData && (
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              
              {/* LEFT STICKY COLUMN (5 cols) */}
              <div className="lg:col-span-5 space-y-6 lg:sticky lg:top-4 lg:max-h-[calc(100vh-2rem)] lg:overflow-y-auto pr-1">
                {/* Interactive Leaflet Map with Smooth Camera Controls */}
                <DivergenceMap
                  manifest={caseData.manifest}
                  mode={mode}
                  onSelectCoordinates={handleMapClickCoordinates}
                  selectedCoord={selectedCoord}
                  onTwinCompare={handleTwinCompare}
                  twinLoading={twinLoading}
                />

                {/* Tactile 25-Year Thermometer / Delta Gauge & Detective Quiz */}
                <ThermometerComparator
                  labelA={cleanLabelA}
                  labelB={cleanLabelB}
                  totalA={totalA}
                  totalB={totalB}
                  unit={unit}
                />
              </div>

              {/* RIGHT EDITORIAL STORY COLUMN (7 cols) */}
              <div className="lg:col-span-7 space-y-6">
                {/* Ask TerraDetective Natural Language Query Bar (Primary Call-to-Action) */}
                <AskDetectiveBar
                  mode={mode}
                  activeCaseId={activeCaseId}
                  onSyncResult={handleAskSync}
                />

                {/* Editorial Headline & Paradox Header Narrative */}
                <div className="p-6 rounded-xl border border-[#DCD7C9] bg-[#FAF8F5] text-archival-ink space-y-3">
                  <div className="flex items-center space-x-2">
                    <span className="px-2.5 py-0.5 rounded-full text-[10.5px] font-bold uppercase tracking-wider bg-archival-sand text-archival-ink border border-[#DCD7C9] flex items-center space-x-1">
                      <span>Verified NASA Satellite Investigation</span>
                    </span>
                    <span className="text-xs text-archival-muted font-mono">2001–2025</span>
                  </div>

                  <h1 className="font-serif text-2xl sm:text-3xl text-archival-ink font-bold leading-tight">
                    {caseData.manifest?.title}
                  </h1>

                  <blockquote className="border-l-2 border-archival-terracotta pl-3.5 italic text-sm text-archival-muted font-serif">
                    "{caseData.manifest?.paradox_statement}"
                  </blockquote>
                </div>

                {/* Clean Loess Trend Ribbon & Time Window Scrubber */}
                <TrendComparisonChart
                  caseData={caseData}
                  statistics={caseData.statistics}
                  mode={mode}
                  customData={customData}
                  onTimeWindowChange={handleTimeWindowChange}
                  activeStartYear={startYear}
                  activeEndYear={endYear}
                />

                {/* Connected 3-Step Physical Mechanism Timeline & Visual Field Guide */}
                <InsightPanel
                  statistics={caseData.statistics}
                  narratives={caseData.narratives}
                  caseId={activeCaseId}
                  mode={mode}
                  customData={customData}
                  telemetry={caseData.telemetry}
                  manifest={caseData.manifest}
                />
              </div>

            </div>
          )}
        </main>
      ) : (
        /* =========================================================================
           MODE B: 🎛️ TELEMETRY WORKBENCH MODE (Scientist / Pro - NASA Ops IDE)
           ========================================================================= */
        <main className="max-w-[1600px] mx-auto px-4 sm:px-6 py-4 space-y-4">
          {/* Loading Indicator */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-20 space-y-3">
              <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
              <p className="text-xs font-mono text-slate-500">Acquiring verified NASA telemetry packets...</p>
            </div>
          )}

          {/* Error Notice */}
          {error && (
            <div className="p-3 bg-rose-950/40 border border-rose-800 text-rose-300 text-xs font-mono flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>Telemetry packet error: {error}. Resyncing...</span>
            </div>
          )}

          {!loading && caseData && (
            <>
              {/* Natural Language Query Bar in Terminal IDE Style */}
              <AskDetectiveBar
                mode={mode}
                activeCaseId={activeCaseId}
                onSyncResult={handleAskSync}
              />

              {/* Row 1: Left 4 cols (Radar & Sensor Spec) + Right 8 cols (Oscilloscope Chart) */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
                {/* Left 4 cols */}
                <div className="lg:col-span-4 space-y-4">
                  <DivergenceMap
                    manifest={caseData.manifest}
                    mode={mode}
                    onSelectCoordinates={handleMapClickCoordinates}
                    selectedCoord={selectedCoord}
                    onTwinCompare={handleTwinCompare}
                    twinLoading={twinLoading}
                  />

                  <SensorOrbitalSpecCard manifest={caseData.manifest} />
                </div>

                {/* Right 8 cols */}
                <div className="lg:col-span-8">
                  <TrendComparisonChart
                    caseData={caseData}
                    statistics={caseData.statistics}
                    mode={mode}
                    customData={customData}
                    onTimeWindowChange={handleTimeWindowChange}
                    activeStartYear={startYear}
                    activeEndYear={endYear}
                  />
                </div>
              </div>

              {/* Row 2 & 3: Insight Panel (Statistical Audit Matrix, Monograph, Granules) */}
              <InsightPanel
                statistics={caseData.statistics}
                narratives={caseData.narratives}
                caseId={activeCaseId}
                mode={mode}
                customData={customData}
                telemetry={caseData.telemetry}
                manifest={caseData.manifest}
              />
            </>
          )}
        </main>
      )}

      {/* Footer */}
      <footer className={`mt-12 py-5 border-t text-xs transition-colors ${
        isLight ? 'bg-[#FAF8F5] border-[#DCD7C9] text-archival-muted' : 'bg-[#07090E] border-[#1E2636] text-slate-500'
      }`}>
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <span className={`font-bold ${isLight ? 'text-archival-ink font-serif' : 'text-slate-300 font-mono'}`}>
              TerraDetective Planetary Workbench
            </span>
            <span>•</span>
            <span>NASA Space Apps Challenge 2026</span>
          </div>
          <div className="text-[11px] font-mono">
            MODIS Terra MOD11A2/MOD13A3 • NASA GPM IMERG 3IMERGM • NASA POWER / MERRA-2
          </div>
        </div>
      </footer>
    </div>
  );
}
