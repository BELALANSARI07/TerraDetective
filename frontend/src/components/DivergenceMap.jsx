import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { MapPin, Globe, Compass, Crosshair, Sparkles, Navigation2, RefreshCw, Play, Layers } from 'lucide-react';

// Marker icon fix for Leaflet in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Free, high-quality, open-data tile layers (No API keys or paid tiers required)
const BASEMAPS = {
  satellite: {
    id: 'satellite',
    label: 'Satellite',
    icon: '🛰️',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, GIS User Community',
    maxZoom: 19,
  },
  osm: {
    id: 'osm',
    label: 'OpenStreetMap',
    icon: '🗺️',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap</a> contributors',
    subdomains: ['a', 'b', 'c'],
    maxZoom: 19,
  },
  dark: {
    id: 'dark',
    label: 'Dark Canvas',
    icon: '🌙',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
    maxZoom: 16,
  },
  topo: {
    id: 'topo',
    label: 'Topography',
    icon: '⛰️',
    url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}',
    attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ, TomTom, Intermap, USGS, FAO, NPS, NRCAN',
    maxZoom: 18,
  },
};

// Create styled circular div icons
const createPillMarker = (label, color) => {
  return L.divIcon({
    className: 'custom-pill-marker',
    html: `<div style="
      background-color: ${color};
      color: #FFFFFF;
      padding: 3px 8px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
      border: 2px solid #FFFFFF;
      box-shadow: 0 4px 12px rgba(0,0,0,0.35);
      display: flex;
      align-items: center;
      gap: 4px;
    "><span style="width: 6px; height: 6px; border-radius: 50%; background: #FFF;"></span>${label}</div>`,
    iconSize: [110, 24],
    iconAnchor: [55, 12],
  });
};

