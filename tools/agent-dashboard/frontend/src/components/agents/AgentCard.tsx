import type { Session, SessionState } from '../../types'
import { fmtTime, fmtRelative, fmtNum, truncate } from '../../utils/format'

interface AgentCardProps {
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

export default function AgentCard({ session }: AgentCardProps) {
  const cfg = STATUS_CONFIG[session.state]
  const { token_total: t } = session

  return (
    <div
      className="border border-kz-gray rounded-card p-4 bg-white hover:shadow-sm transition-shadow"
      role="article"
      aria-label={`Agent ${session.agent_type}, trạng thái ${cfg.label}`}
    >
      {/* Header row */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className={`text-base shrink-0 ${cfg.dot}`} aria-hidden="true">{cfg.dotChar}</span>
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded-badge text-caption font-semibold shrink-0 ${cfg.badge}`}
            aria-label={`Trạng thái: ${cfg.label}`}
          >
            {cfg.badgeText}
          </span>
          <span className="text-sm font-semibold text-kz-navy truncate" title={session.agent_type}>
            {session.agent_type}
          </span>
          <span className="text-caption text-kz-gray hidden sm:inline truncate">
            / {session.project}
          </span>
        </div>
        <div className="text-caption text-kz-navy-mid shrink-0 font-mono">
          {session.state === 'Ended'
            ? `Kết thúc: ${fmtTime(session.last_event_at)}`
            : `Bắt đầu: ${fmtTime(session.started_at)}`}
        </div>
      </div>

      {/* Activity row — subagent badge + description when available, else fallback */}
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
              <span className="text-kz-text truncate" title={session.current_subagent.activity}>
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

      {/* Token row */}
      <div className="flex flex-wrap gap-x-4 gap-y-1 pl-6 text-caption">
        <span>
          <span className="text-kz-navy-mid">IN </span>
          <span
            className="font-mono text-kz-navy font-semibold"
            aria-label={`${fmtNum(t.input)} input tokens`}
          >
            {fmtNum(t.input)}
          </span>
        </span>
        <span>
          <span className="text-kz-navy-mid">OUT </span>
          <span
            className="font-mono text-kz-navy font-semibold"
            aria-label={`${fmtNum(t.output)} output tokens`}
          >
            {fmtNum(t.output)}
          </span>
        </span>
        <span>
          <span className="text-kz-navy-mid">Cache R </span>
          <span
            className="font-mono text-kz-navy font-semibold"
            aria-label={`${fmtNum(t.cache_read)} cache read tokens`}
          >
            {fmtNum(t.cache_read)}
          </span>
        </span>
        <span>
          <span className="text-kz-navy-mid">Cache W </span>
          <span
            className="font-mono text-kz-navy font-semibold"
            aria-label={`${fmtNum(t.cache_creation)} cache write tokens`}
          >
            {fmtNum(t.cache_creation)}
          </span>
        </span>
      </div>
    </div>
  )
}
