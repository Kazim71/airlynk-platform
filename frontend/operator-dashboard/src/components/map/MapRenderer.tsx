"use client";

import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
// @ts-ignore
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix for default Leaflet marker icons in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface Driver {
  id: string;
  lat: number;
  lng: number;
  status: string;
}

interface MapRendererProps {
  drivers: Driver[];
}

export default function MapRenderer({ drivers }: MapRendererProps) {
  // New York City center
  const center: [number, number] = [40.7128, -74.0060];

  return (
    // @ts-ignore
    <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%", zIndex: 0 }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
      />
      {drivers.map(driver => (
        <Marker key={driver.id} position={[driver.lat, driver.lng]}>
          <Popup>
            <div className="text-sm">
              <p className="font-bold">Driver {driver.id.substring(0,6)}</p>
              <p className="text-gray-600">Status: {driver.status}</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
