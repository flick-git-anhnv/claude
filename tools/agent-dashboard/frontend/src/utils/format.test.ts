/**
 * Tests for format.ts — focus on fmtRelative / normalizeIso
 *
 * Root cause being tested:
 *   Python datetime.isoformat() produces "2026-08-06T08:30:00.123456+00:00"
 *   - 6-digit microseconds (ECMAScript Date.parse only handles 3 digits → NaN)
 *   - "+00:00" timezone suffix (can fail in older V8 builds)
 */
import { describe, it, expect, vi, afterEach } from 'vitest'
import { normalizeIso, fmtRelative, fmtDateShort, decodeProjectSlug, getUsageErrorMsg } from './format'

// ── Helper ────────────────────────────────────────────────────────────────────

/** Return an ISO string (Z-suffix, ms-precision) offset by `secs` from now */
function ago(secs: number): string {
  return new Date(Date.now() - secs * 1000).toISOString()
}

/** Return a Python-style isoformat string (microseconds + +00:00 suffix) */
function pyIso(date: Date): string {
  const iso = date.toISOString() // "...123Z"
  // Simulate Python: replace 3-digit ms with 6-digit µs, replace Z with +00:00
  return iso.replace(/(\.\d{3})Z$/, '$1000+00:00')
}

// ── normalizeIso ──────────────────────────────────────────────────────────────

describe('normalizeIso', () => {
  it('leaves a standard Z-suffix ISO string unchanged', () => {
    const ts = '2026-08-06T08:30:00.123Z'
    expect(normalizeIso(ts)).toBe('2026-08-06T08:30:00.123Z')
  })

  it('truncates 6-digit microseconds to 3-digit milliseconds', () => {
    expect(normalizeIso('2026-08-06T08:30:00.123456+00:00')).toBe('2026-08-06T08:30:00.123Z')
  })

  it('converts +00:00 timezone suffix to Z', () => {
    expect(normalizeIso('2026-08-06T08:30:00.000+00:00')).toBe('2026-08-06T08:30:00.000Z')
  })

  it('handles Python isoformat (microseconds + +00:00) — produces parseable string', () => {
    const normalized = normalizeIso('2026-08-06T08:30:00.987654+00:00')
    expect(isNaN(new Date(normalized).getTime())).toBe(false)
  })

  it('does not alter strings without fractional seconds or +00:00', () => {
    const ts = '2026-08-06T08:30:00Z'
    expect(normalizeIso(ts)).toBe('2026-08-06T08:30:00Z')
  })
})

// ── fmtRelative ───────────────────────────────────────────────────────────────

describe('fmtRelative — JS-native timestamps (Z suffix, 3-digit ms)', () => {
  it('returns "vừa xong" for timestamps < 5 s ago', () => {
    expect(fmtRelative(ago(2))).toBe('vừa xong')
  })

  it('returns "Xs trước" for timestamps a few seconds ago', () => {
    expect(fmtRelative(ago(30))).toBe('30s trước')
  })

  it('returns "Xm trước" for timestamps a few minutes ago', () => {
    expect(fmtRelative(ago(90))).toBe('1m trước')
    expect(fmtRelative(ago(300))).toBe('5m trước')
  })

  it('returns "Xh Ym trước" for timestamps a few hours ago (< 24 h)', () => {
    expect(fmtRelative(ago(3600))).toBe('1h trước')
    expect(fmtRelative(ago(5400))).toBe('1h 30m trước')
    expect(fmtRelative(ago(7200))).toBe('2h trước')
  })

  it('returns absolute date string (not "Xh trước") for timestamps > 24 h ago', () => {
    const result = fmtRelative(ago(86401))
    // Must NOT be a relative "Xh trước" pattern
    expect(result).not.toMatch(/h trước/)
    // Must NOT be 'NaN' anywhere
    expect(result).not.toContain('NaN')
  })

  it('returns absolute date string for timestamps several days ago', () => {
    const result = fmtRelative(ago(86400 * 3))
    expect(result).not.toMatch(/h trước/)
    expect(result).not.toContain('NaN')
  })
})

describe('fmtRelative — Python-style timestamps (microseconds + +00:00)', () => {
  it('does NOT return "NaNh trước" for Python timestamp seconds ago', () => {
    const ts = pyIso(new Date(Date.now() - 30_000))
    const result = fmtRelative(ts)
    expect(result).not.toContain('NaN')
    expect(result).toBe('30s trước')
  })

  it('does NOT return "NaNh trước" for Python timestamp hours ago', () => {
    const ts = pyIso(new Date(Date.now() - 3 * 3600 * 1000))
    const result = fmtRelative(ts)
    expect(result).not.toContain('NaN')
    expect(result).toBe('3h trước')
  })

  it('shows absolute date (not NaN) for Python timestamp days ago', () => {
    const ts = pyIso(new Date(Date.now() - 2 * 86400 * 1000))
    const result = fmtRelative(ts)
    expect(result).not.toContain('NaN')
    expect(result).not.toMatch(/h trước/)
  })

  it('handles Python timestamp with +00:00 but no fractional seconds', () => {
    const ts = '2026-08-04T10:00:00+00:00'
    const result = fmtRelative(ts)
    expect(result).not.toContain('NaN')
  })

  it('handles Python timestamp with +00:00 and 6-digit microseconds for recent event', () => {
    // This is the exact format Python datetime.now(timezone.utc).isoformat() produces
    const recentPy = pyIso(new Date(Date.now() - 55_000)) // ~55s ago (matches UXR report)
    const result = fmtRelative(recentPy)
    expect(result).not.toContain('NaN')
    expect(result).toBe('55s trước')
  })
})

describe('fmtRelative — edge cases', () => {
  it('returns fallback string (not NaN) for completely invalid timestamp', () => {
    const result = fmtRelative('not-a-date')
    expect(result).not.toContain('NaN')
  })

  it('returns fallback string (not NaN) for empty string', () => {
    const result = fmtRelative('')
    expect(result).not.toContain('NaN')
  })
})

// ── fmtDateShort ─────────────────────────────────────────────────────────────

describe('fmtDateShort', () => {
  it('returns a non-NaN string for Python-style timestamp', () => {
    const ts = '2026-08-04T10:00:00.123456+00:00'
    const result = fmtDateShort(ts)
    expect(result).not.toContain('NaN')
    expect(result.length).toBeGreaterThan(0)
  })

  it('returns raw-slice fallback for completely unparseable input', () => {
    const result = fmtDateShort('not-a-date')
    expect(result).not.toContain('NaN')
  })
})

describe('decodeProjectSlug', () => {
  it('decodes windows path from project slug correctly', () => {
    expect(decodeProjectSlug('c--Users--nguye--Desktop')).toBe('C:\\Users\\nguye\\Desktop')
    expect(decodeProjectSlug('d--MyProject--Sub')).toBe('D:\\MyProject\\Sub')
  })

  it('keeps other slugs unchanged', () => {
    expect(decodeProjectSlug('my-project-slug')).toBe('my-project-slug')
  })
})

describe('getUsageErrorMsg', () => {
  it('translates quota error codes to friendly Vietnamese messages', () => {
    expect(getUsageErrorMsg('http_429')).toContain('Rate Limit 429')
    expect(getUsageErrorMsg('unauthorized')).toContain('hết hạn')
    expect(getUsageErrorMsg('timeout')).toContain('quá thời gian')
    expect(getUsageErrorMsg('network')).toContain('kết nối mạng')
    expect(getUsageErrorMsg('some_unknown_error')).toContain('Lỗi lấy quota')
    expect(getUsageErrorMsg(null)).toBe('')
  })
})
