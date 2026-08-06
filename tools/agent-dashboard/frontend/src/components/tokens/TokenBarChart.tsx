import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ResponsiveContainer,
} from 'recharts'
import type { TokenBucket } from '../../types'
import { fmtNum } from '../../utils/format'

export interface SeriesConfig {
  key: string
  name: string
  color: string
}

// Chart 1: Input / Output — dùng màu brand Navy + Cam
export const SERIES_INPUT_OUTPUT: SeriesConfig[] = [
  { key: 'input',  name: 'Input Tokens',  color: '#251C53' }, // Navy dark
  { key: 'output', name: 'Output Tokens', color: '#F05922' }, // Cam
]

// Chart 2: Cache — dùng Navy mid + Cam nhạt để phân biệt rõ
export const SERIES_CACHE: SeriesConfig[] = [
  { key: 'cache_creation', name: 'Cache Write', color: '#4A3F8C' }, // Navy mid
  { key: 'cache_read',     name: 'Cache Read',  color: '#FFAA80' }, // Cam nhạt
]

interface TokenBarChartProps {
  data: TokenBucket[]
  series?: SeriesConfig[]
}

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

function fmtYAxis(v: number): string {
  if (v >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000) return `${(v / 1_000).toFixed(0)}K`
  return String(v)
}

export default function TokenBarChart({ data, series = SERIES_INPUT_OUTPUT }: TokenBarChartProps) {
  if (data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-48 text-center">
        <div className="text-4xl text-kz-navy-light mb-3" aria-hidden="true">📊</div>
        <p className="text-sm text-kz-navy-mid">Không có dữ liệu trong khoảng thời gian này</p>
      </div>
    )
  }

  return (
    <div style={{ height: 240 }}>
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
            tickFormatter={fmtYAxis}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
            iconType="square"
          />
          {series.map((s, idx) => (
            <Bar
              key={s.key}
              dataKey={s.key}
              name={s.name}
              fill={s.color}
              stackId="stack"
              radius={idx === series.length - 1 ? [4, 4, 0, 0] : undefined}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
