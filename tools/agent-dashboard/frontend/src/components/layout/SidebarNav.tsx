import { useNavigate, useLocation } from 'react-router-dom'
import { useWsState } from '../../contexts/WsContext'
import WebSocketStatus from './WebSocketStatus'

interface NavItem {
  path: string
  label: string
  icon: string
  ariaLabel: string
}

const NAV_ITEMS: NavItem[] = [
  { path: '/agents',   label: 'Agents',          icon: '⬛', ariaLabel: 'Agent Status Panel' },
  { path: '/tokens',   label: 'Token Usage',      icon: '📊', ariaLabel: 'Token Analytics' },
  { path: '/sessions', label: 'Session History',  icon: '🕐', ariaLabel: 'Session History' },
  { path: '/accounts', label: 'Account Manager',  icon: '👤', ariaLabel: 'Account Manager' },
]

export default function SidebarNav() {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { wsStatus } = useWsState()

  return (
    <nav
      className="flex flex-col h-full w-sidebar bg-kz-navy shrink-0"
      aria-label="Main navigation"
    >
      <ul className="flex-1 pt-2" role="list">
        {NAV_ITEMS.map(item => {
          const isActive = pathname === item.path || (pathname === '/' && item.path === '/agents')
          return (
            <li key={item.path}>
              <button
                onClick={() => navigate(item.path)}
                aria-label={item.ariaLabel}
                aria-current={isActive ? 'page' : undefined}
                className={[
                  'w-full flex items-center gap-3 px-4 py-3 text-sm text-left transition-colors duration-150',
                  isActive
                    ? 'bg-kz-navy-mid text-white border-l-[3px] border-kz-orange pl-[13px]'
                    : 'text-kz-navy-light hover:bg-kz-navy-mid/50',
                ].join(' ')}
              >
                <span className="text-base w-4 text-center shrink-0" aria-hidden="true">
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </button>
            </li>
          )
        })}
      </ul>

      {/* Divider */}
      <div className="mx-3 border-t border-kz-navy-mid/40 my-2" />

      {/* WebSocket status */}
      <WebSocketStatus status={wsStatus} />
      <div className="pb-4" />
    </nav>
  )
}
