'use client';

import { motion } from 'framer-motion';
import { ArrowRight, Plane, MapPin, Shield, Clock, Star } from 'lucide-react';
import Link from 'next/link';

export default function Home() {
  const airports = [
    { code: 'DEL', name: 'Indira Gandhi International', city: 'Delhi', image: 'https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&q=80&w=1000' },
    { code: 'BOM', name: 'Chhatrapati Shivaji Maharaj', city: 'Mumbai', image: 'https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&q=80&w=1000' },
    { code: 'BLR', name: 'Kempegowda International', city: 'Bengaluru', image: 'https://images.unsplash.com/photo-1596422846543-75c6fc197f0a?auto=format&fit=crop&q=80&w=1000' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Hero Section */}
      <section className="relative h-[90vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&q=80&w=2000" 
            alt="Luxury Airport Transfer" 
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-black/50" />
        </div>
        
        <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-5xl md:text-7xl font-bold text-white mb-6 tracking-tight"
          >
            Premium Airport Transfers in India
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="text-xl md:text-2xl text-gray-200 mb-10 font-light"
          >
            Reliable, comfortable, and trackable rides to and from major airports.
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <Link href="/booking" className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-full text-lg font-medium transition-all shadow-lg hover:shadow-blue-500/30">
              Book Your Ride <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto bg-blue-50 rounded-full flex items-center justify-center mb-6 text-blue-600">
              <Clock className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold mb-3">On-Time Guarantee</h3>
            <p className="text-gray-600 leading-relaxed">We track your flight in real-time. Whether early or delayed, your chauffeur will be waiting.</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 mx-auto bg-blue-50 rounded-full flex items-center justify-center mb-6 text-blue-600">
              <Shield className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Premium Fleet</h3>
            <p className="text-gray-600 leading-relaxed">Travel in comfort with our meticulously maintained sedans, SUVs, and luxury vehicles.</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 mx-auto bg-blue-50 rounded-full flex items-center justify-center mb-6 text-blue-600">
              <MapPin className="w-8 h-8" />
            </div>
            <h3 className="text-xl font-semibold mb-3">Live Tracking</h3>
            <p className="text-gray-600 leading-relaxed">Share your live trip status with loved ones for peace of mind during your journey.</p>
          </div>
        </div>
      </section>

      {/* Top Destinations */}
      <section className="py-24 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h2 className="text-4xl font-bold mb-4 tracking-tight">Major Hubs</h2>
              <p className="text-xl text-gray-600">Available across top Indian airports</p>
            </div>
            <Link href="/airports" className="hidden md:flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium">
              View all airports <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {airports.map((airport) => (
              <Link href={`/airports/${airport.code.toLowerCase()}`} key={airport.code} className="group relative rounded-2xl overflow-hidden shadow-lg h-80">
                <img src={airport.image} alt={airport.city} className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                <div className="absolute bottom-0 left-0 p-8 w-full">
                  <div className="flex items-center gap-2 text-blue-300 font-medium mb-2">
                    <Plane className="w-4 h-4" />
                    <span>{airport.code}</span>
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-1">{airport.city}</h3>
                  <p className="text-gray-300 text-sm">{airport.name}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 text-center border-t border-gray-800">
        <div className="max-w-6xl mx-auto px-4 flex flex-col items-center">
          <h2 className="text-2xl font-bold text-white mb-6">AirLynk</h2>
          <div className="flex gap-6 mb-8">
            <Link href="/booking" className="hover:text-white transition-colors">Book a Ride</Link>
            <Link href="/airports" className="hover:text-white transition-colors">Airports</Link>
            <Link href="/login" className="hover:text-white transition-colors">Sign In</Link>
          </div>
          <p>&copy; {new Date().getFullYear()} AirLynk. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
