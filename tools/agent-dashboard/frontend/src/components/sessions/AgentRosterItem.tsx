/**
 * AgentRosterItem — Sprint 5 (nâng cấp từ Sprint 4)
 *
 * Thay đổi Sprint 5:
 * - FR-004: Dispatcher node (`is_dispatcher=true`) → style Navy #251C53, icon 🧠
 * - BUG-004: Khi ACTIVE + !model → "đang khởi tạo…" (italic, cam)
 *            Khi ACTIVE + tokens=0 → "— tokens" thay vì ẩn hẳn
 * - BUG-005: hasHistory = `call_count >= 1 && history.length > 0` (sửa từ `> 1`)
 *
 * FR-006-dispatcher (sau Sprint 5):
 * - Dispatcher cũng có nút "Xem lịch sử" khi backend trả về history[] không rỗng
 *   (history = các tool call top-level của Dispatcher: Read, Write, Bash, v.v.)
 *
 * Layout per entry (196×100px):
 * - Dòng 1: indicator + tên + "(xN)" badge
 * - Dòng 2: model (bold) : description  hoặc  "đang khởi tạo…" (BUG-004)
 * - Dòng 3: tokens + "Xem lịch sử" (nếu hasHistory)
 */
import type { RosterEntry } from '../../types'
import { fmtTokensCompact, fmtTokenDisplay, fmtModelShort } from '../../utils/format'

interface AgentRosterItemProps {
  entry: RosterEntry
  position: number
  onShowHistory: (entry: RosterEntry) => void
}

// ── Dispatcher node (FR-004, FR-006-dispatcher) ──────────────────────────────

function DispatcherNode({
  entry,
  position,
  onShowHistory,
}: {
  entry: RosterEntry
  position: number
  onShowHistory: (entry: RosterEntry) => void
}) {
  const isActive = entry.status === 'active'
  const modelShort = fmtModelShort(entry.latest_model)
  const totalTokens = entry.total_tokens.input + entry.total_tokens.output
  const tokensLabel = totalTokens > 0 ? fmtTokensCompact(totalTokens) : null
  // FR-006-dispatcher: show history button when backend populates history[]
  const hasHistory = entry.history.length > 0

  // ACTIVE: nền Navy đặc, chữ trắng
  // DONE: nền Navy nhạt, chữ Navy, opacity 0.65
  const bgColor = isActive ? '#251C53' : 'rgba(37,28,83,0.08)'
  const textColor = isActive ? '#FFFFFF' : '#251C53'
  const textMutedColor = isActive ? 'rgba(255,255,255,0.7)' : '#6B7280'
  const tokenColor = isActive ? 'rgba(255,255,255,0.6)' : '#9CA3AF'

  return (
    <div
      role="listitem"
      aria-label={`${position}. Claude (Dispatcher) — phiên chính — ${isActive ? 'đang chạy' : 'đã hoàn thành'}`}
      data-dispatcher="true"
      className="inline-flex flex-col rounded p-2"
      style={{
        width: 196,
        height: 100,
        flexShrink: 0,
        overflow: 'hidden',
        background: bgColor,
        border: '4px solid #251C53',
        borderRadius: 6,
        opacity: isActive ? 1 : 0.65,
        transition: 'opacity 150ms ease, box-shadow 150ms ease',
        cursor: isActive ? 'default' : 'default',
      }}
      onMouseEnter={isActive ? undefined : e => {
        const el = e.currentTarget as HTMLDivElement
        el.style.opacity = '1'
        el.style.boxShadow = '0 1px 4px rgba(37,28,83,0.2)'
      }}
      onMouseLeave={isActive ? undefined : e => {
        const el = e.currentTarget as HTMLDivElement
        el.style.opacity = '0.65'
        el.style.boxShadow = ''
      }}
    >
      {/* Dòng 1: 🧠 icon (tĩnh, không pulse) + tên */}
      <div className="flex items-center gap-1.5 mb-1">
        <span style={{ fontSize: 14, flexShrink: 0, lineHeight: 1 }}>🧠</span>
        <span
          className="font-semibold truncate flex-1"
          style={{ fontSize: 12, color: textColor, lineHeight: 1.3 }}
        >
          Claude (Dispatcher)
        </span>
      </div>

      {/* Dòng 2: model : description — ẩn nếu cả 2 đều null */}
      {(modelShort || entry.latest_description) && (
        <p
          className="line-clamp-2"
          style={{ fontSize: 10, color: textMutedColor, lineHeight: 1.4, marginBottom: 4 }}
        >
          {modelShort && (
            <span style={{ fontWeight: 700, color: isActive ? '#FFFFFF' : '#4A3F8C' }}>
              {modelShort}
            </span>
          )}
          {modelShort && entry.latest_description && (
            <span style={{ fontWeight: 400, color: textMutedColor }}> : </span>
          )}
          {entry.latest_description}
        </p>
      )}

      {/* Dòng 3: tokens + "Xem lịch sử" (FR-006-dispatcher) */}
      {(tokensLabel || hasHistory) && (
        <div
          className="flex items-center"
          style={{ marginTop: 'auto', paddingTop: 2, gap: 4 }}
        >
          <span style={{ fontSize: 10, color: tokenColor, flex: 1 }}>
            {tokensLabel ? `${tokensLabel} tokens` : ''}
          </span>
          {hasHistory && (
            <button
              onClick={() => onShowHistory(entry)}
              style={{
                fontSize: 9,
                color: isActive ? 'rgba(255,255,255,0.8)' : '#4A3F8C',
                background: 'none',
                border: 'none',
                padding: 0,
                cursor: 'pointer',
                textDecoration: 'underline',
                textDecorationStyle: 'dotted',
                flexShrink: 0,
              }}
            >
              Xem lịch sử
            </button>
          )}
        </div>
      )}
    </div>
  )
}

