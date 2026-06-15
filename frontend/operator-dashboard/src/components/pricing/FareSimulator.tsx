"use client";

import React, { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Calculator } from "lucide-react";

export function FareSimulator() {
  const [form, setForm] = useState({
    city: "New York",
    vehicle_type: "sedan",
    pickup_lat: 40.7128,
    pickup_lon: -74.0060,
    dropoff_lat: 40.7580,
    dropoff_lon: -73.9855,
    estimated_duration_minutes: 15,
    estimated_distance_km: 5.2,
    is_airport: false,
  });

  const [estimate, setEstimate] = useState<any>(null);

  const mutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.post("/api/v1/pricing/estimate", data);
      return response.data;
    },
    onSuccess: (data) => {
      setEstimate(data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate(form);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Calculator className="w-5 h-5 text-blue-500" />
          Fare Simulator
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">City</label>
                <input 
                  type="text" 
                  value={form.city}
                  onChange={(e) => setForm({...form, city: e.target.value})}
                  className="w-full p-2 border rounded-md"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Vehicle Type</label>
                <select 
                  value={form.vehicle_type}
                  onChange={(e) => setForm({...form, vehicle_type: e.target.value})}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="sedan">Sedan</option>
                  <option value="suv">SUV</option>
                  <option value="luxury">Luxury</option>
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Est. Distance (km)</label>
                <input 
                  type="number" step="0.1"
                  value={form.estimated_distance_km}
                  onChange={(e) => setForm({...form, estimated_distance_km: parseFloat(e.target.value)})}
                  className="w-full p-2 border rounded-md"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Est. Duration (min)</label>
                <input 
                  type="number" 
                  value={form.estimated_duration_minutes}
                  onChange={(e) => setForm({...form, estimated_duration_minutes: parseInt(e.target.value)})}
                  className="w-full p-2 border rounded-md"
                />
              </div>
            </div>

            <div className="flex items-center gap-2 pt-2">
              <input 
                type="checkbox" 
                id="is_airport"
                checked={form.is_airport}
                onChange={(e) => setForm({...form, is_airport: e.target.checked})}
                className="rounded border-gray-300"
              />
              <label htmlFor="is_airport" className="text-sm font-medium">Apply Airport Surcharge</label>
            </div>

            <Button type="submit" disabled={mutation.isPending} className="w-full mt-4">
              {mutation.isPending ? "Calculating..." : "Calculate Estimate"}
            </Button>
          </form>

          {/* Results Panel */}
          <div className="bg-gray-50 p-6 rounded-lg border border-gray-100">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Calculation Breakdown</h3>
            {estimate ? (
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Base Fare</span>
                  <span className="font-medium">${estimate.base_fare}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Distance Fare ({estimate.estimated_distance_km} km)</span>
                  <span className="font-medium">${estimate.distance_fare}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Time Fare ({estimate.estimated_duration_minutes} min)</span>
                  <span className="font-medium">${estimate.time_fare}</span>
                </div>
                {parseFloat(estimate.airport_fee) > 0 && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Airport Surcharge</span>
                    <span className="font-medium">${estimate.airport_fee}</span>
                  </div>
                )}
                <div className="pt-2 border-t border-gray-200 flex justify-between">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium">${estimate.subtotal}</span>
                </div>
                <div className="flex justify-between text-indigo-600">
                  <span>Surge Multiplier</span>
                  <span className="font-bold">x{estimate.surge_applied}</span>
                </div>
                <div className="pt-3 border-t border-gray-200 flex justify-between items-center">
                  <span className="font-bold text-gray-900">Total Estimate</span>
                  <span className="text-2xl font-black text-gray-900">${estimate.total_estimate}</span>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                Submit the form to see calculation breakdown
              </div>
            )}
            {mutation.isError && (
              <div className="mt-4 p-3 bg-red-50 text-red-600 rounded-md text-sm">
                Error: {(mutation.error as any).response?.data?.detail || mutation.error.message}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
