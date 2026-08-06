import { useEffect, useRef, useState } from 'react'

type TabKind = 'api_key' | 'oauth_session'

interface AddAccountPanelProps {
  onSaveApiKey: (name: string, apiKey: string) => Promise<void>
  onSaveOAuth: (name: string) => Promise<void>
  onClose: () => void
}

export default function AddAccountPanel({ onSaveApiKey, onSaveOAuth, onClose }: AddAccountPanelProps) {
  const [tab, setTab] = useState<TabKind>('api_key')
  const [name, setName] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [nameError, setNameError] = useState('')
  const [keyWarning, setKeyWarning] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState('')
  const nameInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    nameInputRef.current?.focus()
  }, [tab])

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  function switchTab(t: TabKind) {
    setTab(t)
    setName('')
    setApiKey('')
    setNameError('')
    setKeyWarning('')
    setSaveError('')
  }

  function validateKey(val: string) {
    if (val && !val.startsWith('sk-')) {
      setKeyWarning('API key nên bắt đầu bằng "sk-ant-" — kiểm tra lại nếu không phải key Anthropic')
    } else {
      setKeyWarning('')
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setNameError('')
    setSaveError('')

    if (!name.trim()) { setNameError('Tên hiển thị không được để trống'); return }
    if (name.length > 50) { setNameError('Tối đa 50 ký tự'); return }

    if (tab === 'api_key') {
      if (!apiKey.trim()) { setNameError('API Key không được để trống'); return }
    }

    setSaving(true)
    try {
      if (tab === 'api_key') {
        await onSaveApiKey(name.trim(), apiKey.trim())
      } else {
        await onSaveOAuth(name.trim())
      }
      onClose()
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Lỗi không xác định')
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/20 z-30"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Slide-in panel */}
      <aside
        className="fixed top-0 right-0 h-full w-80 bg-white shadow-2xl z-40 flex flex-col"
        role="complementary"
        aria-label="Thêm tài khoản mới"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-kz-gray">
          <h3 className="text-h2 text-kz-navy">Thêm tài khoản mới</h3>
          <button
            onClick={onClose}
            className="text-kz-navy-mid hover:text-kz-navy text-lg leading-none"
            aria-label="Đóng panel"
          >
            ✕
          </button>
        </div>

        {/* Tab switcher */}
        <div className="flex border-b border-kz-gray">
          <button
            onClick={() => switchTab('api_key')}
            className={[
              'flex-1 py-2.5 text-sm font-semibold transition-colors',
              tab === 'api_key'
                ? 'text-kz-orange border-b-2 border-kz-orange'
                : 'text-kz-navy-mid hover:text-kz-navy',
            ].join(' ')}
            aria-selected={tab === 'api_key'}
            role="tab"
          >
            API Key
          </button>
          <button
            onClick={() => switchTab('oauth_session')}
            className={[
              'flex-1 py-2.5 text-sm font-semibold transition-colors',
              tab === 'oauth_session'
                ? 'text-kz-orange border-b-2 border-kz-orange'
                : 'text-kz-navy-mid hover:text-kz-navy',
            ].join(' ')}
            aria-selected={tab === 'oauth_session'}
            role="tab"
          >
            OAuth Session
          </button>
        </div>

        {/* Form */}
        <form
          onSubmit={handleSubmit}
          className="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-4"
          noValidate
        >
          {saveError && (
            <p className="text-caption text-kz-red bg-kz-error-bg px-3 py-2 rounded-sm">
              {saveError}
            </p>
          )}

          {/* Common: name field */}
          <div>
            <label className="block text-sm font-medium text-kz-navy mb-1" htmlFor="acc-name">
              Tên hiển thị <span className="text-kz-red">*</span>
            </label>
            <input
              ref={nameInputRef}
              id="acc-name"
              type="text"
              value={name}
              maxLength={50}
              placeholder="VD: KZTEK Production"
              onChange={e => { setName(e.target.value); setNameError('') }}
              className={[
                'w-full px-3 py-2 text-sm border rounded-btn outline-none transition-colors',
                nameError
                  ? 'border-kz-red focus:border-kz-red'
                  : 'border-kz-gray focus:border-kz-navy',
              ].join(' ')}
              aria-describedby={nameError ? 'acc-name-error' : undefined}
              aria-invalid={!!nameError}
            />
            {nameError && (
              <p id="acc-name-error" className="mt-1 text-caption text-kz-red">{nameError}</p>
            )}
          </div>

          {/* Tab: API Key */}
          {tab === 'api_key' && (
            <div>
              <label className="block text-sm font-medium text-kz-navy mb-1" htmlFor="acc-key">
                API Key <span className="text-kz-red">*</span>
              </label>
              <input
                id="acc-key"
                type="text"
                value={apiKey}
                placeholder="sk-ant-..."
                onChange={e => { setApiKey(e.target.value); validateKey(e.target.value) }}
                className="w-full px-3 py-2 text-sm border border-kz-gray rounded-btn outline-none focus:border-kz-navy transition-colors font-mono"
                autoComplete="off"
              />
              {keyWarning && (
                <p className="mt-1 text-caption text-kz-orange-light">{keyWarning}</p>
              )}
            </div>
          )}

          {/* Tab: OAuth Session instructions */}
          {tab === 'oauth_session' && (
            <div className="flex flex-col gap-3">
              <div className="bg-kz-navy-light/10 border border-kz-navy-light rounded-sm px-3 py-3 text-caption text-kz-navy-mid leading-relaxed">
                <p className="font-semibold mb-1 text-kz-navy">Hướng dẫn:</p>
                <ol className="list-decimal list-inside space-y-1">
                  <li>Mở terminal, chạy <code className="font-mono bg-kz-gray/40 px-1 rounded">claude login</code> với tài khoản này.</li>
                  <li>Sau khi đăng nhập xong, quay lại đây và bấm <strong>Import từ Claude Code hiện tại</strong>.</li>
                </ol>
              </div>
              <p className="text-caption text-kz-navy-mid">
                Dashboard sẽ đọc snapshot OAuth token hiện tại từ{' '}
                <code className="font-mono text-xs bg-kz-gray/40 px-1 rounded">.claude/.credentials.json</code>.
              </p>
            </div>
          )}
        </form>

        {/* Footer */}
        <div className="flex justify-end gap-3 px-5 py-4 border-t border-kz-gray">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-kz-navy-mid hover:text-kz-navy"
          >
            Huỷ
          </button>
          <button
            onClick={handleSubmit as unknown as React.MouseEventHandler}
            disabled={saving}
            className="px-4 py-2 text-sm font-semibold text-white bg-kz-orange hover:bg-orange-600 rounded-btn transition-colors disabled:opacity-60"
            aria-label={tab === 'oauth_session' ? 'Import từ Claude Code hiện tại' : 'Lưu tài khoản mới'}
          >
            {saving
              ? 'Đang lưu...'
              : tab === 'oauth_session'
                ? 'Import từ Claude Code hiện tại'
                : 'Lưu tài khoản'}
          </button>
        </div>
      </aside>
    </>
  )
}
