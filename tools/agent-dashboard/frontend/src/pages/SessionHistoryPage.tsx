import { useEffect, useState } from 'react'
import type { HistorySession } from '../types'
import { useApi } from '../hooks/useApi'
import SessionTable from '../components/sessions/SessionTable'

const PAGE_SIZE = 20

export default function SessionHistoryPage() {
  const { getSessionsHistory } = useApi()
  const [sessions, setSessions] = useState<HistorySession[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Date filter
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [filterApplied, setFilterApplied] = useState({ from: '', to: '' })

  function loadPage(p: number, from: string, to: string) {
    setLoading(true)
    setError('')
    getSessionsHistory({
      limit: PAGE_SIZE,
      offset: (p - 1) * PAGE_SIZE,
      from: from || undefined,
      to: to || undefined,
    })
      .then(res => {
        setSessions(res.items)
        setTotal(res.total)
      })
      .catch(err => setError(err instanceof Error ? err.message : 'Lỗi tải dữ liệu'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadPage(1, '', '')
  }, [])

  function handleFilter(e: React.FormEvent) {
    e.preventDefault()
    setPage(1)
    setFilterApplied({ from: fromDate, to: toDate })
    loadPage(1, fromDate, toDate)
  }

  function handlePageChange(newPage: number) {
    setPage(newPage)
    loadPage(newPage, filterApplied.from, filterApplied.to)
  }

  return (
    <div>
      <h2 className="text-h2 text-kz-navy mb-4">Lịch sử Session</h2>

      {/* Filter bar */}
      <form onSubmit={handleFilter} className="flex flex-wrap items-end gap-3 mb-5">
        <div>
          <label className="block text-caption text-kz-navy-mid mb-1" htmlFor="hist-from">
            Từ ngày
          </label>
          <input
            id="hist-from"
            type="date"
            value={fromDate}
            onChange={e => setFromDate(e.target.value)}
            className="px-3 py-1.5 text-sm border border-kz-gray rounded-btn outline-none focus:border-kz-navy"
          />
        </div>
        <div>
          <label className="block text-caption text-kz-navy-mid mb-1" htmlFor="hist-to">
            Đến ngày
          </label>
          <input
            id="hist-to"
            type="date"
            value={toDate}
            onChange={e => setToDate(e.target.value)}
            className="px-3 py-1.5 text-sm border border-kz-gray rounded-btn outline-none focus:border-kz-navy"
          />
        </div>
        <button
          type="submit"
          className="px-4 py-1.5 text-sm font-semibold text-white bg-kz-navy hover:bg-kz-navy-mid rounded-btn transition-colors"
        >
          Lọc
        </button>
        {(filterApplied.from || filterApplied.to) && (
          <button
            type="button"
            onClick={() => {
              setFromDate(''); setToDate('')
              setFilterApplied({ from: '', to: '' })
              setPage(1)
              loadPage(1, '', '')
            }}
            className="px-3 py-1.5 text-sm text-kz-navy-mid hover:text-kz-navy"
          >
            Xoá bộ lọc
          </button>
        )}
        <span className="ml-auto text-caption text-kz-navy-mid self-center">
          {!loading && `Hiển thị ${total} session`}
        </span>
      </form>

      {/* Error */}
      {error && (
        <div className="p-3 bg-kz-error-bg border-l-4 border-kz-red rounded-sm mb-4 text-sm text-kz-red">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <span className="text-caption text-kz-navy-mid animate-pulse">Đang tải...</span>
        </div>
      ) : (
        <SessionTable
          sessions={sessions}
          total={total}
          page={page}
          pageSize={PAGE_SIZE}
          onPageChange={handlePageChange}
        />
      )}
    </div>
  )
}
