/**
 * Tests for wsReducer — Sprint 7 failover state machine
 *
 * Kiểm tra các failover event transitions:
 *  failover_started → failover_completed → toast nonce
 *  failover_failed
 *  all_accounts_exhausted → wait state
 *  retry_success → idle
 *  retry_cancelled_by_manual → idle
 *  failover_paused
 *  wait_retry_tick → no state change (FE self-calculates)
 *  anti-flicker: cùng identity khi state không đổi
 */
import { describe, it, expect } from 'vitest'
import { wsReducer, initialWsState } from './wsReducer'
import type { WsAppState, WsAction, DeltaEvent } from '../types'

// ── Helpers ──────────────────────────────────────────────────────────────────

function delta(payload: object): WsAction {
  return { type: 'DELTA', payload: payload as DeltaEvent }
}

const FROM_ACCOUNT = { id: 'acc-1', name: 'vietanh' }
const TO_ACCOUNT = { id: 'acc-2', name: 'OAuth (Imported)' }

// ── failover_started ──────────────────────────────────────────────────────────

describe('failover_started', () => {
  it('sets failoverState to swapping and stores pendingFromId', () => {
    const next = wsReducer(
      initialWsState,
      delta({
        event: 'failover_started',
        from: FROM_ACCOUNT,
        to: TO_ACCOUNT,
        reason: 'http_429',
        at: new Date().toISOString(),
      }),
    )
    expect(next.failoverState).toBe('swapping')
    expect(next.failoverPendingFromId).toBe('acc-1')
    expect(next.failoverPendingReason).toBe('429 detected')
  })

  it('maps quota_5h_full reason to human label', () => {
    const next = wsReducer(
      initialWsState,
      delta({
        event: 'failover_started',
        from: FROM_ACCOUNT,
        to: TO_ACCOUNT,
        reason: 'quota_5h_full',
        at: new Date().toISOString(),
      }),
    )
    expect(next.failoverPendingReason).toBe('Quota 5h full')
  })

  it('dedupes: returns same state reference when already swapping with same fromId', () => {
    const swappingState: WsAppState = {
      ...initialWsState,
      failoverState: 'swapping',
      failoverPendingFromId: 'acc-1',
    }
    const result = wsReducer(
      swappingState,
      delta({
        event: 'failover_started',
        from: FROM_ACCOUNT,
        to: TO_ACCOUNT,
        reason: 'http_429',
        at: new Date().toISOString(),
      }),
    )
    expect(result).toBe(swappingState)
  })
})

// ── failover_completed ────────────────────────────────────────────────────────

describe('failover_completed', () => {
  const swappingState: WsAppState = {
    ...initialWsState,
    failoverState: 'swapping',
    failoverPendingFromId: 'acc-1',
    failoverPendingReason: '429 detected',
  }

  it('transitions to monitoring and records exhausted account', () => {
    const next = wsReducer(
      swappingState,
      delta({
        event: 'failover_completed',
        failover_id: 'fo-001',
        to: TO_ACCOUNT,
        swap_latency_ms: 42,
      }),
    )
    expect(next.failoverState).toBe('monitoring')
    expect(next.failoverExhaustedIds['acc-1']).toBe(true)
  })

  it('sets failoverActiveInfo with correct toAccountId and latency', () => {
    const next = wsReducer(
      swappingState,
      delta({
        event: 'failover_completed',
        failover_id: 'fo-001',
        to: TO_ACCOUNT,
        swap_latency_ms: 55,
      }),
    )
    expect(next.failoverActiveInfo).not.toBeNull()
    expect(next.failoverActiveInfo!.toAccountId).toBe('acc-2')
    expect(next.failoverActiveInfo!.toAccountName).toBe('OAuth (Imported)')
    expect(next.failoverActiveInfo!.latencyMs).toBe(55)
    expect(next.failoverActiveInfo!.reason).toBe('429 detected')
  })

  it('increments failoverCount24h', () => {
    const stateWith2 = { ...swappingState, failoverCount24h: 2 }
    const next = wsReducer(
      stateWith2,
      delta({
        event: 'failover_completed',
        failover_id: 'fo-002',
        to: TO_ACCOUNT,
        swap_latency_ms: 30,
      }),
    )
    expect(next.failoverCount24h).toBe(3)
  })

  it('increments toast nonce to trigger toast', () => {
    const next = wsReducer(
      swappingState,
      delta({
        event: 'failover_completed',
        failover_id: 'fo-001',
        to: TO_ACCOUNT,
        swap_latency_ms: 42,
      }),
    )
    expect(next.failoverToastNonce).toBeGreaterThan(swappingState.failoverToastNonce)
    expect(next.failoverToastType).toBe('failover')
    expect(next.failoverToastMessage).toContain('OAuth (Imported)')
  })

  it('clears pendingFromId and pendingReason after completion', () => {
    const next = wsReducer(
      swappingState,
      delta({
        event: 'failover_completed',
        failover_id: 'fo-001',
        to: TO_ACCOUNT,
        swap_latency_ms: 42,
      }),
    )
    expect(next.failoverPendingFromId).toBeNull()
    expect(next.failoverPendingReason).toBeNull()
  })
})

// ── failover_failed ───────────────────────────────────────────────────────────

