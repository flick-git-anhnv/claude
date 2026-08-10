// ─── Session & Agent types ────────────────────────────────────────────────────

export type SessionState = 'Running' | 'Idle' | 'Ended';
export type WsStatus = 'connecting' | 'connected' | 'reconnecting' | 'disconnected';
export type RangeFilter = '7d' | '30d' | '12w' | '6m';
export type ViewMode = 'by-agent' | 'by-project';
export type PipelineMode = 'session' | 'aggregate';

// Sprint 3 — Chain types (FR-001) — kept for backward-compat, superseded by Sprint 4 Roster
export interface ChainStep {
  step_index: number;
  subagent_type: string | null;
  subagent_display: string | null;
  description: string | null;
  started_at: string;       // ISO8601
  status: 'done' | 'active';
}

/** @deprecated — Sprint 4: use RosterResponse instead */
export interface ChainResponse {
  session_id: string;
  session_state: SessionState;
  steps?: ChainStep[];   // legacy field — may be absent in Sprint 4 responses
  roster?: RosterEntry[]; // Sprint 4 field
}

// Sprint 4 — Roster types (FR-001 update)
export interface RosterTokens {
  input: number;
  output: number;
  cache_creation: number;
  cache_read: number;
}

export interface RosterHistoryEntry {
  call_index: number;
  started_at: string;          // ISO8601
  description: string | null;
  model: string | null;
  tokens: RosterTokens | null; // null for early sessions where attribution_agent was not captured
  status: 'done' | 'active';
  result_summary?: string | null;  // optional — backend deferred to follow-up commit
  result_full?: string | null;     // optional — backend deferred
  duration_ms?: number | null;     // optional — backend deferred
}

export interface RosterEntry {
  role: string;
  display_name: string;
  call_count: number;
  latest_description: string | null;
  latest_model: string | null;
  first_called_at: string;    // ISO8601
  last_called_at: string;     // ISO8601
  total_tokens: RosterTokens;
  history: RosterHistoryEntry[];
  status: 'done' | 'active';
  is_dispatcher?: boolean;    // Sprint 5 FR-004: true for Dispatcher node (always index 0)
}

export interface RosterResponse {
  session_id: string;
  session_state: SessionState;
  roster: RosterEntry[];
}

export interface TokenCounts {
  input: number;
  output: number;
  cache_creation: number;
  cache_read: number;
}

/** Track B: current subagent running inside this session */
export interface CurrentSubagent {
  type: string;          // raw slug, e.g. "senior-developer"
  display_name: string;  // mapped display, e.g. "Senior Developer"
  activity: string | null;
  at: string;            // ISO8601 timestamp of the Agent tool call
}

export interface Session {
  session_id: string;
  project: string;
  agent_type: string;
  state: SessionState;
  started_at: string;       // ISO8601
  last_event_at: string;    // ISO8601
  token_total: TokenCounts;
  current_subagent?: CurrentSubagent | null;  // Track B
  // Sprint 3 fields — optional, populated when backend Track C is deployed
  title?: string | null;
  context_pct?: number | null;
  last_input_total?: number | null;
  max_context?: number | null;
}

/** Track B: project group for 'Theo Dự án' view */
export interface ProjectGroup {
  project_slug: string;
  project_display: string;
  session_count: number;
  token_total: number;
  sessions: Session[];
}

export interface HistorySession extends Session {
  ended_at?: string;        // ISO8601, set when Ended
}

// ─── Account types ────────────────────────────────────────────────────────────

export type AccountKind = 'api_key' | 'oauth_session';

export interface Account {
  id: string;
  kind: AccountKind;  // changed to required (DEBT-001)
  name: string;
  // api_key accounts
  key_masked?: string;      // "sk-ant-api03-****XXXX"
  // oauth_session accounts
  oauth_masked?: string;    // "sk-ant-****XXXX"
  needs_relogin?: boolean;
  expires_in_sec?: number;
  refresh_expires_in_sec?: number;
  last_refreshed_at?: string | null;
  // common
  is_active: boolean;
  created_at: string;
}

export interface ActiveAccount {
  id: string;
  name: string;
  kind: AccountKind;  // changed to required (DEBT-001)
  key_masked?: string;
  oauth_masked?: string;
}

export interface OAuthStatus {
  expires_in_sec: number;
  refresh_expires_in_sec: number;
  needs_relogin: boolean;
  last_refreshed_at: string | null;
}

// ─── Sprint 5: Usage & Aggregate types ───────────────────────────────────────

