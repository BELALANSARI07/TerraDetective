import React, { useState } from 'react';
import { Sparkles, Search, ArrowRight, Loader2, CheckCircle2, Bot, HelpCircle, X, ChevronDown, ChevronUp } from 'lucide-react';

export default function AskDetectiveBar({
  mode = 'student',
  activeCaseId,
  onSyncResult,
}) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(true);

  const isLight = mode === 'student';

  const STARTER_QUESTIONS = isLight
    ? [
        "Why is the Amazon warming while Punjab cools?",
        "Why is there a deluge in Northeast India while Marathwada has drought?",
        "Compare temperature trends in Delhi vs Mumbai",
        "Compare rainfall in London vs Cairo",
      ]
    : [
        "Compare MOD11A2 Sen's slope in Rondônia vs Punjab",
        "Evaluate GPM IMERG precipitation anomaly in Cherrapunji vs rain shadow",
        "Compare T2M decadal trajectory in Delhi vs Mumbai",
        "Analyze PRECTOTCORR divergence in London vs Cairo",
      ];

  const placeholderText = isLight
    ? "Ask anything... e.g., 'Why is the Amazon warming while Punjab cools?' or 'Compare rainfall in Delhi vs Mumbai'"
    : "Query Earth telemetry... e.g., 'Compare MOD11A2 Sen's slope in Rondônia vs Punjab' or 'Analyze T2M in Cairo vs London'";

  const handleAsk = async (textToAsk) => {
    const q = (textToAsk || query).trim();
    if (!q) return;

    setLoading(true);
    setError(null);
    setQuery(q);

    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q,
          mode,
          active_case_id: activeCaseId,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server responded with ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
      setIsExpanded(true);

      // Auto-sync map and charts in App.jsx
      if (onSyncResult && data.case_payload) {
        onSyncResult(data);
      }
    } catch (err) {
      console.error('Ask TerraDetective error:', err);
      setError(err.message || 'Failed to process natural language query');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !loading) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className={`border transition-all duration-200 rounded-xl ${
      isLight
        ? 'bg-[#FAF8F5] border-[#DCD7C9] shadow-none'
        : 'bg-[#0C1017] border-[#1E2636] shadow-none'
    } dark:bg-[#0C1017] dark:border-[#1E2636]`}>
      {/* Search Input Bar */}
      <div className="p-3 sm:p-3.5 bg-transparent">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
          
          {/* Main Input Field */}
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Sparkles className={`w-3.5 h-3.5 ${
                loading ? 'animate-spin text-amber-500' : isLight ? 'text-archival-terracotta' : 'text-cyan-400'
              }`} />
            </div>

            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={placeholderText}
              disabled={loading}
              className={`w-full pl-9 pr-4 py-2 text-xs sm:text-sm border transition-all font-medium bg-white dark:bg-[#0C1017] border-[#DCD7C9] dark:border-[#1E2636] text-archival-ink dark:text-gray-200 placeholder-stone-500 dark:placeholder-slate-400 focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none rounded-lg ${
                isLight
                  ? ''
                  : 'font-mono text-xs'
              }`}
            />
          </div>

          {/* Ask Button */}
          <button
            onClick={() => handleAsk()}
            disabled={loading || !query.trim()}
            aria-busy={loading}
            className={`px-3.5 py-2 font-bold text-xs flex items-center justify-center space-x-1.5 transition-all rounded-lg focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
              isLight
                ? 'bg-archival-ink hover:bg-black text-white disabled:bg-archival-sand disabled:text-archival-muted'
                : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-mono disabled:bg-slate-800 disabled:text-slate-600'
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Investigating...</span>
              </>
            ) : (
              <>
                <span>Ask AI</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

        {/* 1-Click Starter Question Chips */}
        <div className="mt-2.5 flex items-center space-x-1.5 overflow-x-auto pb-0.5 text-[11px] no-scrollbar">
          <span className="text-[10px] font-bold uppercase tracking-wider text-archival-muted dark:text-slate-400 flex items-center space-x-1 flex-shrink-0 mr-1 font-mono">
            <Bot className="w-3 h-3" />
            <span>Try:</span>
          </span>
          {STARTER_QUESTIONS.map((sq, idx) => (
            <button
              key={idx}
              onClick={() => handleAsk(sq)}
              disabled={loading}
              className={`px-2 py-0.5 rounded text-left whitespace-nowrap transition-all flex-shrink-0 text-[11px] bg-white dark:bg-[#131821] border border-[#DCD7C9] dark:border-[#1E2636] text-archival-ink dark:text-cyan-400 hover:border-archival-terracotta dark:hover:bg-[#1E2636] hover:text-archival-terracotta focus-visible:ring-1 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
                isLight ? '' : 'font-mono text-[10px]'
              }`}
            >
              {sq}
            </button>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="px-4 pb-3 text-xs text-rose-500 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-slate-400 hover:text-slate-600">
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Interactive Answer Drawer */}
      {result && isExpanded && (
        <div className={`border-t px-4 py-3.5 space-y-3 transition-all ${
          isLight ? 'bg-white/95 border-blue-100' : 'bg-[#0C1017] border-[#1E2636]'
        } dark:bg-[#0C1017] dark:border-[#1E2636]`}>
          {/* Header Row: AI Model Badge + Auto-Sync Tag + Collapse Button */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider flex items-center space-x-1 ${
                result.ai_source === 'ollama_qwen3_8b'
                  ? 'bg-purple-100 text-purple-800 dark:bg-purple-950/80 dark:text-purple-300 border border-purple-200 dark:border-purple-800'
                  : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800'
              }`}>
                <Bot className="w-3 h-3" />
                <span>{result.ai_source === 'ollama_qwen3_8b' ? 'qwen3:8b AI Explainer' : 'Verified Statistical Engine'}</span>
              </span>

              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-cyan-300 border border-blue-200 dark:border-cyan-800 flex items-center space-x-1">
                <CheckCircle2 className="w-3 h-3 text-blue-600 dark:text-cyan-400" />
                <span>Auto-Synced to Map & Chart</span>
              </span>
            </div>

            <button
              onClick={() => setIsExpanded(false)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1"
              title="Collapse answer"
            >
              <ChevronUp className="w-4 h-4" />
            </button>
          </div>

          {/* Natural Language Answer Text */}
          <div className={`text-xs sm:text-sm leading-relaxed ${
            isLight ? 'text-slate-700' : 'text-slate-200'
          }`}>
            <p className="whitespace-pre-line">{result.answer}</p>
          </div>

          {/* Key Evidence Metric Badges */}
          {result.key_evidence_badges && result.key_evidence_badges.length > 0 && (
            <div className="pt-1 flex flex-wrap items-center gap-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mr-1">
                Key Evidence:
              </span>
              {result.key_evidence_badges.map((badge, bIdx) => (
                <span
                  key={bIdx}
                  className={`px-2 py-0.5 rounded-md font-mono text-[11px] border ${
                    isLight
                      ? 'bg-slate-100 text-slate-800 border-slate-200'
                      : 'bg-[#131821] text-cyan-300 border-[#1E2636]'
                  } dark:bg-[#131821] dark:text-cyan-300 dark:border-[#1E2636]`}
                >
                  {badge}
                </span>
              ))}
            </div>
          )}

          {/* Suggested Follow-up Questions */}
          {result.suggested_followups && result.suggested_followups.length > 0 && (
            <div className="pt-2 border-t border-dashed border-slate-200 dark:border-slate-800 flex flex-wrap items-center gap-1.5">
              <span className="text-[10px] font-bold text-slate-400 flex items-center space-x-1 mr-1">
                <HelpCircle className="w-3 h-3 text-amber-500" />
                <span>Follow up:</span>
              </span>
              {result.suggested_followups.map((fq, fIdx) => (
                <button
                  key={fIdx}
                  onClick={() => handleAsk(fq)}
                  disabled={loading}
                  className={`px-2 py-0.5 rounded-md text-[11px] border transition-colors ${
                    isLight
                      ? 'bg-blue-50/60 hover:bg-blue-50 text-blue-800 border-blue-200 hover:border-blue-300'
                      : 'bg-[#131821] hover:bg-[#1E2636] text-cyan-400 border-[#1E2636]'
                  } dark:bg-[#131821] dark:hover:bg-[#1E2636] dark:text-cyan-400 dark:border-[#1E2636]`}
                >
                  {fq}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Minimized View Bar */}
      {result && !isExpanded && (
        <div
          onClick={() => setIsExpanded(true)}
          className={`border-t px-4 py-2 flex items-center justify-between text-xs cursor-pointer ${
            isLight ? 'bg-slate-50/70 hover:bg-slate-100/70 text-slate-600' : 'bg-[#0C1017] hover:bg-[#131821] text-slate-300'
          } dark:bg-[#0C1017] dark:hover:bg-[#131821] dark:text-slate-300 dark:border-[#1E2636]`}
        >
          <div className="flex items-center space-x-2 truncate">
            <Bot className="w-3.5 h-3.5 text-blue-500" />
            <span className="font-semibold">AI Investigation Result:</span>
            <span className="truncate max-w-md text-slate-500">{result.answer}</span>
          </div>
          <button className="text-slate-400 hover:text-slate-600 flex items-center space-x-1">
            <span className="text-[10px]">Show Details</span>
            <ChevronDown className="w-3.5 h-3.5" />
          </button>
        </div>
      )}
    </div>
  );
}
