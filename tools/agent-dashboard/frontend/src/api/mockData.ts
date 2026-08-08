import type {
  Session, HistorySession, Account, TokenSummaryResponse, SessionHistoryResponse,
  ChainResponse, UsageInfo, AggregateResponse, RosterEntry,
} from '../types'

// ─── Mock sessions (active) ────────────────────────────────────────────────────

const now = new Date()
const ago = (secs: number) => new Date(now.getTime() - secs * 1000).toISOString()

export const MOCK_SESSIONS: Session[] = [
  {
    // FR-003: title from ai_title | FR-002: low context | FR-001: has chain (dispatcher)
    session_id: 'sess-001',
    project: 'claude-git',
    agent_type: 'senior-developer',
    state: 'Running',
    started_at: ago(480),
    last_event_at: ago(15),
    token_total: { input: 12450, output: 3210, cache_creation: 400, cache_read: 8200 },
    current_subagent: {
      type: 'senior-developer',
      display_name: 'Senior Developer',
      activity: 'Implement backend: parser, DB migration, chain endpoint',
      at: ago(15),
    },
    title: 'WF-FEATURE: Agent Dashboard Sprint 3 — Backend Track C',
    context_pct: 4.5,
    last_input_total: 45000,
    max_context: 1000000,
  },
  {
    // FR-003: null title (fallback to session_id) | FR-002: warning range | no chain
    session_id: 'sess-002',
    project: 'claude-git',
    agent_type: 'junior-developer',
    state: 'Running',
    started_at: ago(300),
    last_event_at: ago(5),
    token_total: { input: 5100, output: 1340, cache_creation: 0, cache_read: 2100 },
    title: null,
    context_pct: 72.3,
    last_input_total: 144600,
    max_context: 200000,
  },
  {
    // FR-003: title | FR-002: context_pct=0 → badge hidden | FR-001: has done chain
    session_id: 'sess-003',
    project: 'ipgs-v4',
    agent_type: 'tech-lead',
    state: 'Idle',
    started_at: ago(2700),
    last_event_at: ago(420),
    token_total: { input: 22100, output: 8450, cache_creation: 900, cache_read: 15000 },
    title: 'WF-BUGFIX: Fix BUG-001 DELETE /api/accounts 500',
    context_pct: 0,
    last_input_total: 0,
    max_context: 200000,
  },
  {
    // FR-003: title | FR-002: danger range (>90%) | no chain
    session_id: 'sess-004',
    project: 'ipgs-v4',
    agent_type: 'qa-engineer',
    state: 'Ended',
    started_at: ago(8400),
    last_event_at: ago(3600),
    token_total: { input: 8230, output: 2100, cache_creation: 200, cache_read: 4500 },
    title: 'WF-FEATURE: QA sign-off Sprint 2 — test plan execution',
    context_pct: 91.5,
    last_input_total: 91500,
    max_context: 100000,
  },
  {
    // FR-003: null title (fallback) | FR-002: null → badge hidden | no chain
    session_id: 'sess-005',
    project: 'claude-git',
    agent_type: 'product-manager',
    state: 'Ended',
    started_at: ago(14400),
    last_event_at: ago(7200),
    token_total: { input: 15600, output: 4200, cache_creation: 300, cache_read: 9800 },
    title: null,
    context_pct: null,
    last_input_total: null,
    max_context: null,
  },
  {
    // No Sprint 3 fields — backward-compat test (undefined fields)
    session_id: 'sess-006',
    project: 'kztek-site',
    agent_type: 'business-analyst',
    state: 'Ended',
    started_at: ago(18000),
    last_event_at: ago(9000),
    token_total: { input: 6800, output: 1900, cache_creation: 150, cache_read: 3200 },
  },
]

// ─── Mock chain data (Sprint 5 — GET /api/sessions/{id}/chain returns roster[]) ──

/** Tạo 1 RosterEntry helper */
function makeEntry(
  overrides: Partial<RosterEntry> & Pick<RosterEntry, 'role' | 'display_name' | 'status'>
): RosterEntry {
  return {
    call_count: 1,
    latest_description: null,
    latest_model: 'claude-sonnet-4-6',
    first_called_at: ago(600),
    last_called_at: ago(300),
    total_tokens: { input: 0, output: 0, cache_creation: 0, cache_read: 0 },
    history: [],
    is_dispatcher: false,
    ...overrides,
  }
}

