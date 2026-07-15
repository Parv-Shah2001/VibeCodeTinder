/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        tinder: {
          pink: '#FF4458',
          orange: '#FD267D',
          purple: '#FF5864',
          dark: '#21262E',
        }
      },
      backgroundImage: {
        'tinder-gradient': 'linear-gradient(to top right, #FF4458, #FD267D)',
      }
    },
  },
  plugins: [],
}
