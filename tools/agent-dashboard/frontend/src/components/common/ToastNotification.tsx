import { useToast } from '../../contexts/ToastContext'
import type { Toast } from '../../contexts/ToastContext'

function toastStyle(toast: Toast): string {
  switch (toast.type) {
    case 'failover':
      return 'bg-kz-orange text-white'
    case 'failover-error':
      return 'bg-kz-error-bg border border-kz-red text-kz-red'
    default:
      return 'bg-kz-navy text-white'
  }
}

function toastIcon(toast: Toast): string {
  switch (toast.type) {
    case 'failover':       return '↺'
    case 'failover-error': return '!'
    default:               return '✓'
  }
}

function toastIconStyle(toast: Toast): string {
  switch (toast.type) {
    case 'failover':       return 'text-white font-bold'
    case 'failover-error': return 'text-kz-red font-bold'
    default:               return 'text-kz-green font-bold'
  }
}

function ariaRole(toast: Toast): 'status' | 'alert' {
  return toast.type === 'failover-error' ? 'alert' : 'status'
}

export default function ToastNotification() {
  const { toasts, removeToast } = useToast()

  if (toasts.length === 0) return null

  return (
    <div
      className="fixed bottom-6 right-6 flex flex-col gap-2 z-50"
      aria-atomic="false"
    >
      {toasts.map(toast => (
        <div
          key={toast.id}
          role={ariaRole(toast)}
          aria-live={toast.type === 'failover-error' ? 'assertive' : 'polite'}
          className={[
            'flex items-center gap-3 px-4 py-3 text-sm rounded-btn shadow-lg max-w-sm animate-fade-in',
            toastStyle(toast),
          ].join(' ')}
        >
          <span className={`${toastIconStyle(toast)} shrink-0`} aria-hidden="true">
            {toastIcon(toast)}
          </span>
          <span className="flex-1">{toast.message}</span>
          <button
            onClick={() => removeToast(toast.id)}
            className="opacity-60 hover:opacity-100 text-base leading-none shrink-0"
            aria-label="Đóng thông báo failover"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}
