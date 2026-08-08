/**
 * AggregatePipelineView — v3 (clean rewrite)
 *
 * Fixes:
 *  1. No more literal \n in JSX
 *  2. Dispatcher node prepended to pipeline when running
 *  3. Active nodes show model + current_activity (same as AgentRosterItem)
 *  4. Pipeline scrolls horizontally (flex-nowrap) — no line wrapping
 *  5. Checkbox "Chỉ đang hoạt động"
 *  6. Node sizes match StepStation (196×100 active, 96×80 done)
 */
import React, { useEffect, useState, useRef } from 'react'
import type {
  AggregateResponse,
  AggregateEntry,
  ActiveAgentEntry,
  ProjectRosterItem,
} from '../../types'
import { fmtTokensCompact, decodeProjectSlug, fmtNum } from '../../utils/format'

const AGGREGATE_POLL_MS = 5_000   // 5s — realtime token updates

interface WindowOption { label: string; value: number }
const WINDOW_OPTIONS: WindowOption[] = [
  { label: 'Tất cả thời gian', value: 0 },
  { label: '7 ngày', value: 7 },
  { label: '30 ngày', value: 30 },
  { label: '90 ngày', value: 90 },
]

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

function shortModel(m: string | null): string | null {
  return m ? m.replace(/^claude-/, '') : null
}

// ─────────────────────────────────────────────────────────────────────────────
// Skeleton
// ─────────────────────────────────────────────────────────────────────────────

function SkeletonCards() {
  return (
    <>
      {[1, 2, 3, 4].map(n => (
        <div
          key={n}
          className="animate-pulse"
          style={{
            background: '#FFFFFF',
            border: '1px solid #E5E7EB',
            borderRadius: 8,
            padding: '14px 16px',
            height: 160,
          }}
        >
          <div style={{ height: 16, width: '55%', background: '#E5E7EB', borderRadius: 4, marginBottom: 12 }} />
          <div style={{ height: 1, background: '#F3F4F6', marginBottom: 12 }} />
          <div style={{ height: 12, background: '#E5E7EB', borderRadius: 3, marginBottom: 8 }} />
          <div style={{ height: 12, background: '#E5E7EB', borderRadius: 3, width: '70%' }} />
        </div>
      ))}
    </>
  )
}

