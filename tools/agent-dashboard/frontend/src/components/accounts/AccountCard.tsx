import type { Account } from '../../types'

interface AccountCardProps {
  account: Account
  onActivate: (id: string) => void
  onCopy: (id: string) => void
  onDelete: (id: string) => void
}

export default function AccountCard({ account, onActivate, onCopy, onDelete }: AccountCardProps) {
  return (
    <div
      className={[
        'border rounded-card p-4 bg-white',
        account.is_active ? 'border-kz-orange' : 'border-kz-gray',
      ].join(' ')}
      role="article"
      aria-label={`Tài khoản ${account.name}${account.is_active ? ', đang active' : ''}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2 min-w-0">
          {account.is_active && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-orange text-white shrink-0">
              ★ ACTIVE
            </span>
          )}
          <span className="text-sm font-semibold text-kz-navy truncate">
            {account.name}
          </span>
        </div>
      </div>

      {/* API key */}
      <div className="mb-3">
        <span
          className="font-mono text-caption text-kz-text select-none"
          aria-label={`API key (masked): ${account.key_masked}`}
        >
          {account.key_masked}
        </span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 flex-wrap">
        {!account.is_active && (
          <button
            onClick={() => onActivate(account.id)}
            className="px-3 py-1.5 text-caption font-semibold text-white bg-kz-navy hover:bg-kz-navy-mid rounded-btn transition-colors"
            aria-label={`Đặt ${account.name} làm tài khoản active`}
          >
            Đặt active
          </button>
        )}
        <button
          onClick={() => onCopy(account.id)}
          className="px-3 py-1.5 text-caption font-semibold text-kz-navy border border-kz-navy hover:bg-kz-navy-light/40 rounded-btn transition-colors"
          aria-label={`Copy API key cho tài khoản ${account.name}`}
        >
          Copy API key
        </button>
        <button
          onClick={() => onDelete(account.id)}
          className="px-3 py-1.5 text-caption font-semibold text-kz-red hover:bg-kz-red-bg rounded-btn transition-colors"
          aria-label={`Xóa tài khoản ${account.name}`}
        >
          Xóa
        </button>
      </div>
    </div>
  )
}
