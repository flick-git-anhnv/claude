interface BannerAlertProps {
  type: 'info' | 'warning' | 'error'
  message: string
  action?: { label: string; onClick: () => void }
  onClose?: () => void
}

const styles = {
  info:    'bg-blue-50 border-blue-400 text-blue-800',
  warning: 'bg-kz-warning-bg border-kz-orange-light text-kz-text',
  error:   'bg-kz-error-bg border-kz-red text-kz-red',
}

const icons = {
  info:    'ℹ',
  warning: '!',
  error:   '!',
}

export default function BannerAlert({ type, message, action, onClose }: BannerAlertProps) {
  return (
    <div
      className={`flex items-start gap-3 px-4 py-3 border-l-4 rounded-sm mb-4 ${styles[type]}`}
      role="alert"
    >
      <span className="font-bold text-base leading-none mt-0.5 shrink-0">{icons[type]}</span>
      <span className="flex-1 text-sm">{message}</span>
      {action && (
        <button
          onClick={action.onClick}
          className="text-sm font-semibold underline hover:opacity-70 shrink-0"
        >
          {action.label}
        </button>
      )}
      {onClose && (
        <button
          onClick={onClose}
          className="shrink-0 opacity-60 hover:opacity-100 text-base leading-none"
          aria-label="Đóng thông báo"
        >
          ✕
        </button>
      )}
    </div>
  )
}
