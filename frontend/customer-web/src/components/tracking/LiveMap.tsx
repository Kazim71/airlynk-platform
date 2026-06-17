'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';

// Fix Leaflet default icon issues in React
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const carIcon = new L.Icon({
  iconUrl: 'https://cdn-icons-png.flaticon.com/512/3204/3204066.png',
  iconSize: [32, 32],
  iconAnchor: [16, 16]
});

interface LiveMapProps {
  driverLat: number | null;
  driverLng: number | null;
  pickupLat: number;
  pickupLng: number;
  dropoffLat: number;
  dropoffLng: number;
}

export default function LiveMap({ driverLat, driverLng, pickupLat, pickupLng, dropoffLat, dropoffLng }: LiveMapProps) {
  const centerLat = driverLat || pickupLat;
  const centerLng = driverLng || pickupLng;

  return (
    <MapContainer 
      center={[centerLat, centerLng]} 
      zoom={13} 
      style={{ height: '100%', width: '100%', zIndex: 0 }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      
      <Marker position={[pickupLat, pickupLng]}>
        <Popup>Pickup Location</Popup>
      </Marker>
      
      <Marker position={[dropoffLat, dropoffLng]}>
        <Popup>Dropoff Location</Popup>
      </Marker>

      {driverLat && driverLng && (
        <Marker position={[driverLat, driverLng]} icon={carIcon}>
          <Popup>Your Driver</Popup>
        </Marker>
      )}

      {/* Basic straight line route for visualization */}
      <Polyline positions={[[pickupLat, pickupLng], [dropoffLat, dropoffLng]]} color="blue" dashArray="10, 10" />
    </MapContainer>
  );
}
