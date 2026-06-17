"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";
import { Badge } from "@/components/ui/Badge";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";

export default function BookingsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["bookings"],
    queryFn: async () => {
      // Mocked fallback if endpoint is unavailable
        const res = await api.get("/bookings");
        return res.data;
      }
    });

  return (
    <Card>
      <CardHeader>
        <CardTitle>All Bookings</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="py-10 text-center text-gray-500">Loading bookings...</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Customer</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data?.map((b: any) => (
                <TableRow key={b.id}>
                  <TableCell className="font-medium">{b.id}</TableCell>
                  <TableCell>{b.customer_id}</TableCell>
                  <TableCell>{new Date(b.created_at).toLocaleString()}</TableCell>
                  <TableCell>
                    <Badge variant={
                      b.booking_status === "completed" ? "success" : 
                      b.booking_status === "cancelled" ? "destructive" : "default"
                    }>
                      {b.booking_status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
