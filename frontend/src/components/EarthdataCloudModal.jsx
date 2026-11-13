import React, { useState, useEffect } from 'react';
import { X, ShieldCheck, Download, ExternalLink, Satellite, Layers, RefreshCw, Database } from 'lucide-react';

export default function EarthdataCloudModal({ isOpen, onClose, health }) {
  const [keyword, setKeyword] = useState('MOD11A2');
  const [minLon, setMinLon] = useState(-65.0);
  const [minLat, setMinLat] = useState(-15.0);
  const [maxLon, setMaxLon] = useState(-55.0);
  const [maxLat, setMaxLat] = useState(-5.0);
  const [isLoading, setIsLoading] = useState(false);
  const [discoveryData, setDiscoveryData] = useState(null);
  const [error, setError] = useState(null);

  const PRESET_KEYWORDS = [
    { label: 'MODIS LST Day', value: 'MOD11A2', desc: 'Terra 8-Day 1km Land Surface Temperature' },
    { label: 'MODIS NDVI', value: 'MOD13A3', desc: 'Terra Monthly 1km Vegetation Index' },
    { label: 'GPM IMERG', value: 'GPM_3IMERGM', desc: 'Global Precipitation Measurement v07' },
    { label: 'GLDAS Noah', value: 'GLDAS_NOAH025_M', desc: 'GES DISC 0.25° Root Zone Soil Moisture' },
    { label: 'NASA SWOT', value: 'SWOT', desc: 'Surface Water and Ocean Topography' }
  ];

  const fetchGranules = async (kw = keyword) => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        keyword: kw,
        min_lon: minLon,
        min_lat: minLat,
        max_lon: maxLon,
        max_lat: maxLat,
        limit: 6
      });
      const res = await fetch(`/api/earthdata/discover?${params.toString()}`);
      if (!res.ok) {
        throw new Error(`Discovery failed: HTTP ${res.status}`);
      }
      const data = await res.json();
      setDiscoveryData(data);
    } catch (err) {
      console.error('Earthdata discovery error:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchGranules(keyword);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-4xl bg-slate-900 border border-slate-750 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-850/60">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Satellite className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-extrabold text-white">NASA Earthdata Cloud & CMR Granule Explorer</h2>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-950/90 text-emerald-300 border border-emerald-600/50 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3 text-emerald-400" />
                  Bearer Authenticated
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Live NASA Common Metadata Repository (CMR) Granule Search & OPeNDAP Hyrax Subset Probe
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5 overflow-y-auto">
          {/* Science Keyword Selectors */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              Target Science Dataset / Sensor:
            </label>
            <div className="flex flex-wrap gap-2">
              {PRESET_KEYWORDS.map((k) => (
                <button
                  key={k.value}
                  onClick={() => {
                    setKeyword(k.value);
                    fetchGranules(k.value);
                  }}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all text-left border ${
                    keyword === k.value
                      ? 'bg-cyan-950/90 text-cyan-300 border-cyan-500 shadow-sm shadow-cyan-500/20'
                      : 'bg-slate-850 text-slate-400 border-slate-750 hover:bg-slate-800 hover:text-slate-200'
                  }`}
                >
                  <span className="font-bold block text-[11px]">{k.label}</span>
                  <span className="text-[10px] opacity-75 font-mono">{k.value}</span>
                </button>
              ))}
            </div>
          </div>

          {/* OPeNDAP Live Probe Status Banner */}
          {discoveryData?.opendap_probe && (
            <div className="bg-slate-850/80 p-3.5 rounded-xl border border-slate-750 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white flex items-center gap-1.5">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    OPeNDAP Cloud Subset Endpoint:
                  </span>
                  <span className="px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 font-mono text-[10px] border border-emerald-800">
                    Hyrax Subset Active
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 font-mono truncate max-w-xl">
                  {discoveryData.opendap_probe.opendap_endpoint}
                </p>
              </div>

              <div className="flex items-center gap-2 text-[11px] text-slate-300">
                <span className="text-slate-400">Formats:</span>
                <span className="font-mono text-cyan-300">NetCDF-4, DAP2/DAP4, GeoTIFF</span>
              </div>
            </div>
          )}

          {/* Granules List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-300">
                Discovered Satellite Granules ({discoveryData?.total_granules_found || 0})
              </span>
              <button
                onClick={() => fetchGranules(keyword)}
                disabled={isLoading}
                className="flex items-center gap-1 text-[11px] text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                <RefreshCw className={`w-3 h-3 ${isLoading ? 'animate-spin' : ''}`} />
                Refresh CMR Search
              </button>
            </div>

            {isLoading ? (
              <div className="py-12 flex flex-col items-center justify-center space-y-2 text-slate-400 text-xs">
                <RefreshCw className="w-6 h-6 animate-spin text-cyan-400" />
                <span>Querying NASA Common Metadata Repository (CMR)...</span>
              </div>
            ) : error ? (
              <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/50 text-rose-300 text-xs">
                {error}
              </div>
            ) : (
              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                {discoveryData?.granules?.map((g, idx) => (
                  <div
                    key={g.granule_id || idx}
                    className="p-3 rounded-xl bg-slate-850 border border-slate-750/70 hover:border-slate-700 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                  >
                    <div className="space-y-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-white text-xs truncate max-w-md">
                          {g.title}
                        </span>
                        {g.cloud_hosted && (
                          <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-800 shrink-0">
                            Cloud Hosted
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-3 text-[11px] text-slate-400 font-mono">
                        <span>Acquired: {g.time_start ? g.time_start.split('T')[0] : 'N/A'}</span>
                        <span>•</span>
                        <span>Size: {g.granule_size_mb} MB</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      {g.opendap_url && (
                        <a
                          href={g.opendap_url}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-cyan-300 border border-cyan-800/40 text-[11px] font-medium flex items-center gap-1 transition-colors"
                        >
                          OPeNDAP <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                      {g.download_url && (
                        <a
                          href={g.download_url}
                          target="_blank"
                          rel="noreferrer"
                          className="px-3 py-1.5 rounded-lg bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-700/50 text-[11px] font-medium flex items-center gap-1 transition-colors shadow-sm"
                        >
                          <Download className="w-3 h-3" />
                          Download
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-850/60 flex items-center justify-between text-xs text-slate-400 font-mono">
          <div className="flex items-center gap-2">
            <span>Auth User:</span>
            <span className="text-emerald-400 font-bold">{health?.earthdata?.username || 'belal_ansari'}</span>
          </div>
          <span className="text-[11px] text-slate-500">
            cmr.earthdata.nasa.gov • Protected Earthdata Cloud Link
          </span>
        </div>
      </div>
    </div>
  );
}
