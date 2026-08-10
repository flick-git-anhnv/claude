/**
 * Tests for WaitRetryBanner helpers — Sprint 7
 *
 * Chỉ test pure function formatCountdown (exported).
 * React rendering không test ở đây (node environment).
 */
import { describe, it, expect } from 'vitest'
import { formatCountdown } from './WaitRetryBanner'

describe('formatCountdown', () => {
  it('returns 00:00:00 for zero seconds', () => {
    expect(formatCountdown(0)).toBe('00:00:00')
  })

  it('returns 00:00:00 for negative seconds (clamp to 0)', () => {
    expect(formatCountdown(-10)).toBe('00:00:00')
  })

  it('pads single-digit minutes and seconds', () => {
    expect(formatCountdown(61)).toBe('00:01:01')
  })

  it('shows hours correctly for large values', () => {
    expect(formatCountdown(3600)).toBe('01:00:00')
    expect(formatCountdown(3661)).toBe('01:01:01')
    expect(formatCountdown(7322)).toBe('02:02:02')
  })

  it('handles exactly 59 minutes 59 seconds', () => {
    expect(formatCountdown(3599)).toBe('00:59:59')
  })

  it('truncates fractional seconds (floor)', () => {
    // 90.9 seconds → 1m 30s
    expect(formatCountdown(90.9)).toBe('00:01:30')
  })

  it('handles large countdown (24h - 1s)', () => {
    expect(formatCountdown(86399)).toBe('23:59:59')
  })

  it('returns string with exactly HH:MM:SS format (length 8)', () => {
    const result = formatCountdown(1234)
    expect(result).toMatch(/^\d{2}:\d{2}:\d{2}$/)
    expect(result.length).toBe(8)
  })
})
