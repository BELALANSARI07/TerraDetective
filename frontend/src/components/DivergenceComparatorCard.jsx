import React from 'react';
import { ArrowRightLeft, AlertOctagon, CheckCircle2, AlertTriangle, Sparkles, ArrowRight, FlaskConical } from 'lucide-react';

export default function DivergenceComparatorCard({
  divergence,
  regionA,
  regionB,
  variableName,
  units,
  uxMode = 'story',
  onSwitchToScientistMode
}) {
  if (!divergence) return null;

  const {
    slope_difference_per_decade,
    divergence_ratio,
    opposite_trends,
    divergence_severity,
    comparative_verdict,
    headline,
    plain_summary
  } = divergence;

  const getSeverityBadge = () => {
    if (divergence_severity === 'Extreme Divergence') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono bg-rose-950/80 text-rose-300 border border-rose-500/60 glow-rose animate-pulse">
          <AlertOctagon className="w-3.5 h-3.5 text-rose-400" /> Extreme Regional Divergence
        </span>
      );
    }
    if (divergence_severity === 'Moderate Divergence') {
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono bg-amber-950/80 text-amber-300 border border-amber-500/60 glow-amber">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Moderate Trend Divergence
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold font-mono bg-blue-950/80 text-blue-300 border border-blue-500/60">
        <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" /> Synchronous Climate Trajectory
      </span>
    );
  };

  // --- STORY MODE CARD ---
  if (uxMode === 'story') {
    return (
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-cyan-500/30 p-6 shadow-2xl space-y-4 animate-fade-in relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Story Mode Top Tag */}
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold tracking-wide uppercase bg-cyan-950/90 text-cyan-300 border border-cyan-800/70 flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-cyan-400" />
              Climate Detective Story
            </span>
            <span className="text-xs text-slate-400">
              {regionA?.location_label || 'Region A'} vs. {regionB?.location_label || 'Region B'}
            </span>
          </div>

          {getSeverityBadge()}
        </div>

        {/* Big Bold Headline */}
        <div className="space-y-2">
          <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight leading-snug">
            {headline || `${regionA?.location_label || 'Region A'} and ${regionB?.location_label || 'Region B'} are heading on opposite climate paths.`}
          </h2>

          {/* Plain English Summary */}
          <p className="text-sm sm:text-base text-slate-300 leading-relaxed font-sans max-w-4xl">
            {plain_summary || comparative_verdict}
          </p>
        </div>

        {/* Action strip to switch to Scientist Mode */}
        <div className="pt-2 flex flex-wrap items-center justify-between gap-3 text-xs border-t border-slate-800/60">
          <span className="text-slate-400 font-mono text-[11px]">
            Observed 25-Year Trend Differential (2001–2025)
          </span>

          <button
            onClick={onSwitchToScientistMode}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-cyan-300 hover:text-cyan-200 border border-cyan-500/40 font-semibold transition-all group"
          >
            <FlaskConical className="w-3.5 h-3.5 text-cyan-400" />
            <span>View Scientific Proof & Formulas</span>
            <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
          </button>
        </div>
      </div>
    );
  }

  // --- SCIENTIST MODE CARD (Mathematical Rigor) ---
  return (
    <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-750 p-5 shadow-xl space-y-4 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <ArrowRightLeft className="w-5 h-5 text-cyan-400" />
          <div>
            <h3 className="font-extrabold text-sm md:text-base text-white">
              Regional Divergence Diagnosis: {regionA?.location_label || 'Region A'} vs. {regionB?.location_label || 'Region B'}
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Parameter: {variableName} ({units})
            </p>
          </div>
        </div>

        {getSeverityBadge()}
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono">
        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <span className="text-slate-400 text-xs block mb-1">Slope Differential (ΔS)</span>
          <span className="text-xl font-extrabold text-white">
            {slope_difference_per_decade > 0 ? `+${slope_difference_per_decade}` : slope_difference_per_decade}
          </span>
          <span className="text-[11px] text-cyan-400 ml-1.5">{units}/decade</span>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <span className="text-slate-400 text-xs block mb-1">Divergence Magnitude Ratio</span>
          <span className="text-xl font-extrabold text-white">{divergence_ratio}x</span>
          <span className="text-[11px] text-slate-400 ml-1.5">differential scaling</span>
        </div>

        <div className="bg-slate-900/80 p-3 rounded-xl border border-slate-800">
          <span className="text-slate-400 text-xs block mb-1">Opposite Trend Vectors</span>
          <span className={`text-xl font-extrabold ${opposite_trends ? 'text-rose-400' : 'text-slate-300'}`}>
            {opposite_trends ? 'DETECTED' : 'CONCURRENT'}
          </span>
        </div>
      </div>

      {/* Executive Verdict */}
      <div className="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800 text-xs text-slate-200 leading-relaxed font-sans">
        <span className="text-cyan-400 font-bold block mb-1 uppercase tracking-wider font-mono text-[11px]">
          Executive Detective Comparative Verdict:
        </span>
        {comparative_verdict}
      </div>
    </div>
  );
}
