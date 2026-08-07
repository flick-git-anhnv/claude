/**
 * AppHeader — Sprint 5 (nâng cấp)
 * - Thêm UsageBar (2 bars: 5h + 7d) khi active account là OAuth
 * - Polling /api/accounts/usage/active mỗi 60s (khớp cache TTL backend)
 * - Ẩn bars khi: không có active account, API key account, hoặc usage.error != null
 * - Height: 56px (không có bars) → 80px (có bars, OAuth)
 */
import { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useWsState } from '../../contexts/WsContext'
import { truncate } from '../../utils/format'
import UsageBar from '../common/UsageBar'
import type { UsageInfo } from '../../types'

const USAGE_POLL_MS = 60_000  // 60s — khớp cache TTL backend

export default function AppHeader() {
  const navigate = useNavigate()
  const { activeAccount } = useWsState()

  const [usage, setUsage] = useState<UsageInfo | null>(null)
  const [usageLoading, setUsageLoading] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    // Chỉ fetch khi có active account (kind !== 'api_key' hoặc kind chưa biết)
    if (!activeAccount) {
      setUsage(null)
      return
    }
    // API key account → không có quota 5hr/7day → ẩn hẳn
    if (activeAccount.kind === 'api_key') {
      setUsage(null)
      return
    }

    let cancelled = false

    async function fetchUsage() {
      try {
        setUsageLoading(true)
        const r = await fetch('/api/accounts/usage/active')
        if (!r.ok) {
          if (!cancelled) setUsage(null)
          return
        }
        const data: UsageInfo = await r.json()
        if (!cancelled) {
          setUsage(data)
          setUsageLoading(false)
        }
      } catch {
        if (!cancelled) {
          setUsage(null)
          setUsageLoading(false)
        }
      }
    }

    // Fetch ngay lập tức
    setUsageLoading(true)
    fetchUsage()

    // Poll mỗi 60s
    pollRef.current = setInterval(fetchUsage, USAGE_POLL_MS)

    return () => {
      cancelled = true
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [activeAccount?.id, activeAccount?.kind])

  // Hiển thị bars khi: có usage data không có error, hoặc đang loading (skeleton)
  const showBars = usageLoading || (usage != null && usage.error == null)
  const headerHeight = showBars ? 80 : 56

  return (
    <header
      className="flex items-center justify-between px-6 bg-kz-navy text-white shrink-0"
      style={{ height: headerHeight, transition: 'height 150ms ease' }}
    >
      {/* Left: Logo + Title */}
      <div className="flex items-center gap-3">
        <div
          className="flex items-center justify-center w-8 h-8 bg-kz-orange rounded font-bold text-white text-xs shrink-0"
          aria-hidden="true"
        >
          KZ
        </div>
        <span className="text-h1 font-semibold tracking-tight">Agent Dashboard</span>
      </div>

      {/* Right: Account indicator + UsageBar */}
      <div className="flex items-center">
        {activeAccount ? (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-kz-green shrink-0" aria-hidden="true" />
            <div className="text-right">
              <div
                className="text-sm font-semibold text-white leading-tight"
                title={activeAccount.name}
              >
                {truncate(activeAccount.name, 30)}
              </div>
              <div className="font-mono text-caption text-kz-navy-light leading-tight">
                {activeAccount.oauth_masked ?? activeAccount.key_masked}
              </div>
              {/* Sprint 5: Usage bars — chỉ khi OAuth và có data */}
              <UsageBar
                usage={usage}
                onHeader={true}
                loading={usageLoading && usage == null}
              />
            </div>
          </div>
        ) : (
          <button
            onClick={() => navigate('/accounts')}
            className="flex items-center gap-2 px-3 py-1.5 bg-kz-orange text-white text-sm font-medium rounded-badge hover:bg-orange-600 transition-colors"
            aria-label="Chưa có tài khoản active — vào Account Manager để đặt"
          >
            <span aria-hidden="true">!</span>
            <span>Chưa có tài khoản active</span>
          </button>
        )}
      </div>
    </header>
  )
}
