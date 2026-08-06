/**
 * StepStation — FR-001 Sprint 3 (child of PipelineCard)
 * Một "trạm" trong pipeline: ACTIVE (164px, highlight cam) hoặc DONE (96px, mờ).
 * DONE: hover expand +16px, transition 150ms.
 * ACTIVE: animated pulse dot #F05922.
 */
import type { ChainStep } from '../../types'

interface StepStationProps {
  step: ChainStep
  /** Vị trí 1-indexed dùng cho aria-label */
  position: number
}

export default function StepStation({ step, position }: StepStationProps) {
  const isActive = step.status === 'active'

  const ariaLabel = isActive
    ? `Bước ${position}: ${step.subagent_display} — ${step.description} — đang chạy`
    : `Bước ${position}: ${step.subagent_display} — ${step.description} — đã hoàn thành`

  if (isActive) {
    return (
      <div
        role="listitem"
        aria-label={ariaLabel}
        data-station-active="true"
        className="inline-flex flex-col rounded p-2"
        style={{
          width: 164,
          minHeight: 80,
          flexShrink: 0,
          verticalAlign: 'top',
          background: 'rgba(255, 170, 128, 0.12)',
          border: '1px solid rgba(240, 89, 34, 0.3)',
          borderLeft: '4px solid #F05922',
          borderRadius: 6,
        }}
      >
        {/* Pulse dot + tên vai trò */}
        <div className="flex items-center gap-1.5 mb-1.5">
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
          <span
            className="font-semibold truncate"
            style={{ fontSize: 13, color: '#251C53', lineHeight: 1.3 }}
          >
            {step.subagent_display}
          </span>
        </div>
        {/* Description: max 3 dòng */}
        {step.description && (
          <p
            className="line-clamp-3"
            style={{ fontSize: 12, color: '#1F2937', lineHeight: 1.4, wordBreak: 'break-word' }}
          >
            {step.description}
          </p>
        )}
      </div>
    )
  }

  // DONE station — hover expand inline (pure CSS transition)
  return (
    <div
      role="listitem"
      aria-label={ariaLabel}
      title={step.description}
      className="inline-flex flex-col rounded p-2 cursor-default group"
      style={{
        width: 96,
        minHeight: 80,
        flexShrink: 0,
        verticalAlign: 'top',
        background: '#F5F5F5',
        border: '1px solid #CBCBCB',
        borderRadius: 6,
        opacity: 0.65,
        transition: 'width 150ms ease, opacity 150ms ease, box-shadow 150ms ease',
      }}
      onMouseEnter={(e) => {
        const el = e.currentTarget as HTMLDivElement
        el.style.width = '112px'   // 96 + 16
        el.style.opacity = '1'
        el.style.boxShadow = '0 1px 4px rgba(0,0,0,0.1)'
        el.style.position = 'relative'
        el.style.zIndex = '1'
      }}
      onMouseLeave={(e) => {
        const el = e.currentTarget as HTMLDivElement
        el.style.width = '96px'
        el.style.opacity = '0.65'
        el.style.boxShadow = ''
        el.style.position = ''
        el.style.zIndex = ''
      }}
    >
      {/* Checkmark + tên vai trò */}
      <div className="flex items-center gap-1 mb-1">
        <span style={{ color: '#22C55E', fontSize: 12, fontWeight: 600, lineHeight: 1, flexShrink: 0 }}>✓</span>
        <span
          className="font-semibold truncate"
          style={{ fontSize: 11, color: '#4A3F8C', lineHeight: 1.3 }}
        >
          {step.subagent_display}
        </span>
      </div>
      {/* Description: max 2 dòng */}
      {step.description && (
        <p
          className="line-clamp-2"
          style={{ fontSize: 10, color: '#9CA3AF', lineHeight: 1.4, wordBreak: 'break-word' }}
        >
          {step.description}
        </p>
      )}
    </div>
  )
}
