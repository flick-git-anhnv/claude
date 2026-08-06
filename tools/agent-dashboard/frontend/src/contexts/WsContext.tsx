import { createContext, useContext, useEffect, useReducer, useRef } from 'react'
import { wsReducer, initialWsState } from '../state/wsReducer'
import type { WsAppState, WsAction, WsSnapshot, DeltaEvent } from '../types'
import { MockWebSocket } from '../mocks/mockWebSocket'
import { isMock } from '../api/interceptor'

interface WsContextValue {
  state: WsAppState
  dispatch: React.Dispatch<WsAction>
}

const WsContext = createContext<WsContextValue | null>(null)

// Exponential backoff delays (ms): 1s, 2s, 5s, 10s
const BACKOFF = [1000, 2000, 5000, 10000]

interface RawWsMessage {
  type: 'snapshot' | 'delta' | 'pong'
  ts: string
  payload: unknown
}

export function WsProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(wsReducer, initialWsState)
  const wsRef = useRef<WebSocket | MockWebSocket | null>(null)
  const retryCountRef = useRef(0)
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const unmountedRef = useRef(false)

  useEffect(() => {
    unmountedRef.current = false

    function connect() {
      if (unmountedRef.current) return
      dispatch({ type: 'WS_CONNECTING' })

      const wsUrl = import.meta.env.VITE_WS_URL ?? 'ws://localhost:7770/ws'
      const ws: WebSocket | MockWebSocket = isMock
        ? new MockWebSocket(wsUrl)
        : new WebSocket(wsUrl)

      wsRef.current = ws
      let pingTimer: ReturnType<typeof setInterval> | null = null

      ws.onopen = () => {
        if (unmountedRef.current) return
        retryCountRef.current = 0
        dispatch({ type: 'WS_CONNECTED' })
        // Ping every 30s
        pingTimer = setInterval(() => {
          if (ws.readyState === 1) ws.send(JSON.stringify({ type: 'ping' }))
        }, 30000)
      }

      ws.onmessage = (evt: MessageEvent) => {
        if (unmountedRef.current) return
        try {
          const msg = JSON.parse(evt.data as string) as RawWsMessage
          if (msg.type === 'snapshot') {
            dispatch({ type: 'SNAPSHOT', payload: msg.payload as WsSnapshot })
          } else if (msg.type === 'delta') {
            dispatch({ type: 'DELTA', payload: msg.payload as DeltaEvent })
          }
          // 'pong' silently ignored
        } catch {
          console.warn('[WS] Failed to parse message', evt.data)
        }
      }

      ws.onerror = () => {
        console.warn('[WS] Connection error')
      }

      ws.onclose = () => {
        if (pingTimer) clearInterval(pingTimer)
        if (unmountedRef.current) return
        wsRef.current = null
        const delay = BACKOFF[Math.min(retryCountRef.current, BACKOFF.length - 1)]
        retryCountRef.current += 1
        dispatch({ type: 'WS_RECONNECTING' })
        retryTimerRef.current = setTimeout(() => {
          if (!unmountedRef.current) connect()
        }, delay)
      }
    }

    connect()

    return () => {
      unmountedRef.current = true
      if (retryTimerRef.current) clearTimeout(retryTimerRef.current)
      if (wsRef.current) {
        wsRef.current.onclose = null // prevent reconnect loop on intentional unmount
        wsRef.current.close()
        wsRef.current = null
      }
    }
  }, [])

  return (
    <WsContext.Provider value={{ state, dispatch }}>
      {children}
    </WsContext.Provider>
  )
}

export function useWs(): WsContextValue {
  const ctx = useContext(WsContext)
  if (!ctx) throw new Error('useWs must be used within WsProvider')
  return ctx
}

export function useWsState(): WsAppState {
  return useWs().state
}
