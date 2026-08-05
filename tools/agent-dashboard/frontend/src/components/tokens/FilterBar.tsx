import type { RangeFilter } from '../../types'

interface FilterBarProps {
  active: RangeFilter
  onChange: (range: RangeFilter) => void
}

const RANGES: { value: RangeFilter; label: string }[] = [
  { value: '7d',  label: '7 ngày' },
  { value: '30d', label: '30 ngày' },
  { value: '12w', label: '12 tuần' },
  { value: '6m',  label: '6 tháng' },
]

export default function FilterBar({ active, onChange }: FilterBarProps) {
  return (
    <div className="flex items-center gap-2 flex-wrap">
      {RANGES.map(r => (
        <button
          key={r.value}
          onClick={() => onChange(r.value)}
          aria-pressed={active === r.value}
          className={[
            'px-3 py-1.5 text-sm rounded-btn border transition-colors',
            active === r.value
              ? 'bg-kz-navy text-white border-kz-navy'
              : 'bg-kz-navy-light/30 text-kz-navy border-kz-navy-light hover:bg-kz-navy-light/60',
          ].join(' ')}
        >
          {r.label}
        </button>
      ))}
    </div>
  )
}
