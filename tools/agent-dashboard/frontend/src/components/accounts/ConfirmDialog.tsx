import { useEffect, useRef } from 'react'

interface ConfirmDialogProps {
  title: string
  message: string
  confirmLabel?: string
  confirmDanger?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmDialog({
  title,
  message,
  confirmLabel = 'Xác nhận',
  confirmDanger = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const cancelRef = useRef<HTMLButtonElement>(null)

  // Focus trap: focus cancel button on mount
  useEffect(() => {
    cancelRef.current?.focus()
  }, [])

  // Close on Escape
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onCancel()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onCancel])

  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      onClick={e => { if (e.target === e.currentTarget) onCancel() }}
    >
      <div className="bg-white rounded-card shadow-xl w-full max-w-md">
        {/* Header */}
        <div className="px-6 pt-5 pb-4 border-b border-kz-gray">
          <h3 id="confirm-dialog-title" className="text-h2 text-kz-navy">
            {title}
          </h3>
        </div>

        {/* Body */}
        <div className="px-6 py-4 text-sm text-kz-text">
          {message}
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-3 px-6 pb-5">
          <button
            ref={cancelRef}
            onClick={onCancel}
            className="px-4 py-2 text-sm text-kz-navy-mid hover:text-kz-navy transition-colors"
          >
            Huỷ
          </button>
          <button
            onClick={onConfirm}
            className={[
              'px-4 py-2 text-sm font-semibold text-white rounded-btn transition-colors',
              confirmDanger
                ? 'bg-kz-red hover:bg-red-600'
                : 'bg-kz-navy hover:bg-kz-navy-mid',
            ].join(' ')}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
