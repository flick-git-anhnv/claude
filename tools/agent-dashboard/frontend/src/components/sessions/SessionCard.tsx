/**
 * SessionCard v2 — Sprint 3 (nâng cấp từ AgentCard)
 * FR-003: Dòng tiêu đề session (ai_title / user_text / session_id fallback)
 * FR-002: ContextBadge cuối dòng token
 * FR-001: PipelineCard bên dưới token row (chỉ render khi có chain)
 *
 * Backward-compatible: session không có title/context_pct/chain → giữ layout v1.
 */
import type { Session, SessionState } from '../../types'
import { fmtTime, fmtRelative, fmtNum, truncate } from '../../utils/format'
import ContextBadge from './ContextBadge'
import PipelineCard from './PipelineCard'

interface SessionCardProps {
  session: Session
}

interface BadgeConfig {
  dot: string
  dotChar: string
  badge: string
  badgeText: string
  label: string
}

const STATUS_CONFIG: Record<SessionState, BadgeConfig> = {
  Running: {
    dot: 'text-kz-orange',
    dotChar: '●',
    badge: 'bg-kz-orange text-white',
    badgeText: 'RUNNING',
    label: 'Đang chạy',
  },
  Idle: {
    dot: 'text-kz-orange-light',
    dotChar: '○',
    badge: 'bg-kz-orange-light text-kz-navy',
    badgeText: 'IDLE',
    label: 'Không hoạt động',
  },
  Ended: {
    dot: 'text-kz-red',
    dotChar: '✕',
    badge: 'bg-kz-red-bg text-kz-red',
    badgeText: 'DONE',
    label: 'Đã kết thúc',
  },
}

/** FR-003: Resolve title hiển thị.
 *  - title string    → dùng trực tiếp (từ ai_title hoặc user_text)
 *  - title null/undefined → trả null (không hiển thị dòng tiêu đề)
 */
function resolveTitle(title: string | null | undefined): string | null {
  if (title === null || title === undefined) return null
  const trimmed = title.trim()
  return trimmed.length > 0 ? trimmed : null
}

export default function SessionCard({ session }: SessionCardProps) {
  const cfg = STATUS_CONFIG[session.state]
  const { token_total: t } = session
  const isDone = session.state === 'Ended'

  const displayTitle = resolveTitle(session.title)

  return (
    <div
      className="border border-kz-gray rounded-card bg-white hover:shadow-sm transition-shadow overflow-hidden"
      role="article"
      aria-label={`Session ${session.agent_type}, trạng thái ${cfg.label}`}
    >
      {/* ── Phần trên: header + title + activity + tokens ─────────────────── */}
      <div className="p-4">
        {/* Header row: dot + status badge + agent type + timestamp */}
        <div className="flex items-center justify-between gap-2 mb-1">
          <div className="flex items-center gap-2 min-w-0">
            <span className={`text-base shrink-0 ${cfg.dot}`} aria-hidden="true">
              {cfg.dotChar}
            </span>
            <span
              className={`inline-flex items-center px-2 py-0.5 rounded-badge text-caption font-semibold shrink-0 ${cfg.badge}`}
              aria-label={`Trạng thái: ${cfg.label}`}
            >
              {cfg.badgeText}
            </span>
            <span
              className="text-sm font-semibold text-kz-navy truncate"
              title={session.agent_type}
            >
              {session.agent_type}
            </span>
            <span className="text-caption text-kz-gray hidden sm:inline truncate">
              / {session.project}
            </span>
          </div>
          <div className="text-caption text-kz-navy-mid shrink-0 font-mono">
            {isDone
              ? `Kết thúc: ${fmtTime(session.last_event_at)}`
              : `Bắt đầu: ${fmtTime(session.started_at)}`}
          </div>
        </div>

        {/* FR-003: Dòng tiêu đề session — CHỈ render khi title không null */}
        {displayTitle !== null && (
          <p
            className="truncate mb-1 pl-6"
            title={displayTitle}
            style={{ fontSize: 13, color: '#4A3F8C', lineHeight: 1.4 }}
          >
            {truncate(displayTitle, 80)}
          </p>
        )}

        {/* Activity row — subagent badge + description / fallback */}
        <div className="text-sm text-kz-text mb-3 pl-6">
          {session.current_subagent ? (
            <div className="flex items-center gap-2 flex-wrap">
              <span
                className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-navy text-white shrink-0"
                aria-label={`Vai trò: ${session.current_subagent.display_name}`}
              >
                {session.current_subagent.display_name}
              </span>
              {session.current_subagent.activity && (
                <span
                  className="text-kz-text truncate"
                  title={session.current_subagent.activity}
                >
                  {truncate(session.current_subagent.activity, 80)}
                </span>
              )}
              <span className="text-caption text-kz-navy-mid shrink-0">
                {fmtRelative(session.current_subagent.at)}
              </span>
            </div>
          ) : (
            <>
              <span className="text-caption text-kz-navy-mid">Hoạt động cuối: </span>
              {fmtRelative(session.last_event_at)}
              {session.state === 'Running' && (
                <span className="ml-2 text-caption text-kz-navy-mid">
                  — session {truncate(session.session_id, 20)}
                </span>
              )}
            </>
          )}
        </div>

        {/* Token row + FR-002: ContextBadge cuối hàng */}
        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 pl-6 text-caption">
          <span>
            <span className="text-kz-navy-mid">IN </span>
            <span className="font-mono text-kz-navy font-semibold" aria-label={`${fmtNum(t.input)} input tokens`}>
              {fmtNum(t.input)}
            </span>
          </span>
          <span>
            <span className="text-kz-navy-mid">OUT </span>
            <span className="font-mono text-kz-navy font-semibold" aria-label={`${fmtNum(t.output)} output tokens`}>
              {fmtNum(t.output)}
            </span>
          </span>
          <span>
            <span className="text-kz-navy-mid">Cache R </span>
            <span className="font-mono text-kz-navy font-semibold" aria-label={`${fmtNum(t.cache_read)} cache read tokens`}>
              {fmtNum(t.cache_read)}
            </span>
          </span>
          <span>
            <span className="text-kz-navy-mid">Cache W </span>
            <span className="font-mono text-kz-navy font-semibold" aria-label={`${fmtNum(t.cache_creation)} cache write tokens`}>
              {fmtNum(t.cache_creation)}
            </span>
          </span>
          {/* FR-002: ContextBadge — ẩn khi context_pct === 0 hoặc null */}
          <ContextBadge
            contextPct={session.context_pct}
            lastInputTotal={session.last_input_total}
            maxContext={session.max_context}
            sessionDone={isDone}
          />
        </div>
      </div>

      {/* FR-001: PipelineCard — chỉ render khi session có chain (fetch tự quyết định) */}
      <PipelineCard
        sessionId={session.session_id}
        sessionState={session.state}
        lastSubagentAt={session.current_subagent?.at ?? null}
      />
    </div>
  )
}
