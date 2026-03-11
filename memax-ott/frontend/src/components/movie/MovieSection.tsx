import { useRef } from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/solid';
import MovieCard from './MovieCard';

interface Movie {
    id: number;
    title: string;
    description?: string;
    thumbnail_url?: string;
    poster_url?: string;
    video_url?: string;
    match_score?: number;
    rating?: number;
    duration?: string; // from mock
    duration_minutes?: number; // from backend
    genre?: string[]; // from mock
    genres?: { id: number; name: string }[]; // from backend
    release_year?: number;
}

interface MovieSectionProps {
    title: string;
    movies: Movie[];
    subtitle?: string;
}

const MovieSection = ({ title, movies, subtitle }: MovieSectionProps) => {
    const scrollRef = useRef<HTMLDivElement>(null);

    const scroll = (direction: 'left' | 'right') => {
        if (scrollRef.current) {
            const current = scrollRef.current;
            const scrollAmount = 600; // Scroll by multiple card widths
            if (direction === 'left') {
                current.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
            } else {
                current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
            }
        }
    };

    return (
        <section className="mb-8 px-4 sm:px-6 lg:px-8 relative group">
            <div className="mb-4">
                <h2 className="text-xl md:text-2xl font-bold text-white hover:text-cyan transition-colors cursor-pointer flex items-center gap-2">
                    {title} <span className="text-sm text-cyan opacity-0 group-hover:opacity-100 transition-opacity translate-x-[-10px] group-hover:translate-x-0 duration-300">Explore All &gt;</span>
                </h2>
                {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
            </div>

            <div className="relative group/slider">
                {/* Left Arrow */}
                <button
                    onClick={() => scroll('left')}
                    className="absolute left-0 top-0 bottom-0 z-40 bg-black/50 hover:bg-black/80 text-white w-12 flex items-center justify-center opacity-0 group-hover/slider:opacity-100 transition-opacity duration-300 backdrop-blur-sm"
                >
                    <ChevronLeftIcon className="w-8 h-8" />
                </button>

                {/* Movie List */}
                <div
                    ref={scrollRef}
                    className="flex gap-4 overflow-x-auto scrollbar-hide pb-8 pt-4 px-2 -mx-2 snap-x snap-mandatory"
                    style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
                >
                    {movies.map((movie) => (
                        <div key={movie.id} className="flex-none snap-start">
                            <MovieCard movie={movie} />
                        </div>
                    ))}
                </div>

                {/* Right Arrow */}
                <button
                    onClick={() => scroll('right')}
                    className="absolute right-0 top-0 bottom-0 z-40 bg-black/50 hover:bg-black/80 text-white w-12 flex items-center justify-center opacity-0 group-hover/slider:opacity-100 transition-opacity duration-300 backdrop-blur-sm"
                >
                    <ChevronRightIcon className="w-8 h-8" />
                </button>
            </div>
        </section>
    );
};

export default MovieSection;
