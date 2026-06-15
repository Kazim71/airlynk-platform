import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  user: { id: string; email: string; role: string | null } | null;
  setAuth: (token: string, user: any) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setAuth: (token, user) => {
        localStorage.setItem("airlynk_access_token", token);
        set({ token, user });
      },
      logout: () => {
        localStorage.removeItem("airlynk_access_token");
        set({ token: null, user: null });
      },
    }),
    {
      name: 'auth-storage',
    }
  )
);
