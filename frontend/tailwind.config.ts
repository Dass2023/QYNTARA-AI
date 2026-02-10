import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        void: "#030712", // Deepest Void
        surface: {
          DEFAULT: "#0B1221", // Dark Navy
          highlight: "#162032",
          border: "rgba(0, 243, 255, 0.15)" // Neon Cyan Tint
        },
        cyan: {
          DEFAULT: "#00f3ff", // NEON CYAN
          dim: "rgba(0, 243, 255, 0.1)",
          glow: "rgba(0, 243, 255, 0.5)"
        },
        purple: {
          DEFAULT: "#bc13fe", // NEON PURPLE
          dim: "rgba(188, 19, 254, 0.1)",
          glow: "rgba(188, 19, 254, 0.5)"
        },
        danger: {
          DEFAULT: "#ff003c", // CYBER RED
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Orbitron', 'sans-serif'],
        mono: ['Rajdhani', 'monospace'],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "grid-pattern": "linear-gradient(to right, rgba(0, 243, 255, 0.05) 1px, transparent 1px), linear-gradient(to bottom, rgba(0, 243, 255, 0.05) 1px, transparent 1px)",
      },
      animation: {
        "scanline": "scanline 8s linear infinite",
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "float": "float 6s ease-in-out infinite",
        "glitch": "glitch 1s linear infinite",
      },
      keyframes: {
        scanline: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100%)" }
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" }
        },
        glitch: {
          "2%, 64%": { transform: "translate(2px,0) skew(0deg)" },
          "4%, 60%": { transform: "translate(-2px,0) skew(0deg)" },
          "62%": { transform: "translate(0,0) skew(5deg)" }
        }
      }
    },
  },
  plugins: [],
};
export default config;
