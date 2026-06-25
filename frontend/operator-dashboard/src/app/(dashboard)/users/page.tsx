"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/Card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/Table";

interface User {
  id: string;
  email: string;
  role: string;
  created_at: string;
}

export default function UsersPage() {
  const [drivers, setDrivers] = useState<User[]>([]);
  const [customers, setCustomers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const [driversRes, customersRes] = await Promise.all([
          api.get("/auth/users?role=driver"),
          api.get("/auth/users?role=customer")
        ]);
        setDrivers(driversRes.data);
        setCustomers(customersRes.data);
      } catch (err) {
        console.error("Failed to fetch users", err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchUsers();
  }, []);

  const renderTable = (users: User[]) => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>User ID</TableHead>
          <TableHead>Email</TableHead>
          <TableHead>Role</TableHead>
          <TableHead>Created Date</TableHead>
          <TableHead>Password</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {users.length === 0 ? (
          <TableRow>
            <TableCell colSpan={5} className="text-center text-gray-500 py-8">
              No users found.
            </TableCell>
          </TableRow>
        ) : (
          users.map((user) => (
            <TableRow key={user.id}>
              <TableCell className="font-medium text-xs text-gray-500">{user.id}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell className="capitalize">{user.role}</TableCell>
              <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
              <TableCell className="text-gray-400">********</TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );

  if (loading) {
    return <div className="p-8 text-center text-gray-500">Loading users...</div>;
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle>User Management</CardTitle>
          <CardDescription>View and manage registered customers and drivers across the platform.</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="customers">
            <TabsList className="mb-6">
              <TabsTrigger value="customers">Customers</TabsTrigger>
              <TabsTrigger value="drivers">Drivers</TabsTrigger>
            </TabsList>
            <TabsContent value="customers">
              {renderTable(customers)}
            </TabsContent>
            <TabsContent value="drivers">
              {renderTable(drivers)}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
