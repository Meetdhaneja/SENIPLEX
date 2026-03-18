"use client";

import { useEffect, useState, useRef } from "react";
import Navbar from "@/components/layout/Navbar";
import Hero from "@/components/layout/Hero";
import MovieSection from "@/components/movie/MovieSection";
import Footer from "@/components/layout/Footer";
import { movieService } from "@/services/movie.service";
import { recommendationService } from "@/services/recommendation.service";
import { useAuthStore } from "@/store/authStore";
import { SparklesIcon } from "@heroicons/react/24/solid";

export default function Home() {
  const [featuredMovies, setFeaturedMovies] = useState<any[]>([]);
  const [trendingMovies, setTrendingMovies] = useState<any[]>([]);
  const [newReleases, setNewReleases] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [recsLoading, setRecsLoading] = useState(false);
  const [backendReachable, setBackendReachable] = useState(true);
  const [backendCheckInProgress, setBackendCheckInProgress] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuthStore();

  // Hero Carousel State
  const [heroIndex, setHeroIndex] = useState(0);
  const heroIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const base = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
        if (!base) throw new Error("NEXT_PUBLIC_API_URL is not configured");

        const res = await fetch(`${base}/api/ping`, { method: "GET" });
        if (!res.ok) throw new Error(`Ping failed: ${res.status}`);

        setBackendReachable(true);
      } catch (err: any) {
        console.warn("Backend health check failed", err);
        setBackendReachable(false);
        setError(
          "Backend not reachable. Please verify NEXT_PUBLIC_API_URL and ensure the backend is running."
        );
      } finally {
        setBackendCheckInProgress(false);
      }
    };

    checkBackend();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [featured, trending, movies] = await Promise.all([
          movieService.getFeaturedMovies(10),
          movieService.getTrendingMovies(12),
          movieService.getMovies(1, 20),
        ]);

        setFeaturedMovies(featured);
        setTrendingMovies(trending);
        setNewReleases(movies.movies);
      } catch (err: any) {
        console.error("Failed to fetch movies", err);
        setError(err.message || "Failed to connect to the movie server. Please check if the backend is running.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // AI Recommendations
  useEffect(() => {
    if (!user) {
      setRecommendations([]);
      return;
    }
    const fetchRecs = async () => {
      setRecsLoading(true);
      try {
        let recs: any[] = [];
        try {
          const result = await recommendationService.getPersonalizedRecommendations(16);
          // Flatten {recommendations: [{movie: {...}}]} to [{...}]
          const rawRecs = result?.recommendations || [];
          recs = rawRecs.map((item: any) => item.movie || item);
        } catch (error) {
          console.error("AI recommendations failed, falling back to cold start", error);
          recs = await recommendationService.getColdStartRecommendations(16);
        }
        setRecommendations(Array.isArray(recs) ? recs : []);
      } catch (err) {
        console.error("Cold start also failed", err);
        setRecommendations([]);
      } finally {
        setRecsLoading(false);
      }
    };
    fetchRecs();
  }, [user]);

  // Handle Hero Rotation every 4 seconds - cycles through heroMovies
  const heroMovies = user && recommendations.length > 0
    ? recommendations.slice(0, 5)
    : trendingMovies.slice(0, 5);

  useEffect(() => {
    if (heroMovies.length > 0) {
      if (heroIntervalRef.current) clearInterval(heroIntervalRef.current);
      
      heroIntervalRef.current = setInterval(() => {
        setHeroIndex((prev) => (prev + 1) % heroMovies.length);
      }, 4000);
    }
    return () => {
      if (heroIntervalRef.current) clearInterval(heroIntervalRef.current);
    };
  }, [heroMovies.length]);


  return (
    <div className="min-h-screen bg-dark-900 text-white overflow-x-hidden">
      <Navbar />

      {/* Backend reachability warning */}
      {!backendReachable && !backendCheckInProgress && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 text-yellow-100 px-6 py-4 text-center">
          <strong>Warning:</strong> Backend is not reachable at <span className="font-mono">{process.env.NEXT_PUBLIC_API_URL}</span>.
          Please verify your deployment configuration.
        </div>
      )}

      {/* Hero Section - Cycles through AI Recommended or Trending */}
      <Hero 
        movie={heroMovies.length > 0 ? heroMovies[heroIndex] : null} 
      />

      {/* Main Content */}
      <div className="relative z-10 -mt-32 pb-20 space-y-8 bg-gradient-to-b from-transparent via-dark-900 to-dark-900">
        {loading ? (
          <div className="px-8 space-y-10 pt-8">
            {[...Array(3)].map((_, section) => (
              <div key={section}>
                <div className="h-6 w-44 bg-dark-700 rounded animate-pulse mb-4" />
                <div className="flex gap-4 overflow-hidden">
                  {[...Array(6)].map((_, i) => (
                    <div
                      key={i}
                      className="w-[200px] h-[300px] bg-dark-800 rounded-md animate-pulse flex-none"
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <>
            {trendingMovies.length > 0 && (
              <MovieSection title="🔥 Trending Now" movies={trendingMovies} />
            )}

            {newReleases.length > 0 && (
              <MovieSection title="🆕 New Releases" movies={newReleases} />
            )}

            {/* AI Recommendations Section - Moved under New Releases */}
            {user && (
              <div>
                {recsLoading ? (
                  <div className="px-8">
                    <div className="flex items-center gap-2 mb-4">
                      <SparklesIcon className="w-5 h-5 text-yellow-400 animate-pulse" />
                      <div className="h-6 w-56 bg-dark-700 rounded animate-pulse" />
                    </div>
                    <div className="flex gap-4 overflow-hidden">
                      {[...Array(6)].map((_, i) => (
                        <div
                          key={i}
                          className="w-[200px] h-[300px] bg-dark-800 rounded-md animate-pulse flex-none"
                        />
                      ))}
                    </div>
                  </div>
                ) : recommendations.length > 0 ? (
                  <MovieSection
                    title="✨ Recommended For You"
                    movies={recommendations}
                    subtitle="Based on your watch history, likes & activity"
                  />
                ) : (
                  <div className="px-8 py-4">
                    <div className="flex items-center gap-2 mb-2">
                      <SparklesIcon className="w-5 h-5 text-yellow-400" />
                      <h2 className="text-xl font-bold text-white">
                        Recommended For You
                      </h2>
                    </div>
                    <p className="text-gray-500 text-sm">
                      Watch, like, and interact with content to get personalized
                      recommendations!
                    </p>
                  </div>
                )}
              </div>
            )}

            {featuredMovies.length > 0 && (
              <MovieSection
                title="⭐ Featured Collection"
                movies={featuredMovies}
              />
            )}

            {error ? (
              <div className="text-center py-20 px-8">
                <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-lg max-w-2xl mx-auto">
                  <h3 className="text-xl font-bold mb-2">Connection Issue</h3>
                  <p className="text-sm opacity-80 mb-4">{error}</p>
                  <button 
                    onClick={() => window.location.reload()}
                    className="bg-white text-black px-6 py-2 rounded font-bold hover:bg-gray-200"
                  >
                    Retry Connection
                  </button>
                  <p className="text-xs mt-6 opacity-60">
                    If this is your first deploy on Render, the backend might still be starting up or the Database URL might be missing.
                  </p>
                </div>
              </div>
            ) : (
              !loading &&
              trendingMovies.length === 0 &&
              newReleases.length === 0 && (
                <div className="text-center py-20 text-gray-500">
                  <p className="animate-pulse">
                    Populating our expansive library of 8,800+ titles...
                  </p>
                  <p className="text-sm mt-2">
                    Please refresh in a moment if you don&apos;t see content yet.
                  </p>
                  <div className="mt-8 flex justify-center gap-4">
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                  </div>
                </div>
              )
            )}
          </>
        )}
      </div>

      <Footer />
    </div>
  );
}
