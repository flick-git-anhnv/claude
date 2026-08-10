import { useEffect, useState } from 'react'
import type { Account } from '../types'
import { useApi } from '../hooks/useApi'
import { useToast } from '../contexts/ToastContext'
import { useWs } from '../contexts/WsContext'
import AccountCard from '../components/accounts/AccountCard'
import AddAccountPanel from '../components/accounts/AddAccountPanel'
import ConfirmDialog from '../components/accounts/ConfirmDialog'
import BannerAlert from '../components/common/BannerAlert'
import FailoverChainConfig from '../components/accounts/failover/FailoverChainConfig'
import FailoverLogTable from '../components/accounts/failover/FailoverLogTable'

// ── Tab type ─────────────────────────────────────────────────────────────────

type Tab = 'accounts' | 'chain' | 'log'

const TABS: { id: Tab; label: string }[] = [
  { id: 'accounts', label: 'Danh sách Account' },
  { id: 'chain',    label: 'Failover Chain' },
  { id: 'log',      label: 'Failover Log' },
]

// ── Tab bar component ─────────────────────────────────────────────────────────

function TabBar({
  active,
  onChange,
}: {
  active: Tab
  onChange: (tab: Tab) => void
}) {
  return (
    <div
      className="flex border-b border-kz-gray mb-5"
      role="tablist"
      aria-label="Account Manager tabs"
    >
      {TABS.map(tab => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={active === tab.id}
          aria-controls={`tabpanel-${tab.id}`}
          id={`tab-${tab.id}`}
          onClick={() => onChange(tab.id)}
          className={[
            'px-4 py-2 text-sm font-semibold transition-colors border-b-2 -mb-px',
            active === tab.id
              ? 'border-kz-orange text-kz-orange'
              : 'border-transparent text-kz-navy-mid hover:text-kz-navy hover:border-kz-navy-light',
          ].join(' ')}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function AccountManagerPage() {
  const { getAccounts, addAccount, addOAuthAccount, deleteAccount, activateAccount, revealApiKey } =
    useApi()
  const { showToast } = useToast()
  const { dispatch } = useWs()

  const [activeTab, setActiveTab] = useState<Tab>('accounts')
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

  async function handleSaveApiKey(name: string, apiKey: string) {
    const created = await addAccount(name, apiKey)
    setAccounts(prev => [...prev, created])
    showToast(`Đã thêm tài khoản "${name}"`)
  }

  async function handleSaveOAuth(name: string) {
    const created = await addOAuthAccount(name)
    setAccounts(prev => [...prev, created])
    showToast(`Đã import OAuth session "${name}"`)
  }

  async function handleActivate(id: string) {
    await activateAccount(id)
    const updated = accounts.map(a => ({ ...a, is_active: a.id === id }))
    setAccounts(updated)
    const activated = updated.find(a => a.id === id)
    if (activated) {
      dispatch({
        type: 'DELTA',
        payload: {
          event: 'account_changed',
          active_id: activated.id,
          name: activated.name,
          kind: activated.kind,
          key_masked: activated.kind === 'api_key' ? activated.key_masked : undefined,
          oauth_masked:
            activated.kind === 'oauth_session' ? activated.oauth_masked : undefined,
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
        <h2 className="text-h2 text-kz-navy">Quản lý tài khoản</h2>
        {activeTab === 'accounts' && (
          <button
            onClick={() => setShowAddPanel(true)}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold text-white bg-kz-orange hover:bg-orange-600 rounded-btn transition-colors"
            aria-label="Thêm tài khoản mới"
          >
            <span aria-hidden="true">+</span>
            <span>Thêm tài khoản</span>
          </button>
        )}
      </div>

      {/* Tab bar */}
      <TabBar active={activeTab} onChange={setActiveTab} />

      {/* ── Tab: Danh sách Account ── */}
      <div
        id="tabpanel-accounts"
        role="tabpanel"
        aria-labelledby="tab-accounts"
        hidden={activeTab !== 'accounts'}
      >
        {/* Security banner — khi có OAuth account */}
        {accounts.some(a => a.kind === 'oauth_session') && (
          <BannerAlert
            type="warning"
            message="⚠️ Dashboard lưu nhiều refresh-token OAuth cùng lúc trên máy này bằng mã hoá đơn giản (XOR+base64). Đủ chống người ngó qua vai, KHÔNG phải OS keychain. Không dùng nếu máy chia sẻ."
          />
        )}

        {/* No active account banner */}
        {!activeAccount && accounts.length > 0 && (
          <BannerAlert
            type="warning"
            message="Chưa có tài khoản nào được đặt active. Nhấn 'Đặt active' để chọn tài khoản sẽ dùng."
          />
        )}

        {/* Error */}
        {error && <BannerAlert type="error" message={error} />}

        {/* Loading */}
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <span className="text-caption text-kz-navy-mid animate-pulse">
              Đang tải...
            </span>
          </div>
        ) : accounts.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="text-5xl text-kz-navy-light mb-4" aria-hidden="true">
              👤
            </div>
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
      </div>

      {/* ── Tab: Failover Chain ── */}
      <div
        id="tabpanel-chain"
        role="tabpanel"
        aria-labelledby="tab-chain"
        hidden={activeTab !== 'chain'}
      >
        {activeTab === 'chain' && <FailoverChainConfig />}
      </div>

      {/* ── Tab: Failover Log ── */}
      <div
        id="tabpanel-log"
        role="tabpanel"
        aria-labelledby="tab-log"
        hidden={activeTab !== 'log'}
      >
        {activeTab === 'log' && <FailoverLogTable />}
      </div>

      {/* Add panel */}
      {showAddPanel && (
        <AddAccountPanel
          onSaveApiKey={handleSaveApiKey}
          onSaveOAuth={handleSaveOAuth}
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
