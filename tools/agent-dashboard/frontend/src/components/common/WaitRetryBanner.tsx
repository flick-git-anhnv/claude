/**
 * WaitRetryBanner — Sprint 7 (S7-T26)
 *
 * Banner toàn màn hình (full-width, đặt dưới AppHeader, đẩy nội dung xuống, KHÔNG overlay).
 * Hiển thị khi failoverState là 'waiting' | 'retrying' | 'paused'.
 *
 * 5 trạng thái nội dung:
 *  hidden              — failoverState idle/monitoring/swapping
 *  counting            — waiting, next_retry_at hợp lệ, chưa hết lần thử
 *  retrying            — failoverState 'retrying'
 *  retry_failed_n      — paused sau lần thử N thất bại, còn retry tiếp
 *  exhausted_all_retries — retryAttempt >= maxRetries
 *
 * Accessibility: role="alert" + aria-live="assertive"
 */
import { useEffect, useState } from 'react'
import { useWsState } from '../../contexts/WsContext'
import { normalizeIso } from '../../utils/format'

const BASE = '/api'

async function cancelRetryApi(): Promise<void> {
  const r = await fetch(`${BASE}/failover/cancel-retry`, { method: 'POST' })
  if (!r.ok) {
    const d = await r.json().catch(() => ({}))
    throw new Error((d as { error?: { message?: string } }).error?.message ?? `HTTP ${r.status}`)
  }
}

/** Format seconds → "HH:MM:SS" */
export function formatCountdown(totalSeconds: number): string {
  const s = Math.max(0, Math.floor(totalSeconds))
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${pad(h)}:${pad(m)}:${pad(sec)}`
}

export default function WaitRetryBanner() {
  const {
    failoverState,
    failoverNextRetryAt,
    failoverRetryAccount,
    failoverRetryAttempt,
    failoverMaxRetries,
  } = useWsState()

  const [secondsLeft, setSecondsLeft] = useState<number>(0)
  const [cancelling, setCancelling] = useState(false)
  const [cancelError, setCancelError] = useState('')

  // Countdown: tính lại mỗi giây khi đang waiting/paused và có next_retry_at
  useEffect(() => {
    if (failoverState !== 'waiting' && failoverState !== 'paused') return
    if (!failoverNextRetryAt) return

    function computeLeft(): number {
      if (!failoverNextRetryAt) return 0
      const targetMs = new Date(normalizeIso(failoverNextRetryAt)).getTime()
      return Math.max(0, (targetMs - Date.now()) / 1000)
    }

    setSecondsLeft(computeLeft())
    const timer = setInterval(() => setSecondsLeft(computeLeft()), 1000)
    return () => clearInterval(timer)
  }, [failoverState, failoverNextRetryAt])

  const isVisible =
    failoverState === 'waiting' ||
    failoverState === 'retrying' ||
    failoverState === 'paused'

  if (!isVisible) return null

  const isExhausted =
    failoverMaxRetries > 0 && failoverRetryAttempt >= failoverMaxRetries

  async function handleCancel() {
    setCancelling(true)
    setCancelError('')
    try {
      await cancelRetryApi()
    } catch (e) {
      setCancelError(e instanceof Error ? e.message : 'Không thể hủy')
    } finally {
      setCancelling(false)
    }
  }

  // ── Build hiển thị theo trạng thái ──────────────────────────────────────────
  let icon: string
  let heading: string
  let subText: string | null = null
  const showCountdown =
    (failoverState === 'waiting' || failoverState === 'paused') &&
    !!failoverNextRetryAt &&
    !isExhausted
  const showCancelBtn = failoverState === 'waiting' && !isExhausted

  if (failoverState === 'retrying') {
    icon = '↺'
    heading = `Đang thử kết nối lại${failoverRetryAccount?.name ? ` với ${failoverRetryAccount.name}` : ''}...`
    if (failoverMaxRetries > 0) {
      subText = `Lần thử ${failoverRetryAttempt}/${failoverMaxRetries}`
    }
  } else if (isExhausted) {
    icon = '!'
    heading = `Đã thử tối đa ${failoverMaxRetries} lần — không có account khả dụng`
    subText = 'Vui lòng kích hoạt tài khoản thủ công trong trang Quản lý tài khoản'
  } else if (failoverState === 'paused') {
    icon = '↺'
    const attemptPart =
      failoverMaxRetries > 0
        ? ` (${failoverRetryAttempt}/${failoverMaxRetries})`
        : ''
    heading = `Lần thử${attemptPart} thất bại — Thử lại sau`
    if (failoverRetryAccount?.name) {
      subText = `Tài khoản: ${failoverRetryAccount.name}`
    }
  } else {
    // waiting
    icon = '⏳'
    heading = 'Tất cả account đã hết quota — Tự động thử lại sau'
    if (failoverRetryAccount?.name) {
      subText = `Sẽ thử: ${failoverRetryAccount.name}`
    }
  }

  return (
    <div
      className="flex items-center gap-3 px-6 py-2 bg-kz-warning-bg border-b border-kz-orange-light border-l-4 border-l-kz-orange shrink-0"
      role="alert"
      aria-live="assertive"
      aria-atomic="false"
    >
      {/* Icon */}
      <span
        className="text-kz-orange font-bold text-base leading-none shrink-0"
        aria-hidden="true"
      >
        {icon}
      </span>

      {/* Message */}
      <div className="flex-1 min-w-0 flex items-center gap-2 flex-wrap">
        <span className="text-sm font-semibold text-kz-navy">{heading}</span>
        {showCountdown && (
          <span
            className="font-mono font-bold text-kz-orange"
            aria-label={`Còn ${formatCountdown(secondsLeft)} nữa`}
          >
            {formatCountdown(secondsLeft)}
          </span>
        )}
        {subText && (
          <span className="text-caption text-kz-navy-mid">{subText}</span>
        )}
        {cancelError && (
          <span className="text-caption text-kz-red">{cancelError}</span>
        )}
      </div>

      {/* Cancel button */}
      {showCancelBtn && (
        <button
          onClick={handleCancel}
          disabled={cancelling}
          className="shrink-0 px-3 py-1 text-caption font-semibold text-kz-navy border border-kz-navy hover:bg-kz-navy-light/30 rounded-btn transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          aria-label="Hủy auto-retry"
        >
          {cancelling ? 'Đang hủy...' : 'Hủy auto-retry'}
        </button>
      )}
    </div>
  )
}
