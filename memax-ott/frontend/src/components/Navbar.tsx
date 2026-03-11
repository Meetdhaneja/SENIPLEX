"use client";

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