export function getMockChain(sessionId: string): ChainResponse {
  // sess-001 (Running): Dispatcher + 4 done roles + 1 active (SD) đang khởi tạo (BUG-004 demo)
  if (sessionId === 'sess-001') {
    const roster: RosterEntry[] = [
      // FR-004: Dispatcher node — luôn index 0
      makeEntry({
        role: '__dispatcher__',
        display_name: 'Claude (Dispatcher)',
        is_dispatcher: true,
        status: 'active',
        call_count: 1,
        latest_description: 'WF-FEATURE: Agent Dashboard Sprint 5',
        latest_model: 'claude-sonnet-4-6',
        first_called_at: ago(480),
        last_called_at: ago(15),
        total_tokens: { input: 45000, output: 12000, cache_creation: 2000, cache_read: 35000 },
        history: [],
      }),
      makeEntry({
        role: 'product-manager',
        display_name: 'Product Manager',
        status: 'done',
        call_count: 1,
        latest_description: 'Viết PRD Agent Dashboard Sprint 5: 4 hạng mục A-D',
        latest_model: 'claude-sonnet-4-6',
        first_called_at: ago(480),
        last_called_at: ago(420),
        total_tokens: { input: 5200, output: 1800, cache_creation: 0, cache_read: 3200 },
        history: [
          {
            call_index: 0,
            started_at: ago(480),
            description: 'Viết PRD Agent Dashboard Sprint 5: 4 hạng mục A-D',
            model: 'claude-sonnet-4-6',
            tokens: { input: 5200, output: 1800, cache_creation: 0, cache_read: 3200 },
            status: 'done',
            result_summary: 'PRD Sprint 5 hoàn thành: UsageBar (A), BUG-004 (B), FR-004 Dispatcher (C), FR-005 Toggle (D). 12 task S5-T01..T12.',
          },
        ],
      }),
      makeEntry({
        role: 'business-analyst',
        display_name: 'Business Analyst',
        status: 'done',
        call_count: 2,
        latest_description: 'Viết AC chi tiết FR-004 + FR-005 + BUG-004 + BUG-005',
        latest_model: 'claude-sonnet-4-6',
        first_called_at: ago(420),
        last_called_at: ago(300),
        total_tokens: { input: 8100, output: 2400, cache_creation: 0, cache_read: 5600 },
        history: [
          {
            call_index: 0,
            started_at: ago(420),
            description: 'Viết User Stories FR-004/FR-005 với Acceptance Criteria',
            model: 'claude-sonnet-4-6',
            tokens: { input: 4000, output: 1200, cache_creation: 0, cache_read: 2800 },
            status: 'done',
          },
          {
            call_index: 1,
            started_at: ago(350),
            description: 'Viết AC chi tiết FR-004 + FR-005 + BUG-004 + BUG-005',
            model: 'claude-sonnet-4-6',
            tokens: { input: 4100, output: 1200, cache_creation: 0, cache_read: 2800 },
            status: 'done',
          },
        ],
      }),
      makeEntry({
        role: 'tech-lead',
        display_name: 'Tech Lead',
        status: 'done',
        call_count: 1,
        latest_description: 'TDD ADDENDUM Sprint 5 §29-36: usage_service, BUG-004, FR-004, FR-005',
        latest_model: 'claude-opus-4-7',
        first_called_at: ago(300),
        last_called_at: ago(180),
        total_tokens: { input: 22000, output: 8500, cache_creation: 1200, cache_read: 16000 },
        history: [
          {
            call_index: 0,
            started_at: ago(300),
            description: 'TDD ADDENDUM Sprint 5 §29-36',
            model: 'claude-opus-4-7',
            tokens: { input: 22000, output: 8500, cache_creation: 1200, cache_read: 16000 },
            status: 'done',
            result_summary: 'TDD Sprint 5 hoàn thành. 6 task SD + 6 task JD. Schema UsageInfo, Dispatcher entry, aggregate endpoint đã chốt.',
          },
        ],
      }),
      // BUG-004 demo: Senior Dev đang khởi tạo — model=null, tokens=0
      makeEntry({
        role: 'senior-developer',
        display_name: 'Senior Developer',
        status: 'active',
        call_count: 1,
        latest_description: null,   // BUG-004: chưa có description
        latest_model: null,          // BUG-004: chưa có model
        first_called_at: ago(15),
        last_called_at: ago(15),
        total_tokens: { input: 0, output: 0, cache_creation: 0, cache_read: 0 },  // BUG-004: tokens=0
        history: [],
      }),
    ]

    return {
      session_id: 'sess-001',
      session_state: 'Running',
      roster,
    }
  }

  // sess-003 (Idle): Dispatcher (done) + 3 roles done
  if (sessionId === 'sess-003') {
    const roster: RosterEntry[] = [
      makeEntry({
        role: '__dispatcher__',
        display_name: 'Claude (Dispatcher)',
        is_dispatcher: true,
        status: 'done',
        call_count: 1,
        latest_description: 'WF-BUGFIX: Fix BUG-001 DELETE /api/accounts 500',
        latest_model: 'claude-sonnet-4-6',
        first_called_at: ago(2700),
        last_called_at: ago(1800),
        total_tokens: { input: 18000, output: 5500, cache_creation: 800, cache_read: 12000 },
        history: [],
      }),
      makeEntry({
        role: 'senior-developer',
        display_name: 'Senior Developer',
        status: 'done',
        call_count: 1,
        latest_description: 'Fix BUG-001: DELETE /api/accounts/:id returns 500 khi account active',
        latest_model: 'claude-sonnet-4-6',
        first_called_at: ago(2700),
        last_called_at: ago(2100),
        total_tokens: { input: 9800, output: 2900, cache_creation: 400, cache_read: 7200 },
        history: [
          {
            call_index: 0,
            started_at: ago(2700),
            description: 'Fix BUG-001: DELETE /api/accounts/:id returns 500 khi account active',
            model: 'claude-sonnet-4-6',
            tokens: { input: 9800, output: 2900, cache_creation: 400, cache_read: 7200 },
            status: 'done',
            result_summary: 'Fix hoàn thành: thêm guard check active account trước khi delete, 52 tests pass.',
          },
        ],
      }),
      makeEntry({
        role: 'tech-lead',
        display_name: 'Tech Lead',
        status: 'done',
        call_count: 1,
        latest_description: 'Code review PR fix BUG-001, request changes: thiếu test edge case',
        latest_model: 'claude-opus-4-7',
        first_called_at: ago(2100),
        last_called_at: ago(1800),
        total_tokens: { input: 6200, output: 1800, cache_creation: 0, cache_read: 4500 },
        history: [
          {
            call_index: 0,
            started_at: ago(2100),
            description: 'Code review PR fix BUG-001',
            model: 'claude-opus-4-7',
            tokens: { input: 6200, output: 1800, cache_creation: 0, cache_read: 4500 },
            status: 'done',
          },
        ],
      }),
      makeEntry({
        role: 'qa-engineer',
        display_name: 'QA Engineer',
        status: 'done',
        call_count: 1,
        latest_description: 'Verify fix BUG-001 trên staging, regression test DELETE account',
        latest_model: 'claude-sonnet-4-6',
        first_called_at: ago(1800),
        last_called_at: ago(1500),
        total_tokens: { input: 4400, output: 1200, cache_creation: 0, cache_read: 3000 },
        history: [
          {
            call_index: 0,
            started_at: ago(1800),
            description: 'Verify fix BUG-001 trên staging, regression test DELETE account',
            model: 'claude-sonnet-4-6',
            tokens: { input: 4400, output: 1200, cache_creation: 0, cache_read: 3000 },
            status: 'done',
          },
        ],
      }),
    ]

    return {
      session_id: 'sess-003',
      session_state: 'Idle',
      roster,
    }
  }

  // All other sessions: empty roster (no Agent tool calls)
  return {
    session_id: sessionId,
    session_state: 'Ended',
    roster: [],
  }
}

