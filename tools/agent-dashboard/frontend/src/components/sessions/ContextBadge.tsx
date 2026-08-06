/**
 * ContextBadge — FR-002 Sprint 3
 * Hiển thị % context window đã dùng: progress bar 48×8px + text %.
 * Màu: navy (0–70%) → cam nhạt (70–90%) → đỏ (>90%).
 * HIDDEN khi context_pct === 0, null, hoặc undefined.
 */
import { fmtNum } from '../../utils/format'

interface ContextBadgeProps {
  contextPct: number | null | undefined
  lastInputTotal?: number | null
  maxContext?: number | null
  /** Khi session DONE: badge vẫn hiện nhưng opacity 50% */
  sessionDone?: boolean
}

/** Trả về màu progress bar và text theo ngưỡng */
function resolveColors(pct: number): { bar: string; text: string } {
  if (pct >= 90) return { bar: '#EF4444', text: '#EF4444' }
  if (pct >= 70) return { bar: '#FFAA80', text: '#251C53' }
  return { bar: '#4A3F8C', text: '#4A3F8C' }
}

export default function ContextBadge({
  contextPct,
  lastInputTotal,
  maxContext,
  sessionDone = false,
}: ContextBadgeProps) {
  // HIDE khi 0, null, hoặc undefined — watch_out: phân biệt 0 vs null
  if (contextPct === null || contextPct === undefined || contextPct <= 0) return null

  const pct = Math.min(contextPct, 100)
  const { bar: barColor, text: textColor } = resolveColors(pct)

  const hasDetail = lastInputTotal != null && maxContext != null
  const tooltipText = hasDetail
    ? `${fmtNum(lastInputTotal!)} / ${fmtNum(maxContext!)} tokens (lượt gần nhất)`
    : `${pct.toFixed(1)}% context window đã dùng`

  const ariaLabel = hasDetail
    ? `${pct.toFixed(1)}% context window đã dùng (${fmtNum(lastInputTotal!)} / ${fmtNum(maxContext!)} tokens)`
    : `${pct.toFixed(1)}% context window đã dùng`

  return (
    <span
      className={`inline-flex items-center gap-1.5 ml-auto shrink-0${sessionDone ? ' opacity-50' : ''}`}
      title={tooltipText}
      role="progressbar"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={ariaLabel}
    >
      {/* Progress bar: 48×8px, border-radius pill */}
      <span
        className="inline-block rounded relative overflow-hidden"
        style={{ width: 48, height: 8, backgroundColor: '#E5E7EB', flexShrink: 0 }}
      >
        <span
          className="absolute inset-y-0 left-0 rounded transition-all"
          style={{ width: `${pct}%`, backgroundColor: barColor }}
        />
      </span>
      {/* Percentage text: 12px monospace */}
      <span
        className="font-mono text-caption shrink-0"
        style={{ color: textColor }}
      >
        {pct.toFixed(1)}%
      </span>
    </span>
  )
}
