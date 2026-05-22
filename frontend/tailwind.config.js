/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['Geist', 'system-ui', 'sans-serif'],
        mono:    ['Geist Mono', 'monospace'],
        display: ['"Cabinet Grotesk"', 'system-ui', 'sans-serif'],
      },
      colors: {
        surface: {
          0:  '#080b10',
          1:  '#0d1117',
          2:  '#111827',
          3:  '#1a2236',
          4:  '#1f2d45',
        },
        accent: {
          DEFAULT: '#4f8ef7',
          dim:     '#2d5ca8',
          glow:    'rgba(79,142,247,0.18)',
        },
        emerald: {
          glow: 'rgba(52,211,153,0.15)',
        },
        border:  'rgba(255,255,255,0.07)',
        muted:   '#4b5563',
        subtle:  '#6b7280',
      },
      backgroundImage: {
        'grid-pattern': `
          linear-gradient(rgba(79,142,247,0.04) 1px, transparent 1px),
          linear-gradient(90deg, rgba(79,142,247,0.04) 1px, transparent 1px)
        `,
        'glow-top': 'radial-gradient(ellipse 80% 40% at 50% 0%, rgba(79,142,247,0.12), transparent)',
      },
      animation: {
        'pulse-slow':   'pulse 3s cubic-bezier(0.4,0,0.6,1) infinite',
        'fade-in':      'fadeIn 0.4s ease forwards',
        'slide-up':     'slideUp 0.35s ease forwards',
      },
      keyframes: {
        fadeIn:  { from: { opacity: 0 }, to: { opacity: 1 } },
        slideUp: { from: { opacity: 0, transform: 'translateY(8px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
