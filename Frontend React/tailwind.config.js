/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
        colors: {
            cyber: '#0a0e1a',
            neonBlue: '#00d4ff',
            neonRed: '#ff3b6b',
            cyberCard: '#131b2f',
        },
        fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['Space Grotesk', 'monospace']
        }
    },
  },
  plugins: [],
}
