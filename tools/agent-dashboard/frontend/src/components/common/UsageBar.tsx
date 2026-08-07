/**
 * UsageBar — Sprint 5 (Phần A)
 * Hiển thị 2 progress bar quota Anthropic: Session (5hr) + Weekly (7day).
 *
 * Màu ngưỡng:
 *   < 80%  → #22C55E (xanh lá)
 *   ≥ 80%  → #F05922 (cam KZTEK — TUYỆT ĐỐI không dùng đỏ tươi)
 *
 * Props:
 *   usage     — UsageInfo | null từ API, null → skeleton hoặc ẩn
 *   onHeader  — true → style cho nền Navy (AppHeader), false → style cho card trắng
 *   loading   — true → skeleton pulse state
 *
 * States:
 *   - loading=true          → skeleton (2 bars mờ, pulse)
 *   - usage.error = api_key → return null (ẩn hoàn toàn — không phải OAuth)
 *   - usage.error = other   → return null (ẩn lặng lẽ, không crash)
 *   - usage = null          → return null
 *   - bình thường           → 2 bars + label + reset countdown
 */
import type { UsageInfo } from '../../types'
import { fmtResetsIn } from '../../utils/format'

interface UsageBarProps {
  usage: UsageInfo | null
  onHeader?: boolean  // true = nền navy (AppHeader), false = nền trắng (AccountCard)
  loading?: boolean
}

/** Tính màu fill theo ngưỡng % */
function barColor(pct: number | null | undefined): string {
  if (pct == null) return '#22C55E'
  return pct >= 80 ? '#F05922' : '#22C55E'
}

/** Một dòng progress bar đơn lẻ */
function SingleBar({
  label,
  pct,
  resetsAt,
  onHeader,
  loading,
}: {
  label: string
  pct: number | null | undefined
  resetsAt: number | null | undefined
  onHeader: boolean
  loading: boolean
}) {
  const trackBg = onHeader ? 'rgba(255,255,255,0.2)' : 'rgba(203,203,203,0.4)'
  const barW = onHeader ? 120 : 100
  const textColor = onHeader ? 'rgba(255,255,255,0.9)' : '#4A3F8C'
  const resetColor = onHeader ? 'rgba(255,255,255,0.6)' : '#6B7280'
  const fillColor = barColor(pct)
  const fillPct = pct != null ? Math.min(100, Math.max(0, pct)) : 0

  return (
    <div
      className="flex items-center gap-1.5"
      style={{ lineHeight: 1 }}
    >
      {/* Label "5h" / "7d" */}
      <span
        style={{
          fontSize: 10,
          fontFamily: 'monospace',
          color: textColor,
          width: 14,
          textAlign: 'right',
          flexShrink: 0,
        }}
      >
        {label}
      </span>

      {/* Track + fill */}
      <div
        role="progressbar"
        aria-valuenow={pct ?? 0}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${label === '5h' ? 'Session 5 giờ' : 'Weekly 7 ngày'}: ${pct != null ? pct.toFixed(0) : '?'}%`}
        style={{
          width: barW,
          height: 4,
          borderRadius: 2,
          background: trackBg,
          flexShrink: 0,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: loading ? '30%' : `${fillPct}%`,
            height: '100%',
            background: loading ? (onHeader ? 'rgba(255,255,255,0.3)' : '#CBCBCB') : fillColor,
            borderRadius: 2,
            transition: 'width 0.4s ease',
            animation: loading ? 'pulse 1.5s ease-in-out infinite' : undefined,
          }}
        />
      </div>

      {/* Percentage */}
      <span
        style={{
          fontSize: 10,
          color: loading ? (onHeader ? 'rgba(255,255,255,0.4)' : '#CBCBCB') : (pct != null ? fillColor : textColor),
          width: 28,
          textAlign: 'right',
          flexShrink: 0,
        }}
      >
        {loading ? '…' : pct != null ? `${pct.toFixed(0)}%` : '?'}
      </span>

      {/* Reset countdown */}
      {!loading && resetsAt != null && (
        <span style={{ fontSize: 9, color: resetColor, flexShrink: 0 }}>
          Reset {fmtResetsIn(resetsAt)}
        </span>
      )}
    </div>
  )
}

export default function UsageBar({ usage, onHeader = false, loading = false }: UsageBarProps) {
  // Ẩn hoàn toàn khi null hoặc có error
  if (!loading && (usage == null || usage.error != null)) return null

  return (
    <div
      className="flex flex-col"
      style={{ gap: 3, marginTop: 4 }}
      aria-label="Quota sử dụng Anthropic"
    >
      <SingleBar
        label="5h"
        pct={loading ? null : usage?.five_hour_pct}
        resetsAt={usage?.resets_at}
        onHeader={onHeader}
        loading={loading}
      />
      <SingleBar
        label="7d"
        pct={loading ? null : usage?.seven_day_pct}
        resetsAt={usage?.seven_day_resets_at}
        onHeader={onHeader}
        loading={loading}
      />
    </div>
  )
}
