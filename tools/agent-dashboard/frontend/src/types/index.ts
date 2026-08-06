// ─── Session & Agent types ────────────────────────────────────────────────────

export type SessionState = 'Running' | 'Idle' | 'Ended';
export type WsStatus = 'connecting' | 'connected' | 'reconnecting' | 'disconnected';
export type RangeFilter = '7d' | '30d' | '12w' | '6m';
export type ViewMode = 'by-agent' | 'by-project';

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
  kind: AccountKind;
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
  kind: AccountKind;
  key_masked?: string;
  oauth_masked?: string;
}

export interface OAuthStatus {
  expires_in_sec: number;
  refresh_expires_in_sec: number;
  needs_relogin: boolean;
  last_refreshed_at: string | null;
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
  | { event: 'account_changed'; active_id: string; name: string; key_masked: string }
  | { event: 'watcher_status'; alive: boolean; error?: string }
  | { event: 'subagent_changed'; session_id: string; subagent: CurrentSubagent };  // Track B

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
}

export type WsAction =
  | { type: 'WS_CONNECTING' }
  | { type: 'WS_CONNECTED' }
  | { type: 'WS_DISCONNECTED' }
  | { type: 'WS_RECONNECTING' }
  | { type: 'SNAPSHOT'; payload: WsSnapshot }
  | { type: 'DELTA'; payload: DeltaEvent };

// ─── API error ────────────────────────────────────────────────────────────────

export interface ApiError {
  error: { code: string; message: string };
}