const createClickMarker = (color = '#F59E0B') => {
  return L.divIcon({
    className: 'custom-click-marker',
    html: `<div style="
      background: radial-gradient(circle, ${color} 0%, rgba(0,0,0,0.6) 70%, transparent 100%);
      width: 22px;
      height: 22px;
      border-radius: 50%;
      border: 2px solid #FFFFFF;
      box-shadow: 0 0 14px ${color};
      animation: pulse 1.5s infinite;
    "></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });
};

export default function DivergenceMap({
  manifest,
  mode = 'student',
  onSelectCoordinates,
  selectedCoord,
  onTwinCompare,
  twinLoading = false,
}) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const tileLayerRef = useRef(null);
  const layersGroupRef = useRef(null);

  const isLight = mode === 'student';

  // Basemap selection (default to satellite in student mode, dark canvas in scientist mode)
  const [selectedBasemap, setSelectedBasemap] = useState(isLight ? 'satellite' : 'dark');
  const [showBasemapMenu, setShowBasemapMenu] = useState(false);

  // Twin Pin State
  const [isTwinMode, setIsTwinMode] = useState(false);
  const [pinA, setPinA] = useState(null);
  const [pinB, setPinB] = useState(null);
  const [twinVariable, setTwinVariable] = useState('T2M');
  const [clickedCoord, setClickedCoord] = useState(null);

  // Auto-adapt basemap when mode changes, unless user manually picked a different one
  const userSelectedRef = useRef(false);
  useEffect(() => {
    if (!userSelectedRef.current) {
      setSelectedBasemap(isLight ? 'satellite' : 'dark');
    }
  }, [isLight]);

  // Camera flyTo helpers for interactive navigation
  const flyToRegion = (lat, lon) => {
    if (mapInstanceRef.current && lat != null && lon != null) {
      mapInstanceRef.current.flyTo([lat, lon], 7, {
        animate: true,
        duration: 1.5,
      });
    }
  };

  const flyToGlobal = () => {
    if (mapInstanceRef.current) {
      if (latA != null && lonA != null && latB != null && lonB != null) {
        mapInstanceRef.current.flyToBounds(
          [
            [Math.min(latA, latB) - 8, Math.min(lonA, lonB) - 8],
            [Math.max(latA, latB) + 8, Math.max(lonA, lonB) + 8],
          ],
          { animate: true, duration: 1.5, padding: [30, 30] }
        );
      } else {
        mapInstanceRef.current.flyTo([20, 10], 2, { animate: true, duration: 1.5 });
      }
    }
  };

  const regA = manifest?.regions?.[0] || manifest?.region_a;
  const regB = manifest?.regions?.[1] || manifest?.region_b;
  const latA = regA?.latitude ?? regA?.lat;
  const lonA = regA?.longitude ?? regA?.lon;
  const latB = regB?.latitude ?? regB?.lat;
  const lonB = regB?.longitude ?? regB?.lon;
  const cleanPillA = (regA?.region_label && regA.region_label !== 'region_a')
    ? regA.region_label.split(',')[0].slice(0, 14)
    : (regA?.region_name || 'Region A');
  const cleanPillB = (regB?.region_label && regB.region_label !== 'region_b')
    ? regB.region_label.split(',')[0].slice(0, 14)
    : (regB?.region_name || 'Region B');
  const applyTileLayer = (map, basemapKey) => {
    if (!map) return;
    if (tileLayerRef.current) {
      map.removeLayer(tileLayerRef.current);
    }
    const config = BASEMAPS[basemapKey] || BASEMAPS.satellite;
    const newTiles = L.tileLayer(config.url, {
      attribution: config.attribution,
      subdomains: config.subdomains || 'abc',
      maxZoom: config.maxZoom || 19,
    });
    newTiles.addTo(map);
    tileLayerRef.current = newTiles;
  };

  // 1. Initialize Map Once
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const initialMap = L.map(mapContainerRef.current, {
      center: [20.0, 10.0],
      zoom: 2,
      minZoom: 2,
      maxZoom: 14,
      zoomControl: false,
    });

    L.control.zoom({ position: 'topright' }).addTo(initialMap);

    // Mount initial free tile layer
    applyTileLayer(initialMap, selectedBasemap);

    const layersGroup = L.layerGroup().addTo(initialMap);

    // Map Click Handler (Supports Single Probe & Twin Pin Placement)
    initialMap.on('click', (e) => {
      const { lat, lng } = e.latlng;
      const cleanLat = Math.round(lat * 1000) / 1000;
      const cleanLon = Math.round(lng * 1000) / 1000;

      if (isTwinModeRef.current) {
        if (!pinARef.current || (pinARef.current && pinBRef.current)) {
          setPinA({ lat: cleanLat, lon: cleanLon, label: `Pin A (${cleanLat}°, ${cleanLon}°)` });
          setPinB(null);
        } else if (pinARef.current && !pinBRef.current) {
          setPinB({ lat: cleanLat, lon: cleanLon, label: `Pin B (${cleanLat}°, ${cleanLon}°)` });
        }
      } else {
        setClickedCoord({ lat: cleanLat, lon: cleanLon });
        if (onSelectCoordinates) {
          onSelectCoordinates(cleanLat, cleanLon);
        }
      }
    });

    mapInstanceRef.current = initialMap;
    layersGroupRef.current = layersGroup;

    return () => {
      try {
        initialMap.stop();
        initialMap.remove();
      } catch (e) {
        // Safe teardown
      }
      mapInstanceRef.current = null;
      layersGroupRef.current = null;
    };
  }, []);

  // Update tile layer whenever selectedBasemap changes
  useEffect(() => {
    if (mapInstanceRef.current) {
      applyTileLayer(mapInstanceRef.current, selectedBasemap);
    }
  }, [selectedBasemap]);

  // Sync refs for Leaflet click handler closure
  const isTwinModeRef = useRef(isTwinMode);
  isTwinModeRef.current = isTwinMode;
  const pinARef = useRef(pinA);
  pinARef.current = pinA;
  const pinBRef = useRef(pinB);
  pinBRef.current = pinB;

  // 3. Update Markers & Bounding Boxes
  useEffect(() => {
    if (!mapInstanceRef.current || !layersGroupRef.current) return;
    const group = layersGroupRef.current;
    group.clearLayers();

    const bounds = [];

    if (isTwinMode) {
      // Plot Pin A (Cyan)
      if (pinA) {
        const markerA = L.marker([pinA.lat, pinA.lon], {
          icon: createPillMarker(pinA.label || 'Pin A', '#0284C7'),
        }).bindPopup(`<b>Pin A: ${pinA.label}</b><br/>Lat: ${pinA.lat}°, Lon: ${pinA.lon}°`);
        group.addLayer(markerA);
        bounds.push([pinA.lat, pinA.lon]);
      }

      // Plot Pin B (Coral)
      if (pinB) {
        const markerB = L.marker([pinB.lat, pinB.lon], {
          icon: createPillMarker(pinB.label || 'Pin B', '#EA580C'),
        }).bindPopup(`<b>Pin B: ${pinB.label}</b><br/>Lat: ${pinB.lat}°, Lon: ${pinB.lon}°`);
        group.addLayer(markerB);
        bounds.push([pinB.lat, pinB.lon]);
      }
    } else {
      // Preset Mystery Case Markers OR User Uploaded Dataset Markers
      let candidateRegions = [];
      if (manifest?.regions && Array.isArray(manifest.regions) && manifest.regions.length > 0) {
        candidateRegions = manifest.regions;
      } else if (manifest?.region_a || manifest?.region_b) {
        if (manifest.region_a) candidateRegions.push(manifest.region_a);
        if (manifest.region_b) candidateRegions.push(manifest.region_b);
      }

      candidateRegions.forEach((reg, idx) => {
        const lat = reg.latitude ?? reg.lat;
        const lon = reg.longitude ?? reg.lon;
        if (lat === null || lat === undefined || lon === null || lon === undefined) return;
        const latNum = Number(lat);
        const lonNum = Number(lon);
        if (isNaN(latNum) || isNaN(lonNum)) return;
        if (latNum === 0 && lonNum === 0) return; // skip default unplaced coordinates

        const isRegA = idx === 0;
        const color = isRegA ? '#0284C7' : '#EA580C';
        const rawLabel = reg.region_label || reg.label || reg.region_name || reg.name || (isRegA ? 'Region A' : 'Region B');

        // Clean location name: strip "Uploaded: " prefix and format clean human-readable name (not degree)
        const cleanName = String(rawLabel).replace(/^Uploaded:\s*/i, '').trim();
        let pillText = cleanName.split(/[,(]/)[0].trim();
        if (!pillText) pillText = cleanName.slice(0, 18);
        if (pillText.length > 20) pillText = pillText.slice(0, 20);

        const marker = L.marker([latNum, lonNum], {
          icon: createPillMarker(pillText, color),
        }).bindPopup(`<b>${cleanName}</b><br/>Lat: ${latNum}°, Lon: ${lonNum}°`);
        group.addLayer(marker);
        bounds.push([latNum, lonNum]);

        // Bounding Boxes
        if (reg.bounding_box && reg.bounding_box.length === 4) {
          const [w, s, e, n] = reg.bounding_box;
          group.addLayer(L.rectangle([[s, w], [n, e]], {
            color,
            weight: 2,
            fillColor: color,
            fillOpacity: 0.18,
          }));
        }
      });

      // Single Probe Pin
      const activePin = selectedCoord || clickedCoord;
      if (activePin) {
        const clickMarker = L.marker([activePin.lat, activePin.lon], {
          icon: createClickMarker(),
        }).bindPopup(`<b>Custom Explorer Point</b><br/>Lat: ${activePin.lat}°, Lon: ${activePin.lon}°`).openPopup();
        group.addLayer(clickMarker);
        bounds.push([activePin.lat, activePin.lon]);
      }
    }

    if (bounds.length > 0 && mapInstanceRef.current) {
      try {
        if (bounds.length === 1) {
          mapInstanceRef.current.flyTo(bounds[0], 5, { animate: true, duration: 1.2 });
        } else {
          mapInstanceRef.current.flyToBounds(L.latLngBounds(bounds), {
            padding: [40, 40],
            maxZoom: 6,
            animate: true,
            duration: 1.4,
          });
        }
      } catch (e) {}
    }
  }, [manifest, selectedCoord, clickedCoord, isTwinMode, pinA, pinB]);

  const handleRunTwinCompare = () => {
    if (!pinA || !pinB || !onTwinCompare) return;
    onTwinCompare({
      region_a: pinA,
      region_b: pinB,
      variable_id: twinVariable,
    });
  };

  return (
    <div className={`relative border overflow-hidden transition-all ${
      isLight ? 'bg-[#FAF8F5] border-[#DCD7C9] rounded-xl shadow-none' : 'bg-[#0C1017] border-[#1E2636] rounded-none shadow-none'
    }`}>
      {/* Top Header Overlay with Twin Mode Toggle & Basemap Switcher */}
      <div className="absolute top-2.5 left-2.5 right-12 z-[400] flex items-center justify-between pointer-events-none">
        <div className="flex items-center space-x-1.5 pointer-events-auto">
          <div className={`px-2.5 py-1 rounded-md border text-[11px] font-mono backdrop-blur-md flex items-center space-x-1.5 ${
            isLight ? 'bg-[#FAF8F5]/95 border-[#DCD7C9] text-archival-ink' : 'bg-[#0C1017]/95 border-[#1E2636] text-obsidian-text'
          }`}>
            <Globe className="w-3 h-3 text-blue-500 dark:text-cyan-400" />
            <span className="font-bold hidden sm:inline">{isLight ? 'Locator Atlas' : 'Geospatial Radar'}</span>
            <span className="text-[10px] text-slate-400 font-mono hidden md:inline">
              {isTwinMode ? 'Twin Mode' : 'Click to probe'}
            </span>
          </div>

          {/* Free High-Quality Basemap Selector Pill */}
          <div className="relative">
            <button
              onClick={() => setShowBasemapMenu(!showBasemapMenu)}
              title="Change map style (100% Free Satellite, OpenStreetMap, Dark Canvas)"
              aria-label="Change map basemap layer"
              className={`px-2 py-1 rounded-md border text-[11px] font-mono backdrop-blur-md flex items-center space-x-1 transition-all focus-visible:ring-1 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
                isLight
                  ? 'bg-[#FAF8F5]/95 border-[#DCD7C9] text-archival-ink hover:bg-white'
                  : 'bg-[#0C1017]/95 border-[#1E2636] text-obsidian-text hover:bg-[#141B26]'
              }`}
            >
              <Layers className="w-3 h-3 text-cyan-500" />
              <span>{BASEMAPS[selectedBasemap]?.icon}</span>
              <span className="hidden sm:inline font-semibold">{BASEMAPS[selectedBasemap]?.label}</span>
            </button>

            {showBasemapMenu && (
              <div className={`absolute top-full left-0 mt-1 py-1 px-1 rounded-md border shadow-xl backdrop-blur-md z-[500] min-w-[140px] flex flex-col space-y-0.5 text-[11px] font-mono ${
                isLight ? 'bg-[#FAF8F5] border-[#DCD7C9] text-archival-ink' : 'bg-[#0C1017] border-[#1E2636] text-obsidian-text'
              }`}>
                {Object.values(BASEMAPS).map((bm) => (
                  <button
                    key={bm.id}
                    onClick={() => {
                      userSelectedRef.current = true;
                      setSelectedBasemap(bm.id);
                      setShowBasemapMenu(false);
                    }}
                    className={`px-2 py-1 rounded text-left transition-colors flex items-center space-x-1.5 focus-visible:ring-1 focus-visible:ring-cyan-400 focus-visible:outline-none ${
                      selectedBasemap === bm.id
                        ? 'bg-blue-600 text-white font-bold'
                        : isLight
                          ? 'hover:bg-archival-sand text-archival-ink'
                          : 'hover:bg-[#141B26] text-obsidian-muted'
                    }`}
                  >
                    <span>{bm.icon}</span>
                    <span>{bm.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Pin A / Pin B Twin Mode Switch */}
        <button
          onClick={() => {
            setIsTwinMode(!isTwinMode);
            setPinA(null);
            setPinB(null);
          }}
          aria-label="Toggle Twin Probe Comparison Mode"
          className={`px-2.5 py-1 rounded-md text-[11px] font-mono font-bold border transition-all pointer-events-auto flex items-center space-x-1 focus-visible:ring-1 focus-visible:ring-cyan-400 focus-visible:outline-none ${
            isTwinMode
              ? 'bg-gradient-to-r from-blue-600 to-cyan-500 text-white border-transparent'
              : isLight
                ? 'bg-[#FAF8F5]/90 border-[#DCD7C9] text-archival-ink hover:bg-white'
                : 'bg-[#0C1017]/90 border-[#1E2636] text-obsidian-text hover:bg-[#141B26]'
          }`}
        >
          <Crosshair className="w-3 h-3" />
          <span>{isTwinMode ? 'Twin Active' : '📍 Twin Probe'}</span>
        </button>
      </div>

      {/* Fly-To Camera Navigation Bar (Overlay on Top Right / Bottom) */}
      {!isTwinMode && (latA != null || latB != null) && (
        <div className="absolute top-11 left-2.5 z-[400] flex items-center space-x-1 pointer-events-auto">
          {latA != null && lonA != null && (
            <button
              onClick={() => flyToRegion(latA, lonA)}
              title={`Fly camera directly to ${cleanPillA}`}
              aria-label={`Fly camera to ${cleanPillA}`}
              className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold border backdrop-blur-md transition-all flex items-center space-x-1 focus-visible:ring-1 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
                isLight 
                  ? 'bg-[#FAF8F5]/95 border-[#DCD7C9] text-archival-terracotta hover:bg-white' 
                  : 'bg-[#0C1017]/95 border-[#1E2636] text-obsidian-cyan hover:bg-[#141B26]'
              }`}
            >
              <Navigation2 className="w-2.5 h-2.5 rotate-45" />
              <span>Fly: {cleanPillA}</span>
            </button>
          )}

          {latB != null && lonB != null && (
            <button
              onClick={() => flyToRegion(latB, lonB)}
              title={`Fly camera directly to ${cleanPillB}`}
              aria-label={`Fly camera to ${cleanPillB}`}
              className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold border backdrop-blur-md transition-all flex items-center space-x-1 focus-visible:ring-1 focus-visible:ring-archival-viridian dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
                isLight 
                  ? 'bg-[#FAF8F5]/95 border-[#DCD7C9] text-archival-viridian hover:bg-white' 
                  : 'bg-[#0C1017]/95 border-[#1E2636] text-obsidian-amber hover:bg-[#141B26]'
              }`}
            >
              <Navigation2 className="w-2.5 h-2.5 rotate-45" />
              <span>Fly: {cleanPillB}</span>
            </button>
          )}

          <button
            onClick={flyToGlobal}
            title="Reset map camera to global twin view"
            aria-label="Reset map camera to global twin view"
            className={`px-1.5 py-0.5 rounded text-[10px] font-mono border backdrop-blur-md transition-all flex items-center space-x-0.5 focus-visible:ring-1 focus-visible:ring-archival-terracotta dark:focus-visible:ring-cyan-400 focus-visible:outline-none ${
              isLight 
                ? 'bg-[#FAF8F5]/95 border-[#DCD7C9] text-archival-muted hover:bg-white' 
                : 'bg-[#0C1017]/95 border-[#1E2636] text-obsidian-muted hover:bg-[#141B26]'
            }`}
          >
            <Globe className="w-2.5 h-2.5" />
            <span>Global</span>
          </button>
        </div>
      )}

      {/* Twin Pin Control Bar (When Twin Mode Active) */}
      {isTwinMode && (
        <div className={`absolute bottom-3 left-3 right-3 z-[400] p-3 rounded-2xl border backdrop-blur-md shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs ${
          isLight ? 'bg-white/95 border-slate-200 text-slate-900' : 'bg-slate-900/95 border-slate-700 text-slate-100'
        }`}>
          <div className="flex items-center space-x-2">
            <div className={`px-2 py-1 rounded-lg border font-mono text-[11px] ${
              pinA ? 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/60 dark:text-cyan-300' : 'text-slate-400 border-dashed border-slate-300 dark:border-slate-700'
            }`}>
              {pinA ? `Pin A: ${pinA.lat}°, ${pinA.lon}°` : '1. Click Pin A'}
            </div>
            <span className="text-slate-400">vs</span>
            <div className={`px-2 py-1 rounded-lg border font-mono text-[11px] ${
              pinB ? 'bg-orange-50 text-orange-700 border-orange-200 dark:bg-orange-950/60 dark:text-orange-300' : 'text-slate-400 border-dashed border-slate-300 dark:border-slate-700'
            }`}>
              {pinB ? `Pin B: ${pinB.lat}°, ${pinB.lon}°` : '2. Click Pin B'}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <select
              value={twinVariable}
              onChange={(e) => setTwinVariable(e.target.value)}
              className={`text-xs px-2.5 py-1.5 rounded-xl border ${
                isLight ? 'bg-slate-50 border-slate-300 text-slate-800' : 'bg-slate-800 border-slate-700 text-slate-100'
              }`}
            >
              <option value="T2M">Air Temp (T2M)</option>
              <option value="PRECTOTCORR">Precipitation (Rainfall)</option>
              <option value="GWETROOT">Root Soil Moisture</option>
              <option value="ALLSKY_SFC_SW_DWN">Solar Insolation</option>
            </select>

            <button
              onClick={handleRunTwinCompare}
              disabled={!pinA || !pinB || twinLoading}
              className="px-3.5 py-1.5 rounded-xl font-bold text-white bg-blue-600 hover:bg-blue-700 dark:bg-cyan-500 dark:text-slate-950 dark:hover:bg-cyan-400 disabled:opacity-40 flex items-center space-x-1 shadow-sm"
            >
              {twinLoading ? (
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Play className="w-3.5 h-3.5" />
              )}
              <span>Compare</span>
            </button>
          </div>
        </div>
      )}

      {/* Coordinate Readout (Single Probe Mode) */}
      {!isTwinMode && (selectedCoord || clickedCoord) && (
        <div className={`absolute bottom-3 left-3 z-[400] px-3 py-1.5 rounded-xl border text-xs font-mono backdrop-blur-md flex items-center space-x-2 ${
          isLight ? 'bg-white/90 border-amber-300 text-amber-900 shadow-sm' : 'bg-amber-950/80 border-amber-600/50 text-amber-300 shadow-md'
        }`}>
          <Crosshair className="w-3.5 h-3.5 text-amber-500 animate-spin" />
          <span>Custom Probe: {(selectedCoord || clickedCoord).lat}°, {(selectedCoord || clickedCoord).lon}°</span>
        </div>
      )}

      {/* Map Container */}
      <div ref={mapContainerRef} className="w-full h-[280px] sm:h-[320px] md:h-[360px]" />
    </div>
  );
}
