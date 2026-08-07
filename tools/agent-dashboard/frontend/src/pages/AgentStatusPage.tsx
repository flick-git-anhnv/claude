/**
 * AgentStatusPage — Sprint 5 FR-005 (nâng cấp)
 * Thêm Segmented Control "Theo Session" | "Tổng hợp" ở đầu trang.
 * - "Theo Session": giữ nguyên AgentStatusPanel + SessionCard/PipelineCard hiện tại
 * - "Tổng hợp": hiển thị AggregatePipelineView (bảng tổng hợp theo vai trò)
 * State lưu localStorage key "pipelineMode" qua hook usePipelineMode.
 */
import { useState, useEffect } from 'react'
import { useWsState } from '../contexts/WsContext'
import AgentStatusPanel from '../components/agents/AgentStatusPanel'
import AggregatePipelineView from '../components/sessions/AggregatePipelineView'
import { usePipelineMode } from '../hooks/usePipelineMode'

export default function AgentStatusPage() {
  const { sessions, wsStatus, watcherAlive } = useWsState()
  const [lastUpdated, setLastUpdated] = useState(new Date())
  const [mode, setMode] = usePipelineMode()

  useEffect(() => {
    setLastUpdated(new Date())
  }, [sessions])

  const isReconnecting = wsStatus === 'reconnecting'

  return (
    <div>
      {/* FR-005: Segmented Control "Theo Session" | "Tổng hợp" */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h2 className="text-h2 text-kz-navy">Agent Status</h2>
        <div
          role="group"
          aria-label="Chế độ hiển thị pipeline"
          style={{
            display: 'inline-flex',
            border: '1px solid #CBCBCB',
            borderRadius: 6,
            overflow: 'hidden',
          }}
        >
          <button
            onClick={() => setMode('session')}
            aria-pressed={mode === 'session'}
            style={{
              padding: '0 12px',
              height: 32,
              fontSize: 13,
              fontWeight: mode === 'session' ? 600 : 400,
              background: mode === 'session' ? '#251C53' : 'transparent',
              color: mode === 'session' ? '#FFFFFF' : '#4A3F8C',
              border: 'none',
              cursor: 'pointer',
              transition: 'background 120ms ease, color 120ms ease',
            }}
          >
            Theo Session
          </button>
          <button
            onClick={() => setMode('aggregate')}
            aria-pressed={mode === 'aggregate'}
            style={{
              padding: '0 12px',
              height: 32,
              fontSize: 13,
              fontWeight: mode === 'aggregate' ? 600 : 400,
              background: mode === 'aggregate' ? '#251C53' : 'transparent',
              color: mode === 'aggregate' ? '#FFFFFF' : '#4A3F8C',
              border: 'none',
              borderLeft: '1px solid #CBCBCB',
              cursor: 'pointer',
              transition: 'background 120ms ease, color 120ms ease',
            }}
          >
            Tổng hợp
          </button>
        </div>
      </div>

      {/* Nội dung thay đổi theo mode — instant, không animation delay */}
      {mode === 'session' ? (
        <AgentStatusPanel
          sessions={sessions}
          isReconnecting={isReconnecting}
          watcherAlive={watcherAlive}
          lastUpdated={lastUpdated}
        />
      ) : (
        <AggregatePipelineView />
      )}
    </div>
  )
}
