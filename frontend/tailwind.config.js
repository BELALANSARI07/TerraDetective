/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        slate: {
          950: '#0B111A', // deep space slate
          900: '#131C2B', // secondary workbench surface
          850: '#182436', // bento card surface
          800: '#1F2E45', // elevated card/hover
          750: '#273B57', // card borders
          700: '#334D70',
        },
        nasa: {
          blue: '#1A56DB',
          cyan: '#38BDF8',
          red: '#EF4444',
          emerald: '#10B981', // p < 0.05 significant
          amber: '#F59E0B',   // p >= 0.05 non-significant
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Courier New', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
