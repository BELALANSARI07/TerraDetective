import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import CommandBar from './components/CommandBar';
import RegionalMapComparator from './components/RegionalMapComparator';
import PlotlyTimeseriesChart from './components/PlotlyTimeseriesChart';
import MetricsBentoGrid from './components/MetricsBentoGrid';
import DivergenceComparatorCard from './components/DivergenceComparatorCard';
import MethodologyDrawer from './components/MethodologyDrawer';
import { Layers, ArrowRightLeft, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';

export default function App() {
  const [health, setHealth] = useState(null);
  const [variables, setVariables] = useState([]);
  const [presets, setPresets] = useState([]);
  const [selectedPresetId, setSelectedPresetId] = useState('amazon_deforestation_warming');
  const [selectedVariable, setSelectedVariable] = useState('LST_DAY');
  const [isMethodologyOpen, setIsMethodologyOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Region state
  const [regionA, setRegionA] = useState({
    latitude: -10.875,
    longitude: -61.93,
    label: 'Rondonia Amazon Arc'
  });
  const [regionB, setRegionB] = useState({
    latitude: 30.901,
    longitude: 75.8573,
    label: 'Punjab Irrigated Belt'
  });

  // Analysis result state
  const [analysisA, setAnalysisA] = useState(null);
  const [analysisB, setAnalysisB] = useState(null);
  const [divergence, setDivergence] = useState(null);

  // Load initial health, variables, presets
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [hRes, vRes, pRes] = await Promise.all([
          fetch('/api/health'),
          fetch('/api/variables'),
          fetch('/api/paradox-presets')
        ]);

        if (hRes.ok) setHealth(await hRes.json());
        if (vRes.ok) {
          const vData = await vRes.json();
          setVariables(vData.variables || []);
        }
        if (pRes.ok) {
          const pData = await pRes.json();
          setPresets(pData.presets || []);
        }
      } catch (err) {
        console.error('Metadata fetch error:', err);
      }
    };

    fetchMetadata();
  }, []);

  // Run analysis when regions or variable changes
  const runAnalysis = async (customVar = null, customRegA = null, customRegB = null) => {
    setIsLoading(true);
    setError(null);

    const targetVar = customVar || selectedVariable;
    const targetA = customRegA || regionA;
    const targetB = customRegB || regionB;

    try {
      const payload = {
        region_a: {
          latitude: targetA.latitude,
          longitude: targetA.longitude,
          label: targetA.label
        },
        region_b: {
          latitude: targetB.latitude,
          longitude: targetB.longitude,
          label: targetB.label
        },
        variable: targetVar,
        start_year: 2001,
        end_year: 2025
      };

      const res = await fetch('/api/analyze/region-compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Analysis request failed');
      }

      const data = await res.json();
      setAnalysisA(data.region_a);
      setAnalysisB(data.region_b);
      setDivergence(data.divergence);
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to complete time series analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  // Run initial analysis once mounted
  useEffect(() => {
    runAnalysis();
  }, []);

  // Handle Preset Selection
  const handleSelectPreset = (preset) => {
    setSelectedPresetId(preset.id);
    setSelectedVariable(preset.primary_variable);

    const newA = {
      latitude: preset.region_a.latitude,
      longitude: preset.region_a.longitude,
      label: preset.region_a.label
    };
    const newB = preset.region_b
      ? {
          latitude: preset.region_b.latitude,
          longitude: preset.region_b.longitude,
          label: preset.region_b.label
        }
      : {
          latitude: 30.901,
          longitude: 75.8573,
          label: 'Punjab Irrigated Belt'
        };

    setRegionA(newA);
    setRegionB(newB);
    runAnalysis(preset.primary_variable, newA, newB);
  };

  // Handle Variable Change
  const handleSelectVariable = (varIdent) => {
    setSelectedVariable(varIdent);
    runAnalysis(varIdent);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar
        health={health}
        onOpenMethodology={() => setIsMethodologyOpen(true)}
      />

      {/* Main Workbench Body */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 lg:px-8 py-6 space-y-6">
        {/* Command Bar: Natural Language Search & 4 Paradox Presets */}
        <CommandBar
          onSelectVariable={handleSelectVariable}
          onSelectPreset={handleSelectPreset}
          selectedVariable={selectedVariable}
          selectedPresetId={selectedPresetId}
          presets={presets}
          variables={variables}
        />

        {/* Error Alert */}
        {error && (
          <div className="p-3.5 rounded-xl bg-rose-950/80 border border-rose-500/60 text-rose-200 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400" />
              <span>{error}</span>
            </div>
            <button
              onClick={() => runAnalysis()}
              className="text-xs font-mono font-bold text-rose-300 underline hover:text-white"
            >
              Retry
            </button>
          </div>
        )}

        {/* Dual Interactive Regional Map Comparator */}
        <RegionalMapComparator
          regionA={regionA}
          regionB={regionB}
          onChangeRegionA={setRegionA}
          onChangeRegionB={setRegionB}
          selectedVariable={selectedVariable}
          onChangeVariable={handleSelectVariable}
          variables={variables}
          onExecuteAnalysis={() => runAnalysis()}
          isLoading={isLoading}
        />

        {/* Divergence Diagnosis Banner */}
        {divergence && (
          <DivergenceComparatorCard
            divergence={divergence}
            regionA={analysisA}
            regionB={analysisB}
            variableName={analysisA?.variable_name || selectedVariable}
            units={analysisA?.units || ''}
          />
        )}

        {/* Plotly Interactive Timeseries & STL Component Charts */}
        <PlotlyTimeseriesChart
          regionAData={analysisA}
          regionBData={analysisB}
          selectedVariable={selectedVariable}
          variableName={analysisA?.variable_name}
          units={analysisA?.units || ''}
        />

        {/* High-Density Bento Grid Metrics: Region A */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400 px-1">
            <span className="flex items-center gap-1.5 text-cyan-400">
              <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 ring-2 ring-cyan-400/30" />
              Primary Analysis Diagnostics — {analysisA?.location_label || 'Region A'}
            </span>
            <span className="text-slate-500 font-mono text-[11px]">
              Mann-Kendall Rank Test & Loess Residuals
            </span>
          </div>
          <MetricsBentoGrid analysisData={analysisA} />
        </div>

        {/* High-Density Bento Grid Metrics: Region B (Comparator) */}
        {analysisB && (
          <div className="space-y-2 pt-2">
            <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400 px-1">
              <span className="flex items-center gap-1.5 text-rose-400">
                <div className="w-2.5 h-2.5 rounded-full bg-rose-400 ring-2 ring-rose-400/30" />
                Comparative Diagnostics — {analysisB?.location_label || 'Region B'}
              </span>
              <span className="text-slate-500 font-mono text-[11px]">
                Opposing Regional Trend Counterpart
              </span>
            </div>
            <MetricsBentoGrid analysisData={analysisB} />
          </div>
        )}
      </main>

      {/* Methodology & Partner Drawer */}
      <MethodologyDrawer
        isOpen={isMethodologyOpen}
        onClose={() => setIsMethodologyOpen(false)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-900/60 py-4 px-4 text-center text-xs text-slate-500 font-mono">
        TerraDetective — NASA Space Apps Challenge 2026: Be An Earth System Trend Detective! | Powered by NASA Giovanni, AppEEARS, GLDAS & POWER.
      </footer>
    </div>
  );
}
