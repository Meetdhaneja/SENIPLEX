"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import MovieSection from "@/components/movie/MovieSection";
import { useAuthStore } from "@/store/authStore";
import { interactionService } from "@/services/interaction.service";
import api from "@/services/api";
import {
  UserCircleIcon,
  HeartIcon,
  ClockIcon,
  FilmIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
} from "@heroicons/react/24/solid";

export default function ProfilePage() {
  const { user, setUser, logout } = useAuthStore();
  const router = useRouter();

  const [likedMovies, setLikedMovies] = useState<any[]>([]);
  const [watchLaterMovies, setWatchLaterMovies] = useState<any[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [activeTab, setActiveTab] = useState<"liked" | "watchlater">("liked");

  // Edit profile state
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");

  useEffect(() => {
    if (!user) {
      router.push("/login");
      return;
    }
    setFullName(user.full_name || "");
    const load = async () => {
      try {
        setLoadingData(true);
        const [liked, later] = await Promise.allSettled([
          interactionService.getMyLikes(),
          api.get("/interactions/watch-later").catch(() => ({ data: [] })),
        ]);
        setLikedMovies(liked.status === "fulfilled" ? liked.value : []);
        setWatchLaterMovies(
          later.status === "fulfilled" ? (later.value as any).data || [] : []
        );
      } catch {
        // silently fail
      } finally {
        setLoadingData(false);
      }
    };
    load();
  }, [user, router]);

  const handleSave = async () => {
    if (!user) return;
    setSaving(true);
    try {
      const res = await api.patch("/auth/me", { full_name: fullName });
      setUser({ ...user, full_name: res.data.full_name });
      setEditing(false);
      setSaveMsg("Profile updated!");
      setTimeout(() => setSaveMsg(""), 3000);
    } catch {
      setSaveMsg("Failed to save.");
      setTimeout(() => setSaveMsg(""), 3000);
    } finally {
      setSaving(false);
    }
  };

  if (!user) return null;

  const initials = (user.full_name || user.username || "U")
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <div className="min-h-screen bg-dark-900 text-white overflow-x-hidden">
      <Navbar />

      {/* Profile Header */}
      <div className="pt-24 pb-8 bg-gradient-to-b from-dark-800 to-dark-900">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center gap-8">
            {/* Avatar */}
            <div className="relative">
              {user.profile_picture ? (
                <Image
                  src={user.profile_picture}
                  alt={user.username}
                  width={112}
                  height={112}
                  className="w-28 h-28 rounded-full object-cover ring-4 ring-primary-500"
                  unoptimized
                />
              ) : (
                <div className="w-28 h-28 rounded-full bg-gradient-to-br from-primary-600 to-purple-700 flex items-center justify-center ring-4 ring-primary-500 text-3xl font-bold shadow-xl">
                  {initials}
                </div>
              )}
            </div>

            {/* Info */}
            <div className="flex-1 text-center md:text-left">
              {editing ? (
                <div className="flex items-center gap-3 mb-2">
                  <input
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="bg-dark-700 border border-dark-500 rounded-lg px-4 py-2 text-lg font-bold text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Full Name"
                  />
                  <button
                    onClick={handleSave}
                    disabled={saving}
                    className="p-2 bg-green-600 hover:bg-green-700 rounded-lg transition"
                  >
                    <CheckIcon className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setEditing(false)}
                    className="p-2 bg-red-600 hover:bg-red-700 rounded-lg transition"
                  >
                    <XMarkIcon className="w-5 h-5" />
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-3 mb-1">
                  <h1 className="text-3xl font-bold">
                    {user.full_name || user.username}
                  </h1>
                  <button
                    onClick={() => setEditing(true)}
                    className="p-1.5 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition"
                    title="Edit profile"
                  >
                    <PencilIcon className="w-4 h-4" />
                  </button>
                </div>
              )}
              {saveMsg && (
                <p className="text-sm text-green-400 mb-1">{saveMsg}</p>
              )}
              <p className="text-gray-400 text-sm">@{user.username}</p>
              <p className="text-gray-500 text-sm mt-0.5">{user.email}</p>
              {user.is_admin && (
                <span className="inline-block mt-2 px-3 py-0.5 bg-primary-700 text-primary-200 text-xs rounded-full font-semibold">
                  Admin
                </span>
              )}
            </div>

            {/* Stats */}
            <div className="flex gap-6 text-center">
              <div className="bg-dark-800 rounded-xl px-5 py-4 min-w-[90px]">
                <HeartIcon className="w-6 h-6 text-red-500 mx-auto mb-1" />
                <p className="text-2xl font-bold">{likedMovies.length}</p>
                <p className="text-xs text-gray-400">Liked</p>
              </div>
              <div className="bg-dark-800 rounded-xl px-5 py-4 min-w-[90px]">
                <ClockIcon className="w-6 h-6 text-blue-400 mx-auto mb-1" />
                <p className="text-2xl font-bold">{watchLaterMovies.length}</p>
                <p className="text-xs text-gray-400">Watch Later</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        <div className="flex gap-4 border-b border-dark-700 mb-8">
          {[
            { key: "liked", label: "Liked Movies", icon: HeartIcon },
            { key: "watchlater", label: "Watch Later", icon: ClockIcon },
          ].map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key as any)}
              className={`flex items-center gap-2 pb-3 px-2 text-sm font-semibold border-b-2 transition ${
                activeTab === key
                  ? "border-primary-500 text-white"
                  : "border-transparent text-gray-400 hover:text-white"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>

        {loadingData ? (
          <div className="flex gap-4 overflow-hidden animate-pulse pb-10">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="w-[200px] h-[300px] bg-dark-800 rounded-md flex-none"
              />
            ))}
          </div>
        ) : activeTab === "liked" ? (
          likedMovies.length > 0 ? (
            <MovieSection title="Your Liked Movies" movies={likedMovies} />
          ) : (
            <div className="text-center py-20">
              <HeartIcon className="w-16 h-16 text-gray-700 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">No liked movies yet.</p>
              <p className="text-gray-600 text-sm mt-1">
                Like a movie to see it here!
              </p>
            </div>
          )
        ) : watchLaterMovies.length > 0 ? (
          <MovieSection title="Your Watch Later List" movies={watchLaterMovies} />
        ) : (
          <div className="text-center py-20">
            <ClockIcon className="w-16 h-16 text-gray-700 mx-auto mb-4" />
            <p className="text-gray-400 text-lg">Watch Later list is empty.</p>
            <p className="text-gray-600 text-sm mt-1">
              Save movies to watch them later!
            </p>
          </div>
        )}
      </div>

      {/* Danger Zone */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 mb-20">
        <div className="border border-red-900 rounded-xl p-6 bg-red-950/20">
          <h3 className="text-red-400 font-semibold mb-2">Account Actions</h3>
          <button
            onClick={() => {
              logout();
              router.push("/login");
            }}
            className="px-6 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white font-semibold transition"
          >
            Sign Out
          </button>
        </div>
      </div>

      <Footer />
    </div>
  );
}