function EmptyStateCard() {
  return (
    <div
      style={{
        gridColumn: '1 / -1',
        padding: '48px 16px',
        textAlign: 'center',
        background: '#FAFAFA',
        border: '1px dashed #CBCBCB',
        borderRadius: 8,
      }}
    >
      <div style={{ fontSize: 32, marginBottom: 12 }}>🤖</div>
      <p style={{ fontSize: 14, fontWeight: 600, color: '#251C53', marginBottom: 4 }}>
        Chưa có dữ liệu thống kê
      </p>
      <p style={{ fontSize: 12, color: '#CBCBCB' }}>
        Dữ liệu xuất hiện khi có agent hoạt động trong khoảng thời gian này
      </p>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Pipeline — Dispatcher node (Navy dark, same as AgentRosterItem DispatcherNode)
// ─────────────────────────────────────────────────────────────────────────────

function DispatcherPipelineNode({ agent }: { agent: ActiveAgentEntry }) {
  const model = shortModel(agent.model)
  const tok = fmtNum(agent.tokens.input + agent.tokens.output)

  return (
    <div
      style={{
        width: 196,
        height: 100,
        flexShrink: 0,
        background: '#251C53',
        border: '4px solid #251C53',
        borderRadius: 6,
        padding: '8px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      <div className="flex items-center gap-1.5 mb-1">
        <span style={{ fontSize: 14, lineHeight: 1, flexShrink: 0 }}>🧠</span>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#FFFFFF', lineHeight: 1.3 }} className="truncate flex-1">
          Claude (Dispatcher)
        </span>
      </div>

      {(model || agent.current_activity) && (
        <p className="line-clamp-2" style={{ fontSize: 10, color: 'rgba(255,255,255,0.7)', lineHeight: 1.4, marginBottom: 4 }}>
          {model && <span style={{ fontWeight: 700, color: '#FFFFFF' }}>{model}</span>}
          {model && agent.current_activity && <span style={{ color: 'rgba(255,255,255,0.5)' }}> : </span>}
          {agent.current_activity}
        </p>
      )}

      <div style={{ marginTop: 'auto' }}>
        <span style={{ fontSize: 10, color: 'rgba(255,255,255,0.6)' }}>{tok} tokens</span>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Pipeline — Active subagent node (orange, pulse — same as ActiveSubagentNode)
// ─────────────────────────────────────────────────────────────────────────────

function ActiveSubagentPipelineNode({
  sub,
  agent,
  instanceCount = 1,
}: {
  sub: ProjectRosterItem
  agent: ActiveAgentEntry
  instanceCount?: number
}) {
  const model = shortModel(agent.model)
  const tok = fmtNum(agent.tokens.input + agent.tokens.output)

  return (
    <div
      style={{
        position: 'relative',
        width: 196,
        height: 100,
        flexShrink: 0,
        background: 'rgba(255,170,128,0.12)',
        border: '1px solid rgba(240,89,34,0.3)',
        borderLeft: '4px solid #F05922',
        borderRadius: 6,
        padding: '8px',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
      }}
    >
      {/* ×N badge for parallel instances */}
      {instanceCount > 1 && (
        <span
          style={{
            position: 'absolute',
            top: 4, right: 6,
            fontSize: 9,
            fontWeight: 700,
            color: '#FFFFFF',
            background: '#F05922',
            borderRadius: 8,
            padding: '1px 5px',
            lineHeight: 1.5,
          }}
        >
          ×{instanceCount}
        </span>
      )}

      {/* Pulse dot + name */}
      <div className="flex items-center gap-1.5 mb-1">
        <span className="relative flex h-2 w-2 shrink-0">
          <span
            className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
            style={{ backgroundColor: '#F05922' }}
          />
          <span
            className="relative inline-flex rounded-full h-2 w-2"
            style={{ backgroundColor: '#F05922' }}
          />
        </span>
        <span style={{ fontSize: 12, fontWeight: 600, color: '#251C53', lineHeight: 1.3 }} className="truncate flex-1">
          {sub.display_name}
        </span>
      </div>

      {/* Model + activity */}
      {(!model && !agent.current_activity) ? (
        <p style={{ fontSize: 10, color: '#F05922', fontStyle: 'italic', lineHeight: 1.4, marginBottom: 4 }}>
          đang khởi tạo…
        </p>
      ) : (
        <p className="line-clamp-2" style={{ fontSize: 10, color: '#4A3F8C', lineHeight: 1.4, marginBottom: 4 }}>
          {model && <span style={{ fontWeight: 700, color: '#251C53' }}>{model}</span>}
          {model && agent.current_activity && <span> : </span>}
          {agent.current_activity}
        </p>
      )}

      <div style={{ marginTop: 'auto' }}>
        <span style={{ fontSize: 10, color: '#6B7280' }}>{tok} tokens</span>
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Pipeline — Done subagent node (gray, faded — same as StepStation DONE)
// ─────────────────────────────────────────────────────────────────────────────

function DoneSubagentPipelineNode({ sub }: { sub: ProjectRosterItem }) {
  const tok = fmtNum(sub.total_tokens.input + sub.total_tokens.output)

  return (
    <div
      title={`${sub.call_count} việc · ${tok} tokens`}
      style={{
        width: 196,
        height: 100,
        flexShrink: 0,
        background: '#F5F5F5',
        border: '1px solid #CBCBCB',
        borderRadius: 6,
        opacity: 0.65,
        padding: '6px 8px',
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        cursor: 'default',
        overflow: 'hidden',
        transition: 'opacity 150ms ease, box-shadow 150ms ease, background 150ms ease, border-color 150ms ease',
      }}
      onMouseEnter={e => {
        const el = e.currentTarget as HTMLDivElement
        el.style.opacity = '1'
        el.style.boxShadow = '0 1px 4px rgba(0,0,0,0.1)'
        el.style.background = '#EBEBEB'
        el.style.borderColor = '#B8B3D6'
      }}
      onMouseLeave={e => {
        const el = e.currentTarget as HTMLDivElement
        el.style.opacity = '0.65'
        el.style.boxShadow = ''
        el.style.background = '#F5F5F5'
        el.style.borderColor = '#CBCBCB'
      }}
    >
      <div className="flex items-center gap-1">
        <span style={{ color: '#22C55E', fontSize: 12, fontWeight: 600, flexShrink: 0 }}>✓</span>
        <span style={{ fontSize: 11, fontWeight: 600, color: '#4A3F8C', lineHeight: 1.3 }} className="truncate">
          {sub.display_name}
        </span>
      </div>
      <span style={{ fontSize: 9, color: '#9CA3AF' }}>{sub.call_count} việc</span>
      <span style={{ fontSize: 9, color: '#9CA3AF' }}>{tok} tokens</span>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Arrow connector
// ─────────────────────────────────────────────────────────────────────────────

function Arrow() {
  return (
    <span
      aria-hidden="true"
      style={{
        color: '#B8B3D6',
        fontSize: 14,
        flexShrink: 0,
        alignSelf: 'center',
        lineHeight: 1,
        userSelect: 'none',
      }}
    >
      →
    </span>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Project Pipeline row (horizontally scrollable)
// ─────────────────────────────────────────────────────────────────────────────

function ProjectPipelineRow({
  roster,
  activeAgents,
}: {
  roster: ProjectRosterItem[]
  activeAgents: ActiveAgentEntry[]
}) {
  const dispatcher = activeAgents.find(a => a.is_dispatcher) ?? null
  const totalNodes = (dispatcher ? 1 : 0) + roster.length

  return (
    <div
      style={{
        borderTop: '1px solid #F3F4F6',
        paddingTop: 10,
      }}
    >
      <span style={{ fontSize: 10, fontWeight: 600, color: '#4A3F8C', display: 'block', marginBottom: 8 }}>
        🔗 Pipeline ({roster.length} vai trò)
      </span>

      {/* Wrapping row — same as PipelineCard session view */}
      <div
        role="list"
        aria-label="Pipeline vai trò"
        style={{
          display: 'flex',
          flexDirection: 'row',
          flexWrap: 'wrap',
          alignItems: 'flex-start',
          gap: '6px 0',
          paddingBottom: 4,
        }}
      >
        {/* Dispatcher node — if it's currently running */}
        {dispatcher && (
          <div role="listitem" className="flex items-center" style={{ flexShrink: 0, gap: 6, display: 'flex', alignItems: 'center' }}>
            <DispatcherPipelineNode agent={dispatcher} />
            {totalNodes > 1 && <Arrow />}
          </div>
        )}

        {/* Subagent nodes — handle multiple concurrent instances of same role */}
        {roster.map((sub, idx) => {
          // All running instances of this role (can be > 1 in parallel workflows)
          const runningInstances = activeAgents.filter(a => !a.is_dispatcher && a.role === sub.role)
          const isActive = runningInstances.length > 0
          // Use instance with highest token count for display info
          const primaryAgent = runningInstances.length > 0
            ? runningInstances.reduce((best, a) =>
                (a.tokens.input + a.tokens.output) > (best.tokens.input + best.tokens.output) ? a : best
              )
            : null
          const isLast = idx === roster.length - 1

          return (
            <div
              key={sub.role}
              role="listitem"
              style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}
            >
              {isActive && primaryAgent ? (
                <ActiveSubagentPipelineNode
                  sub={sub}
                  agent={primaryAgent}
                  instanceCount={runningInstances.length}
                />
              ) : (
                <DoneSubagentPipelineNode sub={sub} />
              )}
              {!isLast && <Arrow />}
            </div>
          )
        })}
      </div>
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// AggregateCard
// ─────────────────────────────────────────────────────────────────────────────

function AggregateCard({
  entry,
  groupBy,
}: {
  entry: AggregateEntry
  groupBy: 'agent' | 'project'
}) {
  const isActive = entry.active_now > 0
  const tokenIn = fmtNum(entry.total_tokens.input)
  const tokenOut = fmtNum(entry.total_tokens.output)
  const totalTokensLabel = fmtNum(entry.total_tokens.input + entry.total_tokens.output)
  const displayName = groupBy === 'project'
    ? decodeProjectSlug(entry.display_name)
    : entry.display_name
  const activeAgents: ActiveAgentEntry[] = entry.active_agents ?? []
  const roster: ProjectRosterItem[] = entry.project_roster ?? []

  return (
    <div
      style={{
        background: '#FFFFFF',
        border: isActive ? '1px solid #FBBF24' : '1px solid #CBCBCB',
        borderLeft: isActive ? '4px solid #F05922' : '4px solid #251C53',
        borderRadius: 8,
        boxShadow: isActive
          ? '0 4px 12px rgba(240,89,34,0.1)'
          : '0 2px 4px rgba(0,0,0,0.02)',
        padding: '14px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}
    >
      {/* ── Header ── */}
      <div className="flex items-start justify-between gap-2">
        <div style={{ flex: 1, minWidth: 0 }}>
          <span
            style={{ fontSize: 13, fontWeight: 600, color: '#251C53', lineHeight: 1.3, display: 'block', wordBreak: 'break-all' }}
            title={groupBy === 'project' ? entry.display_name : undefined}
          >
            {displayName}
          </span>
          <span style={{ fontSize: 10, color: '#6B7280' }}>
            {entry.session_count} sessions
          </span>
        </div>

        {isActive ? (
          <span
            className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-orange text-white shrink-0"
            style={{ gap: 4 }}
          >
            <span
              style={{
                width: 6, height: 6,
                background: '#FFFFFF',
                borderRadius: '50%',
                display: 'inline-block',
                animation: 'pulse 1.5s ease-in-out infinite',
              }}
            />
            {entry.active_now} đang chạy
          </span>
        ) : (
          <span
            className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-red-bg text-kz-red shrink-0"
          >
            ✓ hoàn thành
          </span>
        )}
      </div>

      {/* ── Metrics ── */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '6px 12px',
          fontSize: 12,
          borderTop: '1px dashed #E5E7EB',
          paddingTop: 10,
        }}
      >
        <div>
          <span style={{ color: '#6B7280' }}>Lần gọi: </span>
          <span style={{ fontWeight: 600, color: '#374151' }}>{entry.call_count.toLocaleString('vi-VN')}</span>
        </div>
        {groupBy === 'agent' ? (
          <div>
            <span style={{ color: '#6B7280' }}>Sessions: </span>
            <span style={{ fontWeight: 600, color: '#374151' }}>{entry.session_count.toLocaleString('vi-VN')}</span>
          </div>
        ) : (
          <div>
            <span style={{ color: '#6B7280' }}>Mô hình: </span>
            <span style={{ fontWeight: 600, color: '#374151' }}>
              {entry.latest_model ? shortModel(entry.latest_model) : '—'}
            </span>
          </div>
        )}
        <div style={{ gridColumn: 'span 2' }}>
          <span style={{ color: '#6B7280' }}>Hiệu quả: </span>
          <span style={{ fontWeight: 600, color: '#4A3F8C' }}>{totalTokensLabel} tokens</span>
          <span style={{ fontSize: 10, color: '#9CA3AF', marginLeft: 6 }}>
            ({tokenIn} in · {tokenOut} out)
          </span>
        </div>
      </div>

      {/* ── Project Pipeline (inline, no scroll) ── */}
      {groupBy === 'project' && roster.length > 0 && (
        <ProjectPipelineRow roster={roster} activeAgents={activeAgents} />
      )}
    </div>
  )
}

// ─────────────────────────────────────────────────────────────────────────────
// Main Component
// ─────────────────────────────────────────────────────────────────────────────

export default function AggregatePipelineView() {
  const [data, setData] = useState<AggregateResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [search, setSearch] = useState('')
  const [windowDays, setWindowDays] = useState(0)
  const [groupBy, setGroupBy] = useState<'agent' | 'project'>('agent')
  const [onlyActive, setOnlyActive] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchAggregate() {
      try {
        const params = new URLSearchParams()
        if (windowDays > 0) params.set('window', String(windowDays))
        params.set('group_by', groupBy)
        const r = await fetch(`/api/pipeline/aggregate?${params}`)
        if (!r.ok) throw new Error(`aggregate fetch ${r.status}`)
        const json: AggregateResponse = await r.json()
        if (!cancelled) {
          setData(json)
          setLastUpdated(new Date())
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
    pollRef.current = setInterval(fetchAggregate, AGGREGATE_POLL_MS)

    return () => {
      cancelled = true
      if (pollRef.current) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [windowDays, groupBy])

  const filteredRoster: AggregateEntry[] = (data?.roster ?? []).filter(e => {
    if (onlyActive && e.active_now === 0) return false
    const term = groupBy === 'project' ? decodeProjectSlug(e.display_name) : e.display_name
    return term.toLowerCase().includes(search.toLowerCase())
  })

  const totalSessions = data?.total_sessions ?? 0
  const totalCalls = data?.total_calls ?? 0
  const activeCount = (data?.roster ?? []).filter(e => e.active_now > 0).length

  return (
    <div>
      {/* Controls header */}
      <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
        <div className="flex items-center gap-3">
          <p style={{ fontSize: 13, color: '#251C53', fontWeight: 600, margin: 0 }}>
            Tổng hợp{' '}
            {data && (
              <span style={{ fontWeight: 400, color: '#6B7280' }}>
                — {totalSessions.toLocaleString('vi-VN')} sessions · {totalCalls.toLocaleString('vi-VN')} lượt gọi
              </span>
            )}
          </p>
          {activeCount > 0 && (
            <span
              className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-orange text-white shrink-0"
              style={{ gap: 4 }}
            >
              <span
                style={{
                  width: 6, height: 6,
                  background: '#FFFFFF',
                  borderRadius: '50%',
                  display: 'inline-block',
                  animation: 'pulse 1.5s ease-in-out infinite',
                }}
              />
              {activeCount} đang hoạt động
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          {/* Only-active checkbox */}
          <label
            className="flex items-center gap-1.5"
            style={{ fontSize: 12, color: '#374151', cursor: 'pointer', userSelect: 'none' }}
          >
            <input
              id="agg-only-active"
              type="checkbox"
              checked={onlyActive}
              onChange={e => setOnlyActive(e.target.checked)}
              style={{ accentColor: '#F05922', cursor: 'pointer', width: 14, height: 14 }}
            />
            Chỉ đang hoạt động
          </label>

          {/* Agent / Project toggle */}
          <div
            role="group"
            aria-label="Chế độ gom nhóm"
            style={{
              display: 'inline-flex',
              border: '1px solid #CBCBCB',
              borderRadius: 6,
              overflow: 'hidden',
              background: '#FFFFFF',
            }}
          >
            {(['agent', 'project'] as const).map((mode, i) => (
              <button
                key={mode}
                onClick={() => setGroupBy(mode)}
                aria-pressed={groupBy === mode}
                style={{
                  padding: '0 10px',
                  height: 26,
                  fontSize: 12,
                  fontWeight: groupBy === mode ? 600 : 400,
                  background: groupBy === mode ? '#251C53' : 'transparent',
                  color: groupBy === mode ? '#FFFFFF' : '#4A3F8C',
                  border: 'none',
                  borderLeft: i > 0 ? '1px solid #CBCBCB' : 'none',
                  cursor: 'pointer',
                  transition: 'background 120ms ease, color 120ms ease',
                }}
              >
                {mode === 'agent' ? 'Vai trò' : 'Dự án'}
              </button>
            ))}
          </div>

          <input
            type="text"
            placeholder={groupBy === 'agent' ? 'Tìm vai trò...' : 'Tìm dự án...'}
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              padding: '4px 10px',
              fontSize: 12,
              border: '1px solid #CBCBCB',
              borderRadius: 6,
              outline: 'none',
              color: '#251C53',
              width: 140,
            }}
            aria-label={groupBy === 'agent' ? 'Tìm vai trò' : 'Tìm dự án'}
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

      {/* Error */}
      {error && (
        <div className="flex items-center justify-center py-8 gap-2">
          <span style={{ fontSize: 13, color: '#F05922' }}>⚠ Không lấy được dữ liệu</span>
          <button
            onClick={() => { setLoading(true); setError(false); setWindowDays(w => w) }}
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

      {/* Grid — 1 col for project (full-width rows), multi-col for agent */}
      {!error && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: groupBy === 'project' ? '1fr' : 'repeat(auto-fill, minmax(260px, 1fr))',
            gap: groupBy === 'project' ? 10 : 14,
            marginTop: 8,
          }}
          aria-label={groupBy === 'agent' ? 'Lưới tổng hợp vai trò' : 'Lưới tổng hợp dự án'}
        >
          {loading ? (
            <SkeletonCards />
          ) : filteredRoster.length === 0 ? (
            <EmptyStateCard />
          ) : (
            filteredRoster.map(entry => (
              <AggregateCard key={entry.role} entry={entry} groupBy={groupBy} />
            ))
          )}
        </div>
      )}
    </div>
  )
}
