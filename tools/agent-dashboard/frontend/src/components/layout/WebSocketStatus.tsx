import type { WsStatus } from '../../types'

interface WebSocketStatusProps {
  status: WsStatus
}

const config: Record<WsStatus, { dot: string; label: string }> = {
  connecting:    { dot: 'bg-kz-orange-light', label: 'Đang kết nối...' },
  connected:     { dot: 'bg-kz-green',        label: 'Live' },
  reconnecting:  { dot: 'bg-kz-orange-light', label: 'Đang kết nối lại...' },
  disconnected:  { dot: 'bg-kz-red',          label: 'Mất kết nối' },
}

export default function WebSocketStatus({ status }: WebSocketStatusProps) {
  const { dot, label } = config[status]
  return (
    <div className="flex items-center gap-2 px-3 py-2">
      <span className={`inline-block w-2 h-2 rounded-full shrink-0 ${dot} ${status === 'reconnecting' || status === 'connecting' ? 'animate-pulse' : ''}`} />
      <span className="text-caption text-kz-navy-light">{label}</span>
    </div>
  )
}
