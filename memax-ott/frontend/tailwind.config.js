/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#7c3aed', // Violet
                    50: '#f5f3ff',
                    100: '#ede9fe',
                    200: '#ddd6fe',
                    300: '#c4b5fd',
                    400: '#a78bfa',
                    500: '#8b5cf6',
                    600: '#7c3aed', // Main Violet
                    700: '#6d28d9',
                    800: '#5b21b6',
                    900: '#4c1d95',
                    950: '#2e1065',
                },
                secondary: '#000000', // Black
                accent: '#d946ef', // Neon Pink/Magenta for Cyberpunk vibe
                cyan: '#06b6d4', // Cyberpunk Cyan
                dark: {
                    DEFAULT: '#0f0f0f',
                    50: '#fafafa',
                    100: '#f5f5f5',
                    200: '#e5e5e5',
                    300: '#d4d4d4',
                    400: '#a3a3a3',
                    500: '#737373',
                    600: '#525252',
                    700: '#404040',
                    800: '#262626', // Card background
                    900: '#1a1a1a', // Darker background
                    950: '#0f0f0f', // Almost black
                },
            },
            fontFamily: {
                sans: ['var(--font-inter)'],
                mono: ['var(--font-robot-mono)'],
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
                'cyber-gradient': 'linear-gradient(to right, #7c3aed, #db2777)',
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'glow': 'glow 2s ease-in-out infinite',
            },
            keyframes: {
                glow: {
                    '0%, 100%': { boxShadow: '0 0 5px #7c3aed, 0 0 10px #7c3aed' },
                    '50%': { boxShadow: '0 0 20px #7c3aed, 0 0 30px #db2777' },
                }
            }
        },
    },
    plugins: [],
}
