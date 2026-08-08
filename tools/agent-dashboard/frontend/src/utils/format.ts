/** Format a number with thousands separator (vi-VN style) */
export function fmtNum(n: number): string {
  return n.toLocaleString('vi-VN')
}

/**
 * Normalize an ISO-8601 string for JavaScript Date parsing.
 *
 * Python's datetime.isoformat() produces timestamps with:
 *   - 6-digit microseconds: "2026-08-06T08:30:00.123456+00:00"
 *   - "+00:00" timezone suffix instead of "Z"
 *
 * ECMAScript Date.parse only supports up to 3 fractional-second digits
 * (milliseconds), so 6-digit microseconds cause NaN in V8/SpiderMonkey.
 * "+00:00" is also not universally supported in older environments.
 *
 * This helper truncates fractional seconds to 3 digits and normalises the
 * timezone suffix to "Z" so that new Date() reliably produces a valid Date.
 */
export function normalizeIso(iso: string): string {
  return iso
    .replace(/(\.\d{3})\d+/, '$1') // truncate microseconds → milliseconds
    .replace(/\+00:00$/, 'Z')      // +00:00 → Z (broader engine support)
}

/** Format ISO timestamp → HH:mm:ss */
export function fmtTime(iso: string): string {
  return new Date(normalizeIso(iso)).toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

/** Format ISO timestamp → DD/MM/YYYY HH:mm */
export function fmtDateTime(iso: string): string {
  return new Date(normalizeIso(iso)).toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Format ISO timestamp → dd/MM HH:mm (no year, used as relative-time fallback) */
export function fmtDateShort(iso: string): string {
  const d = new Date(normalizeIso(iso))
  if (isNaN(d.getTime())) {
    // Last-resort: slice raw string to avoid showing "Invalid Date"
    return iso.length >= 16 ? iso.slice(5, 16).replace('T', ' ') : iso
  }
  return d.toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Format ISO timestamp → DD/MM */
export function fmtDate(iso: string): string {
  return new Date(normalizeIso(iso)).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
  })
}

/**
 * Format relative time.
 *
 * - < 5 s  → "vừa xong"
 * - < 60 s → "Xs trước"
 * - < 1 h  → "Xm trước"
 * - < 24 h → "Xh Ym trước" / "Xh trước"
 * - ≥ 24 h → "dd/MM HH:mm"  (absolute date — more readable than "240h trước")
 * - NaN    → "dd/MM HH:mm"  (graceful fallback for unparseable timestamps)
 */
export function fmtRelative(iso: string): string {
  const ts = new Date(normalizeIso(iso)).getTime()
  if (isNaN(ts)) return fmtDateShort(iso)
  const diff = Math.floor((Date.now() - ts) / 1000)
  if (diff < 5) return 'vừa xong'
  if (diff < 60) return `${diff}s trước`
  if (diff < 3600) return `${Math.floor(diff / 60)}m trước`
  if (diff < 86400) {
    const h = Math.floor(diff / 3600)
    const m = Math.floor((diff % 3600) / 60)
    return m > 0 ? `${h}h ${m}m trước` : `${h}h trước`
  }
  // diff ≥ 24 h: show absolute date instead of "240h trước"
  return fmtDateShort(iso)
}

/** Truncate string to maxLen with ellipsis */
export function truncate(str: string, maxLen: number): string {
  return str.length <= maxLen ? str : str.slice(0, maxLen - 3) + '...'
}

/** Mask API key: sk-ant-api01-xxxx → sk-ant-****XXXX (last 4 visible) */
export function maskKey(key: string): string {
  if (key.length <= 8) return '****'
  return key.slice(0, 8) + '****' + key.slice(-4)
}

/**
 * Format token count to compact human-readable string.
 * 0        → null (caller should hide the element)
 * 1–999    → "999"
 * 1 000+   → "1.5K"
 * 1 000 000+ → "1.2M"
 */
export function fmtTokensCompact(n: number): string | null {
  if (n <= 0) return null
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return n.toString()
}

/**
 * Sprint 5: Format countdown đến thời điểm reset usage quota.
 * resetsAt: unix seconds (từ UsageInfo.resets_at / seven_day_resets_at)
 * Ví dụ: "1h 20m" | "4d 3h" | "45m" | "Đã reset"
 */
export function fmtResetsIn(resetsAt: number): string {
  const diffSec = Math.max(0, resetsAt - Math.floor(Date.now() / 1000))
  if (diffSec === 0) return 'Đã reset'
  const days = Math.floor(diffSec / 86400)
  const hours = Math.floor((diffSec % 86400) / 3600)
  const mins = Math.floor((diffSec % 3600) / 60)
  if (days >= 1) return `${days}d ${hours}h`
  if (hours >= 1) return `${hours}h ${mins}m`
  return `${mins}m`
}

/** Decode project slug back to absolute directory path (Windows support) */
export function decodeProjectSlug(slug: string): string {
  if (/^[a-z]--/.test(slug)) {
    const drive = slug[0].toUpperCase() + ':\\'
    const remainder = slug.slice(3)
    return drive + remainder.split('--').join('\\')
  }
  return slug
}

/** Return friendly error message for Anthropic API usage error */
export function getUsageErrorMsg(error: string | null | undefined): string {
  if (!error) return ''
  if (error === 'http_429') return 'Quá giới hạn lượt gọi (Rate Limit 429). Đang chờ reset...'
  if (error === 'unauthorized') return 'Phiên đăng nhập hết hạn. Cần đăng nhập lại.'
  if (error === 'timeout') return 'Yêu cầu quá thời gian. Đang thử lại...'
  if (error === 'network') return 'Lỗi kết nối mạng. Đang thử lại...'
  return `Lỗi lấy quota (${error}). Đang thử lại...`
}
