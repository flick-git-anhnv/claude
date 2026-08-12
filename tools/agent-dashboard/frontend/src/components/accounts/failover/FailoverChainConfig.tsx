/**
 * FailoverChainConfig — Sprint 7 (S7-T24)
 *
 * Tab "Failover Chain" trong AccountManagerPage.
 * - Hiển thị ordered list account theo priority (GET /api/failover/chain)
 * - Checkbox include/exclude: chặn uncheck account cuối cùng (inline error)
 * - Nút ▲/▼ đổi thứ tự (không dùng drag-drop library)
 * - Nút "Lưu thứ tự" gọi PUT /api/failover/chain
 */
import { useEffect, useState } from 'react'
import type { FailoverChainItem } from '../../../types'

// ── Helpers ──────────────────────────────────────────────────────────────────

function StatusBadge({ status }: { status: FailoverChainItem['status'] }) {
  switch (status) {
    case 'active':
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption font-semibold bg-kz-orange text-white shrink-0">
          ACTIVE
        </span>
      )
    case 'exhausted':
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption bg-kz-gray/40 text-kz-text shrink-0">
          EXHAUSTED
        </span>
      )
    case 'needs_relogin':
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption bg-red-100 text-red-700 shrink-0">
          Cần đăng nhập lại
        </span>
      )
    default:
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-badge text-caption bg-kz-navy-light/30 text-kz-navy-mid shrink-0">
          Standby
        </span>
      )
  }
}

function usageSummary(item: FailoverChainItem): string {
  const parts: string[] = []
  if (item.five_hour_pct != null) parts.push(`5h: ${item.five_hour_pct.toFixed(0)}%`)
  if (item.seven_day_pct != null) parts.push(`7d: ${item.seven_day_pct.toFixed(0)}%`)
  return parts.length > 0 ? parts.join(' | ') : '—'
}

// ── Component ─────────────────────────────────────────────────────────────────

