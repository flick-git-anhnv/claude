import type { WsAppState, WsAction, Session, DeltaEvent } from '../types'

export const initialWsState: WsAppState = {
  wsStatus: 'connecting',
  sessions: [],
  activeAccount: null,
  watcherAlive: true,
}

function applyDelta(sessions: Session[], delta: DeltaEvent): Session[] {
  switch (delta.event) {
    case 'agent_started': {
      const exists = sessions.find(s => s.session_id === delta.session_id)
      if (exists) return sessions
      const newSession: Session = {
        session_id: delta.session_id,
        project: delta.project,
        agent_type: delta.agent_type,
        state: 'Running',
        started_at: delta.started_at,
        last_event_at: delta.started_at,
        token_total: { input: 0, output: 0, cache_creation: 0, cache_read: 0 },
      }
      return [...sessions, newSession]
    }

    case 'agent_update': {
      return sessions.map(s => {
        if (s.session_id !== delta.session_id) return s
        const added = delta.tokens_added ?? {}
        return {
          ...s,
          last_event_at: delta.last_event_at,
          token_total: {
            input: s.token_total.input + (added.input ?? 0),
            output: s.token_total.output + (added.output ?? 0),
            cache_creation: s.token_total.cache_creation + (added.cache_creation ?? 0),
            cache_read: s.token_total.cache_read + (added.cache_read ?? 0),
          },
        }
      })
    }

    case 'agent_state_changed': {
      return sessions.map(s =>
        s.session_id === delta.session_id ? { ...s, state: delta.state } : s
      )
    }

    case 'token_update': {
      return sessions.map(s =>
        s.session_id === delta.session_id
          ? { ...s, token_total: delta.cumulative }
          : s
      )
    }

    default:
      return sessions
  }
}

export function wsReducer(state: WsAppState, action: WsAction): WsAppState {
  switch (action.type) {
    case 'WS_CONNECTING':
      return { ...state, wsStatus: 'connecting' }

    case 'WS_CONNECTED':
      return { ...state, wsStatus: 'connected' }

    case 'WS_DISCONNECTED':
      return { ...state, wsStatus: 'disconnected' }

    case 'WS_RECONNECTING':
      return { ...state, wsStatus: 'reconnecting' }

    case 'SNAPSHOT':
      return {
        ...state,
        wsStatus: 'connected',
        sessions: action.payload.sessions,
        activeAccount: action.payload.active_account,
        watcherAlive: action.payload.watcher_alive,
      }

    case 'DELTA': {
      const delta = action.payload
      if (delta.event === 'account_changed') {
        return {
          ...state,
          activeAccount: {
            id: delta.active_id,
            name: delta.name,
            key_masked: delta.key_masked,
          },
        }
      }
      if (delta.event === 'watcher_status') {
        return { ...state, watcherAlive: delta.alive }
      }
      return { ...state, sessions: applyDelta(state.sessions, delta) }
    }

    default:
      return state
  }
}
