---
description: Setup project React SPA mới với Vite + TypeScript + Tailwind CSS v3 + Vitest. Dùng khi bắt đầu dự án frontend mới, cần scaffold đầy đủ config, brand KZTEK colors, và test setup sẵn sàng.
---

# Skill: vite-react-setup

Scaffold một project React SPA đầy đủ theo chuẩn KZTEK.

## Bước 1 — Nhận tham số

Xác định từ yêu cầu của user:
- `PROJECT_NAME`: tên thư mục project (kebab-case, ví dụ: `my-app`)
- `WORKING_DIR`: thư mục cha chứa project (mặc định: working directory hiện tại)

## Bước 2 — Khởi tạo project Vite

```bash
cd <WORKING_DIR>
npm create vite@latest <PROJECT_NAME> -- --template react-ts
cd <PROJECT_NAME>
npm install
npm install -D tailwindcss@3 postcss autoprefixer
npm install -D vitest @vitest/coverage-v8 @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
npx tailwindcss init -p
```

Nếu `npm create vite` không chạy được (môi trường non-interactive), tạo thủ công `package.json` + các file config rồi chạy `npm install`.

## Bước 3 — Ghi đè / Tạo các file config

### `tailwind.config.js`
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#251C53',
          light: '#4A3F8C',
          pale: '#B8B3D6',
        },
        brand: {
          DEFAULT: '#F05922',
          light: '#FFAA80',
        },
        neutral: {
          border: '#CBCBCB',
        },
      },
    },
  },
  plugins: [],
}
```

### `vite.config.ts`
```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test-setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/services/**', 'src/utils/**'],
    },
  },
})
```

### `tsconfig.app.json` — đảm bảo strict mode
Thêm `"strict": true` vào `compilerOptions` nếu chưa có.

### `src/test-setup.ts`
```ts
import '@testing-library/jest-dom'
```

### `src/index.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### `src/main.tsx`
```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
)
```

### `package.json` — thêm script test
Đảm bảo có:
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "lint": "eslint . --ext ts,tsx"
  }
}
```

## Bước 4 — Tạo cấu trúc thư mục chuẩn

```
src/
├── components/
│   ├── layout/
│   ├── ui/
│   └── (feature folders)
├── context/
├── services/
├── hooks/
├── types/
│   └── index.ts
├── utils/
├── constants/
├── App.tsx
├── main.tsx
├── index.css
└── test-setup.ts
tests/
├── unit/
│   ├── services/
│   └── components/
└── integration/
```

Tạo các thư mục trống với `.gitkeep` nếu cần.

## Bước 5 — Tạo constants chuẩn KZTEK

### `src/constants/categoryColors.ts`
```ts
export const CATEGORY_COLORS = [
  '#F05922', '#251C53', '#4A3F8C', '#10B981', '#3B82F6',
  '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6',
] as const
export type CategoryColor = typeof CATEGORY_COLORS[number]
```

## Bước 6 — Verify

Chạy theo thứ tự:
```bash
npx tsc --noEmit          # phải pass (0 error)
npm run test              # nếu đã có test cases
npm run build             # phải build được
```

Báo cáo:
- Danh sách file đã tạo
- Kết quả `tsc --noEmit`
- Kết quả `npm run build` (kB output)
- Project sẵn sàng để Senior Developer bắt đầu code services
