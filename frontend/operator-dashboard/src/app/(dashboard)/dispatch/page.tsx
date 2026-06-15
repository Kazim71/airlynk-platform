"use client";

import { useEffect, useState } from "react";
import { LiveMap } from "@/components/map/LiveMap";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";

export default function DispatchPage() {
  const [drivers, setDrivers] = useState<any[]>([
    { id: "d1", lat: 40.7128, lng: -74.0060, status: "available" },
    { id: "d2", lat: 40.7580, lng: -73.9855, status: "busy" },
    { id: "d3", lat: 40.7829, lng: -73.9654, status: "available" }
  ]);

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
              <TableRow>
                <TableCell className="font-medium">BK-001</TableCell>
                <TableCell><Badge variant="warning">Pending</Badge></TableCell>
                <TableCell><Button size="sm" variant="outline">Retry</Button></TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">BK-002</TableCell>
                <TableCell><Badge variant="success">Assigned</Badge></TableCell>
                <TableCell></TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">BK-003</TableCell>
                <TableCell><Badge variant="destructive">Failed</Badge></TableCell>
                <TableCell><Button size="sm" variant="outline">Retry</Button></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
