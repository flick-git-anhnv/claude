import type { Session, HistorySession, Account, TokenSummaryResponse, SessionHistoryResponse } from '../types'

// ─── Mock sessions (active) ────────────────────────────────────────────────────

const now = new Date()
const ago = (secs: number) => new Date(now.getTime() - secs * 1000).toISOString()

export const MOCK_SESSIONS: Session[] = [
  {
    session_id: 'sess-001',
    project: 'claude-git',
    agent_type: 'senior-developer',
    state: 'Running',
    started_at: ago(480),
    last_event_at: ago(15),
    token_total: { input: 12450, output: 3210, cache_creation: 400, cache_read: 8200 },
  },
  {
    session_id: 'sess-002',
    project: 'claude-git',
    agent_type: 'junior-developer',
    state: 'Running',
    started_at: ago(300),
    last_event_at: ago(5),
    token_total: { input: 5100, output: 1340, cache_creation: 0, cache_read: 2100 },
  },
  {
    session_id: 'sess-003',
    project: 'ipgs-v4',
    agent_type: 'tech-lead',
    state: 'Idle',
    started_at: ago(2700),
    last_event_at: ago(420),
    token_total: { input: 22100, output: 8450, cache_creation: 900, cache_read: 15000 },
  },
  {
    session_id: 'sess-004',
    project: 'ipgs-v4',
    agent_type: 'qa-engineer',
    state: 'Ended',
    started_at: ago(8400),
    last_event_at: ago(3600),
    token_total: { input: 8230, output: 2100, cache_creation: 200, cache_read: 4500 },
  },
  {
    session_id: 'sess-005',
    project: 'claude-git',
    agent_type: 'product-manager',
    state: 'Ended',
    started_at: ago(14400),
    last_event_at: ago(7200),
    token_total: { input: 15600, output: 4200, cache_creation: 300, cache_read: 9800 },
  },
  {
    session_id: 'sess-006',
    project: 'kztek-site',
    agent_type: 'business-analyst',
    state: 'Ended',
    started_at: ago(18000),
    last_event_at: ago(9000),
    token_total: { input: 6800, output: 1900, cache_creation: 150, cache_read: 3200 },
  },
]

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
