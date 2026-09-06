/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Warm parchment surface -- the manuscript page.
        parchment: {
          DEFAULT: "#F5F1E6",
          dim: "#EDE7D6",
          line: "#DAD2B4",
        },
        // Deep botanical ink -- near-black but genuinely green, not a tinted stand-in.
        ink: {
          DEFAULT: "#1C2B22",
          soft: "#3A4A3E",
          faint: "#6B7A6C",
        },
        // Vana (Skt. "forest") -- the primary brand green, from neem/tulsi.
        vana: {
          50: "#EEF2E9",
          100: "#D7E2CC",
          300: "#8FAE7C",
          500: "#4C7A47",
          600: "#385C36",
          700: "#2F5233",
          900: "#1B3220",
        },
        // Haldi (turmeric) -- accent for citations, highlights, active states.
        haldi: {
          100: "#F6E4C2",
          300: "#E9C583",
          500: "#C67C2E",
          700: "#9A5C1E",
        },
        // Kumkum (vermillion) -- reserved for alerts and required fields.
        kumkum: {
          500: "#A63A2C",
          600: "#8A2F23",
        },
      },
      fontFamily: {
        display: ["Fraunces", "ui-serif", "Georgia", "serif"],
        body: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        devanagari: ["\"Noto Sans Devanagari\"", "ui-sans-serif", "sans-serif"],
      },
      boxShadow: {
        manuscript: "0 1px 0 0 rgba(28,43,34,0.08)",
      },
    },
  },
  plugins: [],
};
