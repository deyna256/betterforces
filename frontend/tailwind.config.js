/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cf-blue': '#1a73e8',
        'cf-green': '#00c853',
        'cf-red': '#d32f2f',
        'cf-orange': '#ff6f00',
      },
    },
  },
  plugins: [],
}
