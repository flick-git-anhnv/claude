import { useState } from 'react'
import type { Session, ViewMode } from '../../types'
import { fmtNum } from '../../utils/format'
import AgentCard from './AgentCard'

interface AgentStatusPanelProps {
  sessions: Session[]
  isReconnecting: boolean
  watcherAlive: boolean
  lastUpdated: Date
}

const DONE_COLLAPSE_THRESHOLD = 3
const VIEW_MODE_KEY = 'agent-dashboard.view-mode'

// ── Project slug decoder (Track B, mirrors backend decode_project_slug) ───────

function decodeProjectSlug(slug: string): string {
  if (/^[a-z]--/.test(slug)) {
    const drive = slug[0].toUpperCase() + ':\\'
    const remainder = slug.slice(3)
    return drive + remainder.split('--').join('\\')
  }
  return slug
}

// ── Group sessions by project for 'Theo Dự án' view ──────────────────────────

interface ProjectGroup {
  slug: string
  display: string
  sessions: Session[]
  tokenTotal: number
}

function groupByProject(sessions: Session[]): ProjectGroup[] {
  const map = new Map<string, Session[]>()
  for (const s of sessions) {
    const list = map.get(s.project) ?? []
    list.push(s)
    map.set(s.project, list)
  }
  return Array.from(map.entries()).map(([slug, slist]) => ({
    slug,
    display: decodeProjectSlug(slug),
    sessions: slist,
    tokenTotal: slist.reduce(
      (acc, s) =>
        acc + s.token_total.input + s.token_total.output +
        s.token_total.cache_creation + s.token_total.cache_read,
      0
    ),
  }))
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function AgentStatusPanel({
  sessions,
  isReconnecting,
  watcherAlive,
  lastUpdated,
}: AgentStatusPanelProps) {
  const [showAllDone, setShowAllDone] = useState(false)

  // View mode persisted in localStorage
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    const stored = localStorage.getItem(VIEW_MODE_KEY)
    return (stored === 'by-project' ? 'by-project' : 'by-agent') as ViewMode
  })

  function switchViewMode(mode: ViewMode) {
    setViewMode(mode)
    localStorage.setItem(VIEW_MODE_KEY, mode)
  }

  const updatedStr = lastUpdated.toLocaleTimeString('vi-VN', {
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  })

  if (!watcherAlive) {
    return (
      <div className="p-4 bg-kz-error-bg border-l-4 border-kz-red rounded-sm">
        <p className="text-sm font-semibold text-kz-red">
          ! Không tìm thấy thư mục log
        </p>
        <p className="text-sm text-kz-text mt-1">
          ~/.claude/projects/ chưa tồn tại hoặc không có quyền đọc. Kiểm tra lại cấu hình.
        </p>
      </div>
    )
  }

  return (
    <div>
      {/* Header + view mode toggle */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h2 className="text-h2 text-kz-navy">Agents đang chạy</h2>
        <div className="flex items-center gap-3">
          {/* Pill toggle: Theo Agent / Theo Dự án */}
          <div className="flex rounded-badge border border-kz-gray overflow-hidden text-caption">
            <button
              onClick={() => switchViewMode('by-agent')}
              className={`px-3 py-1 transition-colors ${
                viewMode === 'by-agent'
                  ? 'bg-kz-navy text-white font-semibold'
                  : 'bg-white text-kz-navy-mid hover:bg-gray-50'
              }`}
              aria-pressed={viewMode === 'by-agent'}
            >
              Theo Agent
            </button>
            <button
              onClick={() => switchViewMode('by-project')}
              className={`px-3 py-1 transition-colors ${
                viewMode === 'by-project'
                  ? 'bg-kz-navy text-white font-semibold'
                  : 'bg-white text-kz-navy-mid hover:bg-gray-50'
              }`}
              aria-pressed={viewMode === 'by-project'}
            >
              Theo Dự án
            </button>
          </div>
          <span className="text-caption text-kz-navy-mid hidden sm:inline">
            Cập nhật lúc: {updatedStr}
          </span>
        </div>
      </div>

      {/* Reconnecting banner */}
      {isReconnecting && (
        <div className="mb-4 p-3 bg-kz-warning-bg border-l-4 border-kz-orange-light rounded-sm">
          <p className="text-sm text-kz-text">
            ~ Đang kết nối lại... — Mất kết nối WebSocket, tự động kết nối lại
          </p>
        </div>
      )}

      {/* Empty state */}
      {sessions.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="text-5xl text-kz-navy-light mb-4" aria-hidden="true">⬛</div>
          <h3 className="text-h2 text-kz-navy mb-2">Không có agent nào đang chạy</h3>
          <p className="text-caption text-kz-navy-mid">
            Khởi động Claude Code để bắt đầu theo dõi
          </p>
        </div>
      )}

      {/* ── VIEW: Theo Agent (default) ─────────────────────────────────────── */}
      {viewMode === 'by-agent' && sessions.length > 0 && (
        <ByAgentView
          sessions={sessions}
          showAllDone={showAllDone}
          setShowAllDone={setShowAllDone}
        />
      )}

      {/* ── VIEW: Theo Dự án ─────────────────────────────────────────────── */}
      {viewMode === 'by-project' && sessions.length > 0 && (
        <ByProjectView groups={groupByProject(sessions)} />
      )}
    </div>
  )
}