describe('failover_failed', () => {
  it('transitions to monitoring and sets error toast', () => {
    const swappingState: WsAppState = {
      ...initialWsState,
      failoverState: 'swapping',
      failoverPendingFromId: 'acc-1',
    }
    const next = wsReducer(
      swappingState,
      delta({
        event: 'failover_failed',
        failover_id: 'fo-003',
        reason: 'Không thể ghi credential file',
      }),
    )
    expect(next.failoverState).toBe('monitoring')
    expect(next.failoverToastType).toBe('failover-error')
    expect(next.failoverToastNonce).toBeGreaterThan(swappingState.failoverToastNonce)
    expect(next.failoverPendingFromId).toBeNull()
  })
})

// ── all_accounts_exhausted ────────────────────────────────────────────────────

describe('all_accounts_exhausted', () => {
  const retryAt = new Date(Date.now() + 3600 * 1000).toISOString()

  it('transitions to waiting state with retry info', () => {
    const next = wsReducer(
      initialWsState,
      delta({
        event: 'all_accounts_exhausted',
        next_retry_at: retryAt,
        retry_account: TO_ACCOUNT,
        retry_attempt: 1,
        max_retries: 3,
      }),
    )
    expect(next.failoverState).toBe('waiting')
    expect(next.failoverNextRetryAt).toBe(retryAt)
    expect(next.failoverRetryAccount?.id).toBe('acc-2')
    expect(next.failoverRetryAttempt).toBe(1)
    expect(next.failoverMaxRetries).toBe(3)
  })

  it('sets failover-error toast type', () => {
    const next = wsReducer(
      initialWsState,
      delta({
        event: 'all_accounts_exhausted',
        next_retry_at: retryAt,
        retry_account: TO_ACCOUNT,
        retry_attempt: 0,
        max_retries: 3,
      }),
    )
    expect(next.failoverToastType).toBe('failover-error')
    expect(next.failoverToastNonce).toBeGreaterThan(initialWsState.failoverToastNonce)
  })
})

// ── retry_success ─────────────────────────────────────────────────────────────

describe('retry_success', () => {
  it('resets to idle and clears retry info', () => {
    const waitingState: WsAppState = {
      ...initialWsState,
      failoverState: 'waiting',
      failoverNextRetryAt: new Date().toISOString(),
      failoverRetryAccount: TO_ACCOUNT,
      failoverRetryAttempt: 2,
    }
    const next = wsReducer(
      waitingState,
      delta({ event: 'retry_success', account: TO_ACCOUNT }),
    )
    expect(next.failoverState).toBe('idle')
    expect(next.failoverNextRetryAt).toBeNull()
    expect(next.failoverRetryAccount).toBeNull()
    expect(next.failoverRetryAttempt).toBe(0)
    expect(next.failoverToastType).toBe('failover')
    expect(next.failoverToastMessage).toContain('OAuth (Imported)')
  })
})

// ── retry_cancelled_by_manual ─────────────────────────────────────────────────

describe('retry_cancelled_by_manual', () => {
  it('resets to idle and clears retry info without toast', () => {
    const waitingState: WsAppState = {
      ...initialWsState,
      failoverState: 'waiting',
      failoverNextRetryAt: new Date().toISOString(),
      failoverRetryAccount: FROM_ACCOUNT,
      failoverRetryAttempt: 1,
    }
    const nonceBefore = waitingState.failoverToastNonce
    const next = wsReducer(
      waitingState,
      delta({
        event: 'retry_cancelled_by_manual',
        activated: TO_ACCOUNT,
      }),
    )
    expect(next.failoverState).toBe('idle')
    expect(next.failoverNextRetryAt).toBeNull()
    expect(next.failoverRetryAccount).toBeNull()
    expect(next.failoverRetryAttempt).toBe(0)
    // Không có toast khi cancel thủ công
    expect(next.failoverToastNonce).toBe(nonceBefore)
  })
})

// ── failover_paused ───────────────────────────────────────────────────────────

describe('failover_paused', () => {
  it('transitions to paused state', () => {
    const next = wsReducer(
      initialWsState,
      delta({
        event: 'failover_paused',
        reason: 'api_wide_suspected',
        backoff_until: new Date(Date.now() + 600 * 1000).toISOString(),
      }),
    )
    expect(next.failoverState).toBe('paused')
  })
})

// ── wait_retry_tick ───────────────────────────────────────────────────────────

describe('wait_retry_tick', () => {
  it('returns same state reference (FE self-calculates countdown)', () => {
    const result = wsReducer(
      initialWsState,
      delta({ event: 'wait_retry_tick', seconds_left: 120 }),
    )
    // Anti-flicker: must be same reference
    expect(result).toBe(initialWsState)
  })
})

// ── Anti-flicker: non-failover delta when no session matches ──────────────────

describe('anti-flicker', () => {
  it('returns same state reference for agent_update with no matching session', () => {
    const result = wsReducer(
      initialWsState,
      delta({
        event: 'agent_update',
        session_id: 'non-existent-session',
        last_event_at: new Date().toISOString(),
        tokens_added: { input: 100 },
      }),
    )
    expect(result).toBe(initialWsState)
  })

  it('returns same state reference for unknown delta event', () => {
    const result = wsReducer(
      initialWsState,
      delta({ event: 'unknown_future_event' }),
    )
    expect(result).toBe(initialWsState)
  })
})
