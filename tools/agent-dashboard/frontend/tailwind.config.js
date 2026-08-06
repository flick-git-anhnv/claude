/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'kz-navy':        '#251C53',
        'kz-orange':      '#F05922',
        'kz-navy-mid':    '#4A3F8C',
        'kz-navy-light':  '#B8B3D6',
        'kz-orange-light':'#FFAA80',
        'kz-gray':        '#CBCBCB',
        'kz-green':       '#22C55E',
        'kz-red':         '#EF4444',
        'kz-red-bg':      '#FEE2E2',
        'kz-warning-bg':  '#FFFBEB',
        'kz-error-bg':    '#FEF2F2',
        'kz-text':        '#1F2937',
      },
      fontSize: {
        'h1': ['20px', { fontWeight: '600', lineHeight: '1.3' }],
        'h2': ['16px', { fontWeight: '600', lineHeight: '1.4' }],
        'body': ['14px', { fontWeight: '400', lineHeight: '1.5' }],
        'caption': ['12px', { fontWeight: '400', lineHeight: '1.4' }],
      },
      borderRadius: {
        'card': '8px',
        'btn': '6px',
        'badge': '12px',
      },
      width: {
        'sidebar': '220px',
      },
      height: {
        'header': '56px',
      },
    },
  },
  plugins: [],
}
