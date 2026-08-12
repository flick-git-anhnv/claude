/**
 * FailoverStatusBadge — Sprint 7 (S7-T22)
 *
 * Hiển thị badge trạng thái failover trên AccountCard:
 *  - FAILOVER ACTIVE (cam)  → tự ẩn sau 30s với CSS fade-out
 *  - EXHAUSTED (xám)        → tồn tại cho đến khi user reset
 *  - LOW QUOTA X% (cam nhạt) → thường xuyên khi backup < 10% quota
 *
 * Props:
 *  failoverBadge: 'active' | 'exhausted' | 'low_quota' | 'none'
 *  lowQuotaPct?: number    — chỉ khi low_quota
 *  reason?: string         — "429 detected" | "Quota 5h full" | ...
 *  swapLatencyMs?: number  — chỉ khi active
 *  triggeredAt?: number    — Date.now() ms khi failover xảy ra (tính 30s auto-hide)
 */
import { useEffect, useState } from 'react'

export type FailoverBadgeState = 'active' | 'exhausted' | 'low_quota' | 'none'

interface FailoverStatusBadgeProps {
  failoverBadge: FailoverBadgeState
  lowQuotaPct?: number
  reason?: string
  swapLatencyMs?: number | null
  triggeredAt?: number
}

const BADGE_VISIBLE_MS = 30_000

export default function FailoverStatusBadge({
  failoverBadge,
  lowQuotaPct,
  reason,
  swapLatencyMs,
  triggeredAt,
}: FailoverStatusBadgeProps) {
  // Track visibility state cho FAILOVER ACTIVE badge (30s auto-hide)
  const [activeVisible, setActiveVisible] = useState(failoverBadge === 'active')
  const [fadingOut, setFadingOut] = useState(false)

  useEffect(() => {
    if (failoverBadge !== 'active' || triggeredAt == null) {
      setActiveVisible(false)
      setFadingOut(false)
      return
    }

    const elapsed = Date.now() - triggeredAt
    const remaining = BADGE_VISIBLE_MS - elapsed

    if (remaining <= 0) {
      setActiveVisible(false)
      return
    }

    setActiveVisible(true)
    setFadingOut(false)

    // Bắt đầu fade-out 1s trước khi hết 30s
    const fadeDelay = Math.max(0, remaining - 1000)
    const fadeTimer = setTimeout(() => setFadingOut(true), fadeDelay)
    const hideTimer = setTimeout(() => setActiveVisible(false), remaining)

    return () => {
      clearTimeout(fadeTimer)
      clearTimeout(hideTimer)
    }
  }, [failoverBadge, triggeredAt])

  if (failoverBadge === 'none') return null

  return (
    <div className="flex flex-col gap-1">
      {/* Badge FAILOVER ACTIVE */}
      {failoverBadge === 'active' && activeVisible && (
        <span
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-orange text-white shrink-0"
          style={{
            transition: fadingOut ? 'opacity 1s ease' : 'opacity 0.3s ease',
            opacity: fadingOut ? 0 : 1,
          }}
          role="status"
          aria-live="polite"
          aria-label="Vừa được tự động kích hoạt bởi failover"
        >
          <span aria-hidden="true">↺</span>
          FAILOVER ACTIVE
        </span>
      )}

      {/* Chip lý do swap — cùng lifecycle 30s với badge FAILOVER ACTIVE */}
      {failoverBadge === 'active' && activeVisible && (reason || swapLatencyMs != null) && (
        <span
          className="text-caption text-kz-navy-mid"
          style={{
            transition: fadingOut ? 'opacity 1s ease' : 'opacity 0.3s ease',
            opacity: fadingOut ? 0 : 1,
          }}
        >
          {reason && `Lý do: ${reason}`}
          {reason && swapLatencyMs != null && '  |  '}
          {swapLatencyMs != null && `Độ trễ swap: ${swapLatencyMs}ms`}
        </span>
      )}

      {/* Badge EXHAUSTED */}
      {failoverBadge === 'exhausted' && (
        <span className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption bg-kz-gray/30 text-kz-text shrink-0">
          EXHAUSTED
        </span>
      )}

      {/* Badge LOW QUOTA */}
      {failoverBadge === 'low_quota' && lowQuotaPct != null && (
        <span className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption bg-kz-orange/15 text-kz-orange shrink-0">
          Ít quota ({lowQuotaPct.toFixed(0)}%)
        </span>
      )}
    </div>
  )
}
