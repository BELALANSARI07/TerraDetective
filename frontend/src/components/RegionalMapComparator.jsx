import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { MapPin, ArrowRightLeft, Layers, Sliders } from 'lucide-react';

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
  isLoading
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
      {/* Control Strip */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pb-3 border-b border-slate-800">
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
              <option value="NDVI">MODIS NDVI (MOD13A3 Vegetation Index)</option>
              <option value="LST_DAY">MODIS LST Day (MOD11A2 Land Temp)</option>
              <option value="GPM_PRECIP">GPM IMERG Final (Giovanni Monthly Precip)</option>
              <option value="GLDAS_ROOTMOIST">GLDAS Noah (GES DISC Root Zone Moisture)</option>
            </optgroup>
            <optgroup label="NASA POWER 20-Variable Catalog">
              {variables.map((v) => (
                <option key={v.identifier} value={v.identifier}>
                  {v.identifier} — {v.name} ({v.units})
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
            <div className="absolute top-2 left-2 z-[400] bg-slate-950/80 backdrop-blur-sm px-2 py-1 rounded text-[10px] font-mono text-cyan-300 border border-slate-800">
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
            <div className="absolute top-2 left-2 z-[400] bg-slate-950/80 backdrop-blur-sm px-2 py-1 rounded text-[10px] font-mono text-rose-300 border border-slate-800">
              Region B Comparator Pin
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
