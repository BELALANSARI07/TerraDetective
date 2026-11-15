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
        nasa: {
          navy: '#0B3D91',
          blue: '#1A56DB',
          cyan: '#00E5FF',
          coral: '#FF6B00',
          red: '#EF4444',
          emerald: '#10B981',
          amber: '#F59E0B',
        },
        space: {
          950: '#07090E',
          900: '#0C1017',
          800: '#141B26',
          700: '#1E2636',
          600: '#374151',
        },
        archival: {
          bg: '#F3F0E6',
          paper: '#FAF8F5',
          border: '#DCD7C9',
          ink: '#141E19',
          muted: '#687268',
          terracotta: '#C84B31',
          viridian: '#1B6B50',
          sand: '#E8E3D5',
          stone: '#F3F0E6',
        },
        obsidian: {
          bg: '#07090E',
          panel: '#0C1017',
          border: '#1E2636',
          subtle: '#141B26',
          cyan: '#00E5FF',
          amber: '#FF6B00',
          text: '#E1E7F0',
          muted: '#6C7D93',
        },
      },
      fontFamily: {
        serif: ['"Instrument Serif"', 'Newsreader', 'Georgia', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'Fira Code', 'Courier New', 'monospace'],
      }
    },
  },
  plugins: [],
}
