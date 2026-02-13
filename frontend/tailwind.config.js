/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#11121a",
        dusk: "#2b2f3a",
        fog: "#ece8e1",
        ember: "#e76f51",
        moss: "#2a9d8f",
        sand: "#f4a261",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "ui-sans-serif", "system-ui"],
        body: ["'Source Sans 3'", "ui-sans-serif", "system-ui"],
      },
      backgroundImage: {
        "hero-glow": "radial-gradient(circle at top left, rgba(231, 111, 81, 0.25), transparent 45%)",
      },
    },
  },
  plugins: [],
};
