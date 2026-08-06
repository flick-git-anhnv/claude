import type { Account } from '../../types'

interface AccountCardProps {
  account: Account
  onActivate: (id: string) => void
  onCopy: (id: string) => void
  onDelete: (id: string) => void
}

/** Format seconds remaining into "X ngày" / "Xh Ym" / "Hết hạn". */
function fmtRemaining(sec: number): string {
  if (sec <= 0) return 'Hết hạn'
  const days = Math.floor(sec / 86400)
  if (days >= 1) return `Còn ${days} ngày`
  const hours = Math.floor(sec / 3600)
  const mins = Math.floor((sec % 3600) / 60)
  if (hours >= 1) return `Còn ${hours}h ${mins}m`
  return `Còn ${mins} phút`
}

export default function AccountCard({ account, onActivate, onCopy, onDelete }: AccountCardProps) {
  const isOAuth = account.kind === 'oauth_session'
  const maskedDisplay = isOAuth ? account.oauth_masked : account.key_masked

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
        <div className="flex items-center gap-2 min-w-0 flex-wrap">
          {account.is_active && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-orange text-white shrink-0">
              ★ ACTIVE
            </span>
          )}

          {/* Kind badge */}
          {isOAuth ? (
            <span className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-navy text-white shrink-0">
              OAuth
            </span>
          ) : (
            <span className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-orange/20 text-kz-orange shrink-0">
              API Key
            </span>
          )}

          <span className="text-sm font-semibold text-kz-navy truncate">
            {account.name}
          </span>
        </div>
      </div>

      {/* Token display */}
      <div className="mb-3 flex flex-col gap-1">
        <span
          className="font-mono text-caption text-kz-text select-none"
          aria-label={`Token (masked): ${maskedDisplay}`}
        >
          {maskedDisplay}
        </span>

        {/* OAuth-specific status badges */}
        {isOAuth && (
          <div className="flex flex-wrap gap-2 mt-1">
            {account.needs_relogin ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-badge text-caption font-semibold bg-red-100 text-red-700">
                ⚠ Cần đăng nhập lại
              </span>
            ) : account.refresh_expires_in_sec !== undefined ? (
              <span className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption text-kz-navy-mid bg-kz-navy-light/20">
                {fmtRemaining(account.refresh_expires_in_sec)}
              </span>
            ) : null}
          </div>
        )}
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

        {/* Copy API key only for api_key accounts */}
        {!isOAuth && (
          <button
            onClick={() => onCopy(account.id)}
            className="px-3 py-1.5 text-caption font-semibold text-kz-navy border border-kz-navy hover:bg-kz-navy-light/40 rounded-btn transition-colors"
            aria-label={`Copy API key cho tài khoản ${account.name}`}
          >
            Copy API key
          </button>
        )}

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
