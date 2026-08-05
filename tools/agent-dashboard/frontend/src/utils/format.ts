/** Format a number with thousands separator (vi-VN style) */
export function fmtNum(n: number): string {
  return n.toLocaleString('vi-VN')
}

/** Format ISO timestamp → HH:mm:ss */
export function fmtTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('vi-VN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

/** Format ISO timestamp → DD/MM/YYYY HH:mm */
export function fmtDateTime(iso: string): string {
  return new Date(iso).toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Format ISO timestamp → DD/MM */
export function fmtDate(iso: string): string {
  return new Date(iso).toLocaleDateString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
  })
}

/** Format relative time: "5s trước", "2m trước", "1h 20m trước" */
export function fmtRelative(iso: string): string {
  const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
  if (diff < 5) return 'vừa xong'
  if (diff < 60) return `${diff}s trước`
  if (diff < 3600) return `${Math.floor(diff / 60)}m trước`
  const h = Math.floor(diff / 3600)
  const m = Math.floor((diff % 3600) / 60)
  return m > 0 ? `${h}h ${m}m trước` : `${h}h trước`
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
