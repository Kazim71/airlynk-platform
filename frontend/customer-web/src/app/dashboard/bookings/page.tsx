'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function BookingsList() {
  const { data, isLoading } = useQuery({
    queryKey: ['bookings'],
    queryFn: async () => {
      const res = await api.get('/bookings');
      return res.data;
    }
  });

  if (isLoading) return <div>Loading...</div>;

  const bookings = data || [];

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">My Bookings</h1>
      
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-gray-50 border-b border-gray-100">
            <tr>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">ID</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">Date & Time</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">Status</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600">Fare</th>
              <th className="px-6 py-4 text-sm font-semibold text-gray-600 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {bookings.map((booking: any) => (
              <tr key={booking.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">#{booking.id.substring(0, 8)}</td>
                <td className="px-6 py-4 text-sm text-gray-600">
                  {new Date(booking.scheduled_time).toLocaleString()}
                </td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold capitalize
                    ${booking.status === 'confirmed' ? 'bg-blue-100 text-blue-700' : 
                      booking.status === 'in_progress' ? 'bg-yellow-100 text-yellow-700' : 
                      booking.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                    {booking.status.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">₹{booking.estimated_fare || booking.actual_fare || '-'}</td>
                <td className="px-6 py-4 text-right">
                  {booking.status === 'in_progress' ? (
                    <Link href={`/tracking/${booking.id}`} className="text-green-600 font-medium hover:underline text-sm">Track</Link>
                  ) : (
                    <span className="text-blue-600 font-medium hover:underline text-sm cursor-pointer">View</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {bookings.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            No bookings found.
          </div>
        )}
      </div>
    </div>
  );
}
