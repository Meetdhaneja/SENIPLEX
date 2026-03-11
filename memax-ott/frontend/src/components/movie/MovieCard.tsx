import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { PlayIcon, PlusIcon, HandThumbUpIcon, HandThumbDownIcon } from '@heroicons/react/24/solid';
import { interactionService } from '@/services/interaction.service';

interface Movie {
    id: number;
    title: string;
    description?: string;
    thumbnail_url?: string;
    poster_url?: string; // fallback
    video_url?: string;
    match_score?: number; // from frontend mock or calculated
    rating?: number; // from backend
    duration_minutes?: number;
    genres?: { id: number; name: string }[];
    release_year?: number;
}

interface MovieCardProps {
    movie: Movie;
}

const MovieCard = ({ movie }: MovieCardProps) => {
    const [isHovered, setIsHovered] = useState(false);
    const [liked, setLiked] = useState<boolean>(false);
    const [inWatchLater, setInWatchLater] = useState<boolean>(false);

    // Prefer thumbnail_url (backend), fallback to poster_url (mock/legacy)
    const imageUrl = movie.thumbnail_url || movie.poster_url || "https://via.placeholder.com/200x300?text=No+Image";
    const duration = movie.duration_minutes ? `${Math.floor(movie.duration_minutes / 60)}h ${movie.duration_minutes % 60}m` : 'N/A';
    const year = movie.release_year || 'N/A';

    const handleLike = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        try {
            if (liked) {
                await interactionService.unlikeMovie(movie.id);
                setLiked(false);
            } else {
                await interactionService.likeMovie(movie.id);
                setLiked(true);
            }
        } catch (err) {
            console.error("Failed to toggle like", err);
        }
    };

    const handleWatchLater = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        try {
            await interactionService.addToWatchLater(movie.id);
            setInWatchLater(true);
            alert("Added to Watch Later!");
        } catch (err) {
            console.error("Failed to add to watch later", err);
        }
    };

    const handleDislike = async (e: React.MouseEvent) => {
        e.preventDefault();
        e.stopPropagation();
        try {
            await interactionService.dislikeMovie(movie.id);
            alert("Disliked");
        } catch (err) {
            console.error("Failed to dislike", err);
        }
    };

    return (
        <Link href={`/watch/${movie.id}`}>
            <div
                className="relative w-[200px] h-[300px] bg-dark-800 rounded-md overflow-hidden transition-all duration-300 md:hover:scale-105 group cursor-pointer border border-transparent hover:border-dark-600 shadow-lg"
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
            >
                <Image
                    src={imageUrl}
                    alt={movie.title}
                    fill
                    className={`object-cover transition-opacity duration-300 ${isHovered ? 'opacity-40' : 'opacity-100'}`}
                    unoptimized
                />

                {/* Overlay Content */}
                <div className={`absolute inset-0 flex flex-col justify-end p-4 transition-opacity duration-300 ${isHovered ? 'opacity-100' : 'opacity-0'}`}>
                    <h3 className="text-white font-bold text-lg mb-1 line-clamp-2 leading-tight">{movie.title}</h3>

                    <div className="flex items-center text-xs text-gray-300 mb-2 space-x-2" style={{ pointerEvents: 'none' }}>
                        <span className="text-green-500 font-bold">{movie.rating ? movie.rating.toFixed(1) : 'NR'}</span>
                        <span>{year}</span>
                        <span>{duration}</span>
                    </div>

                    <div className="flex items-center gap-2 mt-2">
                        <button
                            className="bg-white text-black p-2 rounded-full hover:bg-primary-500 hover:text-white transition-colors flex items-center justify-center transform hover:scale-110"
                            title="Play"
                        >
                            <PlayIcon className="w-5 h-5" />
                        </button>

                        <button
                            onClick={handleWatchLater}
                            className={`border ${inWatchLater ? 'border-primary-500 text-primary-500' : 'border-gray-400 text-gray-300'} p-2 rounded-full hover:border-white hover:text-white transition-colors`}
                            title="Watch Later"
                        >
                            <PlusIcon className="w-5 h-5" />
                        </button>

                        <button
                            onClick={handleLike}
                            className={`border ${liked ? 'border-green-500 text-green-500' : 'border-gray-400 text-gray-300'} p-2 rounded-full hover:border-white hover:text-white transition-colors`}
                            title="Like"
                        >
                            <HandThumbUpIcon className="w-5 h-5" />
                        </button>
                        <button
                            onClick={handleDislike}
                            className={`border border-gray-400 text-gray-300 p-2 rounded-full hover:border-white hover:text-white transition-colors`}
                            title="Dislike"
                        >
                            <HandThumbDownIcon className="w-5 h-5" />
                        </button>
                    </div>

                    <div className="flex flex-wrap gap-1 mt-3">
                        {movie.genres?.slice(0, 2).map((g, i) => (
                            <span key={i} className="text-[10px] bg-dark-600 px-1 py-0.5 rounded text-gray-300">
                                {typeof g === 'string' ? g : g.name}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </Link>
    );
};

export default MovieCard;
