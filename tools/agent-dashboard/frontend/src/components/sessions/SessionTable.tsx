import type { HistorySession } from '../../types'
import { fmtDateTime, fmtNum, truncate } from '../../utils/format'

interface SessionTableProps {
  sessions: HistorySession[]
  total: number
  page: number
  pageSize: number
  onPageChange: (page: number) => void
}

const STATUS_STYLE: Record<string, { text: string; dot: string }> = {
  Ended: { text: 'text-kz-green', dot: '●' },
  Idle:  { text: 'text-kz-orange-light', dot: '○' },
  Running: { text: 'text-kz-orange', dot: '●' },
}

export default function SessionTable({
  sessions, total, page, pageSize, onPageChange,
}: SessionTableProps) {
  const totalPages = Math.ceil(total / pageSize)

  if (sessions.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-sm text-kz-navy font-semibold">Chưa có lịch sử session</p>
        <p className="text-caption text-kz-navy-mid mt-1">
          Dữ liệu sẽ xuất hiện khi agent đầu tiên kết thúc
        </p>
      </div>
    )
  }

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm border-collapse" role="grid">
          <thead>
            <tr>
              {['Agent', 'Task / Session ID', 'Bắt đầu', 'Kết thúc', 'IN', 'OUT', 'Trạng thái'].map(h => (
                <th
                  key={h}
                  scope="col"
                  className="px-3 py-2.5 text-left text-caption font-semibold text-white bg-kz-navy first:rounded-tl-sm last:rounded-tr-sm"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sessions.map((s, i) => {
              const cfg = STATUS_STYLE[s.state] ?? STATUS_STYLE.Ended
              return (
                <tr
                  key={s.session_id}
                  className={`border-b border-kz-gray hover:bg-kz-navy-light/20 transition-colors ${i % 2 === 1 ? 'bg-gray-50' : 'bg-white'}`}
                >
                  <td className="px-3 py-2.5 font-semibold text-kz-navy whitespace-nowrap">
                    {s.agent_type}
                  </td>
                  <td
                    className="px-3 py-2.5 text-kz-text max-w-[200px]"
                    title={s.session_id}
                  >
                    <span className="block truncate">
                      {truncate(s.session_id, 28)}
                    </span>
                    <span className="text-caption text-kz-navy-mid">{s.project}</span>
                  </td>
                  <td className="px-3 py-2.5 text-kz-text whitespace-nowrap font-mono text-caption">
                    {fmtDateTime(s.started_at)}
                  </td>
                  <td
                    className="px-3 py-2.5 text-kz-text whitespace-nowrap font-mono text-caption"
                    title={s.state === 'Idle' ? 'Phiên kết thúc do không có activity trong 5 phút' : undefined}
                  >
                    {s.ended_at ? fmtDateTime(s.ended_at) : '—'}
                    {s.state === 'Idle' && <span className="ml-1 text-kz-orange-light">*</span>}
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-kz-navy">
                    {fmtNum(s.token_total.input)}
                  </td>
                  <td className="px-3 py-2.5 text-right font-mono text-kz-navy">
                    {fmtNum(s.token_total.output)}
                  </td>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    <span className={`inline-flex items-center gap-1 text-caption font-semibold ${cfg.text}`}>
                      <span>{cfg.dot}</span>
                      <span>{s.state}</span>
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 text-sm">
          <span className="text-caption text-kz-navy-mid">
            Hiển thị {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} / {total} session
          </span>
          <div className="flex items-center gap-1">
            <button
              onClick={() => onPageChange(page - 1)}
              disabled={page === 1}
              className="px-2 py-1 rounded border border-kz-gray text-kz-navy disabled:opacity-40 hover:bg-kz-navy-light/30"
              aria-label="Trang trước"
            >
              &lt;
            </button>
            <span className="px-3 text-kz-navy">
              Trang {page} / {totalPages}
            </span>
            <button
              onClick={() => onPageChange(page + 1)}
              disabled={page === totalPages}
              className="px-2 py-1 rounded border border-kz-gray text-kz-navy disabled:opacity-40 hover:bg-kz-navy-light/30"
              aria-label="Trang sau"
            >
              &gt;
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
