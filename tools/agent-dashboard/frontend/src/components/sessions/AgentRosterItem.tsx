/**
 * AgentRosterItem — Sprint 4 (replacement for StepStation)
 * Một ô trong lưới roster: hiển thị 1 vai trò agent (gộp N lần gọi).
 *
 * - ACTIVE (cam #F05922, pulse dot): vai trò đang chạy ở lần gọi mới nhất
 * - DONE (mờ, hover expand): vai trò đã hoàn thành
 * - Nếu call_count > 1 → badge "(xN)" + nút "Xem lịch sử"
 * - tokens: null → ẩn hẳn (không hiển thị "0")
 */
import type { RosterEntry } from '../../types'
import { fmtTokensCompact } from '../../utils/format'

interface AgentRosterItemProps {
  entry: RosterEntry
  position: number
  onShowHistory: (entry: RosterEntry) => void
}

/** Rút gọn model slug: "claude-sonnet-4-6" → "sonnet-4-6" */
function shortModel(model: string | null): string | null {
  if (!model) return null
  return model.replace(/^claude-/, '')
}

export default function AgentRosterItem({ entry, position, onShowHistory }: AgentRosterItemProps) {
  const isActive = entry.status === 'active'
  const totalTokens = entry.total_tokens.input + entry.total_tokens.output
  const tokensLabel = fmtTokensCompact(totalTokens)
  const hasHistory = entry.call_count > 1
  const modelShort = shortModel(entry.latest_model)

  const ariaLabel = `${position}. ${entry.display_name}${hasHistory ? ` (${entry.call_count} lần)` : ''} — ${isActive ? 'đang chạy' : 'đã hoàn thành'}`

  if (isActive) {
    return (
      <div
        role="listitem"
        aria-label={ariaLabel}
        data-roster-active="true"
        className="inline-flex flex-col rounded p-2"
        style={{
          width: 196,
          minHeight: 88,
          flexShrink: 0,
          background: 'rgba(255, 170, 128, 0.12)',
          border: '1px solid rgba(240, 89, 34, 0.3)',
          borderLeft: '4px solid #F05922',
          borderRadius: 6,
        }}
      >
        {/* Dòng 1: pulse dot + tên + "(xN)" badge */}
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
          <span
            className="font-semibold truncate flex-1"
            style={{ fontSize: 12, color: '#251C53', lineHeight: 1.3 }}
          >
            {entry.display_name}
          </span>
          {hasHistory && (
            <span
              style={{
                fontSize: 9,
                color: '#F05922',
                fontWeight: 600,
                whiteSpace: 'nowrap',
                background: 'rgba(240, 89, 34, 0.12)',
                padding: '1px 4px',
                borderRadius: 8,
                flexShrink: 0,
              }}
            >
              x{entry.call_count}
            </span>
          )}
        </div>

        {/* Dòng 2: model · description */}
        {(modelShort || entry.latest_description) && (
          <p
            className="line-clamp-2"
            style={{ fontSize: 10, color: '#4A3F8C', lineHeight: 1.4, marginBottom: 4 }}
          >
            {modelShort && (
              <span style={{ fontWeight: 600 }}>{modelShort}</span>
            )}
            {modelShort && entry.latest_description && ' · '}
            {entry.latest_description}
          </p>
        )}

        {/* Dòng 3: tokens (ẩn nếu null/0) */}
        {tokensLabel && (
          <div
            style={{ fontSize: 10, color: '#6B7280', marginTop: 'auto', paddingTop: 2 }}
          >
            {tokensLabel} tokens
          </div>
        )}

        {/* Dòng 4: nút lịch sử */}
        {hasHistory && (
          <button
            onClick={() => onShowHistory(entry)}
            style={{
              fontSize: 10,
              color: '#F05922',
              marginTop: 4,
              textAlign: 'left',
              background: 'none',
              border: 'none',
              padding: 0,
              cursor: 'pointer',
              textDecoration: 'underline',
              textDecorationStyle: 'dotted',
            }}
          >
            Xem lịch sử ▾
          </button>
        )}
      </div>
    )
  }

  /* DONE — hover expand */
  return (
    <div
      role="listitem"
      aria-label={ariaLabel}
      title={entry.latest_description || undefined}
      className="inline-flex flex-col rounded p-2 cursor-default"
      style={{
        width: 148,
        minHeight: 80,
        flexShrink: 0,
        background: '#F5F5F5',
        border: '1px solid #CBCBCB',
        borderRadius: 6,
        opacity: 0.65,
        transition: 'width 150ms ease, opacity 150ms ease, box-shadow 150ms ease',
      }}
      onMouseEnter={e => {
        const el = e.currentTarget as HTMLDivElement
        el.style.width = '168px'
        el.style.opacity = '1'
        el.style.boxShadow = '0 1px 4px rgba(0,0,0,0.1)'
        el.style.position = 'relative'
        el.style.zIndex = '1'
      }}
      onMouseLeave={e => {
        const el = e.currentTarget as HTMLDivElement
        el.style.width = '148px'
        el.style.opacity = '0.65'
        el.style.boxShadow = ''
        el.style.position = ''
        el.style.zIndex = ''
      }}
    >
      {/* Dòng 1: checkmark + tên + "(xN)" badge */}
      <div className="flex items-center gap-1 mb-1">
        <span style={{ color: '#22C55E', fontSize: 11, fontWeight: 600, flexShrink: 0 }}>✓</span>
        <span
          className="font-semibold truncate flex-1"
          style={{ fontSize: 11, color: '#4A3F8C', lineHeight: 1.3 }}
        >
          {entry.display_name}
        </span>
        {hasHistory && (
          <span style={{ fontSize: 9, color: '#B8B3D6', whiteSpace: 'nowrap', flexShrink: 0 }}>
            x{entry.call_count}
          </span>
        )}
      </div>

      {/* Dòng 2: description (2 dòng max) */}
      {entry.latest_description && (
        <p
          className="line-clamp-2"
          style={{ fontSize: 10, color: '#9CA3AF', lineHeight: 1.4, wordBreak: 'break-word' }}
        >
          {entry.latest_description}
        </p>
      )}

      {/* Dòng 3: tokens (ẩn nếu null/0) */}
      {tokensLabel && (
        <div
          style={{ fontSize: 9, color: '#B8B3D6', marginTop: 'auto', paddingTop: 2 }}
        >
          {tokensLabel} tokens
        </div>
      )}

      {/* Dòng 4: nút lịch sử */}
      {hasHistory && (
        <button
          onClick={() => onShowHistory(entry)}
          style={{
            fontSize: 9,
            color: '#4A3F8C',
            marginTop: 4,
            textAlign: 'left',
            background: 'none',
            border: 'none',
            padding: 0,
            cursor: 'pointer',
            textDecoration: 'underline',
            textDecorationStyle: 'dotted',
          }}
        >
          Xem lịch sử
        </button>
      )}
    </div>
  )
}
