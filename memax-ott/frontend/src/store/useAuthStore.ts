import { create } from 'zustand';
import api from '@/services/api';

interface User {
    id: number;
    email: string;
    username: string;
    full_name: string;
    profile_picture?: string;
    is_admin: boolean;
}

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
    login: (credentials: any) => Promise<void>;
    signup: (userData: any) => Promise<void>;
    logout: () => void;
    checkAuth: () => Promise<void>;
}

const useAuthStore = create<AuthState>((set) => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,

    login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
            const formData = new FormData();
            formData.append('username', credentials.email);
            formData.append('password', credentials.password);

            const response = await api.post('/auth/login', formData, {
                headers: { 'Content-Type': 'multipart/form-data' } // OAuth2 requires form data
            });

            const { access_token } = response.data;
            localStorage.setItem('token', access_token);

            // Get user data
            const userRes = await api.get('/auth/me');
            set({ user: userRes.data, isAuthenticated: true, isLoading: false });
        } catch (error: any) {
            set({
                error: error.response?.data?.detail || 'Login failed',
                isLoading: false
            });
            throw error;
        }
    },

    signup: async (userData) => {
        set({ isLoading: true, error: null });
        try {
            await api.post('/auth/signup', userData);
            // After signup, login properly
            const formData = new FormData();
            formData.append('username', userData.email);
            formData.append('password', userData.password);

            const response = await api.post('/auth/login', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            const { access_token } = response.data;
            localStorage.setItem('token', access_token);

            const userRes = await api.get('/auth/me');
            set({ user: userRes.data, isAuthenticated: true, isLoading: false });
        } catch (error: any) {
            set({
                error: error.response?.data?.detail || 'Signup failed',
                isLoading: false
            });
            throw error;
        }
    },

    logout: () => {
        localStorage.removeItem('token');
        set({ user: null, isAuthenticated: false });
    },

    checkAuth: async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await api.get('/auth/me');
            set({ user: response.data, isAuthenticated: true });
        } catch (error) {
            localStorage.removeItem('token');
            set({ user: null, isAuthenticated: false });
        }
    }
}));

export default useAuthStore;
