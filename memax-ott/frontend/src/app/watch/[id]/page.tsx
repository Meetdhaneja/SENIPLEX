"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { movieService } from "@/services/movie.service";
import { recommendationService } from "@/services/recommendation.service";
import { interactionService } from "@/services/interaction.service";
import Navbar from "@/components/layout/Navbar";
import MovieSection from "@/components/movie/MovieSection";
import Footer from "@/components/layout/Footer";
import ReactPlayer from 'react-player';
import { PlayIcon, PlusIcon, HandThumbUpIcon, HandThumbDownIcon, ArrowLeftIcon } from '@heroicons/react/24/solid';

export default function WatchPage() {
    const params = useParams();
    const router = useRouter();
    const searchParams = useSearchParams();
    const { id } = params;

    const [movie, setMovie] = useState<any>(null);
    const [similarMovies, setSimilarMovies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [isPlaying, setIsPlaying] = useState(false);
    const [actionLoading, setActionLoading] = useState(false);
    const [message, setMessage] = useState("");
    // Watch progress tracking for AI recommendations
    const watchProgressRef = useRef(0); // 0.0 - 1.0

    const handleAction = async (action: 'like' | 'dislike' | 'watch_later') => {
        try {
            setActionLoading(true);
            if (action === 'like') {
                await interactionService.likeMovie(Number(id));
                setMessage("Added to likes!");
            } else if (action === 'dislike') {
                await interactionService.dislikeMovie(Number(id));
                setMessage("Disliked movie.");
            } else if (action === 'watch_later') {
                await interactionService.addToWatchLater(Number(id));
                setMessage("Added to watch later!");
            }
            setTimeout(() => setMessage(""), 3000);
        } catch (e) {
            console.error("Action failed", e);
            setMessage("Action failed. Are you logged in?");
            setTimeout(() => setMessage(""), 3000);
        } finally {
            setActionLoading(false);
        }
    };

    // Track watch progress changes from the player
    const handleProgress = (state: { played: number }) => {
        watchProgressRef.current = state.played; // 0.0 to 1.0
    };

    // Report watch progress to backend when leaving the page
    useEffect(() => {
        if (!id) return;
        const reportProgress = () => {
            const progress = watchProgressRef.current;
            if (progress > 0.02) { // Only report if actually watched something
                interactionService.recordWatchProgress(Number(id), progress).catch(() => {});
            }
        };
        window.addEventListener("beforeunload", reportProgress);
        return () => {
            window.removeEventListener("beforeunload", reportProgress);
            reportProgress(); // Also report on React navigation away
        };
    }, [id]);

    useEffect(() => {
        if (!id) return;

        const fetchData = async () => {
            try {
                setLoading(true);
                const movieData = await movieService.getMovie(Number(id));
                setMovie(movieData);

                try {
                    const fromSearch = searchParams.get('from') === 'search';
                    if (fromSearch) {
                        await interactionService.recordSearchClick(Number(id));
                    } else {
                        await interactionService.recordView(Number(id));
                    }
                } catch (e) {
                    console.warn("Failed to record view", e);
                }

                const similar = await recommendationService.getSimilarMovies(Number(id));
                setSimilarMovies(similar);

            } catch (err: any) {
                console.error("Error fetching data", err);
                setError("Failed to load movie details. Please try again.");
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [id, searchParams]);

    if (loading) {
        return (
            <div className="min-h-screen bg-dark-900 flex items-center justify-center text-white">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
            </div>
        );
    }

    if (error || !movie) {
        return (
            <div className="min-h-screen bg-dark-900 flex flex-col items-center justify-center text-white p-4">
                <h1 className="text-2xl font-bold mb-4">Error</h1>
                <p className="text-red-400 mb-6">{error || "Movie not found"}</p>
                <button
                    onClick={() => router.back()}
                    className="flex items-center px-4 py-2 bg-dark-700 rounded hover:bg-dark-600 transition"
                >
                    <ArrowLeftIcon className="w-5 h-5 mr-2" />
                    Go Back
                </button>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-dark-900 text-white">
            <Navbar />

            {/* Player / Hero Section */}
            <div className="relative w-full aspect-video max-h-[80vh] bg-black">
                {movie.video_url || movie.trailer_url ? (
                    <ReactPlayer
                        url={movie.video_url || movie.trailer_url}
                        width="100%"
                        height="100%"
                        controls
                        playing={true}
                        onProgress={handleProgress}
                        progressInterval={5000}
                    />
                ) : (
                    <div className="w-full h-full flex items-center justify-center bg-dark-800" style={{
                        backgroundImage: `url(${movie.thumbnail_url || movie.poster_url})`,
                        backgroundSize: 'cover',
                        backgroundPosition: 'center'
                    }}>
                        <div className="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
                        <div className="relative z-10 text-center p-8">
                            <h1 className="text-4xl md:text-6xl font-bold mb-4 text-white drop-shadow-lg">{movie.title}</h1>
                            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">{movie.description}</p>
                            <div className="flex justify-center gap-4">
                                <button className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-lg font-bold flex items-center gap-2 transition transform hover:scale-105">
                                    <PlayIcon className="w-6 h-6" /> Play Now
                                </button>
                                <button
                                    onClick={() => handleAction('watch_later')}
                                    disabled={actionLoading}
                                    className="bg-gray-600 hover:bg-gray-500 text-white px-8 py-3 rounded-lg font-bold flex items-center gap-2 transition"
                                >
                                    <PlusIcon className="w-6 h-6" /> Watch Later
                                </button>
                                <button
                                    onClick={() => handleAction('like')}
                                    disabled={actionLoading}
                                    className="bg-dark-700 hover:bg-dark-600 text-green-500 px-4 py-3 rounded-lg font-bold flex items-center gap-2 transition"
                                >
                                    <HandThumbUpIcon className="w-6 h-6" />
                                </button>
                                <button
                                    onClick={() => handleAction('dislike')}
                                    disabled={actionLoading}
                                    className="bg-dark-700 hover:bg-dark-600 text-red-500 px-4 py-3 rounded-lg font-bold flex items-center gap-2 transition"
                                >
                                    <HandThumbDownIcon className="w-6 h-6" />
                                </button>
                            </div>
                            {message && <p className="mt-4 text-primary-400 font-semibold">{message}</p>}
                        </div>
                    </div>
                )}

                {!movie.video_url && !movie.trailer_url && (
                    <div className="absolute top-4 left-4 z-20">
                        <button onClick={() => router.back()} className="p-2 bg-black/50 rounded-full hover:bg-black/70 text-white">
                            <ArrowLeftIcon className="w-6 h-6" />
                        </button>
                    </div>
                )}
            </div>

            {/* Details Section */}
            <div className="container mx-auto px-4 py-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    <div className="md:col-span-2 space-y-6">
                        <div>
                            <h1 className="text-3xl font-bold mb-2">{movie.title}</h1>
                            <div className="flex items-center gap-4 text-sm text-gray-400">
                                <span className="text-green-500 font-bold">
                                    {movie.rating > 0 ? movie.rating.toFixed(1) : (movie.imdb_rating || "NR")} Rating
                                </span>
                                <span>{movie.release_year}</span>
                                <span>{movie.duration_minutes}m</span>
                                <span className="border border-gray-600 px-1 text-xs">HD</span>
                            </div>
                        </div>

                        <p className="text-gray-300 text-lg leading-relaxed">
                            {movie.description}
                        </p>

                        <div className="flex flex-wrap gap-2">
                            {movie.genres?.map((g: any, i: number) => (
                                <span key={i} className="px-3 py-1 bg-dark-700 rounded-full text-sm text-gray-300">
                                    {g.name}
                                </span>
                            ))}
                        </div>
                    </div>

                    <div className="bg-dark-800 p-6 rounded-lg h-fit">
                        <h3 className="text-lg font-semibold mb-4 text-gray-200">Details</h3>
                        <div className="space-y-3 text-sm">
                            <div className="flex justify-between">
                                <span className="text-gray-500">Director</span>
                                <span>{movie.director || "Unknown"}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-500">Cast</span>
                                <span className="text-right max-w-[200px] truncate">{movie.cast || "Unknown"}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-500">Country</span>
                                <span>{movie.countries?.map((c: any) => c.name).join(", ") || "N/A"}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Recommendations */}
                <div className="mt-12">
                    <MovieSection title="You Might Also Like" movies={similarMovies} />
                </div>
            </div>

            <Footer />
        </div>
    );
}
