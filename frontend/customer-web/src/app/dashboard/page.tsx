'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import Link from 'next/link';
import { Car, Clock, MapPin, ArrowRight } from 'lucide-react';

export default function DashboardOverview() {
  const { data, isLoading } = useQuery({
    queryKey: ['bookings'],
    queryFn: async () => {
      const res = await api.get('/bookings');
      return res.data;
    }
  });

  if (isLoading) return <div>Loading...</div>;

  const bookings = data || [];
  const upcomingBookings = bookings.filter((b: any) => ['created', 'confirmed', 'payment_authorized', 'dispatching', 'driver_assigned', 'in_progress'].includes(b.booking_status));

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Welcome back</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
          <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-4">
            <Car className="w-6 h-6" />
          </div>
          <h3 className="text-gray-500 font-medium mb-1">Total Rides</h3>
          <p className="text-3xl font-bold text-gray-900">{bookings.length}</p>
        </div>
      </div>

      <div className="flex justify-between items-end mb-6">
        <h2 className="text-2xl font-bold">Upcoming Rides</h2>
        <Link href="/dashboard/bookings" className="text-blue-600 font-medium hover:underline flex items-center">
          View all <ArrowRight className="w-4 h-4 ml-1" />
        </Link>
      </div>

      {upcomingBookings.length === 0 ? (
        <div className="bg-white p-12 rounded-2xl shadow-sm border border-gray-100 text-center">
          <Car className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-gray-900 mb-2">No upcoming rides</h3>
          <p className="text-gray-500 mb-6">You don't have any upcoming airport transfers scheduled.</p>
          <Link href="/booking" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-medium transition-colors inline-flex items-center">
            Book a Ride Now
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {upcomingBookings.map((booking: any) => (
            <div key={booking.id} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 flex flex-col md:flex-row justify-between items-center gap-4">
              <div className="flex-1 flex gap-6">
                <div className="hidden md:flex flex-col items-center justify-center px-6 border-r border-gray-100">
                  <span className="text-sm font-bold text-gray-500 uppercase">{new Date(booking.scheduled_time).toLocaleString('default', { month: 'short' })}</span>
                  <span className="text-2xl font-bold text-gray-900">{new Date(booking.scheduled_time).getDate()}</span>
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize
                      ${booking.booking_status === 'confirmed' ? 'bg-blue-100 text-blue-700' : 
                        booking.booking_status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'}`}>
                      {booking.booking_status.replace('_', ' ')}
                    </span>
                    <span className="text-gray-500 text-sm font-medium">#{booking.id.substring(0, 8)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-900 font-medium mb-1">
                    <MapPin className="w-4 h-4 text-gray-400" />
                    Pickup at {new Date(booking.scheduled_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                  <p className="text-gray-500 text-sm">{booking.pickup_lat}, {booking.pickup_lng} &rarr; {booking.dropoff_lat}, {booking.dropoff_lng}</p>
                </div>
              </div>
              <div className="flex gap-3 w-full md:w-auto">
                {booking.booking_status === 'in_progress' && (
                  <Link href={`/tracking/${booking.id}`} className="flex-1 md:flex-none bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl font-medium transition-colors text-center">
                    Live Tracking
                  </Link>
                )}
                <Link href={`/dashboard/bookings/${booking.id}`} className="flex-1 md:flex-none bg-gray-100 hover:bg-gray-200 text-gray-900 px-6 py-3 rounded-xl font-medium transition-colors text-center">
                  Details
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
