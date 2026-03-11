"""
MEMAX OTT Frontend - Complete Setup Script
Generates all frontend files for the Next.js application
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

FILES = {
    # Global Styles
    "src/app/globals.css": '''@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 255, 255, 255;
  --background-start-rgb: 15, 23, 42;
  --background-end-rgb: 15, 23, 42;
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
  min-height: 100vh;
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1e293b;
}

::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
''',

    # Root Layout
    "src/app/layout.tsx": '''import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MEMAX - AI-Powered OTT Platform",
  description: "Stream your favorite movies and shows with personalized recommendations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
''',

    # Home Page
    "src/app/page.tsx": '''"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import MovieCard from "@/components/MovieCard";
import Footer from "@/components/Footer";
import { movieService } from "@/services/movie.service";

export default function Home() {
  const [featuredMovies, setFeaturedMovies] = useState([]);
  const [trendingMovies, setTrendingMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMovies();
  }, []);

  const loadMovies = async () => {
    try {
      const [featured, trending] = await Promise.all([
        movieService.getFeaturedMovies(),
        movieService.getTrendingMovies(),
      ]);
      setFeaturedMovies(featured);
      setTrendingMovies(trending);
    } catch (error) {
      console.error("Error loading movies:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-900">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center justify-center bg-gradient-to-b from-dark-800 to-dark-900">
        <div className="text-center z-10 px-4">
          <h1 className="text-6xl md:text-8xl font-bold mb-6 bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent">
            MEMAX
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8">
            AI-Powered Streaming Platform
          </p>
          <button className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-all transform hover:scale-105">
            Start Watching
          </button>
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-dark-900 via-transparent to-transparent"></div>
      </section>

      {/* Featured Movies */}
      <section className="container mx-auto px-4 py-12">
        <h2 className="text-3xl font-bold mb-6">Featured</h2>
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-64 bg-dark-800 animate-pulse rounded-lg"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {featuredMovies.map((movie: any) => (
              <MovieCard key={movie.id} movie={movie} />
            ))}
          </div>
        )}
      </section>

      {/* Trending Movies */}
      <section className="container mx-auto px-4 py-12">
        <h2 className="text-3xl font-bold mb-6">Trending Now</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {trendingMovies.map((movie: any) => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      </section>

      <Footer />
    </div>
  );
}
''',

    # Components
    "src/components/Navbar.tsx": '''"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuthStore } from "@/store/authStore";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout } = useAuthStore();

  return (
    <nav className="bg-dark-900/95 backdrop-blur-sm fixed w-full z-50 border-b border-dark-800">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="text-2xl font-bold text-primary-500">
            MEMAX
          </Link>

          <div className="hidden md:flex space-x-8">
            <Link href="/" className="hover:text-primary-500 transition">
              Home
            </Link>
            <Link href="/search" className="hover:text-primary-500 transition">
              Search
            </Link>
            {user && (
              <Link href="/continue-watching" className="hover:text-primary-500 transition">
                Continue Watching
              </Link>
            )}
          </div>

          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <Link href="/profile" className="hover:text-primary-500 transition">
                  Profile
                </Link>
                {user.is_admin && (
                  <Link href="/admin" className="hover:text-primary-500 transition">
                    Admin
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="bg-primary-600 hover:bg-primary-700 px-4 py-2 rounded transition"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="hover:text-primary-500 transition"
                >
                  Login
                </Link>
                <Link
                  href="/signup"
                  className="bg-primary-600 hover:bg-primary-700 px-4 py-2 rounded transition"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
''',

    "src/components/MovieCard.tsx": '''"use client";

import Link from "next/link";

interface MovieCardProps {
  movie: any;
}

export default function MovieCard({ movie }: MovieCardProps) {
  return (
    <Link href={`/watch/${movie.id}`}>
      <div className="group cursor-pointer transition-transform duration-300 hover:scale-105">
        <div className="relative aspect-[2/3] bg-dark-800 rounded-lg overflow-hidden">
          {movie.thumbnail_url ? (
            <img
              src={movie.thumbnail_url}
              alt={movie.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-dark-700 to-dark-900">
              <span className="text-4xl">🎬</span>
            </div>
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
            <div className="absolute bottom-0 p-4">
              <h3 className="font-semibold text-sm mb-1">{movie.title}</h3>
              <div className="flex items-center space-x-2 text-xs text-gray-300">
                <span>⭐ {movie.rating?.toFixed(1) || "N/A"}</span>
                <span>•</span>
                <span>{movie.release_year}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
''',

    "src/components/Footer.tsx": '''export default function Footer() {
  return (
    <footer className="bg-dark-900 border-t border-dark-800 mt-20">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-xl font-bold text-primary-500 mb-4">MEMAX</h3>
            <p className="text-gray-400 text-sm">
              AI-Powered OTT Platform with Personalized Recommendations
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Platform</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-primary-500">About Us</a></li>
              <li><a href="#" className="hover:text-primary-500">Features</a></li>
              <li><a href="#" className="hover:text-primary-500">Pricing</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-primary-500">Help Center</a></li>
              <li><a href="#" className="hover:text-primary-500">Contact</a></li>
              <li><a href="#" className="hover:text-primary-500">FAQ</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><a href="#" className="hover:text-primary-500">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-primary-500">Terms of Service</a></li>
              <li><a href="#" className="hover:text-primary-500">Cookie Policy</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-dark-800 mt-8 pt-8 text-center text-sm text-gray-400">
          <p>&copy; 2026 MEMAX. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
''',

    # Services
    "src/services/api.ts": '''import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);
''',

    "src/services/auth.service.ts": '''import { api } from "./api";

export interface LoginData {
  email: string;
  password: string;
}

export interface SignupData {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export const authService = {
  async login(data: LoginData) {
    const formData = new FormData();
    formData.append("username", data.email);
    formData.append("password", data.password);
    
    const response = await api.post("/api/auth/login", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    
    if (response.data.access_token) {
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);
    }
    
    return response.data;
  },

  async signup(data: SignupData) {
    const response = await api.post("/api/auth/signup", data);
    return response.data;
  },

  async getCurrentUser() {
    const response = await api.get("/api/auth/me");
    return response.data;
  },

  logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};
''',

    "src/services/movie.service.ts": '''import { api } from "./api";

export const movieService = {
  async getMovies(page = 1, pageSize = 20) {
    const response = await api.get("/api/movies", {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  async getMovie(id: number) {
    const response = await api.get(`/api/movies/${id}`);
    return response.data;
  },

  async getFeaturedMovies(limit = 10) {
    const response = await api.get("/api/movies/featured", {
      params: { limit },
    });
    return response.data;
  },

  async getTrendingMovies(limit = 10) {
    const response = await api.get("/api/movies/trending", {
      params: { limit },
    });
    return response.data;
  },

  async searchMovies(query: string, limit = 20) {
    const response = await api.get("/api/movies/search", {
      params: { q: query, limit },
    });
    return response.data;
  },
};
''',

    "src/services/recommendation.service.ts": '''import { api } from "./api";

export const recommendationService = {
  async getPersonalizedRecommendations(limit = 20) {
    const response = await api.post("/api/recommendations/personalized", {
      limit,
      exclude_watched: true,
    });
    return response.data;
  },

  async getSimilarMovies(movieId: number, limit = 10) {
    const response = await api.get(`/api/recommendations/similar/${movieId}`, {
      params: { limit },
    });
    return response.data;
  },

  async getColdStartRecommendations(limit = 20) {
    const response = await api.get("/api/recommendations/cold-start", {
      params: { limit },
    });
    return response.data;
  },
};
''',

    # Store
    "src/store/authStore.ts": '''import { create } from "zustand";
import { authService } from "@/services/auth.service";

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
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
''',

    # Login Page
    "src/app/login/page.tsx": '''"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/store/authStore";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      router.push("/");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-900 px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-500 mb-2">MEMAX</h1>
          <p className="text-gray-400">Sign in to your account</p>
        </div>

        <div className="bg-dark-800 rounded-lg p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-semibold transition disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-400">
            Don't have an account?{" "}
            <Link href="/signup" className="text-primary-500 hover:text-primary-400">
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
''',

    # Signup Page
    "src/app/signup/page.tsx": '''"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authService } from "@/services/auth.service";

export default function SignupPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    full_name: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await authService.signup(formData);
      router.push("/login");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Signup failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-900 px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-500 mb-2">MEMAX</h1>
          <p className="text-gray-400">Create your account</p>
        </div>

        <div className="bg-dark-800 rounded-lg p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-red-500/10 border border-red-500 text-red-500 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Username</label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Full Name</label>
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Password</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full px-4 py-3 bg-dark-700 border border-dark-600 rounded-lg focus:outline-none focus:border-primary-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-semibold transition disabled:opacity-50"
            >
              {loading ? "Creating account..." : "Sign Up"}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-400">
            Already have an account?{" "}
            <Link href="/login" className="text-primary-500 hover:text-primary-400">
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
''',

    # README
    "README.md": '''# MEMAX Frontend

Next.js frontend for the MEMAX OTT platform.

## Setup

```bash
npm install
npm run dev
```

Visit http://localhost:3000

## Features

- Modern UI with Tailwind CSS
- Authentication
- Movie browsing
- Search functionality
- Personalized recommendations
- Admin dashboard

## Environment Variables

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```
''',
}


def create_file(path: str, content: str):
    """Create file with content"""
    file_path = BASE_DIR / path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Created: {path}")


def main():
    """Generate all frontend files"""
    print("🚀 Generating MEMAX Frontend files...\n")
    
    for path, content in FILES.items():
        create_file(path, content)
    
    print(f"\n✅ Generated {len(FILES)} files successfully!")
    print("\n📝 Next steps:")
    print("1. npm install")
    print("2. npm run dev")
    print("3. Visit http://localhost:3000")


if __name__ == "__main__":
    main()
