import Link from 'next/link';
import { Plane, ArrowRight, Shield, Clock } from 'lucide-react';
import { notFound } from 'next/navigation';

export const metadata = {
  title: 'Airport Routes - AirLynk',
  description: 'View premium transfer routes from this airport.',
};

const airports: Record<string, any> = {
  del: { code: 'DEL', name: 'Indira Gandhi International', city: 'Delhi', image: 'https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&q=80&w=1000', popularDestinations: ['Noida', 'Gurugram', 'South Delhi'] },
  bom: { code: 'BOM', name: 'Chhatrapati Shivaji Maharaj', city: 'Mumbai', image: 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&q=80&w=1000', popularDestinations: ['Colaba', 'Bandra', 'Andheri'] },
  blr: { code: 'BLR', name: 'Kempegowda International', city: 'Bengaluru', image: 'https://images.unsplash.com/photo-1596422846543-75c6fc197f0a?auto=format&fit=crop&q=80&w=1000', popularDestinations: ['Indiranagar', 'Koramangala', 'Whitefield'] },
  hyd: { code: 'HYD', name: 'Rajiv Gandhi International', city: 'Hyderabad', image: 'https://images.unsplash.com/photo-1577085750239-01140026e95c?auto=format&fit=crop&q=80&w=1000', popularDestinations: ['Hitec City', 'Banjara Hills', 'Gachibowli'] },
  maa: { code: 'MAA', name: 'Chennai International', city: 'Chennai', image: 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&q=80&w=1000', popularDestinations: ['OMR', 'Adyar', 'T Nagar'] },
  cok: { code: 'COK', name: 'Cochin International', city: 'Kochi', image: 'https://images.unsplash.com/photo-1590050752118-20410cefae0f?auto=format&fit=crop&q=80&w=1000', popularDestinations: ['Fort Kochi', 'Marine Drive', 'Edappally'] },
};

export default async function AirportDetailPage({ params }: { params: Promise<{ slug: string }> }) {
  const resolvedParams = await params;
  const airport = airports[resolvedParams.slug.toLowerCase()];

  if (!airport) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="h-96 relative">
        <img src={airport.image} alt={airport.city} className="w-full h-full object-cover" />
        <div className="absolute inset-0 bg-black/60" />
        <div className="absolute inset-0 flex items-center">
          <div className="max-w-6xl mx-auto px-4 w-full">
            <Link href="/airports" className="text-gray-300 hover:text-white mb-6 inline-flex items-center text-sm font-medium">
              &larr; Back to Airports
            </Link>
            <div className="flex items-center gap-3 text-blue-400 font-bold mb-2">
              <Plane className="w-6 h-6" /> {airport.code}
            </div>
            <h1 className="text-5xl font-bold text-white mb-2">{airport.city}</h1>
            <p className="text-xl text-gray-200">{airport.name}</p>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-16 grid grid-cols-1 md:grid-cols-3 gap-12">
        <div className="md:col-span-2">
          <h2 className="text-2xl font-bold mb-6">Popular Transfer Destinations</h2>
          <div className="space-y-4">
            {airport.popularDestinations.map((dest: string) => (
              <div key={dest} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold text-gray-900">{dest}</h3>
                  <p className="text-gray-500 text-sm">Approx. fare available dynamically</p>
                </div>
                <Link href={`/booking?pickup=${airport.code}&dropoff=${dest}`} className="text-blue-600 hover:text-blue-700 font-medium flex items-center">
                  Book <ArrowRight className="w-4 h-4 ml-1" />
                </Link>
              </div>
            ))}
          </div>
        </div>
        
        <div>
          <div className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100 sticky top-8">
            <h3 className="text-xl font-bold mb-6">Why book with us?</h3>
            <ul className="space-y-6">
              <li className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Flight Tracking</h4>
                  <p className="text-sm text-gray-500 mt-1">We adjust pickup time automatically if your flight is early or delayed.</p>
                </div>
              </li>
              <li className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                  <Shield className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">Premium Fleet</h4>
                  <p className="text-sm text-gray-500 mt-1">Professional chauffeurs and sanitized vehicles for your safety.</p>
                </div>
              </li>
            </ul>
            <div className="mt-8 pt-8 border-t border-gray-100">
              <Link href="/booking" className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-medium transition-all flex items-center justify-center">
                Book Transfer Now
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
