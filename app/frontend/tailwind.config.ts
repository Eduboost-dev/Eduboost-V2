import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: { "2xl": "1400px" },
    },
    extend: {
      // ── Deep Tech Ocean: Tech Innovation × Ocean Depths ──────────────
      colors: {
        navy: {
          950: "#050d1a",
          900: "#0a1628",
          800: "#1a2332",
          700: "#1e2d40",
          600: "#243550",
          500: "#2a3e60",
          400: "#3a5070",
        },
        teal: {
          DEFAULT: "#2d8b8b",
          50:  "#e6f7f7",
          100: "#b3e5e5",
          200: "#80d4d4",
          300: "#4dc2c2",
          400: "#26b0b0",
          500: "#2d8b8b",
          600: "#226a6a",
          700: "#1a5050",
          800: "#113535",
          900: "#091b1b",
        },
        electric: {
          DEFAULT: "#0d7fc0",
          50:  "#e0f2fb",
          100: "#b3dff5",
          200: "#80c9ee",
          300: "#4db3e7",
          400: "#26a2e0",
          500: "#0d7fc0",
          600: "#0a6396",
          700: "#07486d",
          800: "#042d43",
          900: "#021220",
        },
        aqua: {
          DEFAULT: "#00cfd1",
          50:  "#e0fafa",
          100: "#b3f2f2",
          200: "#80e9ea",
          300: "#4de0e1",
          400: "#26d8d9",
          500: "#00cfd1",
          600: "#00a1a3",
          700: "#007476",
          800: "#004748",
          900: "#001a1b",
        },
        seafoam: {
          DEFAULT: "#a8dadc",
          light:   "#d4eef0",
          dark:    "#6db8bb",
        },
        cream: {
          DEFAULT: "#f1faee",
          muted:   "#c8ddd5",
          dark:    "#9ab8b0",
        },

        // ── shadcn/ui semantic aliases ──────────────────────────────────
        border:      "hsl(var(--border))",
        input:       "hsl(var(--input))",
        ring:        "hsl(var(--ring))",
        background:  "hsl(var(--background))",
        foreground:  "hsl(var(--foreground))",
        primary: {
          DEFAULT:    "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT:    "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT:    "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT:    "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT:    "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT:    "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT:    "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },

        // ── Status colours ──────────────────────────────────────────────
        success: {
          DEFAULT: "#22c55e",
          foreground: "#052e16",
          muted: "#dcfce7",
          dark: "#16a34a",
        },
        warning: {
          DEFAULT: "#f59e0b",
          foreground: "#451a03",
          muted: "#fef3c7",
        },
        error: {
          DEFAULT: "#ef4444",
          foreground: "#450a0a",
          muted: "#fee2e2",
          dark: "#dc2626",
        },
        info: {
          DEFAULT: "#0d7fc0",
          foreground: "#f1faee",
          muted: "#e0f2fb",
        },
      },

      // ── Typography ────────────────────────────────────────────────────
      fontFamily: {
        sans:    ["DM Sans", "var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono:    ["JetBrains Mono", "var(--font-geist-mono)", "monospace"],
        display: ["Bricolage Grotesque", "var(--font-geist-sans)", "system-ui", "sans-serif"],
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
        "3xs": ["0.5rem",   { lineHeight: "0.75rem"  }],
      },

      // ── Spacing ───────────────────────────────────────────────────────
      spacing: {
        "4.5": "1.125rem",
        "13":  "3.25rem",
        "18":  "4.5rem",
        "22":  "5.5rem",
        "26":  "6.5rem",
        sidebar: "16rem",
        topbar:  "3.5rem",
      },

      // ── Border radius ─────────────────────────────────────────────────
      borderRadius: {
        "4xl": "2rem",
        "3xl": "1.5rem",
        "2xl": "1rem",
        xl: "calc(var(--radius) + 4px)",
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },

      // ── Box shadows ───────────────────────────────────────────────────
      boxShadow: {
        "card":        "0 1px 3px rgba(0,0,0,0.5), 0 1px 2px rgba(0,0,0,0.4)",
        "card-hover":  "0 8px 32px rgba(0,207,209,0.18), 0 4px 12px rgba(0,0,0,0.5)",
        "card-lift":   "0 16px 48px rgba(0,207,209,0.22), 0 6px 20px rgba(0,0,0,0.6)",
        "glow":        "0 0 24px rgba(0,207,209,0.4), 0 0 8px rgba(13,127,192,0.2)",
        "glow-sm":     "0 0 12px rgba(13,127,192,0.5)",
        "glow-lg":     "0 0 48px rgba(0,207,209,0.3), 0 0 20px rgba(13,127,192,0.25)",
        "electric":    "0 0 20px rgba(13,127,192,0.45)",
        "inner-glow":  "inset 0 1px 0 rgba(0,207,209,0.12), inset 0 -1px 0 rgba(0,0,0,0.1)",
        "inner-border":"inset 0 0 0 1px rgba(0,207,209,0.15)",
      },

      // ── Backdrop blur ─────────────────────────────────────────────────
      backdropBlur: {
        xs: "2px",
      },

      // ── Keyframes ─────────────────────────────────────────────────────
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to:   { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to:   { height: "0" },
        },
        "fade-in":     { from: { opacity: "0", transform: "translateY(16px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        "fade-in-up":  { from: { opacity: "0", transform: "translateY(20px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        "fade-in-down":{ from: { opacity: "0", transform: "translateY(-12px)" }, to: { opacity: "1", transform: "translateY(0)" } },
        "slide-in-left":{ from: { opacity: "0", transform: "translateX(-20px)" }, to: { opacity: "1", transform: "translateX(0)" } },
        "blur-in":     { from: { opacity: "0", filter: "blur(8px)", transform: "scale(0.97)" }, to: { opacity: "1", filter: "blur(0)", transform: "scale(1)" } },
        "scale-in":    { from: { opacity: "0", transform: "scale(0.90)" }, to: { opacity: "1", transform: "scale(1)" } },
        "float":       {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%":      { transform: "translateY(-12px)" },
        },
        "shimmer": {
          from: { transform: "translateX(-100%)" },
          to:   { transform: "translateX(100%)" },
        },
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 10px rgba(0,207,209,0.3)" },
          "50%":       { boxShadow: "0 0 28px rgba(0,207,209,0.7)" },
        },
        "pulse-ring": {
          "0%":   { transform: "scale(0.95)", boxShadow: "0 0 0 0 rgba(0,207,209,0.45)" },
          "70%":  { transform: "scale(1)",    boxShadow: "0 0 0 10px rgba(0,207,209,0)" },
          "100%": { transform: "scale(0.95)", boxShadow: "0 0 0 0 rgba(0,207,209,0)" },
        },
        "spin-slow": {
          to: { transform: "rotate(360deg)" },
        },
        "morph": {
          "0%, 100%": { borderRadius: "60% 40% 30% 70% / 60% 30% 70% 40%" },
          "25%":  { borderRadius: "30% 60% 70% 40% / 50% 60% 30% 60%" },
          "50%":  { borderRadius: "50% 60% 30% 60% / 40% 30% 70% 60%" },
          "75%":  { borderRadius: "40% 70% 60% 30% / 60% 40% 50% 70%" },
        },
        "notification-ping": {
          "0%":   { transform: "scale(1)", opacity: "1" },
          "75%, 100%": { transform: "scale(2.2)", opacity: "0" },
        },
        "gradient-x": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%":      { backgroundPosition: "100% 50%" },
        },
      },

      // ── Animation shorthands ──────────────────────────────────────────
      animation: {
        "accordion-down":    "accordion-down 0.2s ease-out",
        "accordion-up":      "accordion-up 0.2s ease-out",
        "fade-in":           "fade-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) both",
        "fade-in-up":        "fade-in-up 0.5s cubic-bezier(0.22, 1, 0.36, 1) both",
        "fade-in-slow":      "fade-in 0.7s cubic-bezier(0.22, 1, 0.36, 1) both",
        "slide-in-left":     "slide-in-left 0.4s cubic-bezier(0.22, 1, 0.36, 1) both",
        "blur-in":           "blur-in 0.5s ease-out both",
        "scale-in":          "scale-in 0.35s cubic-bezier(0.22, 1, 0.36, 1) both",
        "float":             "float 6s ease-in-out infinite",
        "float-slow":        "float 9s ease-in-out infinite",
        "shimmer":           "shimmer 1.8s ease-in-out infinite",
        "pulse-glow":        "pulse-glow 2.5s ease-in-out infinite",
        "pulse-ring":        "pulse-ring 2s ease-in-out infinite",
        "spin-slow":         "spin-slow 10s linear infinite",
        "morph":             "morph 12s ease-in-out infinite",
        "notification-ping": "notification-ping 1.5s ease-out infinite",
        "gradient-x":        "gradient-x 4s ease infinite",
      },

      // ── Transition timing functions ───────────────────────────────────
      transitionTimingFunction: {
        "spring":     "cubic-bezier(0.22, 1, 0.36, 1)",
        "bounce-in":  "cubic-bezier(0.68, -0.55, 0.27, 1.55)",
        "smooth-out": "cubic-bezier(0.4, 0, 0.2, 1)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
