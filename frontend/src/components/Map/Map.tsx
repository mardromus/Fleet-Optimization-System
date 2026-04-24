import { useEffect, useRef, Fragment } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';
import { useFleetStore } from '../../store/useFleetStore';
import DispatchPanel from '../DispatchPanel/DispatchPanel';
import 'leaflet/dist/leaflet.css';

const HeatmapLayer = ({ points }: { points: [number, number, number][] }) => {
  const map = useMap();
  const heatLayerRef = useRef<L.Layer | null>(null);

  useEffect(() => {
    if (!map) return;

    // Remove existing layer if it exists
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
    }

    // Adjust radius based on zoom level (dynamic scaling)
    const currentZoom = map.getZoom();
    const baseRadius = 45; // Increased base radius
    const dynamicRadius = baseRadius + (currentZoom - 13) * 10;
    
    // Scale intensity (weight) of each point to ensure visibility (0.6 to 1.0)
    const enhancedPoints = points.map(([lat, lon, score]) => {
      const intensity = 0.6 + (score * 0.4);
      return [lat, lon, intensity] as [number, number, number];
    });

    // Create new heatmap layer
    // @ts-ignore - leaflet.heat adds heatLayer to L
    const heatLayer = (L as any).heatLayer(enhancedPoints, {
      radius: Math.max(25, dynamicRadius),
      blur: 25,
      maxZoom: 18,
      minOpacity: 0.5,
      max: 1.0,
      gradient: {
        0.2: '#3b82f6', // Blue (Low)
        0.4: '#84cc16', // Lime (Medium-Low)
        0.6: '#eab308', // Yellow (Medium)
        0.8: '#f97316', // Orange (High)
        1.0: '#ef4444'  // Red (Very High)
      }
    });

    heatLayer.addTo(map);
    heatLayerRef.current = heatLayer;

    // Add zoom event listener for dynamic scaling
    const onZoomEnd = () => {
      const newZoom = map.getZoom();
      const newRadius = baseRadius + (newZoom - 13) * 10;
      (heatLayer as any).setOptions({ radius: Math.max(25, newRadius) });
    };

    map.on('zoomend', onZoomEnd);

    return () => {
      map.off('zoomend', onZoomEnd);
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
      }
    };
  }, [map, points]);

  return null;
};

const MapEvents = () => {
  const { createEmergency, dispatchMode } = useFleetStore();
  
  useMapEvents({
    click(e) {
      if (dispatchMode) {
        createEmergency(e.latlng.lat, e.latlng.lng, 'high');
      }
    },
  });
  return null;
};

const MapComponent = () => {
  const { ambulances, predictions, activeRoute, showHeatmap, toggleHeatmap, fetchAmbulances, fetchPredictions, fetchEmergencies, fetchMetrics, fetchLastDispatch } = useFleetStore();

  useEffect(() => {
    fetchAmbulances();
    fetchPredictions();
    fetchEmergencies();
    fetchMetrics();
    fetchLastDispatch();
    const interval = setInterval(() => {
      fetchAmbulances();
      fetchPredictions();
      fetchEmergencies();
      fetchMetrics();
      fetchLastDispatch();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const ambulanceIcon = (status: string) => L.divIcon({
    className: 'custom-div-icon',
    html: `<div style="background-color: ${status === 'idle' ? '#22c55e' : status === 'busy' ? '#ef4444' : '#eab308'}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(0,0,0,0.5);"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
  });

  // Convert predictions to heatmap points format: [lat, lon, intensity]
  const heatmapPoints = predictions.map(p => [p.lat, p.lon, p.score] as [number, number, number]);

  return (
    <div className="relative w-full h-full">
      <MapContainer 
        center={[18.51957, 73.85529]} 
        zoom={13} 
        className="w-full h-full"
      >
        <TileLayer
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
          attribution='&copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
        />

        <MapEvents />

        {/* Heatmap Layer */}
        {showHeatmap && <HeatmapLayer points={heatmapPoints} />}

        {/* Active Route Overlay */}
        {activeRoute && (
          <Polyline
            positions={activeRoute.path_coords}
            pathOptions={{ color: '#3b82f6', weight: 6, opacity: 0.8 }}
          />
        )}

        {/* Ambulance Markers */}
        {ambulances.map((a) => (
          <Marker
            key={a.id}
            position={[a.lat, a.lon]}
            icon={ambulanceIcon(a.status)}
          >
            <Popup>
              <div className="text-sm font-sans">
                <p className="font-bold">Ambulance #{a.id}</p>
                <p>Status: <span className="capitalize">{a.status}</span></p>
                {a.destination && <p>Heading to node: {a.destination}</p>}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Floating UI Panels */}
      <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
        <button
          onClick={toggleHeatmap}
          className={`px-4 py-2 rounded-lg shadow-lg font-bold transition-all duration-200 border-2 ${
            showHeatmap 
              ? 'bg-red-500 text-white border-red-400 hover:bg-red-600' 
              : 'bg-white text-gray-700 border-gray-200 hover:bg-gray-50'
          }`}
        >
          {showHeatmap ? '🔥 Hide Heatmap' : '📍 Show Heatmap'}
        </button>

        {showHeatmap && (
          <div className="bg-white/90 backdrop-blur-sm p-3 rounded-lg shadow-lg border border-gray-200 w-48 animate-in fade-in slide-in-from-right-4">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Demand Intensity</p>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#ef4444]"></div>
                  <span className="text-[10px] font-bold text-gray-600">CRITICAL</span>
                </div>
                <span className="text-[10px] font-black text-red-500">80-100%</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#f97316]"></div>
                  <span className="text-[10px] font-bold text-gray-600">HIGH</span>
                </div>
                <span className="text-[10px] font-black text-orange-500">60-80%</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#eab308]"></div>
                  <span className="text-[10px] font-bold text-gray-600">MEDIUM</span>
                </div>
                <span className="text-[10px] font-black text-yellow-600">40-60%</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#84cc16]"></div>
                  <span className="text-[10px] font-bold text-gray-600">MODERATE</span>
                </div>
                <span className="text-[10px] font-black text-lime-600">20-40%</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-[#3b82f6]"></div>
                  <span className="text-[10px] font-bold text-gray-600">NORMAL</span>
                </div>
                <span className="text-[10px] font-black text-blue-500">0-20%</span>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="absolute bottom-6 left-6 z-[1000]">
        <DispatchPanel />
      </div>
    </div>
  );
};

export default MapComponent;
