"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuthStore } from "@/store/authStore";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    
    // Public routes that bypass auth checks
    const publicRoutes = ["/login"];
    
    if (!token && !publicRoutes.includes(pathname)) {
      router.push("/login");
    } else if (token && pathname === "/login") {
      router.push("/");
    }
  }, [token, pathname, router, mounted]);

  if (!mounted) return null; // Prevent hydration mismatch

  return <>{children}</>;
}
