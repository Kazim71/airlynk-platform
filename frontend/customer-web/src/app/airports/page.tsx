import Link from 'next/link';
import { Plane, ArrowRight } from 'lucide-react';

export const metadata = {
  title: 'Airports - AirLynk',
  description: 'View all supported Indian airports for premium transfers.',
};

const airports = [
  { code: 'DEL', name: 'Indira Gandhi International', city: 'Delhi', image: 'https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&q=80&w=1000' },
  { code: 'BOM', name: 'Chhatrapati Shivaji Maharaj', city: 'Mumbai', image: 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&q=80&w=1000' },
  { code: 'BLR', name: 'Kempegowda International', city: 'Bengaluru', image: 'https://images.unsplash.com/photo-1596422846543-75c6fc197f0a?auto=format&fit=crop&q=80&w=1000' },
  { code: 'HYD', name: 'Rajiv Gandhi International', city: 'Hyderabad', image: 'https://images.unsplash.com/photo-1577085750239-01140026e95c?auto=format&fit=crop&q=80&w=1000' },
  { code: 'MAA', name: 'Chennai International', city: 'Chennai', image: 'https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&q=80&w=1000' },
  { code: 'COK', name: 'Cochin International', city: 'Kochi', image: 'https://images.unsplash.com/photo-1590050752118-20410cefae0f?auto=format&fit=crop&q=80&w=1000' },
];

export default function AirportsPage() {
  return (
    <div className="min-h-screen bg-gray-50 pt-24 pb-12 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-12">
          <h1 className="text-4xl font-bold mb-4 tracking-tight">Our Hubs</h1>
          <p className="text-xl text-gray-600">Premium transfers available at these major Indian airports.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {airports.map((airport) => (
            <Link href={`/airports/${airport.code.toLowerCase()}`} key={airport.code} className="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl transition-all block">
              <div className="h-48 relative overflow-hidden">
                <img src={airport.image} alt={airport.city} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
                <div className="absolute top-4 right-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-semibold text-blue-600 shadow-sm flex items-center gap-1">
                  <Plane className="w-4 h-4" /> {airport.code}
                </div>
              </div>
              <div className="p-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-1">{airport.city}</h3>
                <p className="text-gray-500 mb-6">{airport.name}</p>
                <div className="flex items-center text-blue-600 font-medium group-hover:text-blue-700">
                  View Routes <ArrowRight className="w-4 h-4 ml-1 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
