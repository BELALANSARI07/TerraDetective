import React from 'react';
import { X, BookOpen, ExternalLink, ShieldCheck, Database, Award, Sigma } from 'lucide-react';

export default function MethodologyDrawer({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] flex justify-end bg-slate-950/70 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-2xl bg-slate-900 border-l border-slate-750 h-full overflow-y-auto p-6 shadow-2xl flex flex-col justify-between space-y-6 relative z-10">
        <div>
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <BookOpen className="w-6 h-6 text-cyan-400" />
              <div>
                <h2 className="text-lg font-extrabold text-white">Scientific Methodology & Citations</h2>
                <p className="text-xs text-slate-400">NASA Space Apps 2026 — Earth System Trend Detective</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Section 1: Statistical Methodology */}
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold text-cyan-300">
              <Sigma className="w-4 h-4 text-cyan-400" />
              <h3>1. Statistical Architecture: STL Decomposition & Mann-Kendall</h3>
            </div>

            <div className="bg-slate-850 p-4 rounded-xl border border-slate-800 space-y-3 text-xs text-slate-300 leading-relaxed font-sans">
              <p>
                <strong className="text-white">STL Seasonal Decomposition:</strong> Uses Loess smoothing (Cleveland et al., 1990) with an exact periodic window of 12 months (<code className="font-mono text-cyan-300">period=12</code>) and robust outlier weighting. This isolates the non-linear multi-decadal trend <code className="font-mono text-cyan-300">T_t</code> from repetitive annual phenology <code className="font-mono text-emerald-300">S_t</code> and irregular climate shock residuals <code className="font-mono text-amber-300">R_t</code>:
              </p>
              <div className="bg-slate-950 p-3 rounded-lg font-mono text-center text-cyan-300 text-xs border border-slate-800">
                Y_t = T_t + S_t + R_t
              </div>

              <p>
                <strong className="text-white">Mann-Kendall Trend Test:</strong> A non-parametric rank correlation test evaluating monotonic trajectories without assuming normal distribution.
              </p>

              <p>
                <strong className="text-white">Sen's Median Slope per Decade:</strong> Calculated as the median of all pairwise observation slopes scaled by a factor of 120 (months) to produce standardized climate rate metrics per decade:
              </p>
              <div className="bg-slate-950 p-3 rounded-lg font-mono text-center text-cyan-300 text-xs border border-slate-800">
                Q_decade = Median((x_j - x_i) / (j - i)) × 120
              </div>

              <p>
                <strong className="text-white">NASA Missing Value & Key Filtering:</strong> Eliminates NASA missing data sentinel flags (<code className="font-mono text-rose-300">-999, -999.0, -9999.0, NaN</code>), aggregates 8-day MODIS LST to monthly averages, and strips NASA POWER's 13th month summary keys (<code className="font-mono text-amber-300">YYYY13</code>) prior to 12-month STL.
              </p>
            </div>
          </div>

          {/* Section 2: NASA & Partner Dataset Provenance */}
          <div className="mt-6 space-y-4">
            <div className="flex items-center gap-2 text-sm font-bold text-cyan-300">
              <Database className="w-4 h-4 text-cyan-400" />
              <h3>2. Data Provenance & Verified NASA Catalogs</h3>
            </div>

            <div className="space-y-3">
              {/* Giovanni GPM */}
              <div className="bg-slate-850 p-3.5 rounded-xl border border-slate-800 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-white">NASA Giovanni GPM IMERG Final Run (v07)</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">Precipitation Pillar</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Monthly area-averaged precipitation accumulation (0.1° × 0.1°) from the Global Precipitation Measurement constellation. Bounding boxes: Central India (75°E-77.5°E, 18°N-20.5°N) and Meghalaya (90.5°E-92.5°E, 24.5°N-26°N).
                </p>
                <a
                  href="https://giovanni.gsfc.nasa.gov/giovanni/"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] text-cyan-400 hover:underline pt-1"
                >
                  NASA Giovanni GES DISC Portal <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              {/* AppEEARS MODIS */}
              <div className="bg-slate-850 p-3.5 rounded-xl border border-slate-800 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-white">NASA AppEEARS MODIS (MOD11A2 & MOD13A3)</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">Thermal & Canopy Pillar</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Terra MODIS 1km 8-day Land Surface Temperature Day (MOD11A2.061) and 1km Monthly Vegetation Indices NDVI (MOD13A3.061) across Rondonia Amazon Arc and Punjab Irrigated Belt (2001-2025).
                </p>
                <a
                  href="https://appeears.earthdatacloud.nasa.gov/"
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] text-cyan-400 hover:underline pt-1"
                >
                  NASA AppEEARS Earthdata Cloud <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              {/* GLDAS Noah */}
              <div className="bg-slate-850 p-3.5 rounded-xl border border-slate-800 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-white">NASA GES DISC GLDAS Noah Hydrology (v2.1)</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800">Hydrology Pillar</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Global Land Data Assimilation System 0.25° monthly root zone soil moisture (0-100cm) and subsurface water storage deficit validating groundwater exhaustion behind vegetation greening paradoxes.
                </p>
                <span className="text-[10px] text-slate-500 font-mono block">Citation: Rodell et al., BAMS 2004.</span>
              </div>

              {/* NASA POWER & Partner Benchmarks */}
              <div className="bg-slate-850 p-3.5 rounded-xl border border-slate-800 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-xs text-white">NASA POWER, SWOT, CSA & KNMI Climate Explorer</span>
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800">Benchmarks</span>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  20-variable global climatology assimilation from NASA Langley Research Center (LaRC) / MERRA-2, cross-referenced with NASA Surface Water and Ocean Topography (SWOT), Canadian Space Agency (CSA RCM / Geo.ca), and Royal Netherlands Meteorological Institute (KNMI) climate series.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-mono">
          <span>TerraDetective v1.0.0</span>
          <span className="text-emerald-400 flex items-center gap-1">
            <ShieldCheck className="w-4 h-4" /> NASA Space Apps 2026 Verified
          </span>
        </div>
      </div>
    </div>
  );
}
