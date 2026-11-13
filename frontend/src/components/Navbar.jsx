import React from 'react';
import { Globe, Satellite, Database, BookOpen, Activity, ShieldCheck } from 'lucide-react';

export default function Navbar({ health, onOpenMethodology }) {
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
          {/* Data Pillars Indicator */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-850 border border-slate-750 text-slate-300">
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-medium">4 Data Pillars:</span>
            <span className="text-emerald-400 font-mono font-semibold">Active</span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-400 font-mono">
              {Object.values(pillars).reduce((acc, p) => acc + (p?.file_count || 0), 0)} datasets
            </span>
          </div>

          {/* NASA Earthdata Auth Badge */}
          {health?.earthdata?.authenticated && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/70 border border-emerald-600/50 text-emerald-300">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span className="font-medium text-[11px]">NASA Earthdata:</span>
              <span className="font-mono font-bold text-white text-[11px]">{health.earthdata.username}</span>
            </div>
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
