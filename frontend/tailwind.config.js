/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        background: "#080c14",
        surface: "#0f172a",
        "surface-elevated": "#1e293b",
        "surface-card": "#131d31",
        border: "#1e2d48",
        brand: {
          50: "#ecfdf5",
          500: "#10b981",
          600: "#059669",
        },
        accent: {
          cyan: "#06b6d4",
          amber: "#f59e0b",
          rose: "#f43f5e",
          purple: "#8b5cf6",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "SF Mono", "Fira Code", "monospace"],
      },
      screens: {
        xs: "375px",
      }
    },
  },
  plugins: [],
};
