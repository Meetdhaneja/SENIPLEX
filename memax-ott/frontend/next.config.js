/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    images: {
        domains: ['localhost', 'image.tmdb.org', 'placehold.co', 'via.placeholder.com'],
    },
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    },
    async rewrites() {
        // Normalize the API URL
        let apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        // Ensure protocol exists
        if (!apiUrl.startsWith('http')) {
            apiUrl = `https://${apiUrl}`;
        }
        
        // Remove trailing slash and /api
        apiUrl = apiUrl.replace(/\/$/, '').replace(/\/api$/, '');

        console.log(`[NextConfig] Backend Proxy Destination: ${apiUrl}`);

        return [
            {
                source: '/api/:path*',
                destination: `${apiUrl}/api/:path*`,
            },
        ]
    },
}

module.exports = nextConfig
