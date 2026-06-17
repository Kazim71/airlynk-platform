"use client";

import { useEffect, useState } from "react";
import { LiveMap } from "@/components/map/LiveMap";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function DispatchPage() {
  const [drivers, setDrivers] = useState<any[]>([]);

  const { data: bookings } = useQuery({
    queryKey: ["bookings"],
    queryFn: async () => {
      const res = await api.get("/bookings");
      return res.data;
    }
  });

  const handleDispatch = async (bookingId: string) => {
    try {
      await api.post(`/dispatch/${bookingId}/start`);
      alert("Dispatch triggered successfully");
    } catch (e: any) {
      alert(e.response?.data?.detail || "Failed to trigger dispatch");
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100vh-8rem)] gap-6">
      {/* Map Section */}
      <Card className="flex-1 overflow-hidden flex flex-col">
        <CardHeader className="py-3 px-4 border-b shrink-0">
          <CardTitle className="text-md">Live Fleet Tracking</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 p-0 relative">
          <LiveMap drivers={drivers} />
        </CardContent>
      </Card>

      {/* Sidebar List */}
      <Card className="w-full lg:w-96 flex flex-col overflow-hidden">
        <CardHeader className="py-3 px-4 border-b shrink-0">
          <CardTitle className="text-md">Dispatch Queue</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 p-0 overflow-y-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Booking</TableHead>
                <TableHead>Status</TableHead>
                <TableHead></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {bookings?.filter((b: any) => ["created", "confirmed", "payment_authorized", "dispatching"].includes(b.booking_status)).map((b: any) => (
                <TableRow key={b.id}>
                  <TableCell className="font-medium">{b.id.substring(0, 8)}</TableCell>
                  <TableCell><Badge variant="warning">{b.booking_status}</Badge></TableCell>
                  <TableCell>
                    <Button size="sm" variant="outline" onClick={() => handleDispatch(b.id)}>Dispatch</Button>
                  </TableCell>
                </TableRow>
              ))}
              {bookings?.filter((b: any) => ["failed"].includes(b.booking_status)).map((b: any) => (
                <TableRow key={b.id}>
                  <TableCell className="font-medium">{b.id.substring(0, 8)}</TableCell>
                  <TableCell><Badge variant="destructive">{b.booking_status}</Badge></TableCell>
                  <TableCell>
                    <Button size="sm" variant="outline" onClick={() => handleDispatch(b.id)}>Retry</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
