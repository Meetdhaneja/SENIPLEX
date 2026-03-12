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
        // Render's host property omits the protocol (e.g., app-name.onrender.com)
        let apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        if (!apiUrl.startsWith('http://') && !apiUrl.startsWith('https://')) {
            apiUrl = apiUrl.includes('.') ? `https://${apiUrl}` : `https://${apiUrl}.onrender.com`;
        }
        if (apiUrl.endsWith('/api')) {
            apiUrl = apiUrl.slice(0, -4);
        }

        return [
            {
                source: '/api/:path*',
                destination: `${apiUrl}/api/:path*`,
            },
        ]
    },
}

module.exports = nextConfig
