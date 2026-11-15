import React, { useEffect, useRef, useState } from 'react';
import Plotly from 'plotly.js-dist-min';
import { 
  TrendingUp, Sliders, Eye, EyeOff, Calendar, AlertTriangle, 
  CheckCircle2, Clock, HelpCircle, Sparkles, Award, Compass, 
  Lightbulb, Activity, BarChart2, Flame, Snowflake, ArrowRight
} from 'lucide-react';

export default function TrendComparisonChart({
  caseData,
  statistics,
  mode = 'student',
  customData = null,
  onTimeWindowChange,
  activeStartYear = 2001,
  activeEndYear = 2025,
}) {
  const chartContainerRef = useRef(null);
  const trendSubplotRef = useRef(null);
  const seasonalSubplotRef = useRef(null);
  const residualSubplotRef = useRef(null);

  const isLight = mode === 'student';

  // Hover Readout State for Scientist Mode
  const [hoverData, setHoverData] = useState(null);

  // Student Mode State
  const [showRawZigZags, setShowRawZigZags] = useState(false);

  // Scientist Mode Interactive Toggles
  const [showRaw, setShowRaw] = useState(false);
  const [showDeseasonalized, setShowDeseasonalized] = useState(true);
  const [showSensSlope, setShowSensSlope] = useState(true);
  const [showConfidenceBand, setShowConfidenceBand] = useState(true);

  // Local Time Window State
  const [startYear, setStartYear] = useState(activeStartYear);
  const [endYear, setEndYear] = useState(activeEndYear);

  // Sync props to state if parent updates
  useEffect(() => {
    setStartYear(activeStartYear);
    setEndYear(activeEndYear);
  }, [activeStartYear, activeEndYear]);

  // Extract regions and stats with robust label sanitization
  const statA = statistics?.region_a;
  const statB = statistics?.region_b;
  const div = statistics?.divergence_analysis;

  const isCleanName = (str) => {
    if (!str || typeof str !== 'string') return false;
    const lower = str.trim().toLowerCase();
    return (
      lower.length > 0 &&
      !['region_a', 'region_b', 'region a', 'region b', 'region', 'region_id'].includes(lower)
    );
  };

  const getCleanLabel = (stat, manifestReg, index, defaultFallback) => {
    if (isCleanName(stat?.region_label)) return stat.region_label.trim();
    if (isCleanName(manifestReg?.region_label)) return manifestReg.region_label.trim();
    if (isCleanName(manifestReg?.label)) return manifestReg.label.trim();
    if (caseData?.manifest?.title) {
      const match = caseData.manifest.title.match(/(?:Investigation|Probe|Analysis|Comparison|Telemetry)?[:\s]*(.+?)\s+(?:vs\.?|versus|to|and)\s+(.+?)(?:\s*\(|$)/i);
      if (match) {
        const first = match[1].replace(/^.*?: /, '').trim();
        const second = match[2].trim();
        if (index === 0 && isCleanName(first)) return first;
        if (index === 1 && isCleanName(second)) return second;
      }
    }
    return defaultFallback;
  };

  const labelA = getCleanLabel(statA, caseData?.manifest?.regions?.[0] || caseData?.manifest?.region_a, 0, 'Region A');
  const labelB = getCleanLabel(statB, caseData?.manifest?.regions?.[1] || caseData?.manifest?.region_b, 1, 'Region B');

  const shortLabelA = (labelA.split('(')[0] || labelA).trim();
  const shortLabelB = (labelB.split('(')[0] || labelB).trim();

  const slopeA = statA?.mann_kendall?.sens_slope_per_decade;
  const slopeB = statB?.mann_kendall?.sens_slope_per_decade;
  const unit = statistics?.unit || caseData?.manifest?.unit || '°C';
  const varName = statistics?.variable_name || caseData?.manifest?.variable_name || 'Value';

  const totalA = statA?.mann_kendall?.total_estimated_change 
    ?? statA?.mann_kendall?.total_change 
    ?? (slopeA != null ? slopeA * 2.5 : 0);
  const totalB = statB?.mann_kendall?.total_estimated_change 
    ?? statB?.mann_kendall?.total_change 
    ?? (slopeB != null ? slopeB * 2.5 : 0);
  const netDelta = Math.abs(totalA - totalB);

  // Helper to slice arrays strictly within active time window
  const filterByYearRange = (dates, values, startY, endY) => {
    if (!dates || !values || !Array.isArray(dates) || !Array.isArray(values)) {
      return { dates: [], values: [] };
    }
    const minDate = `${startY}-01-01`;
    const maxDate = `${endY}-12-31`;
    const outD = [];
    const outV = [];
    const len = Math.min(dates.length, values.length);
    for (let i = 0; i < len; i++) {
      const d = dates[i];
      if (d >= minDate && d <= maxDate) {
        outD.push(d);
        outV.push(values[i]);
      }
    }
    return { dates: outD, values: outV };
  };

  // Pre-populate hoverData so the Telemetry Oscilloscope ticker displays live data immediately
  useEffect(() => {
    if (!statA && !caseData?.regions_data) return;
    const regKeys = caseData?.regions_data ? Object.keys(caseData.regions_data) : [];
    const rA = caseData?.regions_data && regKeys[0] ? caseData.regions_data[regKeys[0]] : null;
    const rB = caseData?.regions_data && regKeys[1] ? caseData.regions_data[regKeys[1]] : null;

    const datesA = statA?.dates || (rA ? rA.dates : []);
    const valsA = statA?.trend || statA?.deseasonalized || (rA ? rA.values : []);
    const datesB = statB?.dates || (rB ? rB.dates : []);
    const valsB = statB?.trend || statB?.deseasonalized || (rB ? rB.values : []);

    const filteredA = filterByYearRange(datesA, valsA, startYear, endYear);
    const filteredB = filterByYearRange(datesB, valsB, startYear, endYear);

    if (filteredA.dates.length > 0) {
      const lastIdxA = filteredA.dates.length - 1;
      const lastIdxB = filteredB.dates.length - 1;
      setHoverData({
        date: filteredA.dates[lastIdxA],
        valA: filteredA.values[lastIdxA],
        valB: filteredB.values[lastIdxB] ?? null,
      });
    }
  }, [statA, statB, caseData, startYear, endYear]);

  // -------------------------------------------------------------------------
  // Main Plotly Chart Construction
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const traces = [];

    // Bespoke Industrial & Editorial Palette
    const colorA = isLight ? '#C84B31' : '#00E5FF'; // Terracotta (warm) / Cyan (telemetry)
    const colorB = isLight ? '#1B6B50' : '#FF6B00'; // Botanical Viridian / Amber-Orange
    const colorCustom = isLight ? '#1B6B50' : '#00E5FF';

    let unitStr = unit;
    let titleVar = varName;

    // 1. Plot Custom Live Data if active
    if (customData) {
      unitStr = customData.unit || 'units';
      titleVar = customData.variable_name || customData.variable_id || 'Value';

      const rawC = filterByYearRange(customData.dates, customData.observed, startYear, endYear);
      const trendC = filterByYearRange(customData.dates, customData.trend || customData.deseasonalized, startYear, endYear);
      const deseasonC = filterByYearRange(customData.dates, customData.deseasonalized, startYear, endYear);
      const trendlineC = filterByYearRange(customData.dates, customData.trend_line, startYear, endYear);
      const ciUpperC = filterByYearRange(customData.dates, customData.ci_band_upper, startYear, endYear);
      const ciLowerC = filterByYearRange(customData.dates, customData.ci_band_lower, startYear, endYear);

      if (isLight) {
        // STUDENT MODE: Thick smooth trend ribbon
        if (showRawZigZags && rawC.values.length > 0) {
          traces.push({
            x: rawC.dates,
            y: rawC.values,
            name: `${customData.region_label} (Summer/Winter Zig-Zags)`,
            type: 'scatter',
            mode: 'lines',
            line: { color: colorCustom, width: 1.2, dash: 'dot' },
            opacity: 0.45,
            hovertemplate: '%{x}<br>Seasonal: %{y:.3f} ' + unitStr + '<extra></extra>',
          });
        }
        traces.push({
          x: trendC.dates,
          y: trendC.values,
          name: `${customData.region_label} (Clean Trend)`,
          type: 'scatter',
          mode: 'lines',
          line: { color: colorCustom, width: 4.5, shape: 'spline' },
          hovertemplate: '%{x}<br>Trend: %{y:.3f} ' + unitStr + '<extra></extra>',
        });
      } else {
        // SCIENTIST MODE: Multi-layer telemetry
        if (showConfidenceBand && ciUpperC.values.length > 0 && ciLowerC.values.length > 0) {
          traces.push({
            x: [...ciUpperC.dates, ...[...ciLowerC.dates].reverse()],
            y: [...ciUpperC.values, ...[...ciLowerC.values].reverse()],
            fill: 'toself',
            fillcolor: 'rgba(16, 185, 129, 0.22)',
            line: { color: 'transparent' },
            name: '95% CI Mean Response Cone',
            showlegend: false,
            type: 'scatter',
            hoverinfo: 'skip',
          });
        }
        if (showRaw && rawC.values.length > 0) {
          traces.push({
            x: rawC.dates,
            y: rawC.values,
            name: `${customData.region_label} (Raw Observed)`,
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: colorCustom, width: 1.0 },
            marker: { size: 2.5, opacity: 0.5 },
            opacity: 0.4,
            hovertemplate: '%{x}<br>Observed: %{y:.3f} ' + unitStr + '<extra></extra>',
          });
        }
        if (showDeseasonalized && deseasonC.values.length > 0) {
          traces.push({
            x: deseasonC.dates,
            y: deseasonC.values,
            name: `${customData.region_label} (Deseasonalized)`,
            type: 'scatter',
            mode: 'lines',
            line: { color: colorCustom, width: 2.0 },
            hovertemplate: '%{x}<br>Deseasonalized: %{y:.3f} ' + unitStr + '<extra></extra>',
          });
        }
        if (trendC.values.length > 0) {
          traces.push({
            x: trendC.dates,
            y: trendC.values,
            name: `${customData.region_label} (Loess STL Trend T_t)`,
            type: 'scatter',
            mode: 'lines',
            line: { color: colorCustom, width: 3.5 },
            hovertemplate: '%{x}<br>Loess Trend: %{y:.3f} ' + unitStr + '<extra></extra>',
          });
        }
        if (showSensSlope && trendlineC.values.length > 0) {
          traces.push({
            x: trendlineC.dates,
            y: trendlineC.values,
            name: `${customData.region_label} (Sen's Median Slope)`,
            type: 'scatter',
            mode: 'lines',
            line: { color: '#34D399', width: 2.5, dash: 'dash' },
            hovertemplate: '%{x}<br>Sen Linear: %{y:.3f} ' + unitStr + '<extra></extra>',
          });
        }
      }
    } 
    // 2. Preset or Two-Region Case Studies
    else if (caseData && caseData.regions_data) {
      unitStr = caseData.manifest?.unit || 'units';
      titleVar = caseData.manifest?.variable_name || caseData.manifest?.variable_id || 'Value';

      const regKeys = Object.keys(caseData.regions_data);
      const rA = caseData.regions_data[regKeys[0]];
      const rB = regKeys[1] ? caseData.regions_data[regKeys[1]] : null;

      const datesA = statA?.dates || (rA ? rA.dates : []);
      const rawA = rA ? filterByYearRange(rA.dates, rA.values, startYear, endYear) : { dates: [], values: [] };
      const trendA = filterByYearRange(datesA, statA?.trend || statA?.deseasonalized || (rA ? rA.values : []), startYear, endYear);
      const deseasonA = filterByYearRange(datesA, statA?.deseasonalized, startYear, endYear);
      const trendlineA = filterByYearRange(datesA, statA?.trend_line, startYear, endYear);
      const ciUpperA = filterByYearRange(datesA, statA?.ci_band_upper, startYear, endYear);
      const ciLowerA = filterByYearRange(datesA, statA?.ci_band_lower, startYear, endYear);

      const datesB = statB?.dates || (rB ? rB.dates : []);
      const rawB = rB ? filterByYearRange(rB.dates, rB.values, startYear, endYear) : { dates: [], values: [] };
      const trendB = filterByYearRange(datesB, statB?.trend || statB?.deseasonalized || (rB ? rB.values : []), startYear, endYear);
      const deseasonB = filterByYearRange(datesB, statB?.deseasonalized, startYear, endYear);
      const trendlineB = filterByYearRange(datesB, statB?.trend_line, startYear, endYear);
      const ciUpperB = filterByYearRange(datesB, statB?.ci_band_upper, startYear, endYear);
      const ciLowerB = filterByYearRange(datesB, statB?.ci_band_lower, startYear, endYear);

      if (isLight) {
        // ===================================================================
        // 🎓 STUDENT MODE: Smooth Loess STL Trend Ribbon (Clean & Uncluttered)
        // ===================================================================
        if (rA) {
          if (showRawZigZags && rawA.values.length > 0) {
            traces.push({
              x: rawA.dates,
              y: rawA.values,
              name: `${labelA} (Summer/Winter Zig-Zags)`,
              type: 'scatter',
              mode: 'lines',
              line: { color: colorA, width: 1.2, dash: 'dot' },
              opacity: 0.35,
              hovertemplate: '%{x}<br>Observed: %{y:.2f} ' + unitStr + '<extra></extra>',
            });
          }
          if (trendA.values.length > 0) {
            traces.push({
              x: trendA.dates,
              y: trendA.values,
              name: `${labelA} (Clean Multi-Year Trend)`,
              type: 'scatter',
              mode: 'lines',
              line: { color: colorA, width: 4.5, shape: 'spline' },
              hovertemplate: '%{x}<br>Trend: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
        }

        if (rB) {
          if (showRawZigZags && rawB.values.length > 0) {
            traces.push({
              x: rawB.dates,
              y: rawB.values,
              name: `${labelB} (Summer/Winter Zig-Zags)`,
              type: 'scatter',
              mode: 'lines',
              line: { color: colorB, width: 1.2, dash: 'dot' },
              opacity: 0.35,
              hovertemplate: '%{x}<br>Observed: %{y:.2f} ' + unitStr + '<extra></extra>',
            });
          }
          if (trendB.values.length > 0) {
            traces.push({
              x: trendB.dates,
              y: trendB.values,
              name: `${labelB} (Clean Multi-Year Trend)`,
              type: 'scatter',
              mode: 'lines',
              line: { color: colorB, width: 4.5, shape: 'spline' },
              hovertemplate: '%{x}<br>Trend: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
        }
      } else {
        // ===================================================================
        // 🔬 SCIENTIST MODE: Multi-Layer Telemetry & 95% Confidence Cones
        // ===================================================================
        // Region A
        if (rA) {
          if (showConfidenceBand && ciUpperA.values.length > 0 && ciLowerA.values.length > 0) {
            traces.push({
              x: [...ciUpperA.dates, ...[...ciLowerA.dates].reverse()],
              y: [...ciUpperA.values, ...[...ciLowerA.values].reverse()],
              fill: 'toself',
              fillcolor: 'rgba(56, 189, 248, 0.22)',
              line: { color: 'transparent' },
              name: `${labelA} 95% CI Cone`,
              meta: { region: 'A', traceType: 'ci' },
              showlegend: false,
              type: 'scatter',
              hoverinfo: 'skip',
            });
          }
          if (showRaw && rawA.values.length > 0) {
            traces.push({
              x: rawA.dates,
              y: rawA.values,
              name: `${labelA} (Raw Observations)`,
              meta: { region: 'A', traceType: 'raw' },
              type: 'scatter',
              mode: 'lines+markers',
              line: { color: colorA, width: 1.0 },
              marker: { size: 2.5, opacity: 0.5 },
              opacity: 0.35,
              hovertemplate: '%{x}<br>Observed: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
          if (showDeseasonalized && deseasonA.values.length > 0) {
            traces.push({
              x: deseasonA.dates,
              y: deseasonA.values,
              name: `${labelA} (Deseasonalized)`,
              meta: { region: 'A', traceType: 'deseasonalized' },
              type: 'scatter',
              mode: 'lines',
              line: { color: colorA, width: 2.0 },
              opacity: 0.85,
              hovertemplate: '%{x}<br>Deseasonalized: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
          if (trendA.values.length > 0) {
            traces.push({
              x: trendA.dates,
              y: trendA.values,
              name: `${labelA} (Loess STL Trend T_t)`,
              meta: { region: 'A', traceType: 'trend' },
              type: 'scatter',
              mode: 'lines',
              line: { color: colorA, width: 3.5 },
              hovertemplate: '%{x}<br>Loess Trend: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
          if (showSensSlope && trendlineA.values.length > 0) {
            traces.push({
              x: trendlineA.dates,
              y: trendlineA.values,
              name: `${labelA} (Sen's Median Trend)`,
              meta: { region: 'A', traceType: 'sen' },
              type: 'scatter',
              mode: 'lines',
              line: { color: '#38BDF8', width: 2.5, dash: 'dash' },
              hovertemplate: '%{x}<br>Sen Slope: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
        }

        // Region B
        if (rB) {
          if (showConfidenceBand && ciUpperB.values.length > 0 && ciLowerB.values.length > 0) {
            traces.push({
              x: [...ciUpperB.dates, ...[...ciLowerB.dates].reverse()],
              y: [...ciUpperB.values, ...[...ciLowerB.values].reverse()],
              fill: 'toself',
              fillcolor: 'rgba(249, 115, 22, 0.22)',
              line: { color: 'transparent' },
              name: `${labelB} 95% CI Cone`,
              meta: { region: 'B', traceType: 'ci' },
              showlegend: false,
              type: 'scatter',
              hoverinfo: 'skip',
            });
          }
          if (showRaw && rawB.values.length > 0) {
            traces.push({
              x: rawB.dates,
              y: rawB.values,
              name: `${labelB} (Raw Observations)`,
              meta: { region: 'B', traceType: 'raw' },
              type: 'scatter',
              mode: 'lines+markers',
              line: { color: colorB, width: 1.0 },
              marker: { size: 2.5, opacity: 0.5 },
              opacity: 0.35,
              hovertemplate: '%{x}<br>Observed: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
          if (showDeseasonalized && deseasonB.values.length > 0) {
            traces.push({
              x: deseasonB.dates,
              y: deseasonB.values,
              name: `${labelB} (Deseasonalized)`,
              meta: { region: 'B', traceType: 'deseasonalized' },
              type: 'scatter',
              mode: 'lines',
              line: { color: colorB, width: 2.0 },
              opacity: 0.85,
              hovertemplate: '%{x}<br>Deseasonalized: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
          if (trendB.values.length > 0) {
            traces.push({
              x: trendB.dates,
              y: trendB.values,
              name: `${labelB} (Loess STL Trend T_t)`,
              meta: { region: 'B', traceType: 'trend' },
              type: 'scatter',
              mode: 'lines',
              line: { color: colorB, width: 3.5 },
              hovertemplate: '%{x}<br>Loess Trend: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
          if (showSensSlope && trendlineB.values.length > 0) {
            traces.push({
              x: trendlineB.dates,
              y: trendlineB.values,
              name: `${labelB} (Sen's Median Trend)`,
              meta: { region: 'B', traceType: 'sen' },
              type: 'scatter',
              mode: 'lines',
              line: { color: '#FB923C', width: 2.5, dash: 'dash' },
              hovertemplate: '%{x}<br>Sen Slope: %{y:.3f} ' + unitStr + '<extra></extra>',
            });
          }
        }
      }
    }

    const layout = {
      autosize: true,
      height: isLight ? 360 : 340,
      margin: isLight 
        ? { l: typeof window !== 'undefined' && window.innerWidth < 640 ? 45 : 60, r: 20, t: 25, b: 50 }
        : { l: typeof window !== 'undefined' && window.innerWidth < 640 ? 45 : 60, r: 20, t: 20, b: 60 },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {
        family: isLight ? '"Plus Jakarta Sans", system-ui, sans-serif' : '"JetBrains Mono", monospace',
        color: isLight ? '#141E19' : '#94A3B8',
        size: 11,
      },
      showlegend: true,
      legend: {
        orientation: 'h',
        y: -0.2,
        x: 0.5,
        xanchor: 'center',
        font: { size: 10, color: isLight ? '#141E19' : '#94A3B8' },
      },
      xaxis: {
        type: 'date',
        range: [`${startYear}-01-01`, `${endYear}-12-31`],
        showgrid: true,
        gridcolor: isLight ? '#DCD7C9' : '#1E2636',
        zerolinecolor: isLight ? '#DCD7C9' : '#1E2636',
      },
      yaxis: {
        title: { text: `${titleVar} (${unitStr})`, font: { size: 10 } },
        showgrid: true,
        gridcolor: isLight ? '#DCD7C9' : '#1E2636',
        zerolinecolor: isLight ? '#DCD7C9' : '#1E2636',
      },
      hovermode: 'x unified',
    };

    const config = {
      responsive: true,
      displayModeBar: false,
    };

    Plotly.react(chartContainerRef.current, traces, layout, config).then(() => {
      const el = chartContainerRef.current;
      if (el && el.on) {
        if (el.removeAllListeners) {
          el.removeAllListeners('plotly_hover');
        }
        el.on('plotly_hover', (evt) => {
          if (!evt || !evt.points || evt.points.length === 0) return;
          const date = evt.points[0].x;
          let valA = null;
          let valB = null;

          for (const p of evt.points) {
            const reg = p.data?.meta?.region;
            const traceType = p.data?.meta?.traceType;
            const nm = p.data?.name || '';
            const y = p.y;
            if (y == null || isNaN(y)) continue;

            if (reg === 'A' || nm.includes(shortLabelA) || nm.includes(labelA) || nm.includes('Region A')) {
              if (valA === null || traceType === 'trend' || traceType === 'deseasonalized') {
                valA = y;
              }
            } else if (reg === 'B' || nm.includes(shortLabelB) || nm.includes(labelB) || nm.includes('Region B')) {
              if (valB === null || traceType === 'trend' || traceType === 'deseasonalized') {
                valB = y;
              }
            }
          }

          if (valA === null && evt.points[0]?.y != null) {
            valA = evt.points[0].y;
          }
          if (valB === null && evt.points[1]?.y != null) {
            valB = evt.points[1].y;
          }

          setHoverData({
            date: typeof date === 'string' ? date : String(date),
            valA,
            valB,
          });
        });
      }
    });

    return () => {
      if (chartContainerRef.current) {
        if (chartContainerRef.current.removeAllListeners) {
          chartContainerRef.current.removeAllListeners('plotly_hover');
        }
        Plotly.purge(chartContainerRef.current);
      }
    };
  }, [
    caseData, statistics, customData, isLight, showRawZigZags, 
    showRaw, showDeseasonalized, showSensSlope, showConfidenceBand,
    startYear, endYear
  ]);

  // -------------------------------------------------------------------------
  // Scientist Mode: 3-Column STL Sub-Component Mini-Chart Strip
  // -------------------------------------------------------------------------
  useEffect(() => {
    if (isLight) return;
    if (!statA || !statB) return;

    const dates = statA.dates || [];
    const colorA = '#38BDF8';
    const colorB = '#FB923C';

    const sliceT_A = filterByYearRange(dates, statA.trend, startYear, endYear);
    const sliceT_B = filterByYearRange(dates, statB.trend, startYear, endYear);
    const sliceS_A = filterByYearRange(dates, statA.seasonal, startYear, endYear);
    const sliceS_B = filterByYearRange(dates, statB.seasonal, startYear, endYear);
    const sliceR_A = filterByYearRange(dates, statA.residual, startYear, endYear);
    const sliceR_B = filterByYearRange(dates, statB.residual, startYear, endYear);

    const miniConfig = { responsive: true, displayModeBar: false };
    const miniLayoutBase = {
      autosize: true,
      height: 140,
      margin: { l: 40, r: 15, t: 15, b: 25 },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { color: '#94A3B8', size: 9 },
      showlegend: false,
      xaxis: { 
        showgrid: true, 
        gridcolor: '#1E293B',
        range: [`${startYear}-01-01`, `${endYear}-12-31`],
      },
      yaxis: { showgrid: true, gridcolor: '#1E293B' },
      hovermode: 'x unified',
    };

    // 1. Panel A: Multi-Decadal Trend (T_t)
    if (trendSubplotRef.current && sliceT_A.values.length > 0 && sliceT_B.values.length > 0) {
      const tracesT = [
        {
          x: sliceT_A.dates,
          y: sliceT_A.values,
          name: labelA,
          type: 'scatter',
          mode: 'lines',
          line: { color: colorA, width: 2.5 },
        },
        {
          x: sliceT_B.dates,
          y: sliceT_B.values,
          name: labelB,
          type: 'scatter',
          mode: 'lines',
          line: { color: colorB, width: 2.5 },
        },
      ];
      Plotly.react(trendSubplotRef.current, tracesT, { ...miniLayoutBase }, miniConfig);
    }

    // 2. Panel B: 12-Month Seasonal Cycle (S_t)
    if (seasonalSubplotRef.current && sliceS_A.values.length > 0 && sliceS_B.values.length > 0) {
      const tracesS = [
        {
          x: sliceS_A.dates,
          y: sliceS_A.values,
          name: `${labelA} Seasonality`,
          type: 'scatter',
          mode: 'lines',
          line: { color: colorA, width: 1.8 },
        },
        {
          x: sliceS_B.dates,
          y: sliceS_B.values,
          name: `${labelB} Seasonality`,
          type: 'scatter',
          mode: 'lines',
          line: { color: colorB, width: 1.8 },
        },
      ];
      Plotly.react(seasonalSubplotRef.current, tracesS, { ...miniLayoutBase }, miniConfig);
    }

    // 3. Panel C: Stochastic Residuals & Anomalies (R_t)
    if (residualSubplotRef.current && sliceR_A.values.length > 0 && sliceR_B.values.length > 0) {
      const resA = sliceR_A.values || [];
      const varianceA = resA.reduce((sum, v) => sum + v * v, 0) / (resA.length || 1);
      const sigma2 = 2 * Math.sqrt(varianceA);

      const tracesR = [
        {
          x: sliceR_A.dates,
          y: sliceR_A.values,
          name: `${labelA} Residual`,
          type: 'scatter',
          mode: 'lines',
          line: { color: colorA, width: 1.2 },
          opacity: 0.7,
        },
        {
          x: sliceR_B.dates,
          y: sliceR_B.values,
          name: `${labelB} Residual`,
          type: 'scatter',
          mode: 'lines',
          line: { color: colorB, width: 1.2 },
          opacity: 0.7,
        },
        {
          x: [sliceR_A.dates[0], sliceR_A.dates[sliceR_A.dates.length - 1]],
          y: [sigma2, sigma2],
          name: '+2σ Anomaly Threshold',
          type: 'scatter',
          mode: 'lines',
          line: { color: '#EF4444', dash: 'dot', width: 1.5 },
          hoverinfo: 'name+y',
        },
        {
          x: [sliceR_A.dates[0], sliceR_A.dates[sliceR_A.dates.length - 1]],
          y: [-sigma2, -sigma2],
          name: '-2σ Anomaly Threshold',
          type: 'scatter',
          mode: 'lines',
          line: { color: '#EF4444', dash: 'dot', width: 1.5 },
          hoverinfo: 'name+y',
        },
      ];
      Plotly.react(residualSubplotRef.current, tracesR, { ...miniLayoutBase }, miniConfig);
    }

    return () => {
      if (trendSubplotRef.current) Plotly.purge(trendSubplotRef.current);
      if (seasonalSubplotRef.current) Plotly.purge(seasonalSubplotRef.current);
      if (residualSubplotRef.current) Plotly.purge(residualSubplotRef.current);
    };
  }, [isLight, statA, statB, labelA, labelB, startYear, endYear]);

  // Significance Simulator Metrics
  const windowYears = endYear - startYear + 1;
  const isSignificant = windowYears >= 8 && (statA?.mann_kendall?.is_significant || statB?.mann_kendall?.is_significant || statA?.mann_kendall?.p_value < 0.05);

  const handleApplyPresetWindow = (start, end) => {
    setStartYear(start);
    setEndYear(end);
    if (onTimeWindowChange) {
      onTimeWindowChange(start, end);
    }
  };

  return (
    <div className="space-y-4">
      {/* ------------------------------------------------------------------- */}
      {/* Main Chart Container                                                */}
      {/* ------------------------------------------------------------------- */}
      <div className={`transition-all ${
        isLight 
          ? 'p-5 rounded-xl border border-[#DCD7C9] bg-[#FAF8F5] text-archival-ink shadow-none' 
          : 'p-0 border-0 bg-[#0C1017] text-obsidian-text rounded-none shadow-none'
      }`}>
        {/* 🔬 Scientist Exclusive Live Hover Readout Strip */}
        {!isLight && (
          <div className="h-8 px-4 bg-[#0A0E15] border-b border-[#1E2636] flex items-center justify-between text-[11px] font-mono text-slate-300">
            <div className="flex items-center space-x-3 overflow-hidden text-ellipsis whitespace-nowrap">
              <span className="text-slate-500 font-bold">OSCILLOSCOPE:</span>
              <span className="text-cyan-400">
                DATE: <span className="text-white font-bold">{hoverData?.date || 'HOVER ON TRACE'}</span>
              </span>
              <span className="text-cyan-400">
                {shortLabelA}: <span className="text-white font-bold">{hoverData?.valA != null ? Number(hoverData.valA).toFixed(3) : '--'} {unit}</span>
              </span>
              <span className="text-amber-400">
                {shortLabelB}: <span className="text-white font-bold">{hoverData?.valB != null ? Number(hoverData.valB).toFixed(3) : '--'} {unit}</span>
              </span>
              {hoverData?.valA != null && hoverData?.valB != null && (
                <span className="text-emerald-400">
                  Δ: <span className="text-white font-bold">{(hoverData.valA - hoverData.valB > 0 ? '+' : '') + (hoverData.valA - hoverData.valB).toFixed(3)} {unit}</span>
                </span>
              )}
            </div>
            <div className="flex items-center space-x-1.5 text-[10px] text-slate-500">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="hidden sm:inline">LIVE TELEMETRY HOVER</span>
            </div>
          </div>
        )}
        {/* Top Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b gap-3 mb-3 border-slate-100 dark:border-slate-800">
          <div>
            <h3 className="text-sm font-bold flex items-center space-x-2 text-slate-900 dark:text-white">
              <TrendingUp className="w-4 h-4 text-blue-500" />
              <span>{isLight ? 'Multi-Decadal Trajectory Comparison' : 'Loess STL Multi-Layer Telemetry'}</span>
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              {isLight 
                ? 'Smooth deseasonalized multi-year trend curve (annual seasonal swings removed)'
                : 'Loess STL Decomposition + Sen Non-Parametric Median Slope + 95% OLS Response Cone'
              }
            </p>
          </div>

          {/* 🎓 Student Mode: Educational Zig-Zag Toggle */}
          {isLight && (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowRawZigZags(!showRawZigZags)}
                className={`px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all flex items-center space-x-1.5 ${
                  showRawZigZags
                    ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                    : 'bg-slate-100 hover:bg-slate-200 text-slate-700 border-slate-200'
                }`}
              >
                <Activity className="w-3.5 h-3.5" />
                <span>{showRawZigZags ? 'Hide Raw Zig-Zags' : 'Show Raw Summer/Winter Zig-Zags'}</span>
              </button>
            </div>
          )}

          {/* 🔬 Scientist Layer Toggles */}
          {!isLight && (
            <div className="flex items-center space-x-1.5 text-xs">
              <button
                onClick={() => setShowRaw(!showRaw)}
                className={`px-2 py-1 rounded border text-[11px] font-medium transition-colors ${
                  showRaw ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}
              >
                Raw Monthly
              </button>
              <button
                onClick={() => setShowDeseasonalized(!showDeseasonalized)}
                className={`px-2 py-1 rounded border text-[11px] font-medium transition-colors ${
                  showDeseasonalized ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}
              >
                Deseasonalized
              </button>
              <button
                onClick={() => setShowSensSlope(!showSensSlope)}
                className={`px-2 py-1 rounded border text-[11px] font-medium transition-colors ${
                  showSensSlope ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}
              >
                Sen Slope
              </button>
              <button
                onClick={() => setShowConfidenceBand(!showConfidenceBand)}
                className={`px-2 py-1 rounded border text-[11px] font-medium transition-colors ${
                  showConfidenceBand ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' : 'bg-slate-800 text-slate-400 border-slate-700'
                }`}
              >
                95% CI Cone
              </button>
            </div>
          )}
        </div>

        {/* 🎓 Student Educational Callout when Raw Zig-Zags are shown */}
        {isLight && showRawZigZags && (
          <div className="mb-3 p-2.5 rounded-xl bg-blue-50 border border-blue-200 text-blue-900 text-xs flex items-center space-x-2 animate-fadeIn">
            <Lightbulb className="w-4 h-4 text-amber-500 flex-shrink-0" />
            <span>
              <strong>NASA Science Clue:</strong> Natural summer-winter temperature swings bounce up and down by ±15°C every year. The thick smooth line is the <em>mathematical truth</em> with those seasonal swings filtered out!
            </span>
          </div>
        )}

        {/* Interactive Time-Window Scrubber & Significance Simulator */}
        <div className={`p-3 rounded-lg mb-3 border text-xs flex flex-col md:flex-row md:items-center justify-between gap-3 ${
          isLight ? 'bg-white border-[#DCD7C9] text-archival-ink' : 'bg-[#07090E] border-[#1E2636] text-obsidian-text'
        }`}>
          <div className="flex items-center space-x-3">
            <Clock className="w-4 h-4 text-blue-500 dark:text-cyan-400 flex-shrink-0" />
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold">Time-Window Significance Scrubber:</span>
                <span className={`font-mono text-[11px] font-bold px-2 py-0.5 rounded ${
                  isLight ? 'bg-archival-sand text-archival-ink border border-[#DCD7C9]' : 'bg-slate-800 text-cyan-300'
                }`}>
                  {startYear}–{endYear} ({windowYears} yrs)
                </span>
              </div>
              <div className="flex items-center space-x-1.5 mt-1 font-mono text-[11px]">
                <span className="text-archival-muted dark:text-slate-500">Lens:</span>
                <button
                  onClick={() => handleApplyPresetWindow(2020, 2025)}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    startYear === 2020 && endYear === 2025
                      ? 'bg-archival-ink text-white font-bold dark:bg-cyan-500 dark:text-slate-950'
                      : isLight ? 'bg-archival-sand/60 text-archival-ink hover:bg-archival-sand' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  ⚡ 5-Yr Noise
                </button>
                <button
                  onClick={() => handleApplyPresetWindow(2015, 2025)}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    startYear === 2015 && endYear === 2025
                      ? 'bg-archival-ink text-white font-bold dark:bg-cyan-500 dark:text-slate-950'
                      : isLight ? 'bg-archival-sand/60 text-archival-ink hover:bg-archival-sand' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  📈 10-Yr Lens
                </button>
                <button
                  onClick={() => handleApplyPresetWindow(2001, 2025)}
                  className={`px-2 py-0.5 rounded transition-colors ${
                    startYear === 2001 && endYear === 2025
                      ? 'bg-archival-ink text-white font-bold dark:bg-cyan-500 dark:text-slate-950'
                      : isLight ? 'bg-archival-sand/60 text-archival-ink hover:bg-archival-sand' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  🌐 Full 25-Yr Baseline
                </button>
              </div>
            </div>
          </div>

          {/* Live Significance Verdict Badge */}
          <div className={`px-2.5 py-1 rounded-md border font-mono text-[11px] flex items-center space-x-1.5 ${
            isSignificant
              ? 'bg-emerald-50 text-emerald-800 border-emerald-300 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
              : 'bg-amber-50 text-amber-800 border-amber-300 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-800'
          }`}>
            {isSignificant ? (
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
            ) : (
              <AlertTriangle className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 flex-shrink-0" />
            )}
            <span>
              {isSignificant 
                ? 'p < 0.05: Statistically Significant Signal' 
                : 'p ≥ 0.05: Masked by Weather Noise'}
            </span>
          </div>
        </div>

        {/* Plotly Chart Container */}
        <div ref={chartContainerRef} className="w-full min-h-[340px] overflow-hidden" />

        {/* ----------------------------------------------------------------- */}
        {/* 🎓 STUDENT MODE: 2-Column "25-Year Cumulative Shift" Visual Bars   */}
        {/* ----------------------------------------------------------------- */}
        {isLight && (
          <div className="mt-4 pt-4 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-3">
            {/* Region A Summary Bar */}
            <div className="p-3.5 rounded-xl bg-blue-50/70 border border-blue-200/80 flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="font-bold text-blue-900 flex items-center space-x-1.5">
                  {totalA >= 0 ? <Flame className="w-4 h-4 text-rose-500" /> : <Snowflake className="w-4 h-4 text-cyan-600" />}
                  <span>{labelA}</span>
                </span>
                <span className={`font-mono font-extrabold text-xs px-2 py-0.5 rounded-full ${
                  totalA >= 0 ? 'bg-rose-100 text-rose-800' : 'bg-blue-100 text-blue-800'
                }`}>
                  {totalA > 0 ? `+${totalA.toFixed(2)}` : totalA.toFixed(2)} {unit} over 25 yrs
                </span>
              </div>
              <div className="w-full bg-blue-200/50 rounded-full h-2.5 overflow-hidden">
                <div 
                  className={`h-2.5 rounded-full transition-all duration-500 ${
                    totalA >= 0 ? 'bg-rose-500' : 'bg-cyan-500'
                  }`}
                  style={{ width: `${Math.min(100, Math.max(15, Math.abs(totalA) * 45))}%` }}
                />
              </div>
              <div className="mt-2 text-[11px] text-blue-800">
                {totalA >= 0 ? 'Warming Velocity' : 'Cooling Velocity'}: <strong>{slopeA > 0 ? `+${slopeA}` : slopeA} {unit}/decade</strong>
              </div>
            </div>

            {/* Region B Summary Bar */}
            <div className="p-3.5 rounded-xl bg-orange-50/70 border border-orange-200/80 flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="font-bold text-orange-900 flex items-center space-x-1.5">
                  {totalB >= 0 ? <Flame className="w-4 h-4 text-rose-500" /> : <Snowflake className="w-4 h-4 text-cyan-600" />}
                  <span>{labelB}</span>
                </span>
                <span className={`font-mono font-extrabold text-xs px-2 py-0.5 rounded-full ${
                  totalB >= 0 ? 'bg-rose-100 text-rose-800' : 'bg-cyan-100 text-cyan-800'
                }`}>
                  {totalB > 0 ? `+${totalB.toFixed(2)}` : totalB.toFixed(2)} {unit} over 25 yrs
                </span>
              </div>
              <div className="w-full bg-orange-200/50 rounded-full h-2.5 overflow-hidden">
                <div 
                  className={`h-2.5 rounded-full transition-all duration-500 ${
                    totalB >= 0 ? 'bg-rose-500' : 'bg-cyan-500'
                  }`}
                  style={{ width: `${Math.min(100, Math.max(15, Math.abs(totalB) * 45))}%` }}
                />
              </div>
              <div className="mt-2 text-[11px] text-orange-800">
                {totalB >= 0 ? 'Warming Velocity' : 'Cooling Velocity'}: <strong>{slopeB > 0 ? `+${slopeB}` : slopeB} {unit}/decade</strong>
              </div>
            </div>
          </div>
        )}

        {/* ----------------------------------------------------------------- */}
        {/* 🔬 SCIENTIST MODE EXCLUSIVE: 3-Column STL Decomposition Strip     */}
        {/* ----------------------------------------------------------------- */}
        {!isLight && (
          <div className="mt-5 pt-4 border-t border-slate-800">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <BarChart2 className="w-4 h-4 text-cyan-400" />
                <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                  STL Decomposition Tri-Panel Analysis (T_t, S_t, R_t)
                </h4>
              </div>
              <span className="text-[10px] font-mono text-slate-400">
                Cleveland et al. Loess Deseasonalization
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Panel A: Multi-Decadal Trend (T_t) */}
              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-[11px] text-cyan-300 font-mono">
                    1. Trend Component (T_t)
                  </span>
                  <span className="text-[9px] font-mono text-slate-500">Decadal Slope</span>
                </div>
                <div ref={trendSubplotRef} className="w-full" />
                <div className="text-[10px] text-slate-400 font-mono flex items-center justify-between mt-1 pt-1 border-t border-slate-900">
                  <span className="text-cyan-400">A: {slopeA > 0 ? `+${slopeA}` : slopeA}</span>
                  <span className="text-orange-400">B: {slopeB > 0 ? `+${slopeB}` : slopeB}</span>
                </div>
              </div>

              {/* Panel B: 12-Month Seasonal Cycle (S_t) */}
              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-[11px] text-cyan-300 font-mono">
                    2. Seasonal Cycle (S_t)
                  </span>
                  <span className="text-[9px] font-mono text-slate-500">Period = 12 Mo</span>
                </div>
                <div ref={seasonalSubplotRef} className="w-full" />
                <div className="text-[10px] text-slate-400 font-mono flex items-center justify-between mt-1 pt-1 border-t border-slate-900">
                  <span>Harmonic Forcing</span>
                  <span className="text-emerald-400">Stationary Mean</span>
                </div>
              </div>

              {/* Panel C: Stochastic Residuals & Anomalies (R_t) */}
              <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800/80 flex flex-col justify-between">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-[11px] text-cyan-300 font-mono">
                    3. Residual Spikes (R_t)
                  </span>
                  <span className="text-[9px] font-mono text-rose-400">±2σ Threshold</span>
                </div>
                <div ref={residualSubplotRef} className="w-full" />
                <div className="text-[10px] text-slate-400 font-mono flex items-center justify-between mt-1 pt-1 border-t border-slate-900">
                  <span className="text-rose-400">Dotted: ±2σ Boundary</span>
                  <span>ENSO / Spikes</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
