import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      colors: {
        primary: {
          DEFAULT: "#efece4",
          foreground: "#1a1a1a",
        },
        background: "#efece4",
        foreground: "#1a1a1a",
        card: {
          DEFAULT: "#faf9f6",
          foreground: "#1a1a1a",
        },
        muted: {
          DEFAULT: "#e8e4da",
          foreground: "#6b6560",
        },
        accent: {
          DEFAULT: "#2d2a26",
          foreground: "#efece4",
        },
        border: "#d8d4c8",
        input: "#d8d4c8",
        ring: "#2d2a26",
        validator: {
          accept: "#22c55e",
          reject: "#ef4444",
          uncertain: "#f59e0b",
          leader: "#6366f1",
        },
        consensus: {
          forming: "#f59e0b",
          reached: "#22c55e",
          failed: "#ef4444",
          appealed: "#8b5cf6",
        },
      },
      borderRadius: {
        lg: "0.75rem",
        md: "0.5rem",
        sm: "0.375rem",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "monospace"],
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "pulse-glow": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
        "fade-up": {
          from: { transform: "translateY(10px)", opacity: "0" },
          to: { transform: "translateY(0)", opacity: "1" },
        },
        "vote-appear": {
          from: { transform: "scale(0.8)", opacity: "0" },
          to: { transform: "scale(1)", opacity: "1" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "fade-up": "fade-up 0.4s ease-out",
        "vote-appear": "vote-appear 0.3s ease-out",
      },
    },
  },
  plugins: [],
};

export default config;
