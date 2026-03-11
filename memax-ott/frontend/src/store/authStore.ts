import { create } from "zustand";
import { authService } from "@/services/auth.service";

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  profile_picture?: string;
  is_admin: boolean;
}

interface AuthStore {
  user: User | null;
  loading: boolean;
  setUser: (user: User | null) => void;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  loading: true,

  setUser: (user) => set({ user, loading: false }),

  login: async (email, password) => {
    await authService.login({ email, password });
    const user = await authService.getCurrentUser();
    set({ user, loading: false });
  },

  logout: () => {
    authService.logout();
    set({ user: null });
  },

  checkAuth: async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (token) {
        const user = await authService.getCurrentUser();
        set({ user, loading: false });
      } else {
        set({ loading: false });
      }
    } catch (error) {
      set({ user: null, loading: false });
    }
  },
}));