export default function FailoverChainConfig() {
  const [items, setItems] = useState<FailoverChainItem[]>([])
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState('')
  const [saveSuccess, setSaveSuccess] = useState(false)

  async function fetchChain() {
    setLoading(true)
    setFetchError('')
    try {
      const r = await fetch('/api/failover/chain')
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const data: FailoverChainItem[] = await r.json()
      setItems(data)
    } catch (e) {
      setFetchError(e instanceof Error ? e.message : 'Lỗi tải dữ liệu')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchChain() }, [])

  // ── Reorder: swap priority values khi di chuyển ▲/▼ ──────────────────────
  function moveUp(index: number) {
    if (index === 0) return
    setItems(prev => {
      const next = [...prev]
      const priA = next[index - 1].priority
      const priB = next[index].priority
      next[index - 1] = { ...next[index - 1], priority: priB }
      next[index] = { ...next[index], priority: priA }
      // Đổi vị trí trong mảng để UI hiển thị đúng
      ;[next[index - 1], next[index]] = [next[index], next[index - 1]]
      return next
    })
    setSaveSuccess(false)
  }

  function moveDown(index: number) {
    if (index >= items.length - 1) return
    setItems(prev => {
      const next = [...prev]
      const priA = next[index].priority
      const priB = next[index + 1].priority
      next[index] = { ...next[index], priority: priB }
      next[index + 1] = { ...next[index + 1], priority: priA }
      ;[next[index], next[index + 1]] = [next[index + 1], next[index]]
      return next
    })
    setSaveSuccess(false)
  }

  // ── Toggle include_in_chain: chặn uncheck account cuối cùng ──────────────
  const includedCount = items.filter(i => i.include_in_chain).length

  function toggleInclude(accId: string) {
    const item = items.find(i => i.acc_id === accId)
    if (!item) return
    // Block: nếu item đang included và chỉ còn 1 included → không cho uncheck
    if (item.include_in_chain && includedCount <= 1) return
    setItems(prev =>
      prev.map(i =>
        i.acc_id === accId ? { ...i, include_in_chain: !i.include_in_chain } : i
      )
    )
    setSaveSuccess(false)
  }

  // ── Save ─────────────────────────────────────────────────────────────────
  async function handleSave() {
    setSaving(true)
    setSaveError('')
    setSaveSuccess(false)
    try {
      const body = {
        items: items.map(i => ({
          acc_id: i.acc_id,
          priority: i.priority,
          include_in_chain: i.include_in_chain,
        })),
      }
      const r = await fetch('/api/failover/chain', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!r.ok) {
        const d = await r.json().catch(() => ({}))
        const msg = (d as { error?: { message?: string } }).error?.message ?? `HTTP ${r.status}`
        throw new Error(msg)
      }
      setSaveSuccess(true)
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : 'Lỗi lưu cấu hình')
    } finally {
      setSaving(false)
    }
  }

  // ── Render ────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <span className="text-caption text-kz-navy-mid animate-pulse">
          Đang tải cấu hình chain...
        </span>
      </div>
    )
  }

  if (fetchError) {
    return (
      <div className="py-8 text-center">
        <p className="text-sm text-kz-red mb-3">Lỗi: {fetchError}</p>
        <button
          onClick={fetchChain}
          className="text-caption text-kz-navy underline hover:opacity-75"
        >
          Thử lại
        </button>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="text-caption text-kz-navy-mid">
          Chưa có account OAuth nào trong chuỗi failover. Thêm tài khoản OAuth trước.
        </p>
      </div>
    )
  }

  return (
    <div>
      {/* Mô tả */}
      <div className="mb-4">
        <h3 className="text-h2 text-kz-navy mb-1">Cấu hình Failover Chain</h3>
        <p className="text-caption text-kz-navy-mid">
          Sắp xếp thứ tự ưu tiên — hệ thống failover từ trên xuống dưới.
          Cần giữ ít nhất 1 account trong chain.
        </p>
      </div>

      {/* Danh sách */}
      <div className="flex flex-col gap-2 mb-4">
        {items.map((item, idx) => {
          const isOnlyIncluded = item.include_in_chain && includedCount <= 1
          return (
            <div
              key={item.acc_id}
              className={[
                'flex items-center gap-3 px-4 py-3 rounded-card border transition-colors',
                item.include_in_chain
                  ? 'border-kz-navy-light bg-white'
                  : 'border-kz-gray bg-gray-50 opacity-60',
              ].join(' ')}
            >
              {/* Priority badge */}
              <span
                className="w-6 h-6 flex items-center justify-center rounded-full bg-kz-navy text-white font-bold shrink-0"
                style={{ fontSize: 11 }}
                aria-label={`Ưu tiên ${idx + 1}`}
              >
                {idx + 1}
              </span>

              {/* Tên + trạng thái */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold text-kz-navy truncate">
                    {item.name}
                  </span>
                  <StatusBadge status={item.status} />
                </div>
                <div className="text-caption text-kz-navy-mid mt-0.5">
                  Quota: {usageSummary(item)}
                </div>
              </div>

              {/* Checkbox include_in_chain */}
              <label
                className={[
                  'flex items-center gap-1.5 text-caption text-kz-navy-mid select-none',
                  isOnlyIncluded ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer',
                ].join(' ')}
                title={
                  isOnlyIncluded
                    ? 'Phải giữ ít nhất 1 account trong chain'
                    : undefined
                }
              >
                <input
                  type="checkbox"
                  checked={item.include_in_chain}
                  onChange={() => toggleInclude(item.acc_id)}
                  disabled={isOnlyIncluded}
                  className="w-4 h-4 accent-kz-navy"
                  aria-label={`Bao gồm ${item.name} trong failover chain`}
                />
                Trong chain
              </label>

              {/* Nút ▲/▼ */}
              <div className="flex flex-col gap-0.5 shrink-0">
                <button
                  onClick={() => moveUp(idx)}
                  disabled={idx === 0}
                  className="w-7 h-6 flex items-center justify-center text-xs text-kz-navy-mid hover:text-kz-navy disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
                  aria-label={`Di chuyển ${item.name} lên trên`}
                >
                  ▲
                </button>
                <button
                  onClick={() => moveDown(idx)}
                  disabled={idx >= items.length - 1}
                  className="w-7 h-6 flex items-center justify-center text-xs text-kz-navy-mid hover:text-kz-navy disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
                  aria-label={`Di chuyển ${item.name} xuống dưới`}
                >
                  ▼
                </button>
              </div>
            </div>
          )
        })}
      </div>

      {/* Inline error khi chỉ còn 0 included (edge case) */}
      {includedCount === 0 && (
        <p className="text-caption text-kz-red mb-3" role="alert">
          Cần ít nhất 1 account trong failover chain
        </p>
      )}

      {/* Save error */}
      {saveError && (
        <p className="text-caption text-kz-red mb-3" role="alert">
          {saveError}
        </p>
      )}

      {/* Save success */}
      {saveSuccess && (
        <p className="text-caption text-kz-green mb-3" role="status">
          ✓ Đã lưu cấu hình failover chain
        </p>
      )}

      {/* Nút lưu */}
      <button
        onClick={handleSave}
        disabled={saving || includedCount === 0}
        className="px-4 py-2 text-sm font-semibold text-white bg-kz-orange hover:bg-orange-600 rounded-btn transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Lưu thứ tự failover chain"
      >
        {saving ? 'Đang lưu...' : 'Lưu thứ tự'}
      </button>
    </div>
  )
}
