"use client";

import React, { useState } from "react";
import { PricingRulesTable } from "@/components/pricing/PricingRulesTable";
import { SurgeMonitor } from "@/components/pricing/SurgeMonitor";
import { FareSimulator } from "@/components/pricing/FareSimulator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function PricingDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Pricing Engine</h2>
          <p className="text-gray-500">Manage base fares, surge multipliers, and simulate trip costs.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Tabs defaultValue="rules" className="w-full">
            <TabsList className="mb-4">
              <TabsTrigger value="rules">Pricing Rules</TabsTrigger>
              <TabsTrigger value="simulator">Fare Simulator</TabsTrigger>
            </TabsList>
            <TabsContent value="rules" className="p-0 border-none">
              <PricingRulesTable />
            </TabsContent>
            <TabsContent value="simulator" className="p-0 border-none">
              <FareSimulator />
            </TabsContent>
          </Tabs>
        </div>
        <div className="space-y-6">
          <SurgeMonitor />
        </div>
      </div>
    </div>
  );
}