// ── Subagent node (ACTIVE) ────────────────────────────────────────────────────

function ActiveSubagentNode({
  entry,
  position,
  hasHistory,
  onShowHistory,
}: {
  entry: RosterEntry
  position: number
  hasHistory: boolean
  onShowHistory: (e: RosterEntry) => void
}) {
  const totalTokens = entry.total_tokens.input + entry.total_tokens.output
  const modelShort = fmtModelShort(entry.latest_model)

  // BUG-004: ACTIVE + tokens=0 → "— tokens" thay vì ẩn
  const tokensLabel = totalTokens === 0 ? '— tokens' : `${fmtTokensCompact(totalTokens)} tokens`
  const showTokensRow = hasHistory || totalTokens === 0 || totalTokens > 0

  const ariaLabel = `${position}. ${entry.display_name}${hasHistory ? ` (${entry.call_count} lần)` : ''} — đang chạy`

  return (
    <div
      role="listitem"
      aria-label={ariaLabel}
      data-roster-active="true"
      className="inline-flex flex-col rounded p-2"
      style={{
        width: 196,
        height: 100,
        flexShrink: 0,
        overflow: 'hidden',
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
        {hasHistory && entry.call_count > 1 && (
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

      {/* Dòng 2: model : description  |  BUG-004 fallback "đang khởi tạo…" */}
      {!modelShort && !entry.latest_description ? (
        // BUG-004: không có model VÀ không có description → "đang khởi tạo…"
        <p style={{ fontSize: 10, color: '#F05922', fontStyle: 'italic', lineHeight: 1.4, marginBottom: 4 }}>
          đang khởi tạo…
        </p>
      ) : (
        (modelShort || entry.latest_description) && (
          <p
            className="line-clamp-2"
            style={{ fontSize: 10, color: '#4A3F8C', lineHeight: 1.4, marginBottom: 4 }}
          >
            {modelShort && (
              <span style={{ fontWeight: 700, color: '#251C53' }}>{modelShort}</span>
            )}
            {modelShort && entry.latest_description && (
              <span style={{ fontWeight: 400, color: '#251C53' }}> : </span>
            )}
            {entry.latest_description}
          </p>
        )
      )}

      {/* Dòng 3: tokens + "Xem lịch sử" — BUG-004: luôn hiện "— tokens" khi active */}
      {showTokensRow && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            marginTop: 'auto',
            paddingTop: 2,
          }}
        >
          <span style={{ fontSize: 10, color: '#6B7280', flex: 1 }}>
            {tokensLabel}
          </span>
          {hasHistory && (
            <button
              onClick={() => onShowHistory(entry)}
              style={{
                fontSize: 10,
                color: '#F05922',
                background: 'none',
                border: 'none',
                padding: 0,
                cursor: 'pointer',
                textDecoration: 'underline',
                textDecorationStyle: 'dotted',
                flexShrink: 0,
              }}
            >
              Xem lịch sử ▾
            </button>
          )}
        </div>
      )}
    </div>
  )
}

// ── Subagent node (DONE) ──────────────────────────────────────────────────────

function DoneSubagentNode({
  entry,
  position,
  hasHistory,
  onShowHistory,
}: {
  entry: RosterEntry
  position: number
  hasHistory: boolean
  onShowHistory: (e: RosterEntry) => void
}) {
  const totalTokens = entry.total_tokens.input + entry.total_tokens.output
  // Bug 3: dùng fmtTokenDisplay để luôn hiện "— tokens" khi zero (không bao giờ để trống)
  const tokensLabel = fmtTokenDisplay(totalTokens)
  const modelShort = fmtModelShort(entry.latest_model)

  const ariaLabel = `${position}. ${entry.display_name}${hasHistory ? ` (${entry.call_count} lần)` : ''} — đã hoàn thành`

  return (
    <div
      role="listitem"
      aria-label={ariaLabel}
      title={entry.latest_description || undefined}
      className="inline-flex flex-col rounded p-2 cursor-default"
      style={{
        width: 196,
        height: 100,
        flexShrink: 0,
        overflow: 'hidden',
        background: '#F5F5F5',
        border: '1px solid #CBCBCB',
        borderRadius: 6,
        opacity: 0.65,
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
      {/* Dòng 1: checkmark + tên + "(xN)" badge */}
      <div className="flex items-center gap-1 mb-1">
        <span style={{ color: '#22C55E', fontSize: 11, fontWeight: 600, flexShrink: 0 }}>✓</span>
        <span
          className="font-semibold truncate flex-1"
          style={{ fontSize: 11, color: '#4A3F8C', lineHeight: 1.3 }}
        >
          {entry.display_name}
        </span>
        {hasHistory && entry.call_count > 1 && (
          <span style={{ fontSize: 9, color: '#B8B3D6', whiteSpace: 'nowrap', flexShrink: 0 }}>
            x{entry.call_count}
          </span>
        )}
      </div>

      {/* Dòng 2: model : description */}
      {(modelShort || entry.latest_description) && (
        <p
          className="line-clamp-2"
          style={{ fontSize: 10, color: '#9CA3AF', lineHeight: 1.4, wordBreak: 'break-word' }}
        >
          {modelShort && (
            <span style={{ fontWeight: 700, color: '#4A3F8C' }}>{modelShort}</span>
          )}
          {modelShort && entry.latest_description && (
            <span style={{ fontWeight: 400, color: '#6B7280' }}> : </span>
          )}
          {entry.latest_description}
        </p>
      )}

      {/* Dòng 3: tokens (luôn hiện via fmtTokenDisplay) + "Xem lịch sử" */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          marginTop: 'auto',
          paddingTop: 2,
        }}
      >
        <span style={{ fontSize: 9, color: '#B8B3D6', flex: 1 }}>
          {tokensLabel}
        </span>
        {hasHistory && (
          <button
            onClick={() => onShowHistory(entry)}
            style={{
              fontSize: 9,
              color: '#4A3F8C',
              background: 'none',
              border: 'none',
              padding: 0,
              cursor: 'pointer',
              textDecoration: 'underline',
              textDecorationStyle: 'dotted',
              flexShrink: 0,
            }}
          >
            Xem lịch sử
          </button>
        )}
      </div>
    </div>
  )
}

// ── Main export ───────────────────────────────────────────────────────────────

export default function AgentRosterItem({ entry, position, onShowHistory }: AgentRosterItemProps) {
  const isActive = entry.status === 'active'

  // FR-006-dispatcher: nút "Xem lịch sử" hiện khi history[] không rỗng — kể cả Dispatcher.
  // Trước (Sprint 5): !is_dispatcher && call_count >= 1 → Dispatcher không bao giờ có nút.
  // Sau (FR-006-dispatcher): history.length > 0 → Dispatcher cũng có nút khi backend trả dữ liệu.
  //
  // Bug 1 (regression FR-006-dispatcher): đổi điều kiện sang `history.length > 0` cho TẤT CẢ
  // đã làm mất nút "Xem lịch sử" của role thường — mock data có history:[] nhưng call_count:1.
  // Fix: Dispatcher vẫn dùng history.length (call_count dispatcher không có ý nghĩa),
  //      regular roles dùng call_count >= 1 (history[] chắc chắn có nội dung vì call đã xảy ra).
  const hasHistory = entry.is_dispatcher
    ? entry.history.length > 0
    : entry.call_count >= 1

  // FR-004: Dispatcher → render riêng với style Navy
  if (entry.is_dispatcher) {
    return <DispatcherNode entry={entry} position={position} onShowHistory={onShowHistory} />
  }

  // Subagent bình thường
  if (isActive) {
    return (
      <ActiveSubagentNode
        entry={entry}
        position={position}
        hasHistory={hasHistory}
        onShowHistory={onShowHistory}
      />
    )
  }

  return (
    <DoneSubagentNode
      entry={entry}
      position={position}
      hasHistory={hasHistory}
      onShowHistory={onShowHistory}
    />
  )
}