// ─── Mock Usage data (Sprint 5 — GET /api/accounts/usage/*) ──────────────────

const nowSec = Math.floor(Date.now() / 1000)

/** UsageInfo mẫu cho OAuth account đang active */
export const MOCK_USAGE_ACTIVE: UsageInfo = {
  account_id: 'acc-oauth-01',
  five_hour_pct: 78.5,
  seven_day_pct: 42.0,
  resets_at: nowSec + 4800,          // ~1h 20m còn lại
  seven_day_resets_at: nowSec + 86400 * 4 + 3 * 3600,  // ~4d 3h còn lại
  rate_limit_type: 'five_hour',
  fetched_at: nowSec,
  error: null,
}

/** UsageInfo mẫu cho OAuth account không active (usage thấp hơn) */
export const MOCK_USAGE_INACTIVE: UsageInfo = {
  account_id: 'acc-oauth-02',
  five_hour_pct: 12.0,
  seven_day_pct: 8.5,
  resets_at: nowSec + 14400,         // ~4h còn lại
  seven_day_resets_at: nowSec + 86400 * 6,  // ~6d còn lại
  rate_limit_type: 'five_hour',
  fetched_at: nowSec,
  error: null,
}

/** Trả UsageInfo theo account id — dùng trong mock interceptor */
export function getMockUsage(accountId: string): UsageInfo {
  // acc-001 là active (theo MOCK_ACCOUNTS) → trả MOCK_USAGE_ACTIVE
  if (accountId === 'acc-001') return MOCK_USAGE_ACTIVE
  // Các OAuth account khác → trả INACTIVE
  return MOCK_USAGE_INACTIVE
}

