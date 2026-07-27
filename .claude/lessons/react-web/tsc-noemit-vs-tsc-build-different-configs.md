# `tsc --noEmit` sạch nhưng `npm run build` vẫn fail — hai lệnh đọc hai tsconfig khác nhau

**Category:** react-web
**Ngày:** 2026-07-26
**Môi trường:** Vite 7 scaffold `react-ts`, TypeScript 5.9, cấu trúc project references

---

## Triệu chứng

Kiểm tra kiểu nhiều lần bằng `npx tsc --noEmit` → **không lỗi**. Yên tâm viết tiếp cả buổi.
Tới khi chạy `npm run build` (`tsc -b && vite build`) mới lòi ra:

```
error TS1294: This syntax is not allowed when 'erasableSyntaxOnly' is enabled.
error TS2774: This condition will always return true since this function is always defined.
```

## Nguyên nhân

Scaffold Vite mới chia ba file cấu hình:

```
tsconfig.json        ← chỉ chứa "references", gần như KHÔNG kiểm gì
tsconfig.app.json    ← nơi thật sự bật strict, erasableSyntaxOnly, noUnusedLocals…
tsconfig.node.json
```

- `tsc --noEmit` (không có `-b`) đọc **tsconfig.json gốc** → gần như luôn sạch, tạo cảm giác an toàn giả.
- `tsc -b` mới build theo **tsconfig.app.json** với đầy đủ quy tắc.

Kèm theo: `erasableSyntaxOnly` (mặc định bật ở scaffold mới) cấm mọi cú pháp TS không xoá được
khi transpile — trong đó có **parameter property**:

```ts
// ❌ TS1294
class ApiTutor { constructor(private endpoint = '/api/tutor') {} }

// ✅
class ApiTutor {
  private endpoint: string
  constructor(endpoint = '/api/tutor') { this.endpoint = endpoint }
}
```

Cùng nhóm bị cấm: `enum` thường, `namespace` có runtime, `declare` field có khởi tạo.

## Cách xử lý

Dùng `npx tsc -b --noEmit` (hoặc chạy thẳng `npm run build`) trước khi kết luận "kiểu đã sạch".

## Không cần làm lại

- Không tắt `erasableSyntaxOnly` — nó bảo đảm mọi file transpile độc lập được (điều kiện để Vite/esbuild nhanh).
- Không sửa `tsconfig.app.json` — vấn đề nằm ở **cách gọi lệnh kiểm**, không phải cấu hình.
