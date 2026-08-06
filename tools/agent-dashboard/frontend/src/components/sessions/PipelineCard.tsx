/**
 * PipelineCard — FR-001 Sprint 3
 * Hàng ngang các "trạm" (StepStation) thể hiện chain của 1 session cha.
 * - Fetch /api/sessions/{id}/chain khi mount và khi lastSubagentAt thay đổi
 *   (lastSubagentAt = current_subagent?.at → bắt signal WS subagent_changed)
 * - Scroll ngang với fade gradient 2 bên (pointer-events: none)
 * - Auto-scroll tới active station khi steps cập nhật
 * - Fail silently khi API lỗi hoặc steps rỗng
 */
import { useEffect, useRef, useState } from 'react'
import type { ChainResponse, SessionState } from '../../types'
import StepStation from './StepStation'

interface PipelineCardProps {
  sessionId: string
  sessionState: SessionState
  /** Thay đổi khi WS subagent_changed fires → trigger re-fetch chain */
  lastSubagentAt?: string | null
}

type FetchState = 'loading' | 'ready' | 'empty' | 'error'

/** Connector ──▶ giữa 2 station */
function StepConnector() {
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

/** Skeleton loading: 3 pill mờ */
function PipelineSkeleton() {
  return (
    <div className="flex items-center gap-2 py-1" aria-hidden="true">
      {[96, 20, 96, 20, 164].map((w, i) => (
        <span
          key={i}
          className="inline-block rounded animate-pulse"
          style={{
            width: w,
            height: w === 20 ? 12 : 80,
            backgroundColor: '#E5E7EB',
          }}
        />
      ))}
    </div>
  )
}

export default function PipelineCard({ sessionId, sessionState, lastSubagentAt }: PipelineCardProps) {
  const [chainData, setChainData] = useState<ChainResponse | null>(null)
  const [fetchState, setFetchState] = useState<FetchState>('loading')
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  // Fetch chain khi mount hoặc khi lastSubagentAt thay đổi (mới có subagent)
  useEffect(() => {
    let cancelled = false
    setFetchState('loading')

    fetch(`/api/sessions/${sessionId}/chain`)
      .then(r => {
        if (!r.ok) throw new Error(`chain fetch ${r.status}`)
        return r.json() as Promise<ChainResponse>
      })
      .then(data => {
        if (cancelled) return
        if (!data.steps || data.steps.length === 0) {
          setFetchState('empty')
          setChainData(null)
        } else {
          setChainData(data)
          setFetchState('ready')
        }
      })
      .catch(() => {
        if (!cancelled) setFetchState('error')
      })

    return () => { cancelled = true }
  }, [sessionId, lastSubagentAt])

  // Auto-scroll tới active station sau khi steps render
  useEffect(() => {
    if (!scrollContainerRef.current || fetchState !== 'ready') return
    const activeEl = scrollContainerRef.current.querySelector(
      '[data-station-active="true"]'
    ) as HTMLElement | null
    if (activeEl) {
      activeEl.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'end' })
    }
  }, [chainData, fetchState])

  // Fail silently: empty / error → không render gì
  if (fetchState === 'empty' || fetchState === 'error') return null

  const steps = chainData?.steps ?? []
  const isEnded = sessionState !== 'Running'
  const stepCount = steps.length
  const headerLabel = isEnded
    ? `Pipeline [${stepCount} bước — kết thúc]`
    : `Pipeline [${stepCount} bước]`

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
            className="rounded"
            style={{
              fontSize: 11,
              background: '#B8B3D6',
              color: '#251C53',
              padding: '1px 6px',
              borderRadius: 10,
            }}
          >
            {headerLabel.replace('Pipeline ', '')}
          </span>
        )}
      </div>

      {/* Scroll container với fade gradient 2 bên */}
      {fetchState === 'loading' ? (
        <PipelineSkeleton />
      ) : (
        <div className="relative" style={{ opacity: isEnded ? 0.6 : 1 }}>
          {/* Fade left — pointer-events: none để không chặn scroll/click */}
          <div
            className="absolute left-0 top-0 bottom-0 z-10 pointer-events-none"
            style={{
              width: 32,
              background: 'linear-gradient(to right, #FAFAFA, transparent)',
            }}
          />
          {/* Fade right — pointer-events: none */}
          <div
            className="absolute right-0 top-0 bottom-0 z-10 pointer-events-none"
            style={{
              width: 32,
              background: 'linear-gradient(to left, #FAFAFA, transparent)',
            }}
          />

          {/* Stations scroll container */}
          <div
            ref={scrollContainerRef}
            className="overflow-x-auto"
            style={{ paddingBottom: 6 }}
            tabIndex={0}
            aria-label={`Pipeline chain: ${stepCount} bước`}
            role="list"
            onKeyDown={(e) => {
              if (!scrollContainerRef.current) return
              if (e.key === 'ArrowRight') scrollContainerRef.current.scrollBy({ left: 120, behavior: 'smooth' })
              if (e.key === 'ArrowLeft') scrollContainerRef.current.scrollBy({ left: -120, behavior: 'smooth' })
            }}
          >
            {/* align-items: center (KHÔNG stretch) — watch_out */}
            <div className="inline-flex items-center" style={{ whiteSpace: 'nowrap', minWidth: 'max-content' }}>
              {steps.map((step, idx) => (
                <span key={step.step_index} className="inline-flex items-center">
                  <StepStation step={step} position={idx + 1} />
                  {idx < steps.length - 1 && <StepConnector />}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
