import { useEffect, useRef, useState } from 'react'

interface AddAccountPanelProps {
  onSave: (name: string, apiKey: string) => Promise<void>
  onClose: () => void
}

export default function AddAccountPanel({ onSave, onClose }: AddAccountPanelProps) {
  const [name, setName] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [nameError, setNameError] = useState('')
  const [keyWarning, setKeyWarning] = useState('')
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState('')
  const nameInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    nameInputRef.current?.focus()
  }, [])

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

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
    if (!apiKey.trim()) { setNameError('API Key không được để trống'); return }

    setSaving(true)
    try {
      await onSave(name.trim(), apiKey.trim())
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

      {/* Slide-in panel from right */}
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

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-4" noValidate>
          {/* Save error */}
          {saveError && (
            <p className="text-caption text-kz-red bg-kz-error-bg px-3 py-2 rounded-sm">
              {saveError}
            </p>
          )}

          {/* Name field */}
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
            <p className="mt-1 text-caption text-kz-navy-mid">Tối đa 50 ký tự</p>
          </div>

          {/* API Key field */}
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
        </form>

        {/* Footer actions */}
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
            aria-label="Lưu tài khoản mới"
          >
            {saving ? 'Đang lưu...' : 'Lưu tài khoản'}
          </button>
        </div>
      </aside>
    </>
  )
}