/** Quota usage từ Anthropic API — trả về bởi GET /api/accounts/usage/active và /api/accounts/{id}/usage */
export interface UsageInfo {
  account_id?: string;
  five_hour_pct?: number | null;        // 0..100, đã tính %
  seven_day_pct?: number | null;        // 0..100, đã tính %
  seven_day_opus_pct?: number | null;
  seven_day_sonnet_pct?: number | null;
  resets_at?: number | null;            // unix seconds — session (5h) window reset
  seven_day_resets_at?: number | null;  // unix seconds — weekly window reset
  rate_limit_type?: string | null;
  overage_status?: string | null;
  fetched_at?: number;                  // unix seconds, cache timestamp
  error?: string | null;                // 'api_key' | 'no_oauth' | 'unauthorized' | 'timeout' | 'network' | 'http_NNN'
}

export interface ProjectRosterItem {
  role: string;
  display_name: string;
  call_count: number;
  total_tokens: {
    input: number;
    output: number;
  };
  /** Bug 2: backend tính từ active_agents — true nếu role đang Running trong project này */
  is_active?: boolean;
}

export interface ActiveAgentEntry {
  session_id: string;
  role: string | null;
  display_name: string;
  is_dispatcher: boolean;
  model: string | null;
  current_activity: string | null;
  tokens: {
    input: number;
    output: number;
    cache_creation: number;
    cache_read: number;
  };
}

/** 1 entry trong aggregate roster — tổng hợp theo vai trò hoặc dự án */
export interface AggregateEntry {
  role: string;
  display_name: string;
  call_count: number;
  session_count: number;
  latest_model: string | null;
  first_called_at: string;   // ISO8601
  last_called_at: string;    // ISO8601
  total_tokens: RosterTokens;
  status: 'done' | 'active';
  active_now: number;        // số session đang chạy role này hoặc dự án này
  project_roster?: ProjectRosterItem[];
  active_agents?: ActiveAgentEntry[];
}


/** Response từ GET /api/pipeline/aggregate */
export interface AggregateResponse {
  mode: 'aggregate';
  total_sessions: number;
  total_calls: number;
  roster: AggregateEntry[];
}

// ─── Token analytics types ────────────────────────────────────────────────────

export interface TokenBucket {
  label: string;            // "07/07", "W28", "Aug" etc.
  input: number;
  output: number;
  cache_creation: number;
  cache_read: number;
}

export interface TokenSummaryResponse {
  buckets: TokenBucket[];
  totals: TokenCounts & { sessions: number };
}

// ─── Session history types ────────────────────────────────────────────────────

export interface SessionHistoryResponse {
  items: HistorySession[];
  total: number;
}

// ─── WebSocket message types ──────────────────────────────────────────────────

export interface WsSnapshot {
  sessions: Session[];
  active_account: ActiveAccount | null;
  watcher_alive: boolean;
}

export type DeltaEvent =
  | { event: 'agent_started'; session_id: string; project: string; agent_type: string; started_at: string }
  | { event: 'agent_update'; session_id: string; last_event_at: string; tool_use?: string; tokens_added?: Partial<TokenCounts> }
  | { event: 'agent_state_changed'; session_id: string; state: SessionState }
  | { event: 'token_update'; session_id: string; delta: Partial<TokenCounts>; cumulative: TokenCounts }
  | { event: 'account_changed'; active_id: string | null; name: string | null; kind: AccountKind | null; key_masked?: string | null; oauth_masked?: string | null }
  | { event: 'watcher_status'; alive: boolean; error?: string }
  | { event: 'subagent_changed'; session_id: string; subagent: CurrentSubagent }   // Track B
  | { event: 'session_title_changed'; session_id: string; title: string; source: 'ai_title' | 'user_text' }  // Sprint 3
  | { event: 'session_context_updated'; session_id: string; context_pct: number; last_input_total: number; max_context: number }  // Sprint 3
  | { event: 'chain_updated'; session_id: string; child_session_id: string; reason: string }   // Sprint 5 BUG-004
  // Sprint 7: Auto-Failover events
  | { event: 'failover_started'; from: { id: string; name: string } | null; to: { id: string; name: string }; reason: FailoverTriggerReason; at: string }
  | { event: 'failover_completed'; failover_id: string; to: { id: string; name: string }; swap_latency_ms: number }
  | { event: 'failover_failed'; failover_id: string; reason: string }
  | { event: 'all_accounts_exhausted'; next_retry_at: string; retry_account: { id: string; name: string }; retry_attempt: number; max_retries: number }
  | { event: 'wait_retry_tick'; seconds_left: number }   // optional server tick — FE self-calculates from next_retry_at
  | { event: 'retry_success'; account: { id: string; name: string } }
  | { event: 'retry_cancelled_by_manual'; activated: { id: string; name: string } }
  | { event: 'failover_paused'; reason: string; backoff_until: string };