// ─── Mock Aggregate data (Sprint 5 — GET /api/pipeline/aggregate) ─────────────

export const MOCK_AGGREGATE: AggregateResponse = {
  mode: 'aggregate',
  total_sessions: 127,
  total_calls: 847,
  roster: [
    {
      role: 'tech-lead',
      display_name: 'Tech Lead',
      call_count: 247,
      session_count: 45,
      latest_model: 'claude-opus-4-7',
      first_called_at: ago(86400 * 30),
      last_called_at: ago(600),
      total_tokens: { input: 31_200_000, output: 4_800_000, cache_creation: 800_000, cache_read: 18_000_000 },
      status: 'done',
      active_now: 0,
    },
    {
      role: 'senior-developer',
      display_name: 'Senior Developer',
      call_count: 189,
      session_count: 38,
      latest_model: 'claude-sonnet-4-6',
      first_called_at: ago(86400 * 28),
      last_called_at: ago(120),
      total_tokens: { input: 22_400_000, output: 3_100_000, cache_creation: 600_000, cache_read: 14_000_000 },
      status: 'active',
      active_now: 2,
    },
    {
      role: 'junior-developer',
      display_name: 'Junior Developer',
      call_count: 134,
      session_count: 29,
      latest_model: 'claude-sonnet-4-6',
      first_called_at: ago(86400 * 25),
      last_called_at: ago(3600),
      total_tokens: { input: 14_700_000, output: 2_100_000, cache_creation: 400_000, cache_read: 9_000_000 },
      status: 'done',
      active_now: 0,
    },
    {
      role: 'business-analyst',
      display_name: 'Business Analyst',
      call_count: 87,
      session_count: 22,
      latest_model: 'claude-sonnet-4-6',
      first_called_at: ago(86400 * 20),
      last_called_at: ago(7200),
      total_tokens: { input: 9_300_000, output: 1_400_000, cache_creation: 200_000, cache_read: 6_000_000 },
      status: 'done',
      active_now: 0,
    },
    {
      role: 'qa-engineer',
      display_name: 'QA Engineer',
      call_count: 67,
      session_count: 18,
      latest_model: 'claude-sonnet-4-6',
      first_called_at: ago(86400 * 18),
      last_called_at: ago(5400),
      total_tokens: { input: 7_100_000, output: 1_000_000, cache_creation: 100_000, cache_read: 4_500_000 },
      status: 'done',
      active_now: 0,
    },
    {
      role: 'product-manager',
      display_name: 'Product Manager',
      call_count: 54,
      session_count: 15,
      latest_model: 'claude-sonnet-4-6',
      first_called_at: ago(86400 * 15),
      last_called_at: ago(86400),
      total_tokens: { input: 5_800_000, output: 900_000, cache_creation: 80_000, cache_read: 3_600_000 },
      status: 'done',
      active_now: 0,
    },
    {
      role: 'devops-engineer',
      display_name: 'DevOps Engineer',
      call_count: 38,
      session_count: 12,
      latest_model: 'claude-sonnet-4-6',
      first_called_at: ago(86400 * 12),
      last_called_at: ago(86400 * 2),
      total_tokens: { input: 3_900_000, output: 600_000, cache_creation: 50_000, cache_read: 2_400_000 },
      status: 'done',
      active_now: 0,
    },
    {
      role: 'ui-ux-designer',
      display_name: 'UI/UX Designer',
      call_count: 31,
      session_count: 10,
      latest_model: 'claude-sonnet-4-6',
      first_called_at: ago(86400 * 10),
      last_called_at: ago(86400 * 3),
      total_tokens: { input: 3_100_000, output: 480_000, cache_creation: 40_000, cache_read: 1_900_000 },
      status: 'done',
      active_now: 0,
    },
  ],
}

