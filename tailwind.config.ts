import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0f0f0f',
        sidebar: '#1a1a1a',
        border: '#2a2a2a',
        card: {
          DEFAULT: '#1a1a1a',
          foreground: '#ffffff',
        },
        popover: {
          DEFAULT: '#1a1a1a',
          foreground: '#ffffff',
        },
        primary: {
          DEFAULT: '#a855f7',
          foreground: '#ffffff',
        },
        secondary: {
          DEFAULT: '#ec4899',
          foreground: '#ffffff',
        },
        muted: {
          DEFAULT: '#2a2a2a',
          foreground: '#b8b8b8',
        },
        accent: {
          DEFAULT: '#a855f7',
          foreground: '#ffffff',
        },
        destructive: {
          DEFAULT: '#ef4444',
          foreground: '#ffffff',
        },
        input: '#2a2a2a',
        ring: '#a855f7',
        foreground: '#ffffff',
      },
      borderRadius: {
        lg: '0.5rem',
        md: '0.375rem',
        sm: '0.25rem',
      },
      backgroundImage: {
        'gradient-primary': 'linear-gradient(135deg, #a855f7 0%, #ec4899 100%)',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
