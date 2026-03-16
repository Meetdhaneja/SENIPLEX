"use client";
import Link from 'next/link';

export default function PlaceholderPage({ title, description }: { title: string, description: string }) {
  return (
    <div className="min-h-screen bg-dark-900 text-white flex flex-col items-center justify-center p-8 text-center">
      <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-primary-500 to-purple-500 bg-clip-text text-transparent">
        {title}
      </h1>
      <p className="text-xl text-gray-400 max-w-2xl mb-12">
        {description}
      </p>
      <Link 
        href="/"
        className="bg-primary-600 hover:bg-primary-700 text-white px-8 py-3 rounded-full font-bold transition-all transform hover:scale-105"
      >
        Back to Home
      </Link>
      
      <div className="mt-20 opacity-20">
        <div className="text-9xl font-black italic tracking-tighter">MEMAX</div>
      </div>
    </div>
  );
}
