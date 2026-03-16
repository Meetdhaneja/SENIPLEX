/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    images: {
        domains: ['localhost', 'image.tmdb.org'],
    },
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    },
    async rewrites() {
        // Render's host property provides the internal hostname (e.g., "memax-backend")
        let apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        // 1. Internal Render Hostname Support (no dots or protocol)
        if (!apiUrl.includes('.') && !apiUrl.startsWith('http')) {
            // It's the internal service name, use port 8000
            apiUrl = `http://${apiUrl}:8000`;
            console.log(`[NextConfig] Using internal Render hostname: ${apiUrl}`);
        } 
        // 2. External Domain Support (if it has dots but no protocol)
        else if (!apiUrl.startsWith('http')) {
            apiUrl = `https://${apiUrl}`;
        }
        
        // 3. Normalize: Remove trailing slash and /api
        apiUrl = apiUrl.replace(/\/$/, '').replace(/\/api$/, '');

        console.log(`[NextConfig] Final Backend Target: ${apiUrl}`);

        return [
            {
                source: '/api/:path*',
                destination: `${apiUrl}/api/:path*`,
            },
        ]
    },
}

module.exports = nextConfig
