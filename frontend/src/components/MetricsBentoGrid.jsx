import React from 'react';
import { TrendingUp, TrendingDown, Minus, CheckCircle, AlertTriangle, Compass, ShieldCheck, Activity } from 'lucide-react';

export default function MetricsBentoGrid({ analysisData }) {
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
