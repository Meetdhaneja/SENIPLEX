import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import Image from 'next/image';
import useAuthStore from '@/store/useAuthStore';

const Navbar = () => {
    const pathname = usePathname();
    const user = useAuthStore((state) => state.user);
    const logout = useAuthStore((state) => state.logout);
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            if (window.scrollY > 50) {
                setScrolled(true);
            } else {
                setScrolled(false);
            }
        };

        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const routes = [
        { label: 'Home', path: '/' },
        { label: 'Movies', path: '/movies' },
        { label: 'TV Shows', path: '/tv-shows' },
        { label: 'My List', path: '/my-list' },
    ];

    if (pathname === '/login' || pathname === '/signup') return null;

    return (
        <nav
            className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled ? 'bg-black/90 backdrop-blur-md shadow-lg' : 'bg-transparent'
                }`}
        >
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo - Cyberpunk Style */}
                    <Link href="/" className="flex-shrink-0 group relative">
                        <span className="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-accent animate-pulse-slow group-hover:animate-none group-hover:text-cyan transition-colors duration-300">
                            MEMAX
                        </span>
                        <div className="absolute -bottom-1 left-0 w-full h-0.5 bg-accent scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300"></div>
                    </Link>

                    {/* Navigation Links */}
                    <div className="hidden md:block">
                        <div className="ml-10 flex items-baseline space-x-8">
                            {routes.map((route) => (
                                <Link
                                    key={route.path}
                                    href={route.path}
                                    className={`relative px-3 py-2 rounded-md text-sm font-medium transition-colors duration-300 hover:text-cyan ${pathname === route.path
                                        ? 'text-cyan font-bold'
                                        : 'text-gray-300'
                                        }`}
                                >
                                    {route.label}
                                    {pathname === route.path && (
                                        <span className="absolute bottom-0 left-0 w-full h-0.5 bg-cyan shadow-[0_0_10px_2px_rgba(6,182,212,0.6)]"></span>
                                    )}
                                </Link>
                            ))}
                        </div>
                    </div>

                    {/* Right Side (Search, User, Login) */}
                    <div className="flex items-center gap-4">
                        {/* Search Icon (SVG) */}
                        <Link href="/search" className="text-gray-300 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                            </svg>
                        </Link>

                        {user ? (
                            <div className="flex items-center gap-3 relative group">
                                <div className="w-8 h-8 relative">
                                    <Image
                                        src={user.profile_picture || "https://ui-avatars.com/api/?name=" + user.username}
                                        alt="Profile"
                                        fill
                                        className="rounded-full border-2 border-primary-500 cursor-pointer object-cover"
                                        unoptimized
                                    />
                                </div>
                                <div className="absolute right-0 top-full mt-2 w-48 bg-dark-200 rounded-md shadow-xl py-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200 invisible group-hover:visible border border-primary-500/20">
                                    <Link href="/profile" className="block px-4 py-2 text-sm text-gray-300 hover:bg-primary-500/20 hover:text-white">Profile</Link>
                                    <button onClick={logout} className="block w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-primary-500/20 hover:text-white">Sign out</button>
                                </div>
                            </div>
                        ) : (
                            <Link
                                href="/login"
                                className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-1.5 rounded-sm text-sm font-semibold transition-all hover:scale-105 active:scale-95 shadow-[0_0_15px_rgba(124,58,237,0.5)] hover:shadow-[0_0_25px_rgba(124,58,237,0.8)]"
                            >
                                Sign In
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
