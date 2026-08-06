import type { Session, HistorySession, Account, TokenSummaryResponse, SessionHistoryResponse, ChainResponse } from '../types'

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

// ─── Mock chain data (FR-001 — GET /api/sessions/{id}/chain) ─────────────────

export function getMockChain(sessionId: string): ChainResponse {
  // sess-001 (Running): 5-step chain — 4 done, 1 active (SD)
  if (sessionId === 'sess-001') {
    return {
      session_id: 'sess-001',
      session_state: 'Running',
      steps: [
        {
          step_index: 0,
          subagent_type: 'product-manager',
          subagent_display: 'Product Manager',
          description: 'Viết PRD Agent Dashboard: mục tiêu, user persona, feature list',
          started_at: ago(480),
          status: 'done',
        },
        {
          step_index: 1,
          subagent_type: 'business-analyst',
          subagent_display: 'Business Analyst',
          description: 'Viết User Stories FR-001/FR-002/FR-003 với Acceptance Criteria',
          started_at: ago(420),
          status: 'done',
        },
        {
          step_index: 2,
          subagent_type: 'ui-ux-designer',
          subagent_display: 'UI/UX Designer',
          description: 'Wireframe pipeline view, ContextBadge, SessionCard v2',
          started_at: ago(360),
          status: 'done',
        },
        {
          step_index: 3,
          subagent_type: 'tech-lead',
          subagent_display: 'Tech Lead',
          description: 'TDD ADDENDUM Sprint 3: §22-28 chain endpoint, context snapshot, title field',
          started_at: ago(240),
          status: 'done',
        },
        {
          step_index: 4,
          subagent_type: 'senior-developer',
          subagent_display: 'Senior Developer',
          description: 'Implement backend: parser ai_title, DB migration, snapshot last_*, endpoint /chain',
          started_at: ago(60),
          status: 'active',
        },
      ],
    }
  }

  // sess-003 (Idle): 3-step chain — all done
  if (sessionId === 'sess-003') {
    return {
      session_id: 'sess-003',
      session_state: 'Idle',
      steps: [
        {
          step_index: 0,
          subagent_type: 'senior-developer',
          subagent_display: 'Senior Developer',
          description: 'Fix BUG-001: DELETE /api/accounts/:id returns 500 khi account active',
          started_at: ago(2700),
          status: 'done',
        },
        {
          step_index: 1,
          subagent_type: 'tech-lead',
          subagent_display: 'Tech Lead',
          description: 'Code review PR fix BUG-001, request changes: thiếu test edge case',
          started_at: ago(2100),
          status: 'done',
        },
        {
          step_index: 2,
          subagent_type: 'qa-engineer',
          subagent_display: 'QA Engineer',
          description: 'Verify fix BUG-001 trên staging, regression test DELETE account',
          started_at: ago(1800),
          status: 'done',
        },
      ],
    }
  }

  // All other sessions: empty chain (no Agent tool calls)
  return {
    session_id: sessionId,
    session_state: 'Ended',
    steps: [],
  }
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
    key_masked: 'sk-ant-****PROD',
    is_active: true,
    created_at: ago(86400 * 30),
  },
  {
    id: 'acc-002',
    name: 'KZTEK Dev',
    key_masked: 'sk-ant-****DEVX',
    is_active: false,
    created_at: ago(86400 * 14),
  },
  {
    id: 'acc-003',
    name: 'Personal',
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
