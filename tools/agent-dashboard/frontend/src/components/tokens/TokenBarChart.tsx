import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer,
} from 'recharts'
import type { TokenBucket } from '../../types'
import { fmtNum } from '../../utils/format'

interface TokenBarChartProps {
  data: TokenBucket[]
}

// Brand KZTEK colors per series (TDD §11 handoff — đúng thứ tự)
const SERIES = [
  { key: 'input',          name: 'Input Tokens',        color: '#251C53' }, // Navy dark
  { key: 'output',         name: 'Output Tokens',        color: '#F05922' }, // Cam
  { key: 'cache_creation', name: 'Cache Write',          color: '#4A3F8C' }, // Navy mid
  { key: 'cache_read',     name: 'Cache Read',           color: '#B8B3D6' }, // Navy light
]

interface TooltipProps {
  active?: boolean
  payload?: { name: string; value: number; color: string }[]
  label?: string
}

function CustomTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-kz-gray rounded-card p-3 shadow-md text-sm">
      <p className="font-semibold text-kz-navy mb-1">{label}</p>
      {payload.map(p => (
        <div key={p.name} className="flex items-center justify-between gap-4">
          <span className="flex items-center gap-1.5">
            <span
              className="inline-block w-2.5 h-2.5 rounded-sm shrink-0"
              style={{ backgroundColor: p.color }}
            />
            <span className="text-kz-text">{p.name}:</span>
          </span>
          <span className="font-mono font-semibold text-kz-navy">{fmtNum(p.value)}</span>
        </div>
      ))}
    </div>
  )
}

export default function TokenBarChart({ data }: TokenBarChartProps) {
  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <div className="text-5xl text-kz-navy-light mb-3" aria-hidden="true">📊</div>
        <p className="text-sm text-kz-navy-mid">Không có dữ liệu trong khoảng thời gian này</p>
      </div>
    )
  }

  return (
    <div style={{ height: 280 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 4, right: 8, left: 8, bottom: 4 }}
          barCategoryGap="30%"
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#CBCBCB" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: '#4A3F8C' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#4A3F8C' }}
            axisLine={false}
            tickLine={false}
            tickFormatter={v => v >= 1000 ? `${(v / 1000).toFixed(0)}K` : String(v)}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
            iconType="square"
          />
          {SERIES.map(s => (
            <Bar
              key={s.key}
              dataKey={s.key}
              name={s.name}
              fill={s.color}
              stackId="tokens"
              radius={s.key === 'input' ? [4, 4, 0, 0] : undefined}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
