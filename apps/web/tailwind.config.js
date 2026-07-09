/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "../../packages/ui/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        background: "#030712", // Very dark navy/black
        panel: "#0b1528",      // Navy slate panel background
        border: "#1e293b",      // Slate border
        brand: {
          primary: "#10b981",   // Emerald green
          secondary: "#6366f1", // Indigo
          accent: "#3b82f6",    // Blue
          dark: "#064e3b"
        }
      },
      fontFamily: {
        sans: ["var(--font-sans)", "sans-serif"],
        mono: ["var(--font-mono)", "monospace"]
      }
    },
  },
  plugins: [],
}
