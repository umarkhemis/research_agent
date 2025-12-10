/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6366F1',
          hover: '#7C3AED',
        },
        secondary: '#8B5CF6',
        accent: '#10B981',
      },
    },
  },
  plugins: [],
}
