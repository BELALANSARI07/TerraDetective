import React, { useState, useEffect, useCallback } from 'react';
import { Sparkles, ArrowRight, CheckCircle, Satellite, Compass } from 'lucide-react';

const BIOME_SYMPTOMS_MAP = {
  'Forest / Deforestation': [
    'Canopy Clearance & Extreme Surface Heat',
    'Vegetation Browning & Biomass Loss',
    'Forest Microclimate Moisture Loss',
    'Regional Rainfall Decline & Deforestation Drought',
    'Boundary-Layer Tropospheric Warming',
    'Direct Solar Radiation Exposure',
  ],
  'Farmland / Irrigation': [
    'Intense Evaporative Surface Cooling',
    'Artificial Crop Greening Surges',
    'Aquifer & Root-Zone Groundwater Depletion',
    'Agricultural Air Temperature Dampening',
    'Precipitation vs Irrigation Disparity',
    'Canopy Solar Irradiance Conversion',
  ],
  'Monsoon / River Basin': [
    'Extreme Orographic Deluge & Flooding',
    'Monsoon Cloud Shading & Solar Blockage',
    'River Catchment Soil Water Saturation',
    'Monsoon Break Ground Skin Heating',
    'Post-Monsoon Vegetation Flush',
    'Atmospheric Moisture Advection & Cooling',
  ],
  'Arid / Rain Shadow': [
    'Chronic Rain-Shadow Precipitation Deficit',
    'Severe Root-Zone Soil Moisture Exhaustion',
    'Bare Ground Radiant Heat & Thermal Amplitude',
    'Cloud-Free Surface Solar Radiative Forcing',
    'Drought Canopy Browning & Desertification',
    'Sensible Heat Tropospheric Warming',
  ],
  'Urban / Built Environment': [
    'Urban Heat Island (Asphalt Thermal Storage)',
    'Urban Canopy & Greenspace Mitigation',
    'Impervious Surface Runoff & Infiltration Loss',
    'Nocturnal Heat Trapping (2-Meter Air)',
    'Urban Convective Thunderstorm Deluge',
    'Low-Albedo Solar Absorption',
  ],
};

const ENVIRONMENTS = Object.keys(BIOME_SYMPTOMS_MAP);

