'use client';

import { useEffect, useState, use } from 'react';
import dynamic from 'next/dynamic';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { WebSocketClient } from '@/lib/websocket';
import { MapPin, Phone, User, Star } from 'lucide-react';
import Link from 'next/link';

// Dynamically import Map to prevent SSR errors with window/Leaflet
const LiveMap = dynamic(() => import('@/components/tracking/LiveMap'), { ssr: false });

export default function TrackingPage({ params }: { params: Promise<{ bookingId: string }> }) {
  const { bookingId } = use(params);
  
  const [driverLocation, setDriverLocation] = useState<{ lat: number; lng: number } | null>(null);
  const [eta, setEta] = useState<number | null>(null);
  
  const { data: booking, isLoading } = useQuery({
    queryKey: ['booking', bookingId],
    queryFn: async () => {
      const res = await api.get(`/bookings/${bookingId}`);
      return res.data;
    }
  });

  useEffect(() => {
    if (!booking) return;
    
    const ws = new WebSocketClient(`/bookings/${bookingId}`);
    
    ws.connect();
    
    ws.on('location_update', (data: any) => {
      setDriverLocation({ lat: data.lat, lng: data.lng });
      if (data.eta) setEta(data.eta);
    });
    
    ws.on('status_update', (data: any) => {
      // Refresh the booking data
      window.location.reload();
    });

    return () => {
      ws.disconnect();
    };
  }, [booking, bookingId]);

  if (isLoading) return <div className="min-h-screen flex items-center justify-center">Loading live tracking...</div>;
  if (!booking) return <div className="min-h-screen flex items-center justify-center">Booking not found.</div>;

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col md:flex-row">
      {/* Sidebar Info */}
      <div className="w-full md:w-96 bg-white border-r border-gray-200 shadow-xl z-10 flex flex-col h-screen md:h-auto overflow-y-auto">
        <div className="p-6 bg-blue-600 text-white">
          <Link href="/dashboard" className="text-blue-100 hover:text-white text-sm font-medium mb-4 inline-block">&larr; Back to Dashboard</Link>
          <h1 className="text-2xl font-bold mb-1">Live Tracking</h1>
          <p className="text-blue-100 font-medium">#{booking.id.substring(0, 8)}</p>
        </div>
        
        <div className="p-6 flex-1">
          <div className="flex items-center gap-4 mb-8 bg-blue-50 p-4 rounded-xl">
            <div className="flex-1">
              <h2 className="text-sm font-bold text-blue-600 uppercase mb-1">Status</h2>
              <div className="text-xl font-bold text-gray-900 capitalize">{booking.booking_status.replace('_', ' ')}</div>
            </div>
            {eta && (
              <div className="text-right">
                <h2 className="text-sm font-bold text-blue-600 uppercase mb-1">ETA</h2>
                <div className="text-xl font-bold text-gray-900">{eta} min</div>
              </div>
            )}
          </div>

          <div className="relative pl-6 border-l-2 border-gray-200 space-y-8 mb-8 ml-2">
            <div className="relative">
              <div className="absolute -left-[31px] bg-white p-1 rounded-full">
                <div className="w-4 h-4 bg-blue-600 rounded-full" />
              </div>
              <h3 className="text-sm font-bold text-gray-500 uppercase mb-1">Pickup</h3>
              <p className="font-medium text-gray-900">{booking.pickup_lat}, {booking.pickup_lng}</p>
            </div>
            <div className="relative">
              <div className="absolute -left-[31px] bg-white p-1 rounded-full">
                <div className="w-4 h-4 bg-green-600 rounded-full" />
              </div>
              <h3 className="text-sm font-bold text-gray-500 uppercase mb-1">Dropoff</h3>
              <p className="font-medium text-gray-900">{booking.dropoff_lat}, {booking.dropoff_lng}</p>
            </div>
          </div>

          {booking.assigned_driver_id && (
            <div className="border-t border-gray-100 pt-6">
              <h3 className="text-sm font-bold text-gray-500 uppercase mb-4">Your Chauffeur</h3>
              <div className="flex items-center gap-4 bg-gray-50 p-4 rounded-xl">
                <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-gray-500">
                  <User className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <div className="font-bold text-gray-900">Driver #{booking.assigned_driver_id.substring(0, 4)}</div>
                  <div className="flex items-center text-sm text-gray-500 gap-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" /> 4.9 Rating
                  </div>
                </div>
                <button className="w-10 h-10 bg-white border border-gray-200 rounded-full flex items-center justify-center text-blue-600 hover:bg-blue-50 transition-colors">
                  <Phone className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Map Area */}
      <div className="flex-1 h-[50vh] md:h-screen relative bg-gray-100">
        <LiveMap 
          driverLat={driverLocation?.lat || null}
          driverLng={driverLocation?.lng || null}
          pickupLat={booking.pickup_lat}
          pickupLng={booking.pickup_lng}
          dropoffLat={booking.dropoff_lat}
          dropoffLng={booking.dropoff_lng}
        />
      </div>
    </div>
  );
}
