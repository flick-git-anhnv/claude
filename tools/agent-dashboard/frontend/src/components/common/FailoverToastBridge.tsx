/**
 * FailoverToastBridge — Sprint 7
 *
 * Component không có UI — chỉ watch failoverToastNonce từ WsContext
 * và gọi showFailoverToast khi nonce tăng.
 *
 * Đặt bên trong App.tsx (bên trong cả WsProvider + ToastProvider).
 * Tách riêng để tránh ô nhiễm context cho App.
 */
import { useEffect, useRef } from 'react'
import { useWsState } from '../../contexts/WsContext'
import { useToast } from '../../contexts/ToastContext'

export default function FailoverToastBridge() {
  const { failoverToastNonce, failoverToastMessage, failoverToastType } = useWsState()
  const { showFailoverToast } = useToast()

  // Track nonce đã xử lý — tránh trigger khi component mount lần đầu
  const prevNonceRef = useRef(failoverToastNonce)

  useEffect(() => {
    if (failoverToastNonce === prevNonceRef.current) return
    prevNonceRef.current = failoverToastNonce
    if (!failoverToastMessage) return
    showFailoverToast(failoverToastMessage, failoverToastType)
  }, [failoverToastNonce, failoverToastMessage, failoverToastType, showFailoverToast])

  return null
}
