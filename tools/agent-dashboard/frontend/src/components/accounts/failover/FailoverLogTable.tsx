/**
 * FailoverLogTable — Sprint 7 (S7-T25)
 *
 * Tab "Failover Log" trong AccountManagerPage.
 * - GET /api/failover/log?from=&to=&limit=20&offset=...
 * - Table header nền Navy #251C53 chữ trắng
 * - Filter date range (from/to date input)
 * - WS realtime: watch failoverCount24h → refetch trang đầu khi có event mới
 * - Empty state + skeleton loading (5 rows giả)
 * - Phân trang 20 record/trang
 * - animate-fade-in cho hàng đầu tiên khi có event mới
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import type { FailoverEvent, FailoverLogResponse } from '../../../types'
import { useWsState } from '../../../contexts/WsContext'
import { normalizeIso } from '../../../utils/format'

const PAGE_SIZE = 20
const SKELETON_COUNT = 5

// ── Label helpers ─────────────────────────────────────────────────────────────

function triggerLabel(reason: string): string {
  switch (reason) {
    case 'http_429':           return '429 Rate Limit'
    case 'quota_5h_full':      return 'Quota 5h đầy'
    case 'quota_7d_full':      return 'Quota 7d đầy'
    case 'jsonl_rate_limit':   return 'Rate Limit (JSONL)'
    case 'api_wide_suspected': return 'API-wide issue'
    case 'manual_override':    return 'Kích hoạt thủ công'
    default:                   return reason
  }
}

interface ResultDisplay {
  text: string
  className: string
}

function resultDisplay(result: string): ResultDisplay {
  switch (result) {
    case 'success':
      return { text: 'Thành công', className: 'text-kz-green font-semibold' }
    case 'swap_failed':
      return { text: 'Swap thất bại', className: 'text-kz-red font-semibold' }
    case 'wait_and_retry_scheduled':
      return { text: 'Chờ retry', className: 'text-kz-orange' }
    case 'wait_and_retry_success':
      return { text: 'Retry thành công', className: 'text-kz-green font-semibold' }
    case 'wait_and_retry_failed':
      return { text: 'Retry thất bại', className: 'text-kz-red font-semibold' }
    case 'api_wide_suspected':
      return { text: 'API-wide', className: 'text-kz-navy-mid' }
    case 'retry_cancelled_by_manual':
      return { text: 'Hủy bởi user', className: 'text-kz-navy-mid' }
    default:
      return { text: result, className: 'text-kz-navy-mid' }
  }
}

function isFailedResult(result: string): boolean {
  return result === 'swap_failed' || result === 'wait_and_retry_failed'
}

function fmtDatetime(iso: string): string {
  try {
    return new Date(normalizeIso(iso)).toLocaleString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  } catch {
    return iso.slice(0, 19).replace('T', ' ')
  }
}

// ── Skeleton row ──────────────────────────────────────────────────────────────

function SkeletonRow({ idx }: { idx: number }) {
  const widths = [80, 60, 65, 55, 50, 40]
  return (
    <tr className="border-t border-kz-gray">
      {widths.map((w, j) => (
        <td key={j} className="px-3 py-2.5">
          <div
            className="h-3 bg-kz-navy-light/40 rounded animate-pulse"
            style={{ width: `${w - (idx * 3) % 20}%` }}
          />
        </td>
      ))}
    </tr>
  )
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function FailoverLogTable() {
  const { failoverCount24h } = useWsState()
  const prevCount24hRef = useRef(failoverCount24h)
  // Track xem row đầu có phải mới nhất từ WS push không (để animate)
  const hasNewRowRef = useRef(false)

  const [items, setItems] = useState<FailoverEvent[]>([])
  const [total, setTotal] = useState(0)
  const [count24h, setCount24h] = useState(0)
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState('')
  const [page, setPage] = useState(0)
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')

  const fetchLog = useCallback(
    async (pg: number, from: string, to: string) => {
      setLoading(true)
      setFetchError('')
      try {
        const u = new URL('/api/failover/log', window.location.origin)
        u.searchParams.set('limit', String(PAGE_SIZE))
        u.searchParams.set('offset', String(pg * PAGE_SIZE))
        if (from) u.searchParams.set('from', from)
        if (to) u.searchParams.set('to', to + 'T23:59:59')
        const r = await fetch(u.pathname + u.search)
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        const data: FailoverLogResponse = await r.json()
        setItems(data.items)
        setTotal(data.total)
        setCount24h(data.count_24h)
      } catch (e) {
        setFetchError(e instanceof Error ? e.message : 'Lỗi tải dữ liệu')
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  // Initial fetch + khi filter / page thay đổi
  useEffect(() => {
    fetchLog(page, fromDate, toDate)
  }, [page, fromDate, toDate, fetchLog])

  // WS realtime: failover mới → refetch trang đầu (chỉ nếu đang ở page 0)
  useEffect(() => {
    if (failoverCount24h === prevCount24hRef.current) return
    prevCount24hRef.current = failoverCount24h
    hasNewRowRef.current = true
    if (page === 0) {
      fetchLog(0, fromDate, toDate)
    }
  }, [failoverCount24h, page, fromDate, toDate, fetchLog])

  const totalPages = Math.ceil(total / PAGE_SIZE)

  function handleFromChange(v: string) {
    setFromDate(v)
    setPage(0)
  }

  function handleToChange(v: string) {
    setToDate(v)
    setPage(0)
  }

  function clearFilter() {
    setFromDate('')
    setToDate('')
    setPage(0)
  }

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div>
      {/* Header + thống kê + filter */}
      <div className="flex items-start justify-between mb-4 flex-wrap gap-3">
        <div>
          <h3 className="text-h2 text-kz-navy">Failover Log</h3>
          <p className="text-caption text-kz-navy-mid">
            {loading
              ? 'Đang tải...'
              : count24h > 0
              ? `${count24h} sự kiện trong 24h qua`
              : 'Chưa có sự kiện failover trong 24h'}
          </p>
        </div>

        {/* Date range filter */}
        <div className="flex items-center gap-2 flex-wrap text-caption">
          <label className="text-kz-navy-mid" htmlFor="log-from">Từ:</label>
          <input
            id="log-from"
            type="date"
            value={fromDate}
            onChange={e => handleFromChange(e.target.value)}
            className="px-2 py-1 border border-kz-gray rounded-btn text-kz-text focus:outline-none focus:border-kz-navy-mid"
            aria-label="Lọc từ ngày"
          />
          <label className="text-kz-navy-mid" htmlFor="log-to">Đến:</label>
          <input
            id="log-to"
            type="date"
            value={toDate}
            onChange={e => handleToChange(e.target.value)}
            className="px-2 py-1 border border-kz-gray rounded-btn text-kz-text focus:outline-none focus:border-kz-navy-mid"
            aria-label="Lọc đến ngày"
          />
          {(fromDate || toDate) && (
            <button
              onClick={clearFilter}
              className="text-kz-navy-mid underline hover:text-kz-navy"
            >
              Xóa filter
            </button>
          )}
        </div>
      </div>

      {/* Fetch error */}
      {fetchError && (
        <div className="py-4 text-center text-sm text-kz-red mb-3">
          Lỗi: {fetchError} —{' '}
          <button
            onClick={() => fetchLog(page, fromDate, toDate)}
            className="underline hover:opacity-75"
          >
            Thử lại
          </button>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto rounded-card border border-kz-gray">
        <table
          className="w-full border-collapse text-caption"
          role="table"
          aria-label="Bảng failover log"
        >
          <thead>
            <tr style={{ backgroundColor: '#251C53', color: '#ffffff' }}>
              <th className="px-3 py-2.5 text-left font-semibold whitespace-nowrap">
                Thời gian
              </th>
              <th className="px-3 py-2.5 text-left font-semibold whitespace-nowrap">
                Từ account
              </th>
              <th className="px-3 py-2.5 text-left font-semibold whitespace-nowrap">
                Sang account
              </th>
              <th className="px-3 py-2.5 text-left font-semibold whitespace-nowrap">
                Lý do
              </th>
              <th className="px-3 py-2.5 text-left font-semibold whitespace-nowrap">
                Kết quả
              </th>
              <th className="px-3 py-2.5 text-right font-semibold whitespace-nowrap">
                Độ trễ swap
              </th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: SKELETON_COUNT }, (_, i) => (
                <SkeletonRow key={i} idx={i} />
              ))
            ) : items.length === 0 ? (
              <tr>
                <td
                  colSpan={6}
                  className="px-3 py-12 text-center text-kz-navy-mid"
                >
                  {fromDate || toDate
                    ? 'Không có sự kiện trong khoảng thời gian đã chọn'
                    : 'Chưa có sự kiện failover nào'}
                </td>
              </tr>
            ) : (
              items.map((evt, idx) => {
                const { text, className: resCls } = resultDisplay(evt.result)
                const isNew = idx === 0 && hasNewRowRef.current
                const rowBg = isFailedResult(evt.result)
                  ? 'bg-kz-error-bg'
                  : idx % 2 === 0
                  ? 'bg-white'
                  : 'bg-kz-navy-light/10'

                return (
                  <tr
                    key={evt.failover_id}
                    className={[
                      'border-t border-kz-gray',
                      rowBg,
                      isNew ? 'animate-fade-in' : '',
                    ].join(' ')}
                  >
                    <td className="px-3 py-2 text-kz-text whitespace-nowrap">
                      {fmtDatetime(evt.occurred_at)}
                    </td>
                    <td className="px-3 py-2 text-kz-navy-mid">
                      {evt.from_account_name ?? '—'}
                    </td>
                    <td className="px-3 py-2 text-kz-navy font-semibold">
                      {evt.to_account_name ?? '—'}
                    </td>
                    <td className="px-3 py-2 text-kz-text">
                      {triggerLabel(evt.trigger_reason)}
                    </td>
                    <td className={`px-3 py-2 ${resCls}`}>{text}</td>
                    <td className="px-3 py-2 text-right text-kz-navy-mid">
                      {evt.swap_latency_ms != null
                        ? `${evt.swap_latency_ms}ms`
                        : '—'}
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Phân trang */}
      {!loading && totalPages > 1 && (
        <div className="flex items-center justify-between mt-3 flex-wrap gap-2">
          <span className="text-caption text-kz-navy-mid">
            Trang {page + 1}/{totalPages} — {total} sự kiện
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-3 py-1 text-caption font-semibold text-kz-navy border border-kz-navy-light hover:border-kz-navy rounded-btn transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              ← Trước
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="px-3 py-1 text-caption font-semibold text-kz-navy border border-kz-navy-light hover:border-kz-navy rounded-btn transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            >
              Tiếp →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
