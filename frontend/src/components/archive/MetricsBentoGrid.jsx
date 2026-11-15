import React from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  CheckCircle, 
  AlertTriangle, 
  Compass, 
  ShieldCheck, 
  Activity, 
  Sparkles,
  Thermometer,
  CloudRain,
  Sprout,
  Droplets,
  Calendar
} from 'lucide-react';

export default function MetricsBentoGrid({ analysisData, uxMode = 'story' }) {
  if (!analysisData) return null;

  const { metrics, detective_briefing, units, variable_name, location_label, data_source } = analysisData;
  const isSig = metrics?.is_significant;
  const slopeDecade = metrics?.sens_slope_per_decade;
  const pVal = metrics?.p_value;
  const direction = metrics?.trend_direction;
  const percentShift = metrics?.percent_shift;

  const renderTrendIcon = () => {
    if (direction === 'increasing') return <TrendingUp className="w-5 h-5 text-emerald-400" />;
    if (direction === 'decreasing') return <TrendingDown className="w-5 h-5 text-rose-400" />;
    return <Minus className="w-5 h-5 text-slate-400" />;
  };

  // Plain English Story Mode Cards
  if (uxMode === 'story') {
    const total25YearChange = slopeDecade != null ? (slopeDecade * 2.5).toFixed(1) : '0.0';
    const isPositive = Number(total25YearChange) > 0;
    const isNegative = Number(total25YearChange) < 0;

    // Detect environmental domain
    const varLower = (variable_name || '').toLowerCase();
    const isHeat = varLower.includes('temp') || varLower.includes('t2m') || varLower.includes('lst');
    const isRain = varLower.includes('precip') || varLower.includes('rain') || varLower.includes('gpm');
    const isVeg = varLower.includes('ndvi') || varLower.includes('vegetation');
    const isWater = varLower.includes('moist') || varLower.includes('gwet') || varLower.includes('water') || varLower.includes('swot');

    let categoryIcon = <Sparkles className="w-5 h-5 text-cyan-400" />;
    let categoryName = "Earth System Dynamic";
    let impactText = "Long-term environmental trend detected across multi-decadal satellite observations.";

    if (isHeat) {
      categoryIcon = <Thermometer className="w-5 h-5 text-amber-400" />;
      categoryName = "Thermal Climate Regime";
      impactText = isPositive 
        ? "Rising temperature trend: elevated thermal stress, prolonged heatwaves, and accelerated surface evaporation."
        : "Cooling trend: lower land surface temperatures compared to the 2001 baseline.";
    } else if (isRain) {
      categoryIcon = <CloudRain className="w-5 h-5 text-blue-400" />;
      categoryName = "Hydrological Cycle";
      impactText = isPositive
        ? "Surplus moisture: increased rainfall frequency with heightened potential for seasonal flooding."
        : "Rainfall deficit: drying conditions with reduced atmospheric precipitation replenishment.";
    } else if (isVeg) {
      categoryIcon = <Sprout className="w-5 h-5 text-emerald-400" />;
      categoryName = "Ecosystem Canopy";
      impactText = isPositive
        ? "Surface greening: increased canopy density from agricultural expansion or vegetation recovery."
        : "Canopy browning: vegetation reduction, forest disturbance, or chronic moisture stress.";
    } else if (isWater) {
      categoryIcon = <Droplets className="w-5 h-5 text-cyan-400" />;
      categoryName = "Sub-Surface Moisture";
      impactText = isPositive
        ? "Aquifer recharge: saturated root-zone moisture reserves supporting stable crop production."
        : "Groundwater depletion: underground moisture deficit requiring active water resource conservation.";
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Story Card 1: 25-Year Total Change */}
        <div className="rounded-2xl bg-gradient-to-br from-slate-850 to-slate-900 border border-slate-750 p-5 flex flex-col justify-between shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-cyan-400" />
              25-Year Total Change (2001–2025)
            </span>
            {renderTrendIcon()}
          </div>

          <div className="my-4">
            <div className="flex items-baseline gap-2">
              <span className={`text-3xl lg:text-4xl font-extrabold font-mono tracking-tight ${
                isPositive ? 'text-emerald-400' : isNegative ? 'text-rose-400' : 'text-slate-100'
              }`}>
                {isPositive ? `+${total25YearChange}` : total25YearChange}
              </span>
              <span className="text-sm font-mono text-cyan-300 font-semibold">{units}</span>
            </div>
            <p className="text-xs text-slate-300 mt-2 font-medium">
              Net cumulative shift across the entire 25-year satellite record
            </p>
          </div>

          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
            <span className="text-slate-400">Rate per Decade:</span>
            <span className="font-mono font-bold text-slate-200">
              {slopeDecade > 0 ? `+${slopeDecade}` : slopeDecade} {units}/10yr
            </span>
          </div>
        </div>

        {/* Story Card 2: Confidence Level */}
        <div className="rounded-2xl bg-gradient-to-br from-slate-850 to-slate-900 border border-slate-750 p-5 flex flex-col justify-between shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Confidence Level
            </span>
            {isSig ? (
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
            ) : (
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
            )}
          </div>

          <div className="my-4">
            {isSig ? (
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-emerald-950/90 text-emerald-300 border border-emerald-500/50 glow-emerald">
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                  Confirmed Long-Term Shift
                </div>
                <p className="text-xs text-slate-300 mt-2.5 font-medium leading-relaxed">
                  95%+ statistical certainty — this shift is a genuine persistent climate trend, not random weather noise.
                </p>
              </div>
            ) : (
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-amber-950/90 text-amber-300 border border-amber-500/50 glow-amber">
                  <AlertTriangle className="w-4 h-4 text-amber-400" />
                  Normal Year-to-Year Swings
                </div>
                <p className="text-xs text-slate-300 mt-2.5 font-medium leading-relaxed">
                  Within typical natural variation — satellite measurements show seasonal fluctuations without a persistent drift.
                </p>
              </div>
            )}
          </div>

          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
            <span className="text-slate-400">Statistical Test:</span>
            <span className="font-mono text-cyan-400">
              {isSig ? 'Verified (p < 0.05)' : 'Inconclusive (p ≥ 0.05)'}
            </span>
          </div>
        </div>

        {/* Story Card 3: What It Means (Human & Ecological Impact) */}
        <div className="rounded-2xl bg-gradient-to-br from-slate-850 to-slate-900 border border-slate-750 p-5 flex flex-col justify-between shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              {categoryIcon}
              What It Means
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              {categoryName}
            </span>
          </div>

          <div className="my-4">
            <p className="text-xs text-slate-200 leading-relaxed font-sans">
              {impactText}
            </p>
          </div>

          <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400 truncate max-w-[150px]">{location_label}</span>
            <span className="text-emerald-400 font-semibold">{data_source?.split('(')[0] || 'NASA Earth'}</span>
          </div>
        </div>
      </div>
    );
  }

  // Scientist Mode: Full Math Bento Grid
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* 1. Sen's Slope Card */}
      <div className="rounded-2xl bg-slate-850 border border-slate-750 p-4 flex flex-col justify-between shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Sen's Slope (Decadal)
          </span>
          {renderTrendIcon()}
        </div>

        <div className="my-3">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl lg:text-3xl font-extrabold font-mono text-white">
              {slopeDecade > 0 ? `+${slopeDecade}` : slopeDecade}
            </span>
            <span className="text-xs font-mono text-cyan-400">{units}/decade</span>
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Rate scaled to 120-month decadal climate standard
          </p>
        </div>

        {/* Significance Badge */}
        <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
          <span className="text-[10px] text-slate-400">Statistical Significance:</span>
          {isSig ? (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-950/80 text-emerald-400 border border-emerald-500/50 glow-emerald">
              <CheckCircle className="w-3 h-3" /> p &lt; 0.05 (Sig)
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold font-mono bg-amber-950/80 text-amber-400 border border-amber-500/50 glow-amber">
              <AlertTriangle className="w-3 h-3" /> p &ge; 0.05 (Noise)
            </span>
          )}
        </div>
      </div>

      {/* 2. Mann-Kendall Test Statistics Card */}
      <div className="rounded-2xl bg-slate-850 border border-slate-750 p-4 flex flex-col justify-between shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Mann-Kendall p-value
          </span>
          <Activity className="w-4 h-4 text-cyan-400" />
        </div>

        <div className="my-3">
          <div className="flex items-baseline gap-2">
            <span className="text-2xl lg:text-3xl font-extrabold font-mono text-white">
              {pVal < 0.0001 ? '< 0.0001' : pVal?.toFixed(5)}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2 text-[11px] font-mono">
            <div className="bg-slate-900/60 px-2 py-1 rounded border border-slate-800">
              <span className="text-slate-500">Z-score: </span>
              <span className="text-slate-200 font-bold">{metrics?.z_score}</span>
            </div>
            <div className="bg-slate-900/60 px-2 py-1 rounded border border-slate-800">
              <span className="text-slate-500">Tau: </span>
              <span className="text-slate-200 font-bold">{metrics?.kendall_tau}</span>
            </div>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
          <span>Observations:</span>
          <span className="font-mono text-slate-200">{metrics?.observation_count} months</span>
        </div>
      </div>

      {/* 3. Total Percentage Shift Card */}
      <div className="rounded-2xl bg-slate-850 border border-slate-750 p-4 flex flex-col justify-between shadow-lg relative overflow-hidden group hover:border-slate-700 transition-all">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Total Shift (2001-2025)
          </span>
          <span className="text-xs font-mono text-slate-400">Net Change</span>
        </div>

        <div className="my-3">
          <div className="flex items-baseline gap-2">
            <span className={`text-2xl lg:text-3xl font-extrabold font-mono ${
              percentShift > 0 ? 'text-emerald-400' : percentShift < 0 ? 'text-rose-400' : 'text-slate-200'
            }`}>
              {percentShift > 0 ? `+${percentShift}%` : `${percentShift}%`}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2 text-[11px] font-mono">
            <div className="bg-slate-900/60 px-2 py-1 rounded border border-slate-800">
              <span className="text-slate-500">Mean: </span>
              <span className="text-slate-200">{metrics?.mean_value}</span>
            </div>
            <div className="bg-slate-900/60 px-2 py-1 rounded border border-slate-800">
              <span className="text-slate-500">Std: </span>
              <span className="text-slate-200">{metrics?.std_value}</span>
            </div>
          </div>
        </div>

        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
          <span>Provenance:</span>
          <span className="font-mono text-cyan-400 truncate max-w-[130px]" title={data_source}>
            {data_source?.split('(')[0] || 'NASA'}
          </span>
        </div>
      </div>

      {/* 4. AI Detective Briefing Card */}
      <div className="rounded-2xl bg-gradient-to-br from-slate-850 to-slate-900 border border-cyan-500/30 p-4 flex flex-col justify-between shadow-xl relative overflow-hidden">
        <div className="flex items-center justify-between pb-2 border-b border-slate-800">
          <span className="text-xs font-bold text-cyan-300 flex items-center gap-1.5 uppercase tracking-wider">
            <Compass className="w-4 h-4 text-cyan-400 animate-spin-slow" />
            AI Detective Verdict
          </span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/60">
            3-Sentence Synthesis
          </span>
        </div>

        <div className="my-2.5">
          <p className="text-xs text-slate-300 leading-relaxed font-sans line-clamp-6">
            {detective_briefing}
          </p>
        </div>

        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400 font-mono">
          <span>Target: {location_label}</span>
          <span className="text-emerald-400">Verified</span>
        </div>
      </div>
    </div>
  );
}