export default function GuidedDetectiveBar({
  onSelectCase,
  isLight = true
}) {
  const [environment, setEnvironment] = useState('Forest / Deforestation');
  const [symptom, setSymptom] = useState(BIOME_SYMPTOMS_MAP['Forest / Deforestation'][0]);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(false);

  // Available symptoms for currently selected environment
  const currentSymptoms = BIOME_SYMPTOMS_MAP[environment] || BIOME_SYMPTOMS_MAP['Forest / Deforestation'];

  const executeRecommendation = useCallback(async (env, symp) => {
    setLoading(true);
    try {
      const res = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          environment: env,
          symptom: symp,
          timeframe_years: 25,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setRecommendation(data);
        return;
      }
    } catch (err) {
      console.warn('Recommendation API call failed, using local lookup fallback', err);
    } finally {
      setLoading(false);
    }

    // Contextual Local Fallback if API fails
    const envLower = env.toLowerCase();
    const sympLower = symp.toLowerCase();

    let varId = 'MOD11A2';
    let varName = 'Daytime Land Surface Temperature (LST)';
    let unit = '°C (Degrees Celsius)';
    let platform = 'NASA Terra Satellite / MODIS (1 km)';
    let caseId = 'case_2_land_thermal_paradox';
    let caseTitle = 'Land Thermal Paradox';
    let def = `Measures thermal emissions directly from the ground skin, detecting temperature anomalies in ${env.toLowerCase()} biomes.`;
    let tip = `Examine decadal trends to observe localized environmental forcing.`;

    if (sympLower.includes('solar') || sympLower.includes('shading') || sympLower.includes('irradiance')) {
      varId = 'ALLSKY_SFC_SW_DWN';
      varName = 'Solar Downward Surface Irradiance';
      unit = 'MJ/m²/day';
      platform = 'NASA CERES / MERRA-2 Solar Radiative Flux';
      caseId = 'case_1_monsoon_paradox';
      caseTitle = 'The Monsoon Paradox';
      def = `Measures surface solar irradiance, capturing how cloud cover and atmospheric clarity control ground heating.`;
      tip = `Observe solar radiation dips during heavy cloud cover vs clear sky spikes.`;
    } else if (sympLower.includes('green') || sympLower.includes('canopy') || sympLower.includes('biomass')) {
      varId = 'MOD13A3';
      varName = 'Normalized Difference Vegetation Index (NDVI)';
      unit = 'index (0.0 to 1.0)';
      platform = 'NASA Terra Satellite / MODIS (1 km monthly)';
      caseId = 'case_3_vegetation_paradox';
      caseTitle = 'Vegetation Greenness Paradox';
      def = `Measures photosynthetic capacity, quantifying vegetation health changes across ${env.toLowerCase()} landscapes.`;
      tip = `Contrast seasonal greenness peaks with long-term baseline decline or surges.`;
    } else if (sympLower.includes('rain') || sympLower.includes('deluge') || sympLower.includes('precipitation') || sympLower.includes('drought')) {
      varId = 'GPM_3IMERGM_07';
      varName = 'Monthly Precipitation Accumulation';
      unit = 'mm/month';
      platform = 'NASA GPM Core Observatory & Constellation';
      caseId = 'case_1_monsoon_paradox';
      caseTitle = 'The Monsoon Paradox';
      def = `Measures precipitation accumulation, diagnosing regional deluge patterns and rain-shadow deficits.`;
      tip = `Assess rainfall totals against historical decadal baselines.`;
    } else if (sympLower.includes('soil') || sympLower.includes('moisture') || sympLower.includes('groundwater') || sympLower.includes('aquifer')) {
      varId = 'GWETROOT';
      varName = 'Root-Zone Soil Wetness (0-100cm)';
      unit = 'fraction (0.0 to 1.0)';
      platform = 'NASA GLDAS / MERRA-2 Land Surface Model';
      caseId = envLower.includes('farm') ? 'case_3_vegetation_paradox' : 'case_1_monsoon_paradox';
      caseTitle = envLower.includes('farm') ? 'Vegetation Greenness Paradox' : 'The Monsoon Paradox';
      def = `Measures moisture reserves in the 0-100cm root zone, tracking subterranean desiccation and aquifer depletion.`;
      tip = `Correlate root-zone depletion with prolonged dry spells and groundwater withdrawal.`;
    } else if (sympLower.includes('air') || sympLower.includes('tropospheric') || sympLower.includes('ambient') || sympLower.includes('warming')) {
      varId = 'T2M';
      varName = '2-Meter Ambient Air Temperature';
      unit = '°C (Degrees Celsius)';
      platform = 'NASA MERRA-2 Atmospheric Reanalysis (NASA POWER)';
      caseId = 'case_2_land_thermal_paradox';
      caseTitle = 'Land Thermal Paradox';
      def = `Measures ambient tropospheric air temperature 2 meters above ground, tracking boundary-layer climate warming.`;
      tip = `Compare air temperature trends against skin temperature to isolate surface albedo effects.`;
    }

    setRecommendation({
      query: { environment_type: env, symptom_type: symp, timeframe_years: 25 },
      matched_mystery_case: { has_match: true, case_id: caseId, case_title: caseTitle },
      recommended_variable: {
        variable_id: varId,
        common_name: varName,
        satellite_platform: platform,
        unit: unit,
        plain_english_definition: def,
      },
      detective_prompt_tip: tip,
    });
    setLoading(false);
  }, []);

  // Fetch initial recommendation on mount
  useEffect(() => {
    executeRecommendation(environment, symptom);
  }, []);

  // Handler when environment changes (Option 1)
  const handleEnvironmentChange = (newEnv) => {
    setEnvironment(newEnv);
    const newSymptoms = BIOME_SYMPTOMS_MAP[newEnv] || [];
    const firstSymptom = newSymptoms[0] || '';
    setSymptom(firstSymptom);
    // Instantly update recommendation
    executeRecommendation(newEnv, firstSymptom);
  };

  // Handler when symptom changes (Option 2)
  const handleSymptomChange = (newSymptom) => {
    setSymptom(newSymptom);
    // Instantly update recommendation
    executeRecommendation(environment, newSymptom);
  };

  return (
    <div className={`p-4 rounded-xl border transition-all ${
      isLight 
        ? 'bg-[#FAF8F5] border-[#DCD7C9] text-archival-ink shadow-none' 
        : 'bg-[#0C1017] border-[#1E2636] text-obsidian-text shadow-none'
    }`}>
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
        
        {/* Wizard Label */}
        <div className="flex items-center space-x-2.5">
          <div className="w-8 h-8 rounded-lg bg-archival-terracotta text-white flex items-center justify-center shadow-xs flex-shrink-0">
            <Sparkles className="w-4 h-4 text-amber-200" />
          </div>
          <div>
            <h3 className={`text-xs font-bold flex items-center space-x-1.5 ${isLight ? 'text-archival-ink font-serif text-base' : 'text-white'}`}>
              <span>Guided Variable Detective</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-archival-sand text-archival-ink font-bold border border-[#DCD7C9]">
                Dynamic Biome Telemetry
              </span>
            </h3>
            <p className="text-[11px] text-archival-muted">
              Select an environment and specific observed phenomenon to identify the right NASA sensor
            </p>
          </div>
        </div>

        {/* Selectors Form */}
        <div className="flex flex-wrap items-center gap-2.5">
          
          {/* Step 1: Environment */}
          <div className="flex items-center space-x-1.5">
            <label htmlFor="biome-select" className="text-xs font-mono font-bold text-archival-terracotta">
              1. Biome:
            </label>
            <select
              id="biome-select"
              value={environment}
              onChange={(e) => handleEnvironmentChange(e.target.value)}
              className={`text-xs rounded-lg px-2.5 py-1.5 border font-semibold focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none cursor-pointer transition-colors ${
                isLight ? 'bg-white border-[#DCD7C9] text-archival-ink hover:border-archival-terracotta' : 'bg-slate-800 border-slate-700 text-slate-200 hover:border-cyan-500'
              }`}
            >
              {ENVIRONMENTS.map((e) => (
                <option key={e} value={e}>{e}</option>
              ))}
            </select>
          </div>

          {/* Step 2: Symptom (Dynamically populated based on Option 1) */}
          <div className="flex items-center space-x-1.5">
            <label htmlFor="phenomenon-select" className="text-xs font-mono font-bold text-archival-terracotta">
              2. Phenomenon:
            </label>
            <select
              id="phenomenon-select"
              value={symptom}
              onChange={(e) => handleSymptomChange(e.target.value)}
              className={`text-xs rounded-lg px-2.5 py-1.5 border font-semibold focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none cursor-pointer max-w-[280px] truncate transition-colors ${
                isLight ? 'bg-white border-[#DCD7C9] text-archival-ink hover:border-archival-terracotta' : 'bg-slate-800 border-slate-700 text-slate-200 hover:border-cyan-500'
              }`}
            >
              {currentSymptoms.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          {/* Action Button */}
          <button
            onClick={() => executeRecommendation(environment, symptom)}
            disabled={loading}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center space-x-1.5 focus-visible:ring-2 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
              isLight 
                ? 'bg-archival-ink text-white hover:bg-black' 
                : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 font-mono'
            }`}
          >
            <span>Match Observation</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Recommendation Card Banner */}
      {recommendation && (
        <div className={`mt-3.5 pt-3.5 border-t flex flex-col md:flex-row md:items-start md:justify-between gap-4 text-xs ${
          isLight ? 'border-[#DCD7C9] text-archival-ink' : 'border-[#1E2636] text-slate-300'
        }`}>
          <div className="flex items-start space-x-3 max-w-4xl">
            <CheckCircle className="w-4 h-4 text-emerald-600 mt-1 flex-shrink-0" />
            <div className="space-y-1.5">
              
              {/* Dual Badges explicitly reflecting both Option 1 and Option 2 */}
              <div className="flex flex-wrap items-center gap-1.5">
                <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-archival-muted">
                  Active Investigation:
                </span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold font-mono bg-amber-100 text-amber-900 border border-amber-300/80 dark:bg-amber-950/60 dark:text-amber-300 dark:border-amber-700">
                  🌍 {recommendation.query?.environment_type || environment}
                </span>
                <span className="text-archival-muted text-xs font-mono font-bold">×</span>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold font-mono bg-cyan-100 text-cyan-900 border border-cyan-300/80 dark:bg-cyan-950/60 dark:text-cyan-300 dark:border-cyan-700">
                  ⚡ {recommendation.query?.symptom_type || symptom}
                </span>
              </div>

              {/* Sensor & Units */}
              <div className="font-semibold text-slate-900 dark:text-white flex flex-wrap items-center gap-1.5 pt-0.5">
                <span className="font-serif text-sm">Recommended NASA Telemetry:</span>
                <span className="font-mono bg-blue-100 text-blue-900 dark:bg-blue-900/50 dark:text-cyan-300 px-2 py-0.5 rounded text-xs font-bold border border-blue-200 dark:border-blue-800">
                  {recommendation.recommended_variable?.variable_id} — {recommendation.recommended_variable?.common_name}
                </span>
                <span className="text-xs text-gray-600 bg-gray-100 px-2 py-0.5 rounded border border-gray-200 font-mono dark:bg-slate-800 dark:border-slate-700 dark:text-slate-300">
                  {recommendation.recommended_variable?.unit}
                </span>
              </div>

              {/* Satellite Platform & Sensor details */}
              {recommendation.recommended_variable?.satellite_platform && (
                <div className="text-[11px] font-mono text-emerald-800 dark:text-emerald-400 flex items-center space-x-1.5">
                  <Satellite className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>{recommendation.recommended_variable.satellite_platform}</span>
                </div>
              )}

              {/* Plain English Scientific Definition */}
              <p className="text-slate-700 dark:text-slate-300 leading-relaxed font-sans text-xs">
                {recommendation.recommended_variable?.plain_english_definition}
              </p>

              {/* Detective Prompt Tip */}
              {recommendation.detective_prompt_tip && (
                <p className="text-[11px] text-archival-muted dark:text-slate-400 italic">
                  💡 <span className="font-semibold">Detective Tip:</span> {recommendation.detective_prompt_tip}
                </p>
              )}
            </div>
          </div>

          {/* Action Button: Explore Case Demo */}
          {recommendation.matched_mystery_case?.case_id ? (
            <button
              onClick={() => onSelectCase(recommendation.matched_mystery_case.case_id)}
              className="flex-shrink-0 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition-colors flex items-center space-x-1.5 shadow-sm whitespace-nowrap self-start md:self-auto cursor-pointer focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:outline-none"
            >
              <span>Explore Case Demo</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          ) : (
            <button
              onClick={() => onSelectCase('case_1_monsoon_paradox')}
              className="flex-shrink-0 px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition-colors flex items-center space-x-1.5 shadow-sm whitespace-nowrap self-start md:self-auto cursor-pointer focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:outline-none"
            >
              <span>Explore Baseline Demo</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}
    </div>
  );
}
