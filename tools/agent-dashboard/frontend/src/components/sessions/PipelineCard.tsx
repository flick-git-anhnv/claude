/**
 * PipelineCard — Sprint 4 (roster redesign)
 * Lưới wrap các ô AgentRosterItem (1 ô/vai trò, gộp N lần gọi).
 * - Fetch /api/sessions/{id}/chain, đọc roster[]
 * - flex-wrap nhiều hàng — hiển thị TOÀN BỘ roster
 * - Click "Xem lịch sử" → history panel bên dưới grid
 * - tokens null → ẩn gracefully (không hiện "0")
 * - result_summary optional (backend deferred) → ẩn nếu chưa có
 */
import { useEffect, useState } from 'react'
import type { RosterResponse, RosterEntry, RosterHistoryEntry } from '../../types'
import AgentRosterItem from './AgentRosterItem'
import { fmtTokensCompact, fmtDateTime } from '../../utils/format'

interface PipelineCardProps {
  sessionId: string
  sessionState: import('../../types').SessionState
  /** Thay đổi khi WS subagent_changed fires → trigger re-fetch */
  lastSubagentAt?: string | null
}

type FetchState = 'loading' | 'ready' | 'empty' | 'error'

/** Skeleton loading: 3 pill mờ */
function PipelineSkeleton() {
  return (
    <div className="flex items-center gap-2 py-1" aria-hidden="true">
      {[148, 20, 148, 20, 196].map((w, i) => (
        <span
          key={i}
          className="inline-block rounded animate-pulse"
          style={{
            width: w,
            height: w === 20 ? 12 : 88,
            backgroundColor: '#E5E7EB',
          }}
        />
      ))}
    </div>
  )
}

/** Connector ──▶ giữa 2 ô roster */
function RosterConnector() {
  return (
    <span
      className="inline-flex items-center justify-center shrink-0"
      style={{ width: 20, color: '#CBCBCB', fontSize: 12, userSelect: 'none' }}
      aria-hidden="true"
    >
      ──▶
    </span>
  )
}

