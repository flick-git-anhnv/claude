import { createContext, useCallback, useContext, useReducer } from 'react'

export type ToastType = 'default' | 'failover' | 'failover-error'

export interface Toast {
  id: string
  message: string
  /** ms; 0 = không auto-dismiss (user phải bấm ✕) */
  duration: number
  type: ToastType
}

interface ToastState {
  toasts: Toast[]
}

type ToastAction =
  | { type: 'ADD'; toast: Toast }
  | { type: 'REMOVE'; id: string }

function toastReducer(state: ToastState, action: ToastAction): ToastState {
  switch (action.type) {
    case 'ADD':
      return { toasts: [...state.toasts, action.toast] }
    case 'REMOVE':
      return { toasts: state.toasts.filter(t => t.id !== action.id) }
    default:
      return state
  }
}

interface ToastContextValue {
  toasts: Toast[]
  showToast: (message: string, duration?: number) => void
  showFailoverToast: (message: string, type?: ToastType, duration?: number) => void
  removeToast: (id: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(toastReducer, { toasts: [] })

  const removeToast = useCallback((id: string) => {
    dispatch({ type: 'REMOVE', id })
  }, [])

  const showToast = useCallback((message: string, duration = 3000) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
    dispatch({ type: 'ADD', toast: { id, message, duration, type: 'default' } })
    if (duration > 0) {
      setTimeout(() => dispatch({ type: 'REMOVE', id }), duration)
    }
  }, [])

  /**
   * Sprint 7: Toast cho failover events.
   * type='failover'       → cam, auto-dismiss sau duration (mặc định 15s)
   * type='failover-error' → đỏ, KHÔNG auto-dismiss (duration=0)
   */
  const showFailoverToast = useCallback(
    (message: string, type: ToastType = 'failover', duration?: number) => {
      const id = `toast-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
      const effectiveDuration = duration !== undefined
        ? duration
        : type === 'failover-error' ? 0 : 15_000
      dispatch({ type: 'ADD', toast: { id, message, duration: effectiveDuration, type } })
      if (effectiveDuration > 0) {
        setTimeout(() => dispatch({ type: 'REMOVE', id }), effectiveDuration)
      }
    },
    [],
  )

  return (
    <ToastContext.Provider value={{ toasts: state.toasts, showToast, showFailoverToast, removeToast }}>
      {children}
    </ToastContext.Provider>
  )
}

export function useToast(): ToastContextValue {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
