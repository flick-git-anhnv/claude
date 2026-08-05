import type { Account, Session, SessionHistoryResponse, TokenSummaryResponse, RangeFilter } from '../types'

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
      body: JSON.stringify({ name, api_key: apiKey }),
    })
  }

  function deleteAccount(id: string): Promise<void> {
    return apiFetch<void>(`${BASE}/accounts/${id}`, { method: 'DELETE' })
  }

  function activateAccount(id: string): Promise<{ active_id: string }> {
    return apiFetch<{ active_id: string }>(`${BASE}/accounts/${id}/activate`, { method: 'POST' })
  }

  function revealApiKey(id: string): Promise<string> {
    return apiFetch<{ api_key: string }>(`${BASE}/accounts/${id}/reveal`).then(d => d.api_key)
  }

  return {
    getSessions,
    getSessionsHistory,
    getTokensSummary,
    getAccounts,
    addAccount,
    deleteAccount,
    activateAccount,
    revealApiKey,
  }
}
