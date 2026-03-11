"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import Image from "next/image";
import Navbar from "@/components/layout/Navbar";
import MovieSection from "@/components/movie/MovieSection";
import Footer from "@/components/layout/Footer";
import { movieService } from "@/services/movie.service";
import { interactionService } from "@/services/interaction.service";
import { MagnifyingGlassIcon, XMarkIcon } from "@heroicons/react/24/solid";
import Link from "next/link";

const SUGGESTION_DELAY = 350; // ms debounce

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [movies, setMovies] = useState<any[]>([]);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [suggestLoading, setSuggestLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced live suggestions
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!query.trim() || query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    setSuggestLoading(true);
    debounceRef.current = setTimeout(async () => {
      try {
        const results = await movieService.searchMovies(query, 6);
        setSuggestions(results);
        setShowSuggestions(results.length > 0);
      } catch {
        setSuggestions([]);
      } finally {
        setSuggestLoading(false);
      }
    }, SUGGESTION_DELAY);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  const handleSearch = async (e?: React.FormEvent, q?: string) => {
    if (e) e.preventDefault();
    const searchQuery = q || query;
    if (!searchQuery.trim()) return;
    setShowSuggestions(false);
    try {
      setLoading(true);
      const results = await movieService.searchMovies(searchQuery, 40);
      setMovies(results);
    } catch {
      setMovies([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = async (movie: any) => {
    setQuery(movie.title);
    setShowSuggestions(false);
    // Record search click interaction
    try {
      await interactionService.recordSearchClick(movie.id);
    } catch {}
    handleSearch(undefined, movie.title);
  };

  const clearSearch = () => {
    setQuery("");
    setMovies([]);
    setSuggestions([]);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  return (
    <div className="min-h-screen bg-dark-900 text-white overflow-x-hidden">
      <Navbar />

      <div className="pt-24 pb-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 min-h-[70vh]">
        <h1 className="text-3xl font-bold mb-2">Search</h1>
        <p className="text-gray-500 text-sm mb-8">
          Search by title, description, director, or cast name
        </p>

        {/* Search Form */}
        <form onSubmit={handleSearch} className="mb-10">
          <div className="relative max-w-2xl">
            <div className="flex">
              <div className="relative flex-1">
                <MagnifyingGlassIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
                <input
                  ref={inputRef}
                  type="text"
                  id="search-input"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                  onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                  placeholder="Search movies, TV shows, directors, cast..."
                  autoComplete="off"
                  className="w-full bg-dark-800 border border-dark-600 rounded-l-xl pl-11 pr-10 py-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                />
                {query && (
                  <button
                    type="button"
                    onClick={clearSearch}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition"
                  >
                    <XMarkIcon className="w-5 h-5" />
                  </button>
                )}
              </div>
              <button
                type="submit"
                id="search-submit"
                className="bg-primary-600 hover:bg-primary-500 font-bold px-8 py-4 rounded-r-xl transition-colors"
              >
                Search
              </button>
            </div>

            {/* Live Suggestions Dropdown */}
            {showSuggestions && (
              <div className="absolute top-full left-0 right-12 z-50 bg-dark-800 border border-dark-600 rounded-xl mt-2 shadow-2xl overflow-hidden">
                {suggestions.map((movie) => (
                  <button
                    key={movie.id}
                    type="button"
                    onMouseDown={() => handleSuggestionClick(movie)}
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-dark-700 transition text-left group"
                  >
                    {movie.thumbnail_url ? (
                      <div className="w-10 h-14 relative flex-none">
                        <Image
                          src={movie.thumbnail_url}
                          alt={movie.title}
                          fill
                          className="object-cover rounded-md"
                          unoptimized
                        />
                      </div>
                    ) : (
                      <div className="w-10 h-14 bg-dark-600 rounded-md flex-none flex items-center justify-center text-gray-500 text-xs">
                        🎬
                      </div>
                    )}
                    <div className="min-w-0">
                      <p className="font-semibold text-white text-sm truncate group-hover:text-primary-400 transition">
                        {movie.title}
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {movie.release_year}
                        {movie.director ? ` · ${movie.director}` : ""}
                        {movie.content_type ? ` · ${movie.content_type}` : ""}
                      </p>
                    </div>
                    <span className="ml-auto text-xs text-gray-600 flex-none">
                      {movie.rating ? `⭐ ${movie.rating}` : ""}
                    </span>
                  </button>
                ))}
                <div className="px-4 py-2 border-t border-dark-700">
                  <button
                    type="submit"
                    onMouseDown={() => handleSearch(undefined, query)}
                    className="text-xs text-primary-400 hover:text-primary-300 font-semibold transition"
                  >
                    See all results for &quot;{query}&quot; →
                  </button>
                </div>
              </div>
            )}
          </div>
        </form>

        {/* Results */}
        {loading ? (
          <div className="flex gap-4 overflow-hidden animate-pulse">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="w-[200px] h-[300px] bg-dark-800 rounded-md flex-none"
              />
            ))}
          </div>
        ) : movies.length > 0 ? (
          <>
            <p className="text-gray-500 text-sm mb-4">
              Found {movies.length} result{movies.length > 1 ? "s" : ""} for{" "}
              <span className="text-white font-semibold">&quot;{query}&quot;</span>
            </p>
            <MovieSection title="Search Results" movies={movies} />
          </>
        ) : query && !loading ? (
          <div className="text-center py-20">
            <p className="text-4xl mb-4">🔍</p>
            <p className="text-gray-400 text-lg font-semibold">
              No results for &quot;{query}&quot;
            </p>
            <p className="text-gray-600 text-sm mt-2">
              Try searching by director name, cast, or description
            </p>
          </div>
        ) : null}
      </div>

      <Footer />
    </div>
  );
}
