'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Plane, MapPin, Calendar, Clock, Car, CheckCircle, CreditCard, Shield, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/authStore';

// MOCK Destinations for MVP map-less picking.
const MOCK_DESTINATIONS: Record<string, { lat: number; lng: number }> = {
  'Noida': { lat: 28.5355, lng: 77.3910 },
  'Gurugram': { lat: 28.4595, lng: 77.0266 },
  'Colaba': { lat: 18.9067, lng: 72.8147 },
  'Bandra': { lat: 19.0596, lng: 72.8295 },
  'Indiranagar': { lat: 12.9784, lng: 77.6408 },
  'Hitec City': { lat: 17.4435, lng: 78.3772 },
  'OMR': { lat: 12.9674, lng: 80.2589 },
  'Fort Kochi': { lat: 9.9658, lng: 76.2447 },
};

export default function BookingPage() {
  const router = useRouter();
  const token = useAuthStore((state) => state.token);
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Step 1: Trip
  const [airportCode, setAirportCode] = useState('');
  const [destination, setDestination] = useState('Noida');
  const [vehicleClass, setVehicleClass] = useState('sedan');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');

  // Step 2 & 3: Estimate & Intent
  const [estimate, setEstimate] = useState<any>(null);
  const [booking, setBooking] = useState<any>(null);
  const [paymentIntent, setPaymentIntent] = useState<any>(null);

  const { data: airports, isLoading: loadingAirports } = useQuery({
    queryKey: ['airports'],
    queryFn: async () => {
      const res = await api.get('/airports');
      return res.data;
    }
  });

  // Pre-select first airport
  useEffect(() => {
    if (airports && airports.length > 0 && !airportCode) {
      setAirportCode(airports[0].code);
    }
  }, [airports, airportCode]);

  const handleEstimate = async () => {
    setLoading(true);
    setError('');
    
    try {
      const pickup = airports?.find((a: any) => a.code === airportCode);
      const dropoff = MOCK_DESTINATIONS[destination];

      if (!pickup || !dropoff) throw new Error('Invalid locations selected.');

      // 1. Get Geo Estimate (distance/duration)
      const geoRes = await api.post('/geo/estimate', {
        pickup_lat: pickup.latitude,
        pickup_lng: pickup.longitude,
        dropoff_lat: dropoff.lat,
        dropoff_lng: dropoff.lng
      });
      const geoData = geoRes.data;

      // 2. Get Pricing Estimate
      const pricingRes = await api.post('/pricing/estimate', {
        pickup_lat: pickup.latitude,
        pickup_lng: pickup.longitude,
        dropoff_lat: dropoff.lat,
        dropoff_lng: dropoff.lng,
        city: pickup.city,
        vehicle_type: vehicleClass,
        estimated_distance_km: geoData.distance_km,
        estimated_duration_minutes: geoData.duration_minutes,
        is_airport: true
      });

      setEstimate({ ...pricingRes.data, geoData });
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to get estimate');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBooking = async () => {
    if (!token) {
      router.push('/login');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const pickup = airports?.find((a: any) => a.code === airportCode);
      const dropoff = MOCK_DESTINATIONS[destination];
      const scheduledTime = new Date(`${date}T${time}:00Z`).toISOString();

      // Create Booking (PENDING)
      const bookRes = await api.post('/bookings', {
        pickup_location: `${pickup.city} - ${pickup.name}`,
        pickup_lat: pickup.latitude,
        pickup_lng: pickup.longitude,
        dropoff_location: destination,
        dropoff_lat: dropoff.lat,
        dropoff_lng: dropoff.lng,
        vehicle_class: vehicleClass,
        scheduled_time: scheduledTime,
        passenger_count: 1
      });
      
      setBooking(bookRes.data);

      // Create Payment Intent
      const intentRes = await api.post('/payments/create-intent', {
        booking_id: bookRes.data.id,
        amount: estimate.total_estimate,
        currency: "INR"
      });
      
      setPaymentIntent(intentRes.data);
      setStep(3); // Go to Payment UI
    } catch (err: any) {
      if (err.response?.status === 401) {
        router.push('/login');
      } else {
        setError(err.response?.data?.detail || 'Failed to confirm booking');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSimulatePayment = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Simulate Stripe Webhook Success
      await api.post('/payments/webhook/mock', {
        intent_id: paymentIntent.id,
        status: "succeeded"
      });
      
      // Assume success, wait 2 seconds for visual effect
      setTimeout(() => {
        setStep(4);
        setLoading(false);
      }, 2000);
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Payment failed');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pt-24 pb-12 px-4 font-sans text-gray-900">
      <div className="max-w-4xl mx-auto">
        
        {/* Progress Bar */}
        <div className="mb-12 flex justify-between items-center relative px-6">
          <div className="absolute left-6 right-6 top-1/2 h-1 bg-gray-200 -z-10 rounded-full" />
          <motion.div 
            className="absolute left-6 top-1/2 h-1 bg-blue-600 -z-10 rounded-full" 
            initial={{ width: '0%' }}
            animate={{ width: `${(step - 1) * 33.3}%` }}
            transition={{ duration: 0.5 }}
          />
          
          {['Trip', 'Estimate', 'Pay', 'Confirm'].map((label, index) => {
            const i = index + 1;
            const active = step >= i;
            return (
              <div key={i} className="flex flex-col items-center gap-2">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold shadow-md transition-all duration-500 ${active ? 'bg-blue-600 text-white scale-110' : 'bg-white text-gray-400 border border-gray-200'}`}>
                  {i === 4 && active ? <CheckCircle className="w-6 h-6" /> : i}
                </div>
                <span className={`text-xs font-medium uppercase tracking-wider ${active ? 'text-blue-700' : 'text-gray-400'}`}>{label}</span>
              </div>
            );
          })}
        </div>

        <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl border border-white/40 p-8 md:p-12 overflow-hidden relative">
          
          <AnimatePresence mode="wait">
            {error && (
              <motion.div 
                initial={{ opacity: 0, y: -10 }} 
                animate={{ opacity: 1, y: 0 }} 
                exit={{ opacity: 0 }}
                className="mb-8 p-4 bg-red-50 text-red-600 rounded-xl text-sm font-medium flex items-center gap-2 border border-red-100"
              >
                <Shield className="w-5 h-5" /> {error}
              </motion.div>
            )}

            {step === 1 && (
              <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
                <div>
                  <h2 className="text-3xl font-bold mb-2 tracking-tight">Where to?</h2>
                  <p className="text-gray-500">Enter your flight and destination details for a guaranteed premium ride.</p>
                </div>
                
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Pickup Airport</label>
                      <div className="relative">
                        <Plane className="absolute left-4 top-4 w-5 h-5 text-blue-500" />
                        {loadingAirports ? (
                          <div className="w-full pl-12 pr-4 py-3.5 bg-gray-50 rounded-2xl border border-gray-200 animate-pulse text-gray-400">Loading airports...</div>
                        ) : (
                          <select 
                            value={airportCode}
                            onChange={(e) => setAirportCode(e.target.value)}
                            className="w-full pl-12 pr-4 py-3.5 bg-gray-50 hover:bg-gray-100 transition-colors rounded-2xl border border-gray-200 focus:ring-4 focus:ring-blue-600/20 focus:border-blue-600 outline-none appearance-none font-medium text-gray-800"
                          >
                            {airports?.map((a: any) => (
                              <option key={a.code} value={a.code}>{a.city} - {a.name} ({a.code})</option>
                            ))}
                          </select>
                        )}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Dropoff Area</label>
                      <div className="relative">
                        <MapPin className="absolute left-4 top-4 w-5 h-5 text-rose-500" />
                        <select 
                          value={destination}
                          onChange={(e) => setDestination(e.target.value)}
                          className="w-full pl-12 pr-4 py-3.5 bg-gray-50 hover:bg-gray-100 transition-colors rounded-2xl border border-gray-200 focus:ring-4 focus:ring-blue-600/20 focus:border-blue-600 outline-none appearance-none font-medium text-gray-800"
                        >
                          {Object.keys(MOCK_DESTINATIONS).map((dest) => (
                            <option key={dest} value={dest}>{dest}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Date</label>
                        <div className="relative">
                          <Calendar className="absolute left-4 top-4 w-5 h-5 text-gray-400" />
                          <input 
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full pl-12 pr-4 py-3.5 bg-gray-50 hover:bg-gray-100 transition-colors rounded-2xl border border-gray-200 focus:ring-4 focus:ring-blue-600/20 focus:border-blue-600 outline-none font-medium text-gray-800"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">Time</label>
                        <div className="relative">
                          <Clock className="absolute left-4 top-4 w-5 h-5 text-gray-400" />
                          <input 
                            type="time"
                            value={time}
                            onChange={(e) => setTime(e.target.value)}
                            className="w-full pl-12 pr-4 py-3.5 bg-gray-50 hover:bg-gray-100 transition-colors rounded-2xl border border-gray-200 focus:ring-4 focus:ring-blue-600/20 focus:border-blue-600 outline-none font-medium text-gray-800"
                          />
                        </div>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">Service Class</label>
                      <div className="grid grid-cols-3 gap-3">
                        {['sedan', 'suv', 'luxury'].map((cls) => (
                          <button
                            key={cls}
                            onClick={() => setVehicleClass(cls)}
                            className={`p-4 rounded-2xl border-2 transition-all group ${vehicleClass === cls ? 'border-blue-600 bg-blue-50/50 text-blue-700' : 'border-gray-100 hover:border-gray-200 bg-white'}`}
                          >
                            <Car className={`w-8 h-8 mx-auto mb-2 transition-transform group-hover:scale-110 ${vehicleClass === cls ? 'text-blue-600' : 'text-gray-400'}`} />
                            <span className="capitalize font-medium text-sm block text-center">{cls}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="pt-6 border-t border-gray-100">
                  <button 
                    onClick={handleEstimate}
                    disabled={loading || !date || !time || loadingAirports}
                    className="w-full bg-black hover:bg-gray-900 text-white py-5 rounded-2xl font-bold text-lg transition-all flex items-center justify-center gap-2 shadow-xl shadow-black/10 disabled:opacity-50 disabled:shadow-none"
                  >
                    {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : 'Get Premium Estimate'}
                  </button>
                </div>
              </motion.div>
            )}

            {step === 2 && estimate && (
              <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
                <div>
                  <h2 className="text-3xl font-bold mb-2 tracking-tight">Review Trip</h2>
                  <p className="text-gray-500">Your upfront premium fare, fully inclusive.</p>
                </div>
                
                <div className="bg-gradient-to-br from-gray-900 to-black text-white rounded-3xl p-8 shadow-2xl relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-8 opacity-10 pointer-events-none">
                    <Plane className="w-48 h-48" />
                  </div>
                  
                  <div className="flex justify-between items-start mb-8 relative z-10">
                    <div>
                      <span className="bg-white/20 text-white px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider mb-3 inline-block">
                        {vehicleClass} Class
                      </span>
                      <h3 className="text-5xl font-bold">₹{estimate.total_estimate.toFixed(2)}</h3>
                    </div>
                  </div>

                  <div className="space-y-4 relative z-10">
                    <div className="flex justify-between items-center py-3 border-b border-white/10">
                      <span className="text-gray-400">Distance ({estimate.geoData.distance_km.toFixed(1)} km)</span>
                      <span className="font-medium">₹{estimate.distance_fare.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between items-center py-3 border-b border-white/10">
                      <span className="text-gray-400">Time Estimate</span>
                      <span className="font-medium">{estimate.geoData.duration_mins} mins</span>
                    </div>
                    <div className="flex justify-between items-center py-3 border-b border-white/10">
                      <span className="text-gray-400">Airport Fee</span>
                      <span className="font-medium">₹{estimate.airport_fee.toFixed(2)}</span>
                    </div>
                  </div>
                </div>

                <div className="flex gap-4 pt-4 border-t border-gray-100">
                  <button 
                    onClick={() => setStep(1)}
                    className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-800 py-5 rounded-2xl font-bold text-lg transition-colors"
                  >
                    Edit
                  </button>
                  <button 
                    onClick={handleCreateBooking}
                    disabled={loading}
                    className="flex-[2] bg-blue-600 hover:bg-blue-700 text-white py-5 rounded-2xl font-bold text-lg transition-all shadow-xl shadow-blue-600/20 flex justify-center items-center gap-2"
                  >
                    {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : 'Confirm & Proceed'}
                  </button>
                </div>
              </motion.div>
            )}

            {step === 3 && paymentIntent && (
              <motion.div key="step3" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="space-y-8 text-center py-8">
                <div className="w-20 h-20 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-6 ring-8 ring-blue-50/50">
                  <CreditCard className="w-10 h-10" />
                </div>
                
                <h2 className="text-3xl font-bold tracking-tight">Complete Payment</h2>
                <p className="text-gray-500 max-w-md mx-auto">Authorize ₹{paymentIntent.amount} to secure your premium ride.</p>
                
                <div className="max-w-xs mx-auto p-6 bg-gray-50 rounded-3xl border border-gray-200 space-y-4">
                  <div className="h-10 bg-gray-200 rounded animate-pulse" />
                  <div className="h-10 bg-gray-200 rounded animate-pulse" />
                  <div className="flex gap-2">
                    <div className="h-10 bg-gray-200 rounded animate-pulse flex-1" />
                    <div className="h-10 bg-gray-200 rounded animate-pulse flex-1" />
                  </div>
                </div>

                <div className="pt-6">
                  <button 
                    onClick={handleSimulatePayment}
                    disabled={loading}
                    className="w-full max-w-xs mx-auto bg-black hover:bg-gray-900 text-white py-5 rounded-2xl font-bold text-lg transition-all flex items-center justify-center gap-2 shadow-2xl shadow-black/20"
                  >
                    {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : 'Pay Now (Mock)'}
                  </button>
                </div>
              </motion.div>
            )}

            {step === 4 && (
              <motion.div key="step4" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-12">
                <motion.div 
                  initial={{ scale: 0 }} 
                  animate={{ scale: 1 }} 
                  transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
                  className="w-28 h-28 bg-green-50 text-green-500 rounded-full flex items-center justify-center mx-auto mb-8 ring-8 ring-green-50/50"
                >
                  <CheckCircle className="w-14 h-14" />
                </motion.div>
                <h2 className="text-4xl font-extrabold mb-4 tracking-tight">You're All Set!</h2>
                <p className="text-gray-500 mb-10 text-xl font-light">Payment Authorized. Your chauffeur will arrive on time.</p>
                <button 
                  onClick={() => router.push('/dashboard')}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-10 py-5 rounded-full font-bold text-lg transition-all shadow-xl shadow-blue-600/30"
                >
                  Go to Dashboard
                </button>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </div>
    </div>
  );
}
