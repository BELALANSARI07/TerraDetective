import React from 'react';
import { Globe, Satellite, Database, BookOpen, Activity, ShieldCheck, FlaskConical } from 'lucide-react';

export default function Navbar({ health, onOpenMethodology, onOpenEarthdataCloud, uxMode = 'story', onChangeUxMode }) {
  const isHealthy = health?.status === 'healthy';
  const pillars = health?.data_pillars || {};

  return (
    <header className="border-b border-slate-750 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40 px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20 text-slate-950 font-bold">
            <Globe className="w-6 h-6 text-slate-950 animate-pulse" />
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-400 rounded-full border-2 border-slate-900" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight text-white flex items-center gap-1.5">
                Terra<span className="text-cyan-400">Detective</span>
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold tracking-wider uppercase rounded-md bg-cyan-950/80 text-cyan-300 border border-cyan-800/60">
                NASA Space Apps 2026
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Earth System Trend Analysis & Regional Divergence Workbench
            </p>
          </div>
        </div>

        {/* Status Pills & Actions */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          {/* Dual-Mode Toggle: Story Mode vs Scientist Mode */}
          <div className="flex items-center p-0.5 rounded-lg bg-slate-950 border border-slate-750">
            <button
              onClick={() => onChangeUxMode && onChangeUxMode('story')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
                uxMode === 'story'
                  ? 'bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>📖 Story Mode</span>
            </button>
            <button
              onClick={() => onChangeUxMode && onChangeUxMode('scientist')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold transition-all ${
                uxMode === 'scientist'
                  ? 'bg-gradient-to-r from-emerald-400 to-teal-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <FlaskConical className="w-3 h-3" />
              <span>🔬 Scientist Mode</span>
            </button>
          </div>

          {/* NASA Earthdata Cloud Auth Badge */}
          {health?.earthdata?.authenticated ? (
            <button 
              onClick={onOpenEarthdataCloud}
              title={`Click to explore live NASA CMR & OPeNDAP granules (${health.earthdata.username || 'Active'})`}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/80 hover:bg-emerald-900/80 border border-emerald-500/60 text-emerald-300 shadow-sm shadow-emerald-950/40 transition-all cursor-pointer active:scale-95"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
              <span className="font-semibold text-[11px] tracking-tight">Earthdata Cloud Live Link:</span>
              <span className="px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-200 font-mono font-bold text-[10px] border border-emerald-500/30">
                Authenticated
              </span>
            </button>
          ) : (
            <button
              onClick={onOpenEarthdataCloud}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-850 hover:bg-slate-800 border border-slate-750 text-slate-400 transition-all cursor-pointer"
            >
              <ShieldCheck className="w-3.5 h-3.5 text-slate-500" />
              <span className="font-medium text-[11px]">Earthdata Cloud:</span>
              <span className="font-mono text-[10px] text-amber-400">Offline / Guest</span>
            </button>
          )}

          {/* Engine Health */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-850 border border-slate-750 text-slate-300">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400 font-mono">
              {health?.local_llm?.available ? 'Ollama Active' : 'Offline AI Engine'}
            </span>
            <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-emerald-400 shadow-sm shadow-emerald-400/50' : 'bg-amber-400'}`} />
          </div>

          {/* Methodology Trigger */}
          <button
            onClick={onOpenMethodology}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-slate-800 to-slate-750 hover:from-slate-750 hover:to-slate-700 text-cyan-300 border border-cyan-500/30 font-medium transition-all shadow-sm hover:shadow-cyan-500/10 active:scale-95"
          >
            <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
            Methodology & Citations
          </button>
        </div>
      </div>
    </header>
  );
}
