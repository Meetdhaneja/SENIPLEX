"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/layout/Navbar";
import MovieSection from "@/components/movie/MovieSection";
import Footer from "@/components/layout/Footer";
import { interactionService } from "@/services/interaction.service";
import { useAuthStore } from "@/store/authStore";
import { useRouter } from "next/navigation";

export default function MyListPage() {
    const [movies, setMovies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const user = useAuthStore((state) => state.user);
    const router = useRouter();

    useEffect(() => {
        if (!user) {
            router.push("/login");
            return;
        }

        const fetchMyList = async () => {
            try {
                setLoading(true);
                // Using getMyLikes as a proxy for "my list" or watch later if getWatchLater doesn't exist
                // Note: memax_ott backend exposes /api/likes for liked movies.
                const likedMovies = await interactionService.getMyLikes();
                setMovies(likedMovies);
            } catch (error) {
                console.error("Failed to fetch my list", error);
            } finally {
                setLoading(false);
            }
        };
        fetchMyList();
    }, [user, router]);

    if (!user) return null;

    return (
        <div className="min-h-screen bg-dark-900 text-white overflow-x-hidden">
            <Navbar />
            <div className="pt-24 pb-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <h1 className="text-3xl font-bold mb-8">My List</h1>

                {loading ? (
                    <div className="flex gap-4 overflow-hidden animate-pulse">
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className="w-[200px] h-[300px] bg-dark-800 rounded-md flex-none"></div>
                        ))}
                    </div>
                ) : movies.length > 0 ? (
                    <MovieSection title="Saved Movies" movies={movies} />
                ) : (
                    <p className="text-gray-400 mt-10">You haven&apos;t added any movies to your list yet.</p>
                )}
            </div>
            <Footer />
        </div>
    );
}
