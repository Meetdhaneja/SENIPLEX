import Link from 'next/link';
import Image from 'next/image';
import { PlayIcon, InformationCircleIcon } from '@heroicons/react/24/solid';

interface HeroProps {
    movie?: any; // Should be Movie interface but using any for flexibility with backend response
}

const Hero = ({ movie }: HeroProps) => {
    if (!movie) {
        // Fallback or Skeleton
        return (
            <div className="relative h-[80vh] w-full bg-dark-900 flex items-center justify-center">
                <div className="animate-pulse flex flex-col items-center">
                    <div className="w-64 h-8 bg-dark-700 rounded mb-4"></div>
                    <div className="w-12 h-12 bg-dark-700 rounded-full"></div>
                </div>
            </div>
        );
    }

    return (
        <div className="relative h-[85vh] w-full transition-opacity duration-1000 ease-in-out" key={movie.id}>
            {/* Background Image/Video */}
            <div className="absolute inset-0">
                <Image
                    src={movie.thumbnail_url || movie.poster_url || "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=2070&auto=format&fit=crop"}
                    alt={movie.title}
                    fill
                    className="object-cover animate-fade-in"
                    priority
                    unoptimized
                />
                {/* Gradient Overlays */}
                <div className="absolute inset-0 bg-gradient-to-t from-dark-900 via-dark-900/40 to-transparent"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-dark-900 via-transparent to-transparent"></div>
            </div>

            {/* Content Container */}
            <div className="absolute bottom-[25%] left-[5%] max-w-2xl text-white space-y-4 z-10 animate-slide-up">
                {/* Badge */}
                <span className="bg-primary-600/20 text-cyan text-xs font-bold px-3 py-1 rounded-full border border-cyan/30 flex items-center gap-1 w-fit">
                    <span className="w-1.5 h-1.5 bg-cyan rounded-full animate-pulse"></span>
                    Trending Dynamic Carousel
                </span>

                {/* Title */}
                <h1 className="text-4xl md:text-7xl font-black drop-shadow-2xl text-white tracking-tight leading-none">
                    {movie.title}
                </h1>

                {/* Meta Info */}
                <div className="flex items-center gap-4 text-sm font-semibold text-gray-300">
                    <span className="text-green-400 font-bold">{movie.rating ? `${movie.rating} Rating` : '98% Match'}</span>
                    <span className="border border-gray-600 px-2 py-0.5 rounded text-xs">{movie.release_year || '2023'}</span>
                    <span className="border border-gray-600 px-2 py-0.5 rounded text-xs">18+</span>
                    <span className="text-gray-400">{movie.duration_minutes ? `${Math.floor(movie.duration_minutes / 60)}h ${movie.duration_minutes % 60}m` : '1 Season'}</span>
                </div>

                {/* Description */}
                <p className="text-lg text-gray-400 drop-shadow-md line-clamp-3 max-w-xl">
                    {movie.description}
                </p>

                {/* Buttons */}
                <div className="flex gap-4 pt-4">
                    <Link href={`/watch/${movie.id}`}>
                        <button className="flex items-center gap-2 bg-white text-black hover:bg-cyan hover:text-white px-8 py-3 rounded-md font-black transition-all hover:scale-105 shadow-[0_0_20px_rgba(255,255,255,0.2)]">
                            <PlayIcon className="w-6 h-6" /> Play Now
                        </button>
                    </Link>
                    <Link href={`/watch/${movie.id}`}>
                        <button className="flex items-center gap-2 bg-dark-200/40 hover:bg-dark-200/60 text-white px-8 py-3 rounded-md font-semibold transition-all hover:scale-105 backdrop-blur-md border border-white/10">
                            <InformationCircleIcon className="w-6 h-6" /> Info
                        </button>
                    </Link>
                </div>
            </div>
            
            {/* Visual Indicator of carousel (Subtle dots) */}
            <div className="absolute bottom-10 right-10 flex gap-2 z-20">
                {[...Array(5)].map((_, i) => (
                    <div 
                        key={i} 
                        className={`h-1 rounded-full transition-all duration-500 ${movie.id % 5 === i ? 'w-8 bg-cyan' : 'w-2 bg-white/20'}`}
                    ></div>
                ))}
            </div>
        </div>
    );
};

export default Hero;
