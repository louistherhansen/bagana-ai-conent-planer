/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        bagana: {
          primary: "#0f766e",
          secondary: "#0d9488",
          accent: "#14b8a6",
          muted: "#99f6e4",
          dark: "#134e4a",
        },
      },
    },
  },
  plugins: [],
};
