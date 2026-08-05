import { useEffect, useState } from 'react'
import type { Account } from '../types'
import { useApi } from '../hooks/useApi'
import { useToast } from '../contexts/ToastContext'
import { useWs } from '../contexts/WsContext'
import AccountCard from '../components/accounts/AccountCard'
import AddAccountPanel from '../components/accounts/AddAccountPanel'
import ConfirmDialog from '../components/accounts/ConfirmDialog'
import BannerAlert from '../components/common/BannerAlert'

export default function AccountManagerPage() {
  const { getAccounts, addAccount, deleteAccount, activateAccount, revealApiKey } = useApi()
  const { showToast } = useToast()
  const { dispatch } = useWs()

  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showAddPanel, setShowAddPanel] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<Account | null>(null)

  function load() {
    setLoading(true)
    setError('')
    getAccounts()
      .then(setAccounts)
      .catch(err => setError(err instanceof Error ? err.message : 'Lỗi tải dữ liệu'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  async function handleSave(name: string, apiKey: string) {
    const created = await addAccount(name, apiKey)
    setAccounts(prev => [...prev, created])
    showToast(`Đã thêm tài khoản "${name}"`)
  }

  async function handleActivate(id: string) {
    await activateAccount(id)
    const updated = accounts.map(a => ({ ...a, is_active: a.id === id }))
    setAccounts(updated)
    const activated = updated.find(a => a.id === id)
    if (activated) {
      // Notify WS context so header updates immediately
      dispatch({
        type: 'DELTA',
        payload: {
          event: 'account_changed',
          active_id: activated.id,
          name: activated.name,
          key_masked: activated.key_masked,
        },
      })
      showToast(`Đã đặt "${activated.name}" làm tài khoản active`)
    }
  }

  async function handleCopy(id: string) {
    try {
      const key = await revealApiKey(id)
      await navigator.clipboard.writeText(key)
      showToast('Đã copy API key — tự nhập vào Claude Code')
      // Clear clipboard after 30s (security)
      setTimeout(() => {
        navigator.clipboard.writeText('').catch(() => {})
      }, 30000)
    } catch {
      showToast('Không thể copy — kiểm tra quyền clipboard trong trình duyệt')
    }
  }

  async function handleDeleteConfirm() {
    if (!deleteTarget) return
    try {
      await deleteAccount(deleteTarget.id)
      setAccounts(prev => prev.filter(a => a.id !== deleteTarget.id))
      showToast(`Đã xóa tài khoản "${deleteTarget.name}"`)
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Không thể xóa tài khoản')
    } finally {
      setDeleteTarget(null)
    }
  }

  const activeAccount = accounts.find(a => a.is_active)

  return (
    <div>
      {/* Page header */}
      <div className="flex items-center justify-between mb-5">
        <h2 className="text-h2 text-kz-navy">Quản lý tài khoản API</h2>
        <button
          onClick={() => setShowAddPanel(true)}
          className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-kz-orange hover:bg-orange-600 rounded-btn transition-colors"
          aria-label="Thêm tài khoản mới"
        >
          <span aria-hidden="true">+</span>
          <span>Thêm tài khoản</span>
        </button>
      </div>

      {/* No active account banner */}
      {!activeAccount && accounts.length > 0 && (
        <BannerAlert
          type="warning"
          message="Chưa có tài khoản nào được đặt active. Nhấn 'Đặt active' để chọn tài khoản sẽ dùng."
        />
      )}

      {/* Error */}
      {error && (
        <BannerAlert type="error" message={error} />
      )}

      {/* Loading */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <span className="text-caption text-kz-navy-mid animate-pulse">Đang tải...</span>
        </div>
      ) : accounts.length === 0 ? (
        /* Empty state */
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="text-5xl text-kz-navy-light mb-4" aria-hidden="true">👤</div>
          <h3 className="text-h2 text-kz-navy mb-2">Chưa có tài khoản nào</h3>
          <p className="text-caption text-kz-navy-mid mb-5">
            Nhấn "Thêm tài khoản" để bắt đầu
          </p>
          <button
            onClick={() => setShowAddPanel(true)}
            className="px-4 py-2 text-sm font-semibold text-white bg-kz-orange hover:bg-orange-600 rounded-btn"
          >
            + Thêm tài khoản
          </button>
        </div>
      ) : (
        /* Account list */
        <div className="flex flex-col gap-3">
          {accounts.map(account => (
            <AccountCard
              key={account.id}
              account={account}
              onActivate={handleActivate}
              onCopy={handleCopy}
              onDelete={id => {
                const target = accounts.find(a => a.id === id)
                if (target) setDeleteTarget(target)
              }}
            />
          ))}
        </div>
      )}

      {/* Add panel */}
      {showAddPanel && (
        <AddAccountPanel
          onSave={handleSave}
          onClose={() => setShowAddPanel(false)}
        />
      )}

      {/* Delete confirm dialog */}
      {deleteTarget && (
        <ConfirmDialog
          title="Xác nhận xóa tài khoản"
          message={`Bạn có chắc muốn xóa tài khoản "${deleteTarget.name}"? Thao tác này không thể hoàn tác.`}
          confirmLabel="Xóa tài khoản"
          confirmDanger
          onConfirm={handleDeleteConfirm}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  )
}
