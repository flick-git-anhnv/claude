import { useNavigate } from 'react-router-dom'
import { useWsState } from '../../contexts/WsContext'
import { truncate } from '../../utils/format'

export default function AppHeader() {
  const navigate = useNavigate()
  const { activeAccount } = useWsState()

  return (
    <header
      className="flex items-center justify-between px-6 bg-kz-navy text-white shrink-0"
      style={{ height: 'var(--header-height)' }}
    >
      {/* Left: Logo + Title */}
      <div className="flex items-center gap-3">
        {/* KZTEK logo placeholder — replace with <img src="/kztek-logo.png"> when asset available */}
        <div
          className="flex items-center justify-center w-8 h-8 bg-kz-orange rounded font-bold text-white text-xs shrink-0"
          aria-hidden="true"
        >
          KZ
        </div>
        <span className="text-h1 font-semibold tracking-tight">Agent Dashboard</span>
      </div>

      {/* Right: Account indicator */}
      <div className="flex items-center">
        {activeAccount ? (
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-kz-green shrink-0" aria-hidden="true" />
            <div className="text-right">
              <div
                className="text-sm font-semibold text-white leading-tight"
                title={activeAccount.name}
              >
                {truncate(activeAccount.name, 30)}
              </div>
              <div className="font-mono text-caption text-kz-navy-light leading-tight">
                {activeAccount.key_masked}
              </div>
            </div>
          </div>
        ) : (
          <button
            onClick={() => navigate('/accounts')}
            className="flex items-center gap-2 px-3 py-1.5 bg-kz-orange text-white text-sm font-medium rounded-badge hover:bg-orange-600 transition-colors"
            aria-label="Chưa có tài khoản active — vào Account Manager để đặt"
          >
            <span aria-hidden="true">!</span>
            <span>Chưa có tài khoản active</span>
          </button>
        )}
      </div>
    </header>
  )
}
