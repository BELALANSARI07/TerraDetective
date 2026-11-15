import React, { useState, useEffect } from 'react';
import { Flame, Snowflake, HelpCircle, CheckCircle2, Award, Sparkles, ArrowRight } from 'lucide-react';

export default function ThermometerComparator({
  labelA = 'Region A',
  labelB = 'Region B',
  totalA = 0.94,
  totalB = -0.94,
  unit = '°C',
  quizData = null,
  quizSelection = null,
  onSelectQuiz = () => {},
}) {
  const cleanLabelA = labelA.split(',')[0].slice(0, 18);
  const cleanLabelB = labelB.split(',')[0].slice(0, 18);

  const signA = totalA >= 0 ? '+' : '';
  const signB = totalB >= 0 ? '+' : '';
  const netDelta = Math.abs(totalA - totalB);

  // Normalize bar fill height (-2.0 to +2.0 scale)
  const maxScale = Math.max(1.5, Math.abs(totalA), Math.abs(totalB));
  const heightPctA = Math.min(100, Math.max(10, (Math.abs(totalA) / maxScale) * 100));
  const heightPctB = Math.min(100, Math.max(10, (Math.abs(totalB) / maxScale) * 100));

  // Local selection state so the quiz is always functional
  const [internalSelection, setInternalSelection] = useState(null);

  useEffect(() => {
    setInternalSelection(null);
  }, [labelA, labelB]);

  const activeSelection = quizSelection !== null ? quizSelection : internalSelection;

  const handleSelectOption = (id) => {
    setInternalSelection(id);
    onSelectQuiz(id);
  };

  // Build high-craft dynamic hypothesis challenge for every case
  const isAWarmingMore = totalA >= totalB;
  const activeQuiz = quizData || {
    question: `Before inspecting the satellite curves, test your detective intuition: Over the 25-year record (2001–2025), which region shifted more rapidly?`,
    options: [
      {
        id: 'opt_a',
        label: `${cleanLabelA} (Region A)`,
        isCorrect: isAWarmingMore,
      },
      {
        id: 'opt_b',
        label: `${cleanLabelB} (Region B)`,
        isCorrect: !isAWarmingMore,
      },
    ],
    explanationCorrect: `🎯 Spot-on detective intuition! NASA satellites confirm that ${isAWarmingMore ? cleanLabelA : cleanLabelB} experienced a cumulative 25-year shift of ${isAWarmingMore ? signA + Number(totalA).toFixed(2) : signB + Number(totalB).toFixed(2)} ${unit}, outpacing the contrasting trajectory of ${isAWarmingMore ? cleanLabelB : cleanLabelA} (${isAWarmingMore ? signB + Number(totalB).toFixed(2) : signA + Number(totalA).toFixed(2)} ${unit})!`,
    explanationIncorrect: `🔍 A surprising Earth system paradox! NASA satellite telemetry reveals that ${isAWarmingMore ? cleanLabelA : cleanLabelB} actually showed the stronger cumulative trajectory (${isAWarmingMore ? signA + Number(totalA).toFixed(2) : signB + Number(totalB).toFixed(2)} ${unit}) versus ${isAWarmingMore ? cleanLabelB : cleanLabelA}'s ${isAWarmingMore ? signB + Number(totalB).toFixed(2) : signA + Number(totalA).toFixed(2)} ${unit}. Inspect the physical mechanism below to see why!`,
  };

  return (
    <div className="space-y-4">
      {/* 25-Year Tactile Thermometer / Cumulative Shift Gauge */}
      <div className="p-4 rounded-xl border border-[#DCD7C9] bg-[#FAF8F5] text-archival-ink shadow-none">
        <div className="flex items-center justify-between pb-3 border-b border-[#DCD7C9] mb-3">
          <div>
            <span className="text-[10px] font-mono uppercase tracking-wider text-archival-muted font-bold block">
              25-Year Cumulative Delta
            </span>
            <h4 className="font-serif text-lg text-archival-ink font-semibold">
              Net Planetary Separation
            </h4>
          </div>
          <div className="px-2.5 py-1 rounded-md bg-archival-sand text-archival-ink font-mono text-xs font-bold border border-[#DCD7C9]">
            Δ = {netDelta.toFixed(2)} {unit}
          </div>
        </div>

        {/* Side-by-Side Dual Gauges */}
        <div className="grid grid-cols-2 gap-3 pt-1">
          {/* Region A Column */}
          <div className="p-3 rounded-lg border border-[#DCD7C9]/80 bg-white/70 flex flex-col justify-between space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-archival-ink truncate">{cleanLabelA}</span>
              {totalA >= 0 ? (
                <Flame className="w-3.5 h-3.5 text-archival-terracotta flex-shrink-0" />
              ) : (
                <Snowflake className="w-3.5 h-3.5 text-archival-viridian flex-shrink-0" />
              )}
            </div>

            {/* Visual Bar Gauge */}
            <div className="relative h-16 bg-archival-sand/60 rounded-md overflow-hidden flex items-end p-1 border border-[#DCD7C9]/60">
              <div
                style={{ height: `${heightPctA}%` }}
                className={`w-full rounded-sm transition-all duration-700 ${
                  totalA >= 0
                    ? 'bg-gradient-to-t from-archival-terracotta/70 to-archival-terracotta'
                    : 'bg-gradient-to-t from-archival-viridian/70 to-archival-viridian'
                }`}
              />
              <span className="absolute inset-0 flex items-center justify-center font-mono text-xs font-bold text-archival-ink drop-shadow-xs">
                {signA}{Number(totalA).toFixed(2)} {unit}
              </span>
            </div>

            <span className="text-[10px] font-mono text-archival-muted text-center block">
              {totalA >= 0 ? 'Warming Shift' : 'Cooling Shift'}
            </span>
          </div>

          {/* Region B Column */}
          <div className="p-3 rounded-lg border border-[#DCD7C9]/80 bg-white/70 flex flex-col justify-between space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-archival-ink truncate">{cleanLabelB}</span>
              {totalB >= 0 ? (
                <Flame className="w-3.5 h-3.5 text-archival-terracotta flex-shrink-0" />
              ) : (
                <Snowflake className="w-3.5 h-3.5 text-archival-viridian flex-shrink-0" />
              )}
            </div>

            {/* Visual Bar Gauge */}
            <div className="relative h-16 bg-archival-sand/60 rounded-md overflow-hidden flex items-end p-1 border border-[#DCD7C9]/60">
              <div
                style={{ height: `${heightPctB}%` }}
                className={`w-full rounded-sm transition-all duration-700 ${
                  totalB >= 0
                    ? 'bg-gradient-to-t from-archival-terracotta/70 to-archival-terracotta'
                    : 'bg-gradient-to-t from-archival-viridian/70 to-archival-viridian'
                }`}
              />
              <span className="absolute inset-0 flex items-center justify-center font-mono text-xs font-bold text-archival-ink drop-shadow-xs">
                {signB}{Number(totalB).toFixed(2)} {unit}
              </span>
            </div>

            <span className="text-[10px] font-mono text-archival-muted text-center block">
              {totalB >= 0 ? 'Warming Shift' : 'Cooling Shift'}
            </span>
          </div>
        </div>
      </div>

      {/* Interactive Detective Hypothesis Quiz */}
      {activeQuiz && (
        <div className="p-4 rounded-xl border border-[#DCD7C9] bg-[#FAF8F5] text-archival-ink shadow-none">
          <div className="flex items-center space-x-2 mb-2">
            <Sparkles className="w-4 h-4 text-amber-600 flex-shrink-0" />
            <h5 className="font-serif text-base text-archival-ink font-semibold">
              Detective Hypothesis Challenge
            </h5>
          </div>

          <p className="text-xs text-archival-muted mb-3 leading-relaxed">
            {activeQuiz.question}
          </p>

          <div className="space-y-1.5">
            {activeQuiz.options.map((opt) => {
              const isSelected = activeSelection === opt.id;
              const hasAnswered = activeSelection !== null;
              return (
                <button
                  key={opt.id}
                  onClick={() => handleSelectOption(opt.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs font-medium border transition-all flex items-center justify-between focus-visible:ring-2 focus-visible:ring-archival-terracotta focus-visible:outline-none ${
                    isSelected
                      ? opt.isCorrect
                        ? 'bg-emerald-50 border-emerald-400 text-emerald-900 font-bold'
                        : 'bg-rose-50 border-rose-300 text-rose-900'
                      : hasAnswered && opt.isCorrect
                        ? 'bg-emerald-50/60 border-emerald-300 text-emerald-800'
                        : 'bg-white border-[#DCD7C9] text-archival-ink hover:bg-archival-sand/50'
                  }`}
                >
                  <span>{opt.label}</span>
                  {isSelected && (
                    opt.isCorrect ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                    ) : (
                      <span className="text-[10px] text-rose-600 font-mono">Revealed</span>
                    )
                  )}
                </button>
              );
            })}
          </div>

          {activeSelection && (
            <div className="mt-3 p-2.5 rounded-lg bg-archival-sand/70 border border-[#DCD7C9] text-[11px] leading-relaxed text-archival-ink animate-fadeIn">
              {activeQuiz.options.find(o => o.id === activeSelection)?.isCorrect
                ? activeQuiz.explanationCorrect
                : activeQuiz.explanationIncorrect}
            </div>
          )}
        </div>
      )}
    </div>
  );
}