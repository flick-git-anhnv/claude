import { useState, useEffect } from 'react'
import { useWsState } from '../contexts/WsContext'
import AgentStatusPanel from '../components/agents/AgentStatusPanel'

export default function AgentStatusPage() {
  const { sessions, wsStatus, watcherAlive } = useWsState()
  const [lastUpdated, setLastUpdated] = useState(new Date())

  // Update "last updated" timestamp whenever sessions change
  useEffect(() => {
    setLastUpdated(new Date())
  }, [sessions])

  const isReconnecting = wsStatus === 'reconnecting'

  return (
    <div>
      <AgentStatusPanel
        sessions={sessions}
        isReconnecting={isReconnecting}
        watcherAlive={watcherAlive}
        lastUpdated={lastUpdated}
      />
    </div>
  )
}