/** Panel lịch sử gọi của 1 vai trò */
function HistoryPanel({
  entry,
  onClose,
}: {
  entry: RosterEntry
  onClose: () => void
}) {
  const [expandedResult, setExpandedResult] = useState<number | null>(null)

  return (
    <div
      style={{
        marginTop: 10,
        padding: '10px 12px',
        background: '#F0EFF9',
        borderRadius: 6,
        border: '1px solid #B8B3D6',
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-2">
        <span style={{ fontSize: 12, fontWeight: 600, color: '#251C53' }}>
          Lịch sử: {entry.display_name}{' '}
          <span style={{ fontWeight: 400, color: '#6B7280' }}>
            ({entry.call_count} lần gọi)
          </span>
        </span>
        <button
          onClick={onClose}
          aria-label="Đóng lịch sử"
          style={{
            fontSize: 14,
            color: '#9CA3AF',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            lineHeight: 1,
            padding: '0 2px',
          }}
        >
          ✕
        </button>
      </div>

      {/* Danh sách history entries */}
      <div className="flex flex-col" style={{ gap: 6 }}>
        {entry.history.map((h: RosterHistoryEntry) => {
          const tokenLabel = h.tokens
            ? fmtTokensCompact(h.tokens.input + h.tokens.output)
            : null
          const isExpanded = expandedResult === h.call_index

          return (
            <div
              key={h.call_index}
              style={{
                padding: '6px 8px',
                background: '#FFFFFF',
                borderRadius: 4,
                border: '1px solid #CBCBCB',
              }}
            >
              {/* Row: index · model · tokens · status */}
              <div className="flex items-center gap-2 flex-wrap">
                <span
                  style={{
                    fontSize: 10,
                    color: '#FFFFFF',
                    background: '#B8B3D6',
                    padding: '1px 5px',
                    borderRadius: 8,
                    fontWeight: 600,
                    flexShrink: 0,
                  }}
                >
                  #{h.call_index}
                </span>
                {h.model && (
                  <span style={{ fontSize: 10, color: '#4A3F8C', fontWeight: 600 }}>
                    {h.model.replace(/^claude-/, '')}
                  </span>
                )}
                {tokenLabel && (
                  <span style={{ fontSize: 10, color: '#6B7280' }}>
                    {tokenLabel} tokens
                  </span>
                )}
                {h.started_at && (
                  <span style={{ fontSize: 10, color: '#9CA3AF' }}>
                    {fmtDateTime(h.started_at)}
                  </span>
                )}
                <span
                  style={{
                    fontSize: 10,
                    color: h.status === 'active' ? '#F05922' : '#22C55E',
                    marginLeft: 'auto',
                    flexShrink: 0,
                  }}
                >
                  {h.status === 'active' ? '● đang chạy' : '✓ hoàn thành'}
                </span>
              </div>

              {/* Description */}
              {h.description && (
                <p
                  style={{
                    fontSize: 11,
                    color: '#374151',
                    marginTop: 4,
                    lineHeight: 1.4,
                  }}
                >
                  {h.description}
                </p>
              )}

              {/* result_summary (optional — ẩn nếu null/undefined) */}
              {h.result_summary && (
                <div style={{ marginTop: 4 }}>
                  <p
                    className={isExpanded ? undefined : 'line-clamp-3'}
                    style={{
                      fontSize: 10,
                      color: '#6B7280',
                      lineHeight: 1.5,
                      background: '#F9FAFB',
                      padding: '4px 6px',
                      borderRadius: 3,
                      borderLeft: '2px solid #B8B3D6',
                    }}
                  >
                    {h.result_summary}
                  </p>
                  {h.result_full && (
                    <button
                      onClick={() =>
                        setExpandedResult(isExpanded ? null : h.call_index)
                      }
                      style={{
                        fontSize: 10,
                        color: '#4A3F8C',
                        background: 'none',
                        border: 'none',
                        padding: '2px 0 0 0',
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        textDecorationStyle: 'dotted',
                      }}
                    >
                      {isExpanded ? 'Thu gọn ▲' : 'Xem thêm ▼'}
                    </button>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default function PipelineCard({
  sessionId,
  sessionState,
  lastSubagentAt,
}: PipelineCardProps) {
  const [rosterData, setRosterData] = useState<RosterResponse | null>(null)
  const [fetchState, setFetchState] = useState<FetchState>('loading')
  const [selectedHistory, setSelectedHistory] = useState<RosterEntry | null>(null)

  // Fetch chain khi mount hoặc khi lastSubagentAt thay đổi
  useEffect(() => {
    let cancelled = false
    setFetchState('loading')
    setSelectedHistory(null)

    fetch(`/api/sessions/${sessionId}/chain`)
      .then(r => {
        if (!r.ok) throw new Error(`chain fetch ${r.status}`)
        return r.json() as Promise<RosterResponse>
      })
      .then(data => {
        if (cancelled) return
        if (!data.roster || data.roster.length === 0) {
          setFetchState('empty')
          setRosterData(null)
        } else {
          setRosterData(data)
          setFetchState('ready')
        }
      })
      .catch(() => {
        if (!cancelled) setFetchState('error')
      })

    return () => {
      cancelled = true
    }
  }, [sessionId, lastSubagentAt])

  // Fail silently: empty / error → không render gì
  if (fetchState === 'empty' || fetchState === 'error') return null

  const roster = rosterData?.roster ?? []
  const isEnded = sessionState !== 'Running'
  const roleCount = roster.length
  const headerLabel = isEnded
    ? `[${roleCount} vai trò — kết thúc]`
    : `[${roleCount} vai trò]`

  return (
    <div
      className="border-t"
      style={{ borderColor: '#CBCBCB', background: '#FAFAFA', padding: '10px 16px 12px' }}
    >
      {/* Pipeline header */}
      <div
        className="flex items-center gap-1.5 mb-2"
        style={{ opacity: isEnded ? 0.6 : 1 }}
      >
        {/* Chain-link SVG icon 14px */}
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="#4A3F8C"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
        <span className="font-semibold" style={{ fontSize: 12, color: '#251C53' }}>
          Pipeline
        </span>
        {fetchState === 'ready' && (
          <span
            style={{
              fontSize: 11,
              background: '#B8B3D6',
              color: '#251C53',
              padding: '1px 6px',
              borderRadius: 10,
            }}
          >
            {headerLabel}
          </span>
        )}
      </div>

      {/* Roster grid — flex-wrap nhiều hàng */}
      {fetchState === 'loading' ? (
        <PipelineSkeleton />
      ) : (
        <div
          className="flex flex-wrap items-start"
          style={{ opacity: isEnded ? 0.6 : 1, gap: '6px 0', paddingBottom: 4 }}
          aria-label={`Pipeline roster: ${roleCount} vai trò`}
          role="list"
        >
          {roster.map((entry, idx) => (
            <span key={entry.role} className="inline-flex items-center">
              <AgentRosterItem
                entry={entry}
                position={idx + 1}
                onShowHistory={setSelectedHistory}
              />
              {idx < roster.length - 1 && <RosterConnector />}
            </span>
          ))}
        </div>
      )}

      {/* History panel — hiện bên dưới grid khi user chọn */}
      {selectedHistory && (
        <HistoryPanel
          entry={selectedHistory}
          onClose={() => setSelectedHistory(null)}
        />
      )}
    </div>
  )
}
