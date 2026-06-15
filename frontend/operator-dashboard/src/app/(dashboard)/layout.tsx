"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { Button } from "@/components/ui/Button";
import { Activity, Car, FileText, Map, Settings, LogOut, Bell } from "lucide-react";

import { NotificationFeed } from "@/components/notifications/NotificationFeed";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  const navItems = [
    { href: "/", label: "Overview", icon: Activity },
    { href: "/dispatch", label: "Dispatch", icon: Car },
    { href: "/bookings", label: "Bookings", icon: FileText },
  ];

  return (
    <div className="flex min-h-screen flex-col md:flex-row bg-gray-50">
      {/* Sidebar */}
      <aside className="w-full md:w-64 flex-shrink-0 bg-gray-950 text-white flex flex-col">
        <div className="p-6">
          <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
            <Map className="w-6 h-6 text-blue-500" />
            AirLynk Ops
          </h2>
        </div>
        <nav className="flex-1 px-4 space-y-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link key={item.href} href={item.href} className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors ${isActive ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800 hover:text-white"}`}>
                <item.icon className="w-5 h-5" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-3 mb-4 px-2">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-sm font-medium">
              {user?.email?.charAt(0).toUpperCase() || "O"}
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium leading-none">{user?.email || "Operator"}</span>
              <span className="text-xs text-gray-400 mt-1 capitalize">{user?.role || "Admin"}</span>
            </div>
          </div>
          <Button variant="ghost" className="w-full justify-start text-gray-300 hover:text-white hover:bg-gray-800" onClick={handleLogout}>
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        <header className="h-16 bg-white border-b flex items-center justify-between px-6 shrink-0 shadow-sm">
          <h1 className="text-lg font-semibold text-gray-900 capitalize">
            {pathname === "/" ? "Platform Overview" : pathname.split('/').pop()}
          </h1>
          <div className="flex items-center gap-4">
            <NotificationFeed />
            <Button variant="outline" size="icon">
              <Settings className="w-5 h-5 text-gray-600" />
            </Button>
          </div>
        </header>
        <div className="flex-1 p-6 overflow-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
