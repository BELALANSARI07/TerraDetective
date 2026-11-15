import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { MapPin, ArrowRightLeft, Layers, Sliders, Sparkles, Compass } from 'lucide-react';

// Fix Leaflet marker icons in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom colored map markers
const createCustomMarker = (color) => {
  return L.divIcon({
    className: 'custom-map-marker',
    html: `<div style="
      background-color: ${color};
      width: 14px;
      height: 14px;
      border-radius: 50%;
      border: 2px solid #FFFFFF;
      box-shadow: 0 0 10px ${color};
    "></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7]
  });
};

// Pulsing Climate Mystery marker
const createMysteryMarker = () => {
  return L.divIcon({
    className: 'mystery-map-marker',
    html: `<div style="
      background: radial-gradient(circle, #F59E0B 0%, #D97706 70%, rgba(245, 158, 11, 0) 100%);
      width: 18px;
      height: 18px;
      border-radius: 50%;
      border: 2px solid #FFFFFF;
      box-shadow: 0 0 12px #F59E0B, 0 0 18px rgba(245, 158, 11, 0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    "><span style="font-size: 10px; line-height: 1; color: #FFFFFF; font-weight: bold;">★</span></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });
};

export const CLIMATE_MYSTERIES = [
  {
    id: 'punjab',
    name: 'Punjab Breadbasket',
    emoji: '🌾',
    subtitle: 'Irrigation Greening Paradox',
    latA: 31.1471, lonA: 75.3412, labelA: 'Punjab (Intensive Tube-well Irrigation)',
    latB: 26.9124, lonB: 70.9000, labelB: 'Thar Desert (Natural Baseline)',
    variable: 'GLDAS_ROOTMOIST',
    desc: 'Surface farms appear green and thriving, but underground aquifers are depleting rapidly.'
  },
  {
    id: 'amazon',
    name: 'Amazon Deforestation',
    emoji: '🔥',
    subtitle: 'Evaporative Cooling Loss',
    latA: -10.8261, lonA: -61.9311, labelA: 'Rondônia Deforestation Frontier',
    latB: -3.4653, lonB: -62.2159, labelB: 'Central Amazon Primary Canopy',
    variable: 'LST_DAY',
    desc: 'Clearing rainforest canopies collapses local transpiration, warming land surface by +3°C to +5°C.'
  },
  {
    id: 'marathwada',
    name: 'Marathwada Drought',
    emoji: '☀️',
    subtitle: 'Rain-Shadow Aridity',
    latA: 19.0368, lonA: 75.7139, labelA: 'Marathwada Rain-Shadow Basin',
    latB: 16.9902, lonB: 73.3120, labelB: 'Konkan Coast (Monsoon Influx)',
    variable: 'PRECTOTCORR',
    desc: 'Western Ghats orographic barrier leaves Marathwada prone to structural drought.'
  },
  {
    id: 'meghalaya',
    name: 'Northeast Monsoon Zone',
    emoji: '🌧️',
    subtitle: 'Orographic Wet Extreme',
    latA: 25.2702, lonA: 91.7323, labelA: 'Cherrapunji (Orographic Wet Peak)',
    latB: 26.2006, lonB: 92.9376, labelB: 'Brahmaputra Valley Baseline',
    variable: 'GPM_PRECIP',
    desc: 'The world’s wettest rainfall regime shifting toward more volatile, localized rainbursts.'
  },
  {
    id: 'sahel',
    name: 'Sahel Transition Belt',
    emoji: '🌱',
    subtitle: 'Desert Margin Greening',
    latA: 14.5000, lonA: 2.1000, labelA: 'Sahel Semi-Arid Transition',
    latB: 9.5000, lonB: 2.5000, labelB: 'Sub-Humid Savannah Zone',
    variable: 'NDVI',
    desc: 'Erratic re-greening pulses alongside structural topsoil vulnerability on desert margins.'
  },
  {
    id: 'central_valley',
    name: 'California Central Valley',
    emoji: '💧',
    subtitle: 'Aquifer Subsidence Hotspot',
    latA: 36.7468, lonA: -119.7726, labelA: 'San Joaquin Valley (Ag Pumped)',
    latB: 37.8651, lonB: -119.5383, labelB: 'Sierra Nevada (Snowmelt Basin)',
    variable: 'GWETROOT',
    desc: 'Intense agricultural groundwater extraction during mega-droughts triggering land subsidence.'
  }
];

// Tile Layer presets (100% Free, Zero API Keys, No Credit Card)
const TILE_LAYERS = {
  satellite: {
    name: '🛰️ True Satellite (ESRI / NASA)',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Esri, Maxar, Earthstar Geographics, USDA, USGS'
  },
  dark: {
    name: '🌌 Deep Slate (ESRI Dark)',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Esri, HERE, DeLorme, MapmyIndia, &copy; OpenStreetMap contributors'
  },
  topo: {
    name: '🗺️ Topographic (OpenTopoMap)',
    url: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
    attribution: '&copy; OpenTopoMap contributors'
  }
};

export default function RegionalMapComparator({
  regionA,
  regionB,
  onChangeRegionA,
  onChangeRegionB,
  selectedVariable,
  onChangeVariable,
  variables = [],
  onExecuteAnalysis,
  isLoading,
  uxMode = 'story'
}) {
  const [activeTileType, setActiveTileType] = React.useState('satellite');
  const mapRefA = useRef(null);
  const mapRefB = useRef(null);
  const leafletMapA = useRef(null);
  const leafletMapB = useRef(null);
  const tileLayerA = useRef(null);
  const tileLayerB = useRef(null);
  const markerA = useRef(null);
  const markerB = useRef(null);
  const mysteryGroupA = useRef(null);
  const mysteryGroupB = useRef(null);

  const loadMystery = (m) => {
    onChangeRegionA({ latitude: m.latA, longitude: m.lonA, label: m.labelA });
    onChangeRegionB({ latitude: m.latB, longitude: m.lonB, label: m.labelB });
    if (m.variable) {
      onChangeVariable(m.variable);
    }
  };

  // Initialize Map A
  useEffect(() => {
    if (!mapRefA.current || leafletMapA.current) return;

    const map = L.map(mapRefA.current, {
      center: [regionA.latitude, regionA.longitude],
      zoom: 4,
      zoomControl: false,
      attributionControl: false
    });

    tileLayerA.current = L.tileLayer(TILE_LAYERS[activeTileType].url, {
      maxZoom: 18,
      subdomains: 'abcd',
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const m = L.marker([regionA.latitude, regionA.longitude], {
      icon: createCustomMarker('#38BDF8')
    }).addTo(map);
    markerA.current = m;

    // Add mystery markers to Map A
    const mysteriesLayer = L.layerGroup().addTo(map);
    CLIMATE_MYSTERIES.forEach((mystery) => {
      const pin = L.marker([mystery.latA, mystery.lonA], {
        icon: createMysteryMarker()
      }).addTo(mysteriesLayer);

      pin.bindTooltip(`
        <div style="padding: 4px; font-family: system-ui, sans-serif;">
          <div style="font-weight: 800; color: #F59E0B; font-size: 12px;">★ ${mystery.name}</div>
          <div style="font-size: 11px; color: #E2E8F0; margin-top: 2px;">${mystery.desc}</div>
          <div style="font-size: 10px; color: #38BDF8; margin-top: 4px; font-weight: bold;">Click to investigate this climate mystery →</div>
        </div>
      `, {
        direction: 'top',
        className: 'leaflet-tooltip-dark',
        offset: [0, -10]
      });

      pin.on('click', (e) => {
        L.DomEvent.stopPropagation(e);
        loadMystery(mystery);
      });
    });
    mysteryGroupA.current = mysteriesLayer;

    map.on('click', (e) => {
      const lat = parseFloat(e.latlng.lat.toFixed(4));
      const lng = parseFloat(e.latlng.lng.toFixed(4));
      m.setLatLng([lat, lng]);
      onChangeRegionA({ ...regionA, latitude: lat, longitude: lng, label: `Custom (${lat}°, ${lng}°)` });
    });

    leafletMapA.current = map;

    return () => {
      map.remove();
      leafletMapA.current = null;
    };
  }, []);

  // Initialize Map B
  useEffect(() => {
    if (!mapRefB.current || leafletMapB.current) return;

    const map = L.map(mapRefB.current, {
      center: [regionB.latitude, regionB.longitude],
      zoom: 4,
      zoomControl: false,
      attributionControl: false
    });

    tileLayerB.current = L.tileLayer(TILE_LAYERS[activeTileType].url, {
      maxZoom: 18,
      subdomains: 'abcd',
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const m = L.marker([regionB.latitude, regionB.longitude], {
      icon: createCustomMarker('#F43F5E')
    }).addTo(map);
    markerB.current = m;

    // Add mystery markers to Map B
    const mysteriesLayerB = L.layerGroup().addTo(map);
    CLIMATE_MYSTERIES.forEach((mystery) => {
      const pin = L.marker([mystery.latB, mystery.lonB], {
        icon: createMysteryMarker()
      }).addTo(mysteriesLayerB);

      pin.bindTooltip(`
        <div style="padding: 4px; font-family: system-ui, sans-serif;">
          <div style="font-weight: 800; color: #F59E0B; font-size: 12px;">★ ${mystery.name} (Comparator)</div>
          <div style="font-size: 11px; color: #E2E8F0; margin-top: 2px;">${mystery.desc}</div>
          <div style="font-size: 10px; color: #F43F5E; margin-top: 4px; font-weight: bold;">Click to investigate this climate mystery →</div>
        </div>
      `, {
        direction: 'top',
        className: 'leaflet-tooltip-dark',
        offset: [0, -10]
      });

      pin.on('click', (e) => {
        L.DomEvent.stopPropagation(e);
        loadMystery(mystery);
      });
    });
    mysteryGroupB.current = mysteriesLayerB;

    map.on('click', (e) => {
      const lat = parseFloat(e.latlng.lat.toFixed(4));
      const lng = parseFloat(e.latlng.lng.toFixed(4));
      m.setLatLng([lat, lng]);
      onChangeRegionB({ ...regionB, latitude: lat, longitude: lng, label: `Custom (${lat}°, ${lng}°)` });
    });

    leafletMapB.current = map;

    return () => {
      map.remove();
      leafletMapB.current = null;
    };
  }, []);

  // Switch Tile Layer when activeTileType changes
  useEffect(() => {
    if (leafletMapA.current && tileLayerA.current) {
      leafletMapA.current.removeLayer(tileLayerA.current);
      tileLayerA.current = L.tileLayer(TILE_LAYERS[activeTileType].url, {
        maxZoom: 18,
        subdomains: 'abcd'
      }).addTo(leafletMapA.current);
    }
    if (leafletMapB.current && tileLayerB.current) {
      leafletMapB.current.removeLayer(tileLayerB.current);
      tileLayerB.current = L.tileLayer(TILE_LAYERS[activeTileType].url, {
        maxZoom: 18,
        subdomains: 'abcd'
      }).addTo(leafletMapB.current);
    }
  }, [activeTileType]);

  // Update Map A view when regionA prop changes
  useEffect(() => {
    if (leafletMapA.current && markerA.current) {
      markerA.current.setLatLng([regionA.latitude, regionA.longitude]);
      leafletMapA.current.setView([regionA.latitude, regionA.longitude], leafletMapA.current.getZoom(), {
        animate: true
      });
    }
  }, [regionA.latitude, regionA.longitude]);

  // Update Map B view when regionB prop changes
  useEffect(() => {
    if (leafletMapB.current && markerB.current) {
      markerB.current.setLatLng([regionB.latitude, regionB.longitude]);
      leafletMapB.current.setView([regionB.latitude, regionB.longitude], leafletMapB.current.getZoom(), {
        animate: true
      });
    }
  }, [regionB.latitude, regionB.longitude]);

  return (
    <div className="rounded-2xl bg-slate-900 border border-slate-750 p-4 shadow-xl space-y-4 isolate relative z-0">
      {/* 6 Interactive Climate Mystery Strip */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
            <Compass className="w-3.5 h-3.5 text-amber-400" />
            Interactive Climate Mystery Pins (Click Any To Investigate)
          </span>
          <span className="text-[11px] text-slate-500 hidden md:inline">
            Pins are also rendered directly on the satellite globe below
          </span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          {CLIMATE_MYSTERIES.map((m) => (
            <button
              key={m.id}
              onClick={() => loadMystery(m)}
              className="flex flex-col text-left p-2.5 rounded-xl bg-slate-850/80 hover:bg-slate-800 border border-slate-750 hover:border-amber-500/50 transition-all group relative overflow-hidden"
            >
              <div className="flex items-center gap-1.5 mb-1">
                <span className="text-sm">{m.emoji}</span>
                <span className="text-xs font-bold text-white group-hover:text-amber-300 transition-colors truncate">
                  {m.name.split(' ')[0]}
                </span>
              </div>
              <span className="text-[10px] text-slate-400 truncate font-mono">
                {m.subtitle}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Control Strip */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pb-3 border-b border-slate-800 pt-1">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-sm text-white">Dual-Region Comparator & Global Coordinate Inspector</span>
        </div>

        {/* Tile Layer & Parameter Controls */}
        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          {/* Map Layer Switcher */}
          <div className="flex items-center rounded-lg bg-slate-850 p-0.5 border border-slate-700 text-[11px] font-mono">
            {Object.entries(TILE_LAYERS).map(([key, layer]) => (
              <button
                key={key}
                onClick={() => setActiveTileType(key)}
                className={`px-2 py-1 rounded-md transition-all ${
                  activeTileType === key
                    ? 'bg-cyan-950 text-cyan-300 font-bold border border-cyan-700/60 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {layer.name.split(' ')[0]} {layer.name.split(' ')[1]}
              </button>
            ))}
          </div>

          {/* Variable Selector */}
          <select
            value={selectedVariable}
            onChange={(e) => onChangeVariable(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-cyan-300 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-cyan-500 font-mono"
          >
            <optgroup label="Local Verified Satellite Data">
              <option value="NDVI">MODIS NDVI (Vegetation Greenness Index)</option>
              <option value="LST_DAY">MODIS LST Day (Land Surface Temperature)</option>
              <option value="GPM_PRECIP">GPM IMERG Final (Satellite Precipitation)</option>
              <option value="GLDAS_ROOTMOIST">GLDAS Noah (Root-Zone Soil Moisture)</option>
            </optgroup>
            <optgroup label="NASA POWER 20-Variable Catalog">
              {variables.map((v) => (
                <option key={v.identifier} value={v.identifier}>
                  {v.simple_label || v.name} ({v.identifier})
                </option>
              ))}
            </optgroup>
          </select>

          <button
            onClick={onExecuteAnalysis}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs shadow-md shadow-emerald-500/20 active:scale-95 disabled:opacity-50 transition-all"
          >
            {isLoading ? 'Computing...' : 'Run Analysis'}
          </button>
        </div>
      </div>

      {/* Dual Maps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Region A */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-cyan-400 flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 ring-2 ring-cyan-400/30" />
              Region A: {regionA.label}
            </span>
            <span className="font-mono text-slate-400">
              {regionA.latitude.toFixed(2)}°, {regionA.longitude.toFixed(2)}°
            </span>
          </div>
          <div className="h-56 rounded-xl overflow-hidden border border-slate-800 relative shadow-inner isolate z-0">
            <div ref={mapRefA} className="w-full h-full" />
            <div className="absolute top-2 left-2 z-10 bg-slate-950/80 backdrop-blur-sm px-2 py-1 rounded text-[10px] font-mono text-cyan-300 border border-slate-800">
              Region A Primary Pin
            </div>
          </div>
        </div>

        {/* Region B */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-rose-400 flex items-center gap-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-rose-400 ring-2 ring-rose-400/30" />
              Region B: {regionB.label}
            </span>
            <span className="font-mono text-slate-400">
              {regionB.latitude.toFixed(2)}°, {regionB.longitude.toFixed(2)}°
            </span>
          </div>
          <div className="h-56 rounded-xl overflow-hidden border border-slate-800 relative shadow-inner isolate z-0">
            <div ref={mapRefB} className="w-full h-full" />
            <div className="absolute top-2 left-2 z-10 bg-slate-950/80 backdrop-blur-sm px-2 py-1 rounded text-[10px] font-mono text-rose-300 border border-slate-800">
              Region B Comparator Pin
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
