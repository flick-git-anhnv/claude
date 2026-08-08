import type { WsAppState, WsAction, Session, DeltaEvent } from '../types'

export const initialWsState: WsAppState = {
  wsStatus: 'connecting',
  sessions: [],
  activeAccount: null,
  watcherAlive: true,
  chainUpdateTriggers: {},
}

/**
 * Fix vấn đề 4 (flicker): reducer PHẢI trả về CÙNG identity của mảng sessions
 * khi delta không tác động lên session nào. Nếu luôn tạo mảng mới ngay cả khi
 * không có session_id khớp (VD: subagent update, session không tồn tại) →
 * mọi consumer của WsContext re-render vô ích mỗi lần WS event → gây flicker
 * (skeleton chớp, animate-pulse restart, polling tick trùng).
 */
function mapIfChanged(
  sessions: Session[],
  session_id: string,
  updater: (s: Session) => Session,
): Session[] {
  const idx = sessions.findIndex(s => s.session_id === session_id)
  if (idx < 0) return sessions   // không match → giữ nguyên reference
  const next = updater(sessions[idx])
  if (next === sessions[idx]) return sessions
  const copy = sessions.slice()
  copy[idx] = next
  return copy
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
        current_subagent: null,
      }
      return [...sessions, newSession]
    }

    case 'agent_update': {
      return mapIfChanged(sessions, delta.session_id, s => {
        const added = delta.tokens_added ?? {}
        const addI = added.input ?? 0
        const addO = added.output ?? 0
        const addCC = added.cache_creation ?? 0
        const addCR = added.cache_read ?? 0
        // Nếu không có token mới VÀ last_event_at không đổi → bỏ qua
        if (addI === 0 && addO === 0 && addCC === 0 && addCR === 0 && s.last_event_at === delta.last_event_at) {
          return s
        }
        return {
          ...s,
          last_event_at: delta.last_event_at,
          token_total: {
            input: s.token_total.input + addI,
            output: s.token_total.output + addO,
            cache_creation: s.token_total.cache_creation + addCC,
            cache_read: s.token_total.cache_read + addCR,
          },
        }
      })
    }

    case 'agent_state_changed':
      return mapIfChanged(sessions, delta.session_id, s =>
        s.state === delta.state ? s : { ...s, state: delta.state }
      )

    case 'token_update':
      return mapIfChanged(sessions, delta.session_id, s => ({ ...s, token_total: delta.cumulative }))

    // Track B: subagent role + activity update
    case 'subagent_changed':
      return mapIfChanged(sessions, delta.session_id, s => ({ ...s, current_subagent: delta.subagent }))

    // Sprint 3: session title update (ai_title or user_text)
    case 'session_title_changed':
      return mapIfChanged(sessions, delta.session_id, s =>
        s.title === delta.title ? s : { ...s, title: delta.title }
      )

    // Sprint 3: context window snapshot update
    case 'session_context_updated':
      return mapIfChanged(sessions, delta.session_id, s => ({
        ...s,
        context_pct: delta.context_pct,
        last_input_total: delta.last_input_total,
        max_context: delta.max_context,
      }))

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
        if (!delta.active_id) {
          return {
            ...state,
            activeAccount: null,
          }
        }
        return {
          ...state,
          activeAccount: {
            id: delta.active_id,
            name: delta.name!,
            kind: delta.kind!,
            key_masked: delta.key_masked ?? undefined,
            oauth_masked: delta.oauth_masked ?? undefined,
          },
        }
      }
      if (delta.event === 'watcher_status') {
        return { ...state, watcherAlive: delta.alive }
      }
      // Sprint 5 BUG-004: chain_updated → tăng counter cho parent session_id
      // PipelineCard dùng counter này làm dep trong useEffect để refetch /chain
      if (delta.event === 'chain_updated') {
        const prev = state.chainUpdateTriggers[delta.session_id] ?? 0
        return {
          ...state,
          chainUpdateTriggers: {
            ...state.chainUpdateTriggers,
            [delta.session_id]: prev + 1,
          },
        }
      }
      const nextSessions = applyDelta(state.sessions, delta)
      // Fix vấn đề 4: nếu applyDelta trả CÙNG identity mảng sessions →
      // state không đổi, giữ nguyên reference để tất cả consumers không re-render.
      if (nextSessions === state.sessions) return state
      return { ...state, sessions: nextSessions }
    }

    default:
      return state
  }
}
