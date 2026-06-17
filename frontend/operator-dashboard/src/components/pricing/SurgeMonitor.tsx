"use client";

import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Activity, TrendingUp } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export function SurgeMonitor() {
  const { data: rules } = useQuery({
    queryKey: ["pricing_rules"],
    queryFn: async () => {
      const res = await api.get("/pricing/rules");
      return res.data;
    },
    refetchInterval: 30000,
  });

  const surges = rules?.map((r: any) => ({
    city: r.city,
    multiplier: r.surge_multiplier,
    activeBookings: 0,
    availableDrivers: 0
  })) || [];

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
          {surges.length === 0 ? (
            <div className="text-sm text-slate-400 text-center py-4">No active surge rules found.</div>
          ) : surges.map((surge: any) => (
            <div key={surge.city} className="bg-white/10 p-4 rounded-lg flex flex-col gap-2">
              <div className="flex justify-between items-center">
                <span className="font-semibold">{surge.city}</span>
                <span className={`text-xl font-bold ${surge.multiplier >= 1.5 ? 'text-red-400' : surge.multiplier > 1.0 ? 'text-yellow-400' : 'text-green-400'}`}>
                  {parseFloat(surge.multiplier).toFixed(2)}x
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
