'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // Return null or loading state during SSR to avoid hydration mismatch with persist middleware
    return null;
  }

  return <>{children}</>;
}
