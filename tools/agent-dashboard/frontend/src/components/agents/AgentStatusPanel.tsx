import { useState } from 'react'
import type { Session } from '../../types'
import AgentCard from './AgentCard'

interface AgentStatusPanelProps {
  sessions: Session[]
  isReconnecting: boolean
  watcherAlive: boolean
  lastUpdated: Date
}

const DONE_COLLAPSE_THRESHOLD = 3

export default function AgentStatusPanel({
  sessions,
  isReconnecting,
  watcherAlive,
  lastUpdated,
}: AgentStatusPanelProps) {
  const [showAllDone, setShowAllDone] = useState(false)

  const running = sessions.filter(s => s.state === 'Running')
  const idle    = sessions.filter(s => s.state === 'Idle')
  const done    = sessions.filter(s => s.state === 'Ended')
  const visibleDone = showAllDone ? done : done.slice(0, DONE_COLLAPSE_THRESHOLD)

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
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-h2 text-kz-navy">Agents đang chạy</h2>
        <span className="text-caption text-kz-navy-mid">Cập nhật lúc: {updatedStr}</span>
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

      {/* Running section */}
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

      {/* Idle section */}
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

      {/* Done section */}
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
                ? `Thu gọn ▲`
                : `Xem thêm ${done.length - DONE_COLLAPSE_THRESHOLD} phiên đã kết thúc ▼`}
            </button>
          )}
        </section>
      )}
    </div>
  )
}
