import { useToast } from '../../contexts/ToastContext'

export default function ToastNotification() {
  const { toasts, removeToast } = useToast()

  if (toasts.length === 0) return null

  return (
    <div
      className="fixed bottom-6 right-6 flex flex-col gap-2 z-50"
      role="status"
      aria-live="polite"
      aria-atomic="false"
    >
      {toasts.map(toast => (
        <div
          key={toast.id}
          className="flex items-center gap-3 px-4 py-3 bg-kz-navy text-white text-sm rounded-btn shadow-lg max-w-xs animate-fade-in"
        >
          <span className="text-kz-green font-bold">✓</span>
          <span className="flex-1">{toast.message}</span>
          <button
            onClick={() => removeToast(toast.id)}
            className="opacity-60 hover:opacity-100 text-base leading-none shrink-0"
            aria-label="Đóng thông báo"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  )
}