// ─── Mock session history (ended) ─────────────────────────────────────────────

export const MOCK_HISTORY: HistorySession[] = Array.from({ length: 35 }, (_, i) => {
  const daysAgo = Math.floor(i / 3) + 1
  const start = ago(daysAgo * 86400 + i * 3600)
  const duration = 1800 + i * 600
  const agentTypes = ['senior-developer', 'junior-developer', 'tech-lead', 'qa-engineer', 'product-manager']
  const projects = ['claude-git', 'ipgs-v4', 'kztek-site']
  return {
    session_id: `hist-${String(i + 1).padStart(3, '0')}`,
    project: projects[i % projects.length],
    agent_type: agentTypes[i % agentTypes.length],
    state: 'Ended' as const,
    started_at: start,
    last_event_at: new Date(new Date(start).getTime() + duration * 1000).toISOString(),
    ended_at: new Date(new Date(start).getTime() + duration * 1000).toISOString(),
    token_total: {
      input: 3000 + i * 1200,
      output: 800 + i * 300,
      cache_creation: i * 50,
      cache_read: 1000 + i * 400,
    },
  }
})

// ─── Mock accounts ─────────────────────────────────────────────────────────────

export const MOCK_ACCOUNTS: Account[] = [
  {
    id: 'acc-001',
    name: 'KZTEK Production',
    kind: 'api_key',
    key_masked: 'sk-ant-****PROD',
    is_active: true,
    created_at: ago(86400 * 30),
  },
  {
    id: 'acc-002',
    name: 'KZTEK Dev',
    kind: 'api_key',
    key_masked: 'sk-ant-****DEVX',
    is_active: false,
    created_at: ago(86400 * 14),
  },
  {
    id: 'acc-003',
    name: 'Personal',
    kind: 'api_key',
    key_masked: 'sk-ant-****PERS',
    is_active: false,
    created_at: ago(86400 * 7),
  },
]

// ─── Mock token summary ────────────────────────────────────────────────────────

function buildBuckets(days: number, labels: string[]): TokenSummaryResponse['buckets'] {
  return labels.map((label, i) => ({
    label,
    input: 8000 + Math.floor(Math.sin(i * 0.7) * 4000) + i * 200,
    output: 2000 + Math.floor(Math.cos(i * 0.5) * 1000) + i * 50,
    cache_creation: 100 + i * 30,
    cache_read: 3000 + i * 150,
  }))
}

export function getMockTokenSummary(range: string): TokenSummaryResponse {
  let labels: string[]
  switch (range) {
    case '7d':
      labels = Array.from({ length: 7 }, (_, i) => {
        const d = new Date(); d.setDate(d.getDate() - (6 - i))
        return `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}`
      })
      break
    case '30d':
      labels = Array.from({ length: 30 }, (_, i) => {
        const d = new Date(); d.setDate(d.getDate() - (29 - i))
        return `${String(d.getDate()).padStart(2,'0')}/${String(d.getMonth()+1).padStart(2,'0')}`
      })
      break
    case '12w':
      labels = Array.from({ length: 12 }, (_, i) => `W${i + 1}`)
      break
    case '6m':
      labels = Array.from({ length: 6 }, (_, i) => {
        const d = new Date(); d.setMonth(d.getMonth() - (5 - i))
        return d.toLocaleString('vi-VN', { month: 'short' })
      })
      break
    default:
      labels = []
  }
  const buckets = buildBuckets(labels.length, labels)
  const totals = buckets.reduce(
    (acc, b) => ({
      input: acc.input + b.input,
      output: acc.output + b.output,
      cache_creation: acc.cache_creation + b.cache_creation,
      cache_read: acc.cache_read + b.cache_read,
      sessions: acc.sessions + Math.ceil(b.input / 8000),
    }),
    { input: 0, output: 0, cache_creation: 0, cache_read: 0, sessions: 0 }
  )
  return { buckets, totals }
}

export function getMockSessionHistory(limit = 20, offset = 0): SessionHistoryResponse {
  const slice = MOCK_HISTORY.slice(offset, offset + limit)
  return { items: slice, total: MOCK_HISTORY.length }
}
