/**
 * MockWebSocket — thay thế WebSocket thật trong VITE_MOCK=true.
 * Gửi snapshot khi kết nối, sau đó push delta mỗi 5s.
 */
import type { WsSnapshot, DeltaEvent, Session } from '../types'
import { MOCK_SESSIONS, MOCK_ACCOUNTS } from '../api/mockData'

const activeAccount = MOCK_ACCOUNTS.find(a => a.is_active) ?? null

function buildSnapshot(): WsSnapshot {
  return {
    sessions: MOCK_SESSIONS.filter(s => s.state !== 'Ended'),
    active_account: activeAccount
      ? {
          id: activeAccount.id,
          name: activeAccount.name,
          kind: activeAccount.kind ?? 'api_key',
          key_masked: activeAccount.key_masked,
        }
      : null,
    watcher_alive: true,
  }
}

function buildDelta(sessions: Session[]): DeltaEvent {
  const runningSessions = sessions.filter(s => s.state === 'Running')
  if (runningSessions.length === 0) return { event: 'watcher_status', alive: true }

  const target = runningSessions[Math.floor(Math.random() * runningSessions.length)]
  const events: DeltaEvent[] = [
    {
      event: 'agent_update',
      session_id: target.session_id,
      last_event_at: new Date().toISOString(),
      tool_use: ['Read', 'Write', 'Bash', 'Grep', 'Glob'][Math.floor(Math.random() * 5)],
      tokens_added: {
        input: Math.floor(Math.random() * 500) + 50,
        output: Math.floor(Math.random() * 150) + 10,
        cache_creation: Math.floor(Math.random() * 20),
        cache_read: Math.floor(Math.random() * 200),
      },
    },
    {
      event: 'token_update',
      session_id: target.session_id,
      delta: { input: 200, output: 60 },
      cumulative: {
        input: target.token_total.input + 200,
        output: target.token_total.output + 60,
        cache_creation: target.token_total.cache_creation,
        cache_read: target.token_total.cache_read,
      },
    },
  ]
  return events[Math.floor(Math.random() * events.length)]
}

type WsEventListener = ((e: Event) => void) | ((e: MessageEvent) => void) | null

export class MockWebSocket extends EventTarget {
  readonly url: string
  readyState: number = 0 // CONNECTING
  private _deltaTimer: ReturnType<typeof setInterval> | null = null
  private _sessions: Session[] = []

  // Standard WS constants
  static readonly CONNECTING = 0
  static readonly OPEN = 1
  static readonly CLOSING = 2
  static readonly CLOSED = 3

  onopen: WsEventListener = null
  onmessage: WsEventListener = null
  onclose: WsEventListener = null
  onerror: WsEventListener = null

  constructor(url: string) {
    super()
    this.url = url
    this._sessions = MOCK_SESSIONS.filter(s => s.state !== 'Ended')

    // Simulate connection delay
    setTimeout(() => {
      this.readyState = 1 // OPEN
      const openEvt = new Event('open')
      this.dispatchEvent(openEvt)
      if (this.onopen) (this.onopen as (e: Event) => void)(openEvt)

      // Send snapshot immediately
      this._sendMessage({ type: 'snapshot', ts: new Date().toISOString(), payload: buildSnapshot() })

      // Send deltas periodically
      this._deltaTimer = setInterval(() => {
        if (this.readyState !== 1) return
        const delta = buildDelta(this._sessions)
        this._sendMessage({ type: 'delta', ts: new Date().toISOString(), payload: delta })
      }, 4000)
    }, 300)
  }

  private _sendMessage(data: unknown): void {
    const evt = new MessageEvent('message', { data: JSON.stringify(data) })
    this.dispatchEvent(evt)
    if (this.onmessage) (this.onmessage as (e: MessageEvent) => void)(evt)
  }

  send(data: string): void {
    try {
      const msg = JSON.parse(data)
      if (msg.type === 'ping') {
        setTimeout(() => {
          this._sendMessage({ type: 'pong', ts: new Date().toISOString(), payload: {} })
        }, 20)
      }
    } catch {
      // ignore malformed
    }
  }

  close(): void {
    this.readyState = 3 // CLOSED
    if (this._deltaTimer) {
      clearInterval(this._deltaTimer)
      this._deltaTimer = null
    }
    const closeEvt = new CloseEvent('close', { wasClean: true, code: 1000 })
    this.dispatchEvent(closeEvt)
    if (this.onclose) (this.onclose as (e: Event) => void)(closeEvt)
  }

  addEventListener(type: string, listener: EventListenerOrEventListenerObject | null, options?: boolean | AddEventListenerOptions): void {
    super.addEventListener(type, listener, options)
  }

  removeEventListener(type: string, listener: EventListenerOrEventListenerObject | null, options?: boolean | EventListenerOptions): void {
    super.removeEventListener(type, listener, options)
  }
}
