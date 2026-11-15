import React, { useState } from 'react';
import { Search, Sparkles, Flame, Droplets, Trees, Sun, Compass, ArrowRight } from 'lucide-react';

const EXAMPLE_QUERIES = [
  "Why is soil drying out in Northern India?",
  "How does Amazon deforestation impact land surface temperature?",
  "Compare precipitation trends between Central India and Meghalaya",
  "Track vegetation greening versus groundwater depletion"
];

const CATEGORY_SHORTCUTS = [
  { 
    id: 'heat', 
    emoji: '🌡️', 
    name: 'Heat', 
    desc: 'Surface Temp', 
    preferred: ['LST_DAY', 'T2M', 'TS'],
    activeClass: 'from-amber-500/20 to-orange-500/20 border-amber-500/80 text-amber-300'
  },
  { 
    id: 'rain', 
    emoji: '🌧️', 
    name: 'Rain', 
    desc: 'Precipitation', 
    preferred: ['GPM_PRECIP', 'PRECTOTCORR'],
    activeClass: 'from-blue-500/20 to-cyan-500/20 border-cyan-400 text-cyan-200'
  },
  { 
    id: 'vegetation', 
    emoji: '🌱', 
    name: 'Vegetation', 
    desc: 'Canopy NDVI', 
    preferred: ['NDVI', 'MOD13A3'],
    activeClass: 'from-emerald-500/20 to-teal-500/20 border-emerald-400 text-emerald-200'
  },
  { 
    id: 'water', 
    emoji: '💧', 
    name: 'Groundwater', 
    desc: 'Root-Zone Soil', 
    preferred: ['GLDAS_ROOTMOIST', 'GWETROOT', 'GWETTOP'],
    activeClass: 'from-cyan-500/20 to-indigo-500/20 border-indigo-400 text-indigo-200'
  }
];

