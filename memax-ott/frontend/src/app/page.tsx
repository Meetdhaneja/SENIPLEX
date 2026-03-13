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
  const { user } = useAuthStore();

  // Hero Carousel State
  const [heroIndex, setHeroIndex] = useState(0);
  const heroIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [featured, trending, movies] = await Promise.all([
          movieService.getFeaturedMovies(10),
          movieService.getTrendingMovies(12),
          movieService.getMovies(1, 20),
        ]);

        setFeaturedMovies(featured);
        setTrendingMovies(trending);
        setNewReleases(movies.movies);
      } catch (error) {
        console.error("Failed to fetch movies", error);
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
          recs = result?.recommendations || result || [];
        } catch {
          recs = await recommendationService.getColdStartRecommendations(16);
        }
        setRecommendations(Array.isArray(recs) ? recs : []);
      } catch {
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

            {!loading &&
              trendingMovies.length === 0 &&
              newReleases.length === 0 && (
                <div className="text-center py-20 text-gray-500">
                  <p className="animate-pulse">
                    Populating our expansive library of 8,800+ titles...
                  </p>
                  <p className="text-sm mt-2">
                    Please refresh in a moment if you don't see content yet.
                  </p>
                </div>
              )}
          </>
        )}
      </div>

      <Footer />
    </div>
  );
}
