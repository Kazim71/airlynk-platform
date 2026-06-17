"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Plus, Edit } from "lucide-react";

export function PricingRulesTable() {
  const { data: rules, isLoading } = useQuery({
    queryKey: ["pricing-rules"],
    queryFn: async () => {
      const response = await api.get("/pricing/rules");
      return response.data;
    },
  });

  if (isLoading) {
    return <Card><CardContent className="p-6">Loading pricing rules...</CardContent></Card>;
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Active Pricing Rules</CardTitle>
        <Button size="sm">
          <Plus className="w-4 h-4 mr-2" />
          Add Rule
        </Button>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-gray-500 bg-gray-50 uppercase border-b">
              <tr>
                <th className="px-4 py-3">City</th>
                <th className="px-4 py-3">Vehicle</th>
                <th className="px-4 py-3">Base Fare</th>
                <th className="px-4 py-3">Per Km</th>
                <th className="px-4 py-3">Per Min</th>
                <th className="px-4 py-3">Min Fare</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {rules?.map((rule: any) => (
                <tr key={rule.id} className="border-b">
                  <td className="px-4 py-3 font-medium">{rule.city}</td>
                  <td className="px-4 py-3 capitalize">{rule.vehicle_type}</td>
                  <td className="px-4 py-3">${parseFloat(rule.base_fare).toFixed(2)}</td>
                  <td className="px-4 py-3">${parseFloat(rule.per_km_rate).toFixed(2)}</td>
                  <td className="px-4 py-3">${parseFloat(rule.per_minute_rate).toFixed(2)}</td>
                  <td className="px-4 py-3">${parseFloat(rule.minimum_fare).toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 text-xs rounded-full ${rule.active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {rule.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Button variant="ghost" size="icon">
                      <Edit className="w-4 h-4 text-gray-500" />
                    </Button>
                  </td>
                </tr>
              ))}
              {(!rules || rules.length === 0) && (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                    No pricing rules found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
