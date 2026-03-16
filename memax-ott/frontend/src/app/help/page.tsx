export default function InfoPage() {
  return (
    <div className="min-h-screen bg-[#0f0f0f] flex items-center justify-center p-8 text-center font-sans">
      <div className="max-w-2xl bg-[#1a1a1a] p-12 rounded-2xl border border-white/10 shadow-2xl">
        <h1 className="text-4xl font-bold text-white mb-6 bg-gradient-to-r from-red-600 to-red-400 bg-clip-text text-transparent">Information Page</h1>
        <p className="text-gray-400 text-lg mb-8 leading-relaxed">This page is currently being updated to bring you all the latest details about MEMAX OTT. We are committed to providing you with the best entertainment experience.</p>
        <a href="/" className="inline-block bg-red-600 hover:bg-red-700 text-white font-semibold px-8 py-3 rounded-full transition-all hover:scale-105 active:scale-95 shadow-lg shadow-red-600/20">Return Home</a>
      </div>
    </div>
  );
}
