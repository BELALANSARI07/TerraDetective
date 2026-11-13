import React, { useEffect, useRef, useState } from 'react';
import Plotly from 'plotly.js-dist-min';
import { Eye, TrendingUp, Calendar, Zap, AlertCircle } from 'lucide-react';

export default function PlotlyTimeseriesChart({
  regionAData,
  regionBData,
  selectedVariable,
  variableName,
  units
}) {
  const chartContainerRef = useRef(null);
  const [showRaw, setShowRaw] = useState(true);
  const [showTrend, setShowTrend] = useState(true);
  const [showSeasonal, setShowSeasonal] = useState(false);
  const [showResidual, setShowResidual] = useState(false);

  useEffect(() => {
    if (!chartContainerRef.current || !regionAData) return;

    const traces = [];

    // --- REGION A TRACES ---
    if (showRaw && regionAData.dates && regionAData.raw_values) {
      traces.push({
        x: regionAData.dates,
        y: regionAData.raw_values,
        name: `${regionAData.location_label || 'Region A'} (Raw Monthly)`,
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: 'rgba(56, 189, 248, 0.45)', width: 1.2 },
        marker: { size: 3, color: '#38BDF8' },
        hovertemplate: '%{x}<br>Raw: %{y:.3f} ' + units + '<extra></extra>'
      });
    }

    if (showTrend && regionAData.dates && regionAData.stl?.trend) {
      traces.push({
        x: regionAData.dates,
        y: regionAData.stl.trend,
        name: `${regionAData.location_label || 'Region A'} (STL Trend)`,
        type: 'scatter',
        mode: 'lines',
        line: { color: '#38BDF8', width: 3.5 },
        hovertemplate: '%{x}<br>STL Trend: %{y:.3f} ' + units + '<extra></extra>'
      });
    }

    if (showSeasonal && regionAData.dates && regionAData.stl?.seasonal) {
      traces.push({
        x: regionAData.dates,
        y: regionAData.stl.seasonal,
        name: `${regionAData.location_label || 'Region A'} (12-Mo Seasonal Cycle)`,
        type: 'scatter',
        mode: 'lines',
        line: { color: '#10B981', width: 1.8, dash: 'dot' },
        hovertemplate: '%{x}<br>Seasonal: %{y:.3f} ' + units + '<extra></extra>'
      });
    }

    if (showResidual && regionAData.dates && regionAData.stl?.residual) {
      traces.push({
        x: regionAData.dates,
        y: regionAData.stl.residual,
        name: `${regionAData.location_label || 'Region A'} (Residual Anomalies)`,
        type: 'bar',
        marker: { color: 'rgba(245, 158, 11, 0.55)' },
        hovertemplate: '%{x}<br>Residual: %{y:.3f} ' + units + '<extra></extra>'
      });
    }

    // --- REGION B TRACES (if comparing) ---
    if (regionBData) {
      if (showRaw && regionBData.dates && regionBData.raw_values) {
        traces.push({
          x: regionBData.dates,
          y: regionBData.raw_values,
          name: `${regionBData.location_label || 'Region B'} (Raw Monthly)`,
          type: 'scatter',
          mode: 'lines+markers',
          line: { color: 'rgba(244, 63, 94, 0.45)', width: 1.2 },
          marker: { size: 3, color: '#F43F5E' },
          hovertemplate: '%{x}<br>Raw: %{y:.3f} ' + units + '<extra></extra>'
        });
      }

      if (showTrend && regionBData.dates && regionBData.stl?.trend) {
        traces.push({
          x: regionBData.dates,
          y: regionBData.stl.trend,
          name: `${regionBData.location_label || 'Region B'} (STL Trend)`,
          type: 'scatter',
          mode: 'lines',
          line: { color: '#F43F5E', width: 3.5 },
          hovertemplate: '%{x}<br>STL Trend: %{y:.3f} ' + units + '<extra></extra>'
        });
      }
    }

    const layout = {
      autosize: true,
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      margin: { l: 50, r: 25, t: 30, b: 40 },
      showlegend: true,
      legend: {
        orientation: 'h',
        x: 0,
        y: 1.15,
        font: { color: '#94A3B8', size: 11 },
        bgcolor: 'transparent'
      },
      xaxis: {
        gridcolor: '#1F2E45',
        zerolinecolor: '#1F2E45',
        tickfont: { color: '#64748B', size: 11, family: 'JetBrains Mono' },
        showgrid: true
      },
      yaxis: {
        gridcolor: '#1F2E45',
        zerolinecolor: '#334D70',
        tickfont: { color: '#64748B', size: 11, family: 'JetBrains Mono' },
        title: { text: units, font: { color: '#94A3B8', size: 12 } },
        showgrid: true
      },
      hovermode: 'x unified',
      hoverlabel: {
        bgcolor: '#182436',
        bordercolor: '#273B57',
        font: { color: '#FFFFFF', family: 'JetBrains Mono', size: 12 }
      }
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d']
    };

    Plotly.newPlot(chartContainerRef.current, traces, layout, config);

    const handleResize = () => {
      if (chartContainerRef.current) {
        Plotly.Plots.resize(chartContainerRef.current);
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [regionAData, regionBData, showRaw, showTrend, showSeasonal, showResidual, units]);

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-750 p-4 shadow-xl space-y-3">
      {/* Chart Header & Toggles */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" />
            <h3 className="font-bold text-sm text-white">
              {variableName || selectedVariable} — STL Loess Deseasonalized Analysis
            </h3>
          </div>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            12-month Loess Period Decomposition & Mann-Kendall Sen's Slope
          </p>
        </div>

        {/* Layer Toggles */}
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          <button
            onClick={() => setShowRaw(!showRaw)}
            className={`px-2.5 py-1 rounded-lg border text-xs font-mono transition-all ${
              showRaw
                ? 'bg-slate-800 border-cyan-500/80 text-cyan-300'
                : 'bg-slate-900/60 border-slate-750 text-slate-500 hover:text-slate-400'
            }`}
          >
            Raw Monthly
          </button>
          <button
            onClick={() => setShowTrend(!showTrend)}
            className={`px-2.5 py-1 rounded-lg border text-xs font-mono transition-all ${
              showTrend
                ? 'bg-cyan-950/80 border-cyan-400 text-cyan-200 font-bold'
                : 'bg-slate-900/60 border-slate-750 text-slate-500 hover:text-slate-400'
            }`}
          >
            STL Trendline
          </button>
          <button
            onClick={() => setShowSeasonal(!showSeasonal)}
            className={`px-2.5 py-1 rounded-lg border text-xs font-mono transition-all ${
              showSeasonal
                ? 'bg-emerald-950/80 border-emerald-400 text-emerald-300'
                : 'bg-slate-900/60 border-slate-750 text-slate-500 hover:text-slate-400'
            }`}
          >
            Seasonal (12-Mo)
          </button>
          <button
            onClick={() => setShowResidual(!showResidual)}
            className={`px-2.5 py-1 rounded-lg border text-xs font-mono transition-all ${
              showResidual
                ? 'bg-amber-950/80 border-amber-400 text-amber-300'
                : 'bg-slate-900/60 border-slate-750 text-slate-500 hover:text-slate-400'
            }`}
          >
            Residual Anomalies
          </button>
        </div>
      </div>

      {/* Plotly Container */}
      <div className="w-full h-80 md:h-96">
        <div ref={chartContainerRef} className="w-full h-full" />
      </div>
    </div>
  );
}