// ── Sub-view: Theo Agent ──────────────────────────────────────────────────────

interface ByAgentViewProps {
  sessions: Session[]
  showAllDone: boolean
  setShowAllDone: (fn: (v: boolean) => boolean) => void
}

function ByAgentView({ sessions, showAllDone, setShowAllDone }: ByAgentViewProps) {
  const running = sessions.filter(s => s.state === 'Running')
  const idle    = sessions.filter(s => s.state === 'Idle')
  const done    = sessions.filter(s => s.state === 'Ended')
  const visibleDone = showAllDone ? done : done.slice(0, DONE_COLLAPSE_THRESHOLD)

  return (
    <>
      {running.length > 0 && (
        <section className="mb-5" aria-label={`Running agents — ${running.length}`}>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-caption font-semibold text-kz-orange uppercase tracking-wide">
              Running — {running.length}
            </span>
            <div className="flex-1 h-px bg-kz-gray" />
          </div>
          <div className="flex flex-col gap-2">
            {running.map(s => <AgentCard key={s.session_id} session={s} />)}
          </div>
        </section>
      )}

      {idle.length > 0 && (
        <section className="mb-5" aria-label={`Idle agents — ${idle.length}`}>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-caption font-semibold text-kz-orange-light uppercase tracking-wide">
              Idle — {idle.length}
            </span>
            <div className="flex-1 h-px bg-kz-gray" />
          </div>
          <div className="flex flex-col gap-2">
            {idle.map(s => <AgentCard key={s.session_id} session={s} />)}
          </div>
        </section>
      )}

      {done.length > 0 && (
        <section aria-label={`Done agents — ${done.length}`}>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-caption font-semibold text-kz-red uppercase tracking-wide">
              Done — {done.length}
            </span>
            <div className="flex-1 h-px bg-kz-gray" />
          </div>
          <div className="flex flex-col gap-2">
            {visibleDone.map(s => <AgentCard key={s.session_id} session={s} />)}
          </div>
          {done.length > DONE_COLLAPSE_THRESHOLD && (
            <button
              onClick={() => setShowAllDone(v => !v)}
              className="mt-2 text-caption text-kz-navy-mid hover:text-kz-navy underline"
            >
              {showAllDone
                ? 'Thu gọn ▲'
                : `Xem thêm ${done.length - DONE_COLLAPSE_THRESHOLD} phiên đã kết thúc ▼`}
            </button>
          )}
        </section>
      )}
    </>
  )
}

// ── Sub-view: Theo Dự án (accordion with <details> — no animation lib) ───────

interface ByProjectViewProps {
  groups: ProjectGroup[]
}

function ByProjectView({ groups }: ByProjectViewProps) {
  if (groups.length === 0) return null

  return (
    <div className="flex flex-col gap-2">
      {groups.map(group => (
        <details
          key={group.slug}
          className="border border-kz-gray rounded-card overflow-hidden"
        >
          <summary
            className="flex items-center justify-between gap-3 p-3 cursor-pointer
                       hover:bg-gray-50 select-none list-none"
            aria-label={`Dự án: ${group.display}, ${group.sessions.length} sessions`}
          >
            {/* Project name + slug tooltip */}
            <div className="min-w-0">
              <span
                className="font-semibold text-kz-navy truncate block"
                title={`Slug gốc: ${group.slug}`}
              >
                {group.display}
              </span>
              <span className="text-caption text-kz-navy-mid">
                {group.sessions.length} sessions &bull; {fmtNum(group.tokenTotal)} tokens
              </span>
            </div>
            {/* Expand indicator */}
            <span className="text-caption text-kz-navy-mid shrink-0">▼</span>
          </summary>

          {/* Expanded session list */}
          <div className="p-3 pl-5 flex flex-col gap-2 border-t border-kz-gray bg-white">
            {group.sessions.map(s => (
              <AgentCard key={s.session_id} session={s} />
            ))}
          </div>
        </details>
      ))}
    </div>
  )
}
