import type { Account, OAuthStatus, Session, SessionHistoryResponse, TokenSummaryResponse, RangeFilter, ChainResponse } from '../types'

const BASE = '/api'

async function apiFetch<T>(url: string, init?: RequestInit): Promise<T> {
  const res = await fetch(url, init)
  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: { code: 'UNKNOWN', message: res.statusText } }))
    const msg = (body as { error?: { message?: string } }).error?.message ?? res.statusText
    throw new Error(msg)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export function useApi() {
  // ─── Sessions ─────────────────────────────────────────────────────────────
  function getSessions(): Promise<Session[]> {
    return apiFetch<Session[]>(`${BASE}/sessions`)
  }

  function getSessionsHistory(params: {
    from?: string
    to?: string
    limit?: number
    offset?: number
  } = {}): Promise<SessionHistoryResponse> {
    const u = new URL(`${BASE}/sessions/history`, window.location.origin)
    if (params.from) u.searchParams.set('from', params.from)
    if (params.to) u.searchParams.set('to', params.to)
    u.searchParams.set('limit', String(params.limit ?? 20))
    u.searchParams.set('offset', String(params.offset ?? 0))
    return apiFetch<SessionHistoryResponse>(u.pathname + u.search)
  }

  // ─── Tokens ───────────────────────────────────────────────────────────────
  function getTokensSummary(range: RangeFilter): Promise<TokenSummaryResponse> {
    return apiFetch<TokenSummaryResponse>(`${BASE}/tokens/summary?range=${range}`)
  }

  // ─── Accounts ─────────────────────────────────────────────────────────────
  function getAccounts(): Promise<Account[]> {
    return apiFetch<Account[]>(`${BASE}/accounts`)
  }

  function addAccount(name: string, apiKey: string): Promise<Account> {
    return apiFetch<Account>(`${BASE}/accounts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, kind: 'api_key', api_key: apiKey }),
    })
  }

  /** Import current .credentials.json OAuth session as a new account. */
  function addOAuthAccount(name: string): Promise<Account> {
    return apiFetch<Account>(`${BASE}/accounts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, kind: 'oauth_session' }),
    })
  }

  /** Re-import the current .credentials.json snapshot into an existing OAuth account. */
  function importCurrentOAuth(id: string): Promise<{ ok: boolean; imported_at: string }> {
    return apiFetch(`${BASE}/accounts/${id}/import-current-oauth`, { method: 'POST' })
  }

  function getOAuthStatus(id: string): Promise<OAuthStatus> {
    return apiFetch<OAuthStatus>(`${BASE}/accounts/${id}/oauth-status`)
  }

  function deleteAccount(id: string): Promise<void> {
    return apiFetch<void>(`${BASE}/accounts/${id}`, { method: 'DELETE' })
  }

  function activateAccount(id: string): Promise<{ active_id: string; prev_snapshot_updated: boolean }> {
    return apiFetch(`${BASE}/accounts/${id}/activate`, { method: 'POST' })
  }

  function revealApiKey(id: string): Promise<string> {
    return apiFetch<{ api_key: string }>(`${BASE}/accounts/${id}/reveal`).then(d => d.api_key)
  }

  // ─── Chain (FR-001 Sprint 3) ──────────────────────────────────────────────
  function getSessionChain(sessionId: string): Promise<ChainResponse> {
    return apiFetch<ChainResponse>(`${BASE}/sessions/${sessionId}/chain`)
  }

  return {
    getSessions,
    getSessionsHistory,
    getTokensSummary,
    getAccounts,
    addAccount,
    addOAuthAccount,
    importCurrentOAuth,
    getOAuthStatus,
    deleteAccount,
    activateAccount,
    revealApiKey,
    getSessionChain,
  }
}
