"use client";

import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Activity, TrendingUp } from "lucide-react";

export function SurgeMonitor() {
  // In a real application, this would connect to a WebSocket or polling endpoint
  // to get real-time surge multipliers from the Redis cache.
  const [surges, setSurges] = useState([
    { city: "New York", multiplier: 1.0, activeBookings: 124, availableDrivers: 80 },
    { city: "London", multiplier: 1.2, activeBookings: 89, availableDrivers: 60 },
    { city: "San Francisco", multiplier: 1.8, activeBookings: 210, availableDrivers: 45 },
  ]);

  useEffect(() => {
    // Mocking real-time updates
    const interval = setInterval(() => {
      setSurges(prev => prev.map(s => ({
        ...s,
        multiplier: Math.max(1.0, s.multiplier + (Math.random() * 0.2 - 0.1))
      })));
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="bg-gradient-to-br from-indigo-900 to-slate-900 text-white border-none shadow-xl">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-indigo-400" />
          Live Surge Monitor
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 mt-4">
          {surges.map((surge) => (
            <div key={surge.city} className="bg-white/10 p-4 rounded-lg flex flex-col gap-2">
              <div className="flex justify-between items-center">
                <span className="font-semibold">{surge.city}</span>
                <span className={`text-xl font-bold ${surge.multiplier >= 1.5 ? 'text-red-400' : surge.multiplier > 1.0 ? 'text-yellow-400' : 'text-green-400'}`}>
                  {surge.multiplier.toFixed(2)}x
                </span>
              </div>
              <div className="flex justify-between text-xs text-slate-300 mt-2">
                <span className="flex items-center gap-1"><Activity className="w-3 h-3" /> {surge.activeBookings} reqs</span>
                <span>{surge.availableDrivers} drvrs</span>
              </div>
              {/* Progress bar representing ratio */}
              <div className="w-full bg-white/10 h-1.5 rounded-full mt-1 overflow-hidden">
                <div 
                  className={`h-full ${surge.multiplier >= 1.5 ? 'bg-red-500' : surge.multiplier > 1.0 ? 'bg-yellow-500' : 'bg-green-500'}`}
                  style={{ width: `${Math.min(100, (surge.activeBookings / (surge.availableDrivers || 1)) * 30)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
