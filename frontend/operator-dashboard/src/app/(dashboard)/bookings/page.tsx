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
      try {
        const res = await api.get("/bookings");
        return res.data;
      } catch (err) {
        return [
          { id: "1", customer_id: "cust_abc", status: "pending", created_at: new Date().toISOString() },
          { id: "2", customer_id: "cust_def", status: "completed", created_at: new Date().toISOString() },
          { id: "3", customer_id: "cust_xyz", status: "cancelled", created_at: new Date().toISOString() },
        ];
      }
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
                      b.status === "completed" ? "success" : 
                      b.status === "cancelled" ? "destructive" : "default"
                    }>
                      {b.status}
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
