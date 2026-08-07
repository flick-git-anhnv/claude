/**
 * AggregatePipelineView — Sprint 5 FR-005 (mới)
 * Hiển thị bảng tổng hợp pipeline theo vai trò agent, fetch từ /api/pipeline/aggregate.
 *
 * Layout:
 *   - Header: tổng sessions · tổng lượt gọi
 *   - Filter: ô search theo display_name + dropdown thời gian (window)
 *   - Table: header Navy, row xen kẽ trắng/#F9FAFB, sort call_count DESC
 *   - Active row: viền trái 3px cam + text "N đang chạy"
 *   - Polling mỗi 30s khi component visible
 *
 * Tất cả màu sắc theo brand KZTEK: Navy #251C53, Cam #F05922, không dùng đỏ tươi.
 */
import { useEffect, useState, useRef } from 'react'
import type { AggregateResponse, AggregateEntry } from '../../types'
import { fmtTokensCompact } from '../../utils/format'

const AGGREGATE_POLL_MS = 30_000  // 30s — không cần realtime hard như session view

interface WindowOption {
  label: string
  value: number  // 0 = all-time
}

const WINDOW_OPTIONS: WindowOption[] = [
  { label: 'Tất cả thời gian', value: 0 },
  { label: '7 ngày', value: 7 },
  { label: '30 ngày', value: 30 },
  { label: '90 ngày', value: 90 },
]

// ── Loading skeleton ──────────────────────────────────────────────────────────

