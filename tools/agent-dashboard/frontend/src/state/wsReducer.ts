import type { WsAppState, WsAction, Session, DeltaEvent, FailoverActiveInfo, FailoverTriggerReason } from '../types'

/** Chuyển FailoverTriggerReason thành chuỗi hiển thị tiếng Việt ngắn gọn */
function humanReadableReason(reason: FailoverTriggerReason): string {
  switch (reason) {
    case 'http_429':          return '429 detected'
    case 'quota_5h_full':     return 'Quota 5h full'
    case 'quota_7d_full':     return 'Quota 7d full'
    case 'jsonl_rate_limit':  return 'Rate limit (JSONL)'
    case 'api_wide_suspected':return 'API-wide issue'
    case 'manual_override':   return 'Manual activation'
    default:                  return reason
  }
}

export const initialWsState: WsAppState = {
  wsStatus: 'connecting',
  sessions: [],
  activeAccount: null,
  watcherAlive: true,
  chainUpdateTriggers: {},
  // Sprint 7: Failover initial state
  failoverState: 'idle',
  failoverNextRetryAt: null,
  failoverRetryAccount: null,
  failoverRetryAttempt: 0,
  failoverMaxRetries: 3,
  failoverCount24h: 0,
  failoverActiveInfo: null,
  failoverExhaustedIds: {},
  failoverPendingFromId: null,
  failoverPendingReason: null,
  failoverToastNonce: 0,
  failoverToastMessage: '',
  failoverToastType: 'failover',
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

      // ── Sprint 7: Auto-Failover WS events ─────────────────────────────────
      // Pattern: KHÔNG tạo object mới khi giá trị không đổi (anti-flicker).
      // Failover events không đụng sessions[] → không gọi applyDelta cho chúng.

      if (delta.event === 'failover_started') {
        // Lưu from.id + reason tạm để dùng khi failover_completed đến
        const fromId = delta.from?.id ?? null
        const reason = humanReadableReason(delta.reason)
        if (state.failoverState === 'swapping' &&
            state.failoverPendingFromId === fromId) return state  // dedupe
        return {
          ...state,
          failoverState: 'swapping',
          failoverPendingFromId: fromId,
          failoverPendingReason: reason,
        }
      }

      if (delta.event === 'failover_completed') {
        // Xác nhận swap thành công — cập nhật exhausted + activeInfo + toast
        const newExhaustedIds: Record<string, boolean> = state.failoverPendingFromId
          ? { ...state.failoverExhaustedIds, [state.failoverPendingFromId]: true }
          : state.failoverExhaustedIds
        const activeInfo: FailoverActiveInfo = {
          toAccountId: delta.to.id,
          toAccountName: delta.to.name,
          reason: state.failoverPendingReason ?? 'Failover',
          latencyMs: delta.swap_latency_ms,
          triggeredAt: Date.now(),
        }
        const toastMsg = `↺ Đã tự động chuyển sang ${delta.to.name} — ${state.failoverPendingReason ?? 'Failover'}`
        return {
          ...state,
          failoverState: 'monitoring',
          failoverActiveInfo: activeInfo,
          failoverExhaustedIds: newExhaustedIds,
          failoverCount24h: state.failoverCount24h + 1,
          failoverPendingFromId: null,
          failoverPendingReason: null,
          failoverToastNonce: state.failoverToastNonce + 1,
          failoverToastMessage: toastMsg,
          failoverToastType: 'failover',
        }
      }

      if (delta.event === 'failover_failed') {
        const toastMsg = `! Failover thất bại — ${delta.reason}`
        return {
          ...state,
          failoverState: 'monitoring',
          failoverPendingFromId: null,
          failoverPendingReason: null,
          failoverToastNonce: state.failoverToastNonce + 1,
          failoverToastMessage: toastMsg,
          failoverToastType: 'failover-error',
        }
      }

      if (delta.event === 'all_accounts_exhausted') {
        const toastMsg = '! Tất cả account đã hết quota — Hệ thống đang chờ reset'
        return {
          ...state,
          failoverState: 'waiting',
          failoverNextRetryAt: delta.next_retry_at,
          failoverRetryAccount: delta.retry_account,
          failoverRetryAttempt: delta.retry_attempt,
          failoverMaxRetries: delta.max_retries,
          failoverToastNonce: state.failoverToastNonce + 1,
          failoverToastMessage: toastMsg,
          failoverToastType: 'failover-error',
        }
      }

      if (delta.event === 'wait_retry_tick') {
        // FE tự tính countdown từ next_retry_at — không cần xử lý tick
        return state
      }

      if (delta.event === 'retry_success') {
        const toastMsg = `↺ Đã retry thành công với ${delta.account.name}`
        return {
          ...state,
          failoverState: 'idle',
          failoverNextRetryAt: null,
          failoverRetryAccount: null,
          failoverRetryAttempt: 0,
          failoverToastNonce: state.failoverToastNonce + 1,
          failoverToastMessage: toastMsg,
          failoverToastType: 'failover',
        }
      }

      if (delta.event === 'retry_cancelled_by_manual') {
        return {
          ...state,
          failoverState: 'idle',
          failoverNextRetryAt: null,
          failoverRetryAccount: null,
          failoverRetryAttempt: 0,
        }
      }

      if (delta.event === 'failover_paused') {
        return {
          ...state,
          failoverState: 'paused',
        }
      }
      // ── End Sprint 7 failover events ─────────────────────────────────────

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
