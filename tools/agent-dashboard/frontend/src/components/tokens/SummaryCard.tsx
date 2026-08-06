import { fmtNum } from '../../utils/format'

interface SummaryCardProps {
  label: string
  value: number
  unit: string
  sublabel?: string
}

export default function SummaryCard({ label, value, unit, sublabel }: SummaryCardProps) {
  return (
    <div className="border border-kz-gray rounded-card p-4 bg-white flex-1 min-w-0">
      <div className="text-caption text-kz-navy-mid mb-1">{label}</div>
      <div className="text-[24px] font-semibold text-kz-navy font-mono leading-tight">
        {fmtNum(value)}
      </div>
      <div className="text-caption text-kz-navy-mid mt-0.5">{unit}</div>
      {sublabel && <div className="text-caption text-kz-gray mt-1">{sublabel}</div>}
    </div>
  )
}