function SkeletonRows() {
  return (
    <>
      {[140, 110, 90, 75, 60].map((w, i) => (
        <tr key={i} style={{ borderBottom: '1px solid #F3F4F6' }}>
          {[w, 40, 30, 50, 40, 20].map((barW, j) => (
            <td key={j} style={{ padding: '12px 12px' }}>
              <div
                className="animate-pulse rounded"
                style={{ height: 10, width: barW, background: '#E5E7EB' }}
              />
            </td>
          ))}
        </tr>
      ))}
    </>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────────

function EmptyState() {
  return (
    <tr>
      <td colSpan={6} style={{ padding: '48px 0', textAlign: 'center' }}>
        <div style={{ fontSize: 32, marginBottom: 12 }}>🤖</div>
        <p style={{ fontSize: 14, fontWeight: 600, color: '#251C53', marginBottom: 4 }}>
          Chưa có dữ liệu subagent
        </p>
        <p style={{ fontSize: 12, color: '#CBCBCB' }}>
          Dữ liệu xuất hiện khi có agent được gọi trong session
        </p>
      </td>
    </tr>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export default function AggregatePipelineView() {
  const [data, setData] = useState<AggregateResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [search, setSearch] = useState('')
  const [windowDays, setWindowDays] = useState(0)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchAggregate() {
      try {
        const params = new URLSearchParams()
        if (windowDays > 0) params.set('window', String(windowDays))
        const r = await fetch(`/api/pipeline/aggregate?${params}`)
        if (!r.ok) throw new Error(`aggregate fetch ${r.status}`)
        const json: AggregateResponse = await r.json()
        if (!cancelled) {
          setData(json)
          setError(false)
          setLoading(false)
        }
      } catch {
        if (!cancelled) {
          setError(true)
          setLoading(false)
        }
      }
    }

    setLoading(true)
    setError(false)
    fetchAggregate()

    // Poll mỗi 30s
    pollRef.current = setInterval(fetchAggregate, AGGREGATE_POLL_MS)

    return () => {
      cancelled = true
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [windowDays])

  // Filter theo search (không phân biệt hoa/thường)
  const filteredRoster: AggregateEntry[] = (data?.roster ?? []).filter(e =>
    e.display_name.toLowerCase().includes(search.toLowerCase())
  )

  const totalSessions = data?.total_sessions ?? 0
  const totalCalls = data?.total_calls ?? 0

  return (
    <div>
      {/* Header tổng */}
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <p style={{ fontSize: 13, color: '#251C53', fontWeight: 600 }}>
          Tổng hợp{' '}
          {!loading && data && (
            <span style={{ fontWeight: 400, color: '#6B7280' }}>
              — {totalSessions} sessions · {totalCalls} lượt gọi
            </span>
          )}
          {loading && (
            <span style={{ fontWeight: 400, color: '#CBCBCB' }}>— đang tải...</span>
          )}
        </p>

        {/* Controls: search + window dropdown */}
        <div className="flex items-center gap-2">
          <input
            type="text"
            placeholder="Tìm vai trò..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              padding: '4px 10px',
              fontSize: 12,
              border: '1px solid #CBCBCB',
              borderRadius: 6,
              outline: 'none',
              color: '#251C53',
              width: 160,
            }}
            aria-label="Tìm vai trò"
          />
          <select
            value={windowDays}
            onChange={e => setWindowDays(Number(e.target.value))}
            style={{
              padding: '4px 8px',
              fontSize: 12,
              border: '1px solid #CBCBCB',
              borderRadius: 6,
              color: '#251C53',
              background: '#FFFFFF',
              cursor: 'pointer',
            }}
            aria-label="Chọn khoảng thời gian"
          >
            {WINDOW_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="flex items-center justify-center py-8 gap-2">
          <span style={{ fontSize: 13, color: '#F05922' }}>⚠ Không lấy được dữ liệu</span>
          <button
            onClick={() => {
              setLoading(true)
              setError(false)
              // Re-mount effect bằng cách thay đổi windowDays về chính nó
              setWindowDays(w => w)
            }}
            style={{
              fontSize: 12,
              color: '#4A3F8C',
              background: 'none',
              border: '1px solid #4A3F8C',
              borderRadius: 4,
              padding: '2px 8px',
              cursor: 'pointer',
            }}
          >
            Thử lại
          </button>
        </div>
      )}

      {/* Table */}
      {!error && (
        <div style={{ overflowX: 'auto' }}>
          <table
            role="table"
            style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}
            aria-label="Bảng tổng hợp agent theo vai trò"
          >
            <thead>
              <tr
                style={{
                  background: '#251C53',
                  color: '#FFFFFF',
                  fontSize: 12,
                  fontWeight: 600,
                  textAlign: 'left',
                }}
              >
                <th scope="col" style={{ padding: '10px 12px', borderRadius: '6px 0 0 0' }}>
                  Vai trò
                </th>
                <th scope="col" style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                  Lần gọi
                </th>
                <th scope="col" style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                  Sessions
                </th>
                <th scope="col" style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                  Token IN
                </th>
                <th scope="col" style={{ padding: '10px 12px', textAlign: 'right', whiteSpace: 'nowrap' }}>
                  Token OUT
                </th>
                <th scope="col" style={{ padding: '10px 12px', textAlign: 'right', borderRadius: '0 6px 0 0', whiteSpace: 'nowrap' }}>
                  Active
                </th>
              </tr>
            </thead>

            <tbody>
              {loading ? (
                <SkeletonRows />
              ) : filteredRoster.length === 0 ? (
                <EmptyState />
              ) : (
                filteredRoster.map((entry, idx) => {
                  const isActive = entry.active_now > 0
                  const rowBg = idx % 2 === 0 ? '#FFFFFF' : '#F9FAFB'
                  const tokenIn = fmtTokensCompact(entry.total_tokens.input) ?? '0'
                  const tokenOut = fmtTokensCompact(entry.total_tokens.output) ?? '0'

                  return (
                    <tr
                      key={entry.role}
                      style={{
                        background: rowBg,
                        borderBottom: '1px solid #F3F4F6',
                        borderLeft: isActive ? '3px solid #F05922' : '3px solid transparent',
                        height: 44,
                        transition: 'background 100ms ease',
                      }}
                    >
                      <td style={{ padding: '8px 12px', color: '#251C53', fontWeight: 500 }}>
                        {entry.display_name}
                      </td>
                      <td style={{ padding: '8px 12px', textAlign: 'right', color: '#374151', fontWeight: 600 }}>
                        {entry.call_count.toLocaleString('vi-VN')}
                      </td>
                      <td style={{ padding: '8px 12px', textAlign: 'right', color: '#6B7280' }}>
                        {entry.session_count.toLocaleString('vi-VN')}
                      </td>
                      <td style={{ padding: '8px 12px', textAlign: 'right', color: '#6B7280', fontFamily: 'monospace', fontSize: 12 }}>
                        {tokenIn}
                      </td>
                      <td style={{ padding: '8px 12px', textAlign: 'right', color: '#6B7280', fontFamily: 'monospace', fontSize: 12 }}>
                        {tokenOut}
                      </td>
                      <td style={{ padding: '8px 12px', textAlign: 'right' }}>
                        {isActive ? (
                          <span style={{ fontSize: 11, color: '#F05922', fontWeight: 600, whiteSpace: 'nowrap' }}>
                            {entry.active_now} đang chạy
                          </span>
                        ) : (
                          <span style={{ fontSize: 11, color: '#CBCBCB' }}>—</span>
                        )}
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