export default function CommandBar({
  onSelectVariable,
  onSelectPreset,
  selectedVariable,
  selectedPresetId,
  presets = [],
  variables = []
}) {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [guidance, setGuidance] = useState('');

  const handleSelectCategory = (cat) => {
    // Find best match in available variables
    const availableIds = new Set(variables.map(v => v.identifier));
    const target = cat.preferred.find(id => availableIds.has(id)) || cat.preferred[0];
    onSelectVariable(target);
  };

  const isCategoryActive = (cat) => {
    return cat.preferred.includes(selectedVariable);
  };

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    try {
      const res = await fetch('/api/detective/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim() })
      });
      if (res.ok) {
        const data = await res.json();
        setRecommendations(data.top_recommendations || []);
        setGuidance(data.detective_guidance || '');
      }
    } catch (err) {
      console.error('Failed to query detective:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const getPresetIcon = (id) => {
    if (id.includes('amazon')) return <Flame className="w-3.5 h-3.5 text-rose-400" />;
    if (id.includes('punjab')) return <Trees className="w-3.5 h-3.5 text-emerald-400" />;
    if (id.includes('monsoon')) return <Droplets className="w-3.5 h-3.5 text-cyan-400" />;
    return <Sun className="w-3.5 h-3.5 text-amber-400" />;
  };

  return (
    <div className="space-y-4">
      {/* 4 Guided Earth System Category Pills */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Quick Earth System Categories
          </span>
          <span className="text-[11px] text-slate-500 hidden sm:inline">
            1-click auto-selects verified NASA observation satellite datasets
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {CATEGORY_SHORTCUTS.map((cat) => {
            const active = isCategoryActive(cat);
            return (
              <button
                key={cat.id}
                onClick={() => handleSelectCategory(cat)}
                className={`flex items-center gap-3 p-3 rounded-2xl border transition-all text-left group relative overflow-hidden ${
                  active
                    ? `bg-gradient-to-r ${cat.activeClass} shadow-lg ring-1 ring-cyan-500/40`
                    : 'bg-slate-900 hover:bg-slate-850 border-slate-750 hover:border-slate-700 text-slate-300'
                }`}
              >
                <span className="text-2xl group-hover:scale-110 transition-transform">
                  {cat.emoji}
                </span>
                <div className="min-w-0">
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold text-white group-hover:text-cyan-300 transition-colors">
                      {cat.name}
                    </span>
                    {active && <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />}
                  </div>
                  <span className="text-[11px] text-slate-400 block truncate">
                    {cat.desc}
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Search Input Bar */}
      <div className="relative rounded-2xl bg-slate-900 border border-slate-750 p-2 shadow-xl">
        <form onSubmit={handleSearch} className="flex items-center gap-2">
          <div className="flex items-center justify-center pl-3 text-cyan-400">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask AI Detective: e.g. 'Why is soil drying out in Northern India?' or 'Deforestation warming in Amazon'..."
            className="w-full bg-transparent border-0 text-sm md:text-base text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-0 py-2 px-1"
          />
          <button
            type="submit"
            disabled={isSearching}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-semibold text-xs md:text-sm transition-all shadow-md shadow-cyan-500/20 active:scale-95 disabled:opacity-50"
          >
            {isSearching ? (
              <span className="inline-block animate-spin">⟳</span>
            ) : (
              <Search className="w-4 h-4" />
            )}
            <span>Investigate</span>
          </button>
        </form>

        {/* AI Recommendations Dropdown / Banner */}
        {recommendations.length > 0 && (
          <div className="mt-3 pt-3 border-t border-slate-800 px-2 space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span className="font-semibold text-cyan-300 flex items-center gap-1">
                <Compass className="w-3.5 h-3.5" /> AI Detective Recommended Variables:
              </span>
              <button
                onClick={() => { setRecommendations([]); setGuidance(''); }}
                className="text-[11px] text-slate-500 hover:text-slate-300"
              >
                Clear
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
              {recommendations.map((rec) => (
                <button
                  key={rec.identifier}
                  onClick={() => onSelectVariable(rec.identifier)}
                  className={`flex flex-col text-left p-2.5 rounded-xl border transition-all ${
                    selectedVariable === rec.identifier
                      ? 'bg-cyan-950/60 border-cyan-500 text-cyan-200'
                      : 'bg-slate-850/80 hover:bg-slate-800 border-slate-750 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-xs text-cyan-400">{rec.identifier}</span>
                    <span className="text-[10px] text-emerald-400 font-mono">
                      {(rec.relevance_score * 100).toFixed(0)}% match
                    </span>
                  </div>
                  <span className="text-xs font-medium text-slate-200 truncate">{rec.name}</span>
                  <span className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{rec.match_rationale}</span>
                </button>
              ))}
            </div>
            {guidance && (
              <p className="text-xs text-slate-300 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800 leading-relaxed font-mono">
                💡 <span className="text-cyan-300 font-semibold">Detective Tip:</span> {guidance}
              </p>
            )}
          </div>
        )}
      </div>

      {/* 4 Paradox Case Study Presets Pills */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Paradox Case Studies
            </span>
            <span className="px-1.5 py-0.2 text-[10px] font-mono rounded bg-slate-800 text-cyan-400 border border-slate-700">
              4 Benchmarks
            </span>
          </div>
          <span className="text-[11px] text-slate-500 hidden sm:inline">
            Click to load opposing regional divergence datasets
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
          {presets.map((preset) => {
            const isSelected = selectedPresetId === preset.id;
            return (
              <button
                key={preset.id}
                onClick={() => onSelectPreset(preset)}
                className={`flex flex-col text-left p-3 rounded-xl border transition-all relative overflow-hidden group ${
                  isSelected
                    ? 'bg-slate-800 border-cyan-500 ring-1 ring-cyan-500/50 shadow-lg shadow-cyan-500/10'
                    : 'bg-slate-900 hover:bg-slate-850 border-slate-750 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-1.5">
                    {getPresetIcon(preset.id)}
                    <span className="font-semibold text-xs text-white group-hover:text-cyan-300 transition-colors">
                      {preset.title.split(':')[0]}
                    </span>
                  </div>
                  {isSelected && (
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                  )}
                </div>
                <p className="text-[11px] text-slate-400 line-clamp-2 leading-relaxed mb-2">
                  {preset.description}
                </p>
                <div className="mt-auto flex items-center justify-between text-[10px] text-cyan-400/90 font-mono pt-1.5 border-t border-slate-800/80">
                  <span className="truncate">{preset.expected_divergence_summary}</span>
                  <ArrowRight className="w-3 h-3 flex-shrink-0 ml-1 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
