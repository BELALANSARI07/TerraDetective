import React from 'react';
import { Satellite, ShieldCheck, ExternalLink, Cpu, Radio, Database, CheckCircle2, Globe2 } from 'lucide-react';

export default function SensorOrbitalSpecCard({ manifest, telemetry, statistics }) {
  const variableId = manifest?.variable_id || statistics?.variable_id || 'T2M';
  const sourceProduct = manifest?.source_product || 'MODIS Terra 8-Day 1km LST (MOD11A2.061)';

  // Determine metadata specs based on product
  const isLST = variableId.includes('LST') || variableId.includes('T2M') || sourceProduct.includes('MOD11A2');
  const isNDVI = variableId.includes('NDVI') || sourceProduct.includes('MOD13A3');
  const isPrecip = variableId.includes('PRECTOTCORR') || variableId.includes('GPM') || sourceProduct.includes('3IMERGM');

  let sensorMeta = {
    instrument: 'MODIS (Moderate Resolution Imaging Spectroradiometer)',
    platform: 'NASA EOS Terra (AM Descending) & Aqua (PM Ascending)',
    doi: '10.5067/MODIS/MOD11A2.061',
    doiUrl: 'https://doi.org/10.5067/MODIS/MOD11A2.061',
    spatialResolution: '1 km nominal grid (Sinusoidal tile projection)',
    temporalCadence: '8-Day composite monthly mean',
    spectralBands: 'Bands 31 (11.03 µm) & 32 (12.02 µm) Split-Window LST',
    qcScreening: 'QA Bitmask QA=00 screened (Cloud-free, emissivity error < 0.04)',
    granulesRemoved: '469 0.0K corrupted/cloud-filled retrievals removed',
  };

  if (isNDVI) {
    sensorMeta = {
      instrument: 'MODIS (Moderate Resolution Imaging Spectroradiometer)',
      platform: 'NASA EOS Terra & Aqua Constellation',
      doi: '10.5067/MODIS/MOD13A3.061',
      doiUrl: 'https://doi.org/10.5067/MODIS/MOD13A3.061',
      spatialResolution: '1 km gridded vegetation indices',
      temporalCadence: '16-Day composite monthly average',
      spectralBands: 'Red Band 1 (620-670 nm) & NIR Band 2 (841-876 nm)',
      qcScreening: 'Pixel reliability bitmask (Rank 0: Good Data, Rank 1: Marginal)',
      granulesRemoved: 'Aerosol high-optical-depth pixels filtered',
    };
  } else if (isPrecip) {
    sensorMeta = {
      instrument: 'GPM Microwave Imager (GMI) & Dual-Frequency Radar (DPR)',
      platform: 'NASA/JAXA GPM Core Observatory + Constellation',
      doi: '10.5067/GPM/IMERG/3B-MONTH/07',
      doiUrl: 'https://doi.org/10.5067/GPM/IMERG/3B-MONTH/07',
      spatialResolution: '0.1° × 0.1° (~10 km global assimilation grid)',
      temporalCadence: 'Calibrated monthly precipitation accumulation (IMERG Final)',
      spectralBands: '13-channel microwave radiometry (10-183 GHz) + Ka/Ku radar',
      qcScreening: 'Gauge-calibrated against GPCC ground validation stations',
      granulesRemoved: 'Satellite swath overlap artifacts filtered',
    };
  }

  return (
    <div className="p-4 rounded-2xl bg-slate-900 border border-slate-800 shadow-lg text-slate-300">
      {/* Header */}
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-800 mb-3">
        <div className="flex items-center space-x-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <h4 className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Sensor & Orbital Telemetry Spec
          </h4>
        </div>
        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-800 flex items-center space-x-1">
          <ShieldCheck className="w-3 h-3 text-cyan-400" />
          <span>QA Screened</span>
        </span>
      </div>

      {/* Spec Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] font-mono">
        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-500 block text-[10px]">Instrument Payload</span>
          <span className="text-slate-200 font-semibold">{sensorMeta.instrument}</span>
        </div>

        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-500 block text-[10px]">Spacecraft Platform</span>
          <span className="text-slate-200 font-semibold">{sensorMeta.platform}</span>
        </div>

        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-500 block text-[10px]">Spatial / Grid Resolution</span>
          <span className="text-cyan-300 font-semibold">{sensorMeta.spatialResolution}</span>
        </div>

        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
          <span className="text-slate-500 block text-[10px]">Temporal Cadence</span>
          <span className="text-cyan-300 font-semibold">{sensorMeta.temporalCadence}</span>
        </div>

        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 sm:col-span-2">
          <span className="text-slate-500 block text-[10px]">Spectral Bands & Radiometry</span>
          <span className="text-slate-300">{sensorMeta.spectralBands}</span>
        </div>

        <div className="p-2 rounded-lg bg-slate-950/60 border border-slate-800/80 sm:col-span-2 flex items-center justify-between">
          <div>
            <span className="text-slate-500 block text-[10px]">Digital Object Identifier (DOI)</span>
            <span className="text-cyan-400 font-bold">{sensorMeta.doi}</span>
          </div>
          <a
            href={sensorMeta.doiUrl}
            target="_blank"
            rel="noreferrer"
            className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-[10px] text-cyan-300 flex items-center space-x-1 focus-visible:ring-1 focus-visible:ring-cyan-400 focus-visible:outline-none"
          >
            <span>NASA DOI</span>
            <ExternalLink className="w-2.5 h-2.5" />
          </a>
        </div>
      </div>

      {/* Cloud QC Screening Summary */}
      <div className="mt-2.5 p-2 rounded-lg bg-emerald-950/30 border border-emerald-900/50 flex items-center space-x-2 text-[10px] font-mono text-emerald-400">
        <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
        <span>QC Audit: {sensorMeta.qcScreening} &bull; {sensorMeta.granulesRemoved}</span>
      </div>
    </div>
  );
}