export interface WsMessage {
  type: 'snapshot' | 'delta' | 'pong';
  ts: string;
  payload: WsSnapshot | DeltaEvent;
}

// ─── WS application state ─────────────────────────────────────────────────────

export interface WsAppState {
  wsStatus: WsStatus;
  sessions: Session[];
  activeAccount: ActiveAccount | null;
  watcherAlive: boolean;
  /** Sprint 5 BUG-004: counter tăng khi parent session nhận chain_updated WS event — PipelineCard dùng làm dep để refetch */
  chainUpdateTriggers: Record<string, number>;
  // Sprint 7: Auto-Failover engine state
  failoverState: FailoverEngineState;
  failoverNextRetryAt: string | null;
  failoverRetryAccount: { id: string; name: string } | null;
  failoverRetryAttempt: number;
  failoverMaxRetries: number;
  failoverCount24h: number;
  /** Badge "FAILOVER ACTIVE" tạm thời trên AccountCard — null sau 30s tự ẩn */
  failoverActiveInfo: FailoverActiveInfo | null;
  /** Accounts đã bị swap ra — hiển thị badge EXHAUSTED (cho đến khi user reset) */
  failoverExhaustedIds: Record<string, boolean>;
  /** Temp: lưu from.id và reason từ failover_started để dùng khi failover_completed đến */
  failoverPendingFromId: string | null;
  failoverPendingReason: string | null;
  /** Nonce tăng khi có toast mới cần hiển thị — FailoverToastBridge watch dep này */
  failoverToastNonce: number;
  failoverToastMessage: string;
  failoverToastType: 'failover' | 'failover-error';
}

export type WsAction =
  | { type: 'WS_CONNECTING' }
  | { type: 'WS_CONNECTED' }
  | { type: 'WS_DISCONNECTED' }
  | { type: 'WS_RECONNECTING' }
  | { type: 'SNAPSHOT'; payload: WsSnapshot }
  | { type: 'DELTA'; payload: DeltaEvent };

// ─── Sprint 7: Failover types ────────────────────────────────────────────────

export type FailoverEngineState = 'idle' | 'monitoring' | 'swapping' | 'waiting' | 'retrying' | 'paused'

export type FailoverTriggerReason =
  | 'http_429'
  | 'quota_5h_full'
  | 'quota_7d_full'
  | 'jsonl_rate_limit'
  | 'api_wide_suspected'
  | 'manual_override'

export type FailoverResult =
  | 'success'
  | 'swap_failed'
  | 'wait_and_retry_scheduled'
  | 'wait_and_retry_success'
  | 'wait_and_retry_failed'
  | 'api_wide_suspected'
  | 'retry_cancelled_by_manual'

export interface FailoverChainItem {
  acc_id: string
  name: string
  priority: number
  include_in_chain: boolean
  status: 'active' | 'standby' | 'exhausted' | 'needs_relogin'
  five_hour_pct: number | null
  seven_day_pct: number | null
  resets_at: number | null
}

export interface FailoverEvent {
  failover_id: string
  occurred_at: string           // ISO 8601
  from_account_id: string | null
  from_account_name: string | null
  to_account_id: string | null
  to_account_name: string | null
  trigger_reason: FailoverTriggerReason
  result: FailoverResult
  swap_latency_ms: number | null
  next_retry_at: string | null
  retry_attempt: number | null
  error_message: string | null
}

export interface FailoverLogResponse {
  items: FailoverEvent[]
  total: number
  count_24h: number
}

export interface FailoverStatus {
  state: FailoverEngineState
  active_account: { id: string; name: string } | null
  next_retry_at: string | null
  retry_account: { id: string; name: string } | null
  retry_attempt: number
  max_retries: number
  count_24h: number
  api_wide_backoff_until: string | null
}

/** Thông tin badge "FAILOVER ACTIVE" tạm thời — tự ẩn sau 30s */
export interface FailoverActiveInfo {
  toAccountId: string
  toAccountName: string
  /** Human-readable trigger reason: "429 detected" | "Quota 5h full" | ... */
  reason: string
  latencyMs: number | null
  /** Date.now() ms timestamp khi swap hoàn tất — dùng tính 30s auto-hide */
  triggeredAt: number
}

// ─── API error ────────────────────────────────────────────────────────────────

export interface ApiError {
  error: { code: string; message: string };
}
