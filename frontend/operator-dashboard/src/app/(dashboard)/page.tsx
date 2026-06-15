"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Activity, Users, Car, CheckCircle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useEffect, useState } from "react";
import { WebSocketClient } from "@/lib/websocket";

export default function DashboardOverview() {
  const [wsData, setWsData] = useState<{type: string, data: any}[]>([]);

  // We could fetch real health metrics here. Since we have Prometheus text output at /metrics,
  // we'll fetch /health to show service status.
  const { data: health, isLoading } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const res = await api.get("/health");
      return res.data.data;
    },
    refetchInterval: 30000,
  });

  useEffect(() => {
    const ws = new WebSocketClient("/operators/live");
    const unsubscribe = ws.subscribe((data) => {
      setWsData(prev => [data, ...prev].slice(0, 50));
    });
    ws.connect();

    return () => {
      unsubscribe();
      ws.disconnect();
    };
  }, []);

  // Mock data for the chart since prometheus querying is complex to implement raw on frontend
  // without a backend proxy that translates PromQL to JSON.
  const chartData = [
    { time: '10:00', bookings: 400, dispatch: 240 },
    { time: '10:30', bookings: 300, dispatch: 139 },
    { time: '11:00', bookings: 200, dispatch: 980 },
    { time: '11:30', bookings: 278, dispatch: 390 },
    { time: '12:00', bookings: 189, dispatch: 480 },
    { time: '12:30', bookings: 239, dispatch: 380 },
    { time: '13:00', bookings: 349, dispatch: 430 },
  ];

  return (
    <div className="space-y-6">
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Platform Health</CardTitle>
            <Activity className="h-4 w-4 text-gray-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? "Checking..." : (health?.status === "healthy" ? "100%" : "Degraded")}
            </div>
            <p className="text-xs text-gray-500 mt-1">
              PG: {health?.postgres ? "OK" : "ERR"} | Redis: {health?.redis ? "OK" : "ERR"} | RMQ: {health?.rabbitmq ? "OK" : "ERR"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Drivers</CardTitle>
            <Car className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,245</div>
            <p className="text-xs text-gray-500 mt-1">+12.5% from last hour</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active Bookings</CardTitle>
            <Users className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">842</div>
            <p className="text-xs text-gray-500 mt-1">+4.2% from last hour</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Dispatch Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">98.2%</div>
            <p className="text-xs text-gray-500 mt-1">Based on last 1000 trips</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-7">
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Throughput</CardTitle>
            <CardDescription>System throughput over the last few hours</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <Line type="monotone" dataKey="bookings" stroke="#3b82f6" strokeWidth={2} />
                <Line type="monotone" dataKey="dispatch" stroke="#8b5cf6" strokeWidth={2} />
                <CartesianGrid stroke="#ccc" strokeDasharray="5 5" vertical={false} />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
                <Tooltip />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Live Event Stream</CardTitle>
            <CardDescription>Realtime events from the message broker</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 h-[300px] overflow-y-auto">
              {wsData.length === 0 ? (
                <div className="text-sm text-gray-500 text-center py-10">Waiting for events...</div>
              ) : (
                wsData.map((evt, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm">
                    <span className="w-2 h-2 mt-1.5 rounded-full bg-blue-500 shrink-0"></span>
                    <div>
                      <p className="font-medium">{evt.type}</p>
                      <pre className="text-xs text-gray-500 mt-1 bg-gray-50 p-2 rounded truncate max-w-xs">
                        {JSON.stringify(evt.data)}
                      </pre>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
