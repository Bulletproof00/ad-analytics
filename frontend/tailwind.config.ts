import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#1a4fd8',
          muted: '#eef2ff',
        },
      },
    },
  },
  plugins: [],
};

export default config;
