import { useEffect, useState } from 'react'
import type { RangeFilter, TokenSummaryResponse } from '../types'
import { useApi } from '../hooks/useApi'
import { fmtNum } from '../utils/format'
import FilterBar from '../components/tokens/FilterBar'
import TokenBarChart from '../components/tokens/TokenBarChart'
import SummaryCard from '../components/tokens/SummaryCard'

const RANGE_LABELS: Record<RangeFilter, string> = {
  '7d': '7 ngày qua',
  '30d': '30 ngày qua',
  '12w': '12 tuần qua',
  '6m': '6 tháng qua',
}

export default function TokenAnalyticsPage() {
  const { getTokensSummary } = useApi()
  const [range, setRange] = useState<RangeFilter>('30d')
  const [data, setData] = useState<TokenSummaryResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    setError('')
    getTokensSummary(range)
      .then(setData)
      .catch(err => setError(err instanceof Error ? err.message : 'Lỗi tải dữ liệu'))
      .finally(() => setLoading(false))
  }, [range])

  const totals = data?.totals

  return (
    <div>
      {/* Page title */}
      <h2 className="text-h2 text-kz-navy mb-4">Token Usage</h2>

      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-4 mb-5">
        <FilterBar active={range} onChange={setRange} />
        <span className="text-caption text-kz-navy-mid ml-auto">
          {RANGE_LABELS[range]}
        </span>
      </div>

      {/* Error */}
      {error && (
        <div className="p-3 bg-kz-error-bg border-l-4 border-kz-red rounded-sm mb-4 text-sm text-kz-red">
          {error}
        </div>
      )}

      {/* Chart */}
      <div className="border border-kz-gray rounded-card p-4 mb-5">
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <span className="text-caption text-kz-navy-mid animate-pulse">Đang tải dữ liệu...</span>
          </div>
        ) : (
          <TokenBarChart data={data?.buckets ?? []} />
        )}
      </div>

      {/* Summary cards */}
      {totals && (
        <div className="flex gap-4 mb-6 flex-wrap">
          <SummaryCard
            label="Tổng Input"
            value={totals.input}
            unit="tokens"
            sublabel={RANGE_LABELS[range]}
          />
          <SummaryCard
            label="Tổng Output"
            value={totals.output}
            unit="tokens"
            sublabel={RANGE_LABELS[range]}
          />
          <SummaryCard
            label="Tổng Sessions"
            value={totals.sessions}
            unit="sessions"
            sublabel={RANGE_LABELS[range]}
          />
        </div>
      )}

      {/* Session detail table */}
      {data && data.buckets.length > 0 && (
        <div>
          <h3 className="text-h2 text-kz-navy mb-3">Chi tiết theo bucket</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr>
                  {['Khoảng', 'Input', 'Output', 'Cache Write', 'Cache Read', 'Tổng'].map(h => (
                    <th
                      key={h}
                      scope="col"
                      className="px-3 py-2 text-left text-caption font-semibold text-white bg-kz-navy"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.buckets.map((b, i) => {
                  const total = b.input + b.output + b.cache_creation + b.cache_read
                  return (
                    <tr
                      key={b.label}
                      className={`border-b border-kz-gray hover:bg-kz-navy-light/20 ${i % 2 === 1 ? 'bg-gray-50' : ''}`}
                    >
                      <td className="px-3 py-2 text-kz-navy font-semibold">{b.label}</td>
                      <td className="px-3 py-2 font-mono text-right">{fmtNum(b.input)}</td>
                      <td className="px-3 py-2 font-mono text-right">{fmtNum(b.output)}</td>
                      <td className="px-3 py-2 font-mono text-right">{fmtNum(b.cache_creation)}</td>
                      <td className="px-3 py-2 font-mono text-right">{fmtNum(b.cache_read)}</td>
                      <td className="px-3 py-2 font-mono text-right font-semibold text-kz-navy">
                        {fmtNum(total)}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
