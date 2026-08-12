/**
 * Fetch interceptor cho mock mode (VITE_MOCK=true).
 * Intercept tất cả /api/* requests và trả mock data
 * thay vì gửi request thật đến backend.
 */
import {
  MOCK_SESSIONS,
  MOCK_ACCOUNTS,
  getMockTokenSummary,
  getMockSessionHistory,
  getMockChain,
  MOCK_USAGE_ACTIVE,
  getMockUsage,
  MOCK_AGGREGATE,
} from './mockData'
import type { Account } from '../types'

const isMock = import.meta.env.VITE_MOCK === 'true'

// State in-memory cho accounts (để demo add/delete/activate)
let mockAccounts: Account[] = [...MOCK_ACCOUNTS]
let accountIdCounter = 10

function jsonResponse(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function errorResponse(code: string, message: string, status: number): Response {
  return jsonResponse({ error: { code, message } }, status)
}

function handleMockRequest(input: RequestInfo | URL, init?: RequestInit): Response | null {
  const url = typeof input === 'string' ? input : input.toString()
  const method = (init?.method ?? 'GET').toUpperCase()

  // Strip origin if present
  const path = url.replace(/^https?:\/\/[^/]+/, '')

  // GET /api/sessions
  if (method === 'GET' && path === '/api/sessions') {
    const active = MOCK_SESSIONS.filter(s => s.state !== 'Ended')
    return jsonResponse(active)
  }

  // GET /api/sessions/history
  if (method === 'GET' && path.startsWith('/api/sessions/history')) {
    const u = new URL(url, 'http://localhost')
    const limit = parseInt(u.searchParams.get('limit') ?? '20')
    const offset = parseInt(u.searchParams.get('offset') ?? '0')
    return jsonResponse(getMockSessionHistory(limit, offset))
  }

  // GET /api/tokens/summary
  if (method === 'GET' && path.startsWith('/api/tokens/summary')) {
    const u = new URL(url, 'http://localhost')
    const range = u.searchParams.get('range') ?? '30d'
    return jsonResponse(getMockTokenSummary(range))
  }

  // GET /api/accounts
  if (method === 'GET' && path === '/api/accounts') {
    return jsonResponse(mockAccounts)
  }

  // POST /api/accounts
  if (method === 'POST' && path === '/api/accounts') {
    const body = JSON.parse((init?.body as string) ?? '{}')
    if (!body.api_key) return errorResponse('ACCOUNT_KEY_INVALID', 'API key required', 400)
    if (mockAccounts.some(a => a.name === body.name)) {
      return errorResponse('ACCOUNT_NAME_EXISTS', 'Tên đã tồn tại', 409)
    }
    const newAccount: Account = {
      id: `acc-${++accountIdCounter}`,
      name: body.name,
      kind: 'api_key',
      key_masked: body.api_key.slice(0, 8) + '****' + body.api_key.slice(-4),
      is_active: false,
      created_at: new Date().toISOString(),
    }
    mockAccounts = [...mockAccounts, newAccount]
    return jsonResponse(newAccount, 201)
  }

  // DELETE /api/accounts/:id
  const deleteMatch = path.match(/^\/api\/accounts\/([^/]+)$/)
  if (method === 'DELETE' && deleteMatch) {
    const id = deleteMatch[1]
    const account = mockAccounts.find(a => a.id === id)
    if (!account) return errorResponse('ACCOUNT_NOT_FOUND', 'Không tìm thấy tài khoản', 404)
    if (account.is_active) return errorResponse('ACCOUNT_ACTIVE_CANNOT_DELETE', 'Không thể xóa tài khoản đang active', 409)
    mockAccounts = mockAccounts.filter(a => a.id !== id)
    return new Response(null, { status: 204 })
  }

  // POST /api/accounts/:id/activate
  const activateMatch = path.match(/^\/api\/accounts\/([^/]+)\/activate$/)
  if (method === 'POST' && activateMatch) {
    const id = activateMatch[1]
    if (!mockAccounts.find(a => a.id === id)) return errorResponse('ACCOUNT_NOT_FOUND', 'Không tìm thấy tài khoản', 404)
    mockAccounts = mockAccounts.map(a => ({ ...a, is_active: a.id === id }))
    return jsonResponse({ active_id: id })
  }

  // GET /api/accounts/:id/reveal
  const revealMatch = path.match(/^\/api\/accounts\/([^/]+)\/reveal$/)
  if (method === 'GET' && revealMatch) {
    const id = revealMatch[1]
    const account = mockAccounts.find(a => a.id === id)
    if (!account) return errorResponse('ACCOUNT_NOT_FOUND', 'Không tìm thấy tài khoản', 404)
    // Return a fake full key for mock
    return jsonResponse({ api_key: `sk-ant-api01-mock-key-for-${id}-XXXX` })
  }

  // GET /api/sessions/:id/chain  (FR-001 — Sprint 3)
  const chainMatch = path.match(/^\/api\/sessions\/([^/]+)\/chain$/)
  if (method === 'GET' && chainMatch) {
    const sessionId = chainMatch[1]
    return jsonResponse(getMockChain(sessionId))
  }

  // Sprint 5 — GET /api/accounts/usage/active (active account usage, dùng trong AppHeader)
  // PHẢI match TRƯỚC pattern /:id/usage để tránh "usage" bị coi là account id
  if (method === 'GET' && path === '/api/accounts/usage/active') {
    const activeAcc = mockAccounts.find(a => a.is_active)
    // Chỉ trả usage cho OAuth account (kind === 'oauth') — api_key không có quota bar
    if (!activeAcc || (activeAcc as Account & { kind?: string }).kind === 'api_key') {
      return errorResponse('NO_OAUTH_ACTIVE', 'No active OAuth account', 404)
    }
    return jsonResponse(MOCK_USAGE_ACTIVE)
  }

  // Sprint 5 — GET /api/accounts/:id/usage (per-account usage, dùng trong AccountCard)
  const accountUsageMatch = path.match(/^\/api\/accounts\/([^/]+)\/usage$/)
  if (method === 'GET' && accountUsageMatch) {
    const id = accountUsageMatch[1]
    const account = mockAccounts.find(a => a.id === id)
    if (!account) return errorResponse('ACCOUNT_NOT_FOUND', 'Không tìm thấy tài khoản', 404)
    if ((account as Account & { kind?: string }).kind === 'api_key') {
      return errorResponse('NOT_OAUTH', 'Usage only available for OAuth accounts', 404)
    }
    return jsonResponse(getMockUsage(id))
  }

  // Sprint 5 — GET /api/pipeline/aggregate (FR-005 AggregatePipelineView)
  if (method === 'GET' && path.startsWith('/api/pipeline/aggregate')) {
    return jsonResponse(MOCK_AGGREGATE)
  }

  // GET /api/health
  if (method === 'GET' && path === '/api/health') {
    return jsonResponse({ status: 'ok', uptime_sec: 3600, watcher_alive: true })
  }

  // ── Sprint 7: Failover endpoints ──────────────────────────────────────────

  // GET /api/failover/status
  if (method === 'GET' && path === '/api/failover/status') {
    return jsonResponse({
      state: 'monitoring',
      active_account: mockAccounts.find(a => a.is_active)
        ? { id: mockAccounts.find(a => a.is_active)!.id, name: mockAccounts.find(a => a.is_active)!.name }
        : null,
      next_retry_at: null,
      retry_account: null,
      retry_attempt: 0,
      max_retries: 3,
      count_24h: 2,
      api_wide_backoff_until: null,
    })
  }

  // GET /api/failover/chain
  if (method === 'GET' && path === '/api/failover/chain') {
    const oauthAccounts = mockAccounts.filter(a => a.kind === 'oauth_session')
    return jsonResponse(
      oauthAccounts.map((a, idx) => ({
        acc_id: a.id,
        name: a.name,
        priority: idx + 1,
        include_in_chain: true,
        status: a.is_active ? 'active' : 'standby',
        five_hour_pct: idx === 0 ? 45.2 : null,
        seven_day_pct: idx === 0 ? 12.5 : null,
        resets_at: null,
      })),
    )
  }

  // PUT /api/failover/chain
  if (method === 'PUT' && path === '/api/failover/chain') {
    return jsonResponse({ ok: true })
  }

  // GET /api/failover/log
  if (method === 'GET' && path.startsWith('/api/failover/log')) {
    const u = new URL(url, 'http://localhost')
    const limit = parseInt(u.searchParams.get('limit') ?? '20')
    const offset = parseInt(u.searchParams.get('offset') ?? '0')
    const mockItems = [
      {
        failover_id: 'mock-fo-001',
        occurred_at: new Date(Date.now() - 2 * 3600 * 1000).toISOString(),
        from_account_id: 'acc-1',
        from_account_name: 'vietanh',
        to_account_id: 'acc-2',
        to_account_name: 'OAuth (Imported)',
        trigger_reason: 'http_429',
        result: 'success',
        swap_latency_ms: 42,
        next_retry_at: null,
        retry_attempt: null,
        error_message: null,
      },
      {
        failover_id: 'mock-fo-002',
        occurred_at: new Date(Date.now() - 5 * 3600 * 1000).toISOString(),
        from_account_id: 'acc-2',
        from_account_name: 'OAuth (Imported)',
        to_account_id: null,
        to_account_name: null,
        trigger_reason: 'quota_5h_full',
        result: 'wait_and_retry_scheduled',
        swap_latency_ms: null,
        next_retry_at: new Date(Date.now() + 3600 * 1000).toISOString(),
        retry_attempt: 1,
        error_message: null,
      },
    ]
    const sliced = mockItems.slice(offset, offset + limit)
    return jsonResponse({ items: sliced, total: mockItems.length, count_24h: 2 })
  }

  // POST /api/failover/cancel-retry
  if (method === 'POST' && path === '/api/failover/cancel-retry') {
    return jsonResponse({ ok: true, cancelled: false })
  }

  return null // Not intercepted — pass through
}

export function installMockInterceptor(): void {
  if (!isMock) return

  const originalFetch = window.fetch.bind(window)

  window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const url = typeof input === 'string' ? input : input.toString()
    if (url.includes('/api/')) {
      const mockResp = handleMockRequest(input, init)
      if (mockResp) {
        // Small artificial delay for realism
        await new Promise(r => setTimeout(r, 80))
        return mockResp
      }
    }
    return originalFetch(input, init)
  }

  console.info('[Mock] Fetch interceptor installed — all /api/* calls use mock data')
}

export { isMock }
