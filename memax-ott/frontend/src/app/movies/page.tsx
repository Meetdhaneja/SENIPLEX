"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/layout/Navbar";
import MovieSection from "@/components/movie/MovieSection";
import Footer from "@/components/layout/Footer";
import { movieService } from "@/services/movie.service";

export default function MoviesPage() {
    const [movies, setMovies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchMovies = async () => {
            try {
                setLoading(true);
                const data = await movieService.getMovies(1, 40, "Movie");
                setMovies(data.movies);
            } catch (error) {
                console.error("Failed to fetch movies", error);
            } finally {
                setLoading(false);
            }
        };
        fetchMovies();
    }, []);

    return (
        <div className="min-h-screen bg-dark-900 text-white overflow-x-hidden">
            <Navbar />
            <div className="pt-24 pb-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold mb-8">Movies</h1>

                {loading ? (
                    <div className="flex gap-4 overflow-hidden animate-pulse">
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className="w-[200px] h-[300px] bg-dark-800 rounded-md flex-none"></div>
                        ))}
                    </div>
                ) : (
                    <MovieSection title="All Movies" movies={movies} />
                )}
            </div>
            <Footer />
        </div>
    );
}
