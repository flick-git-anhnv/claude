/**
 * usePipelineMode — Sprint 5 FR-005
 * Toggle trạng thái Pipeline view: "session" (theo phiên) | "aggregate" (tổng hợp).
 * Persist trong localStorage key "pipelineMode".
 * Default: "session" (nếu chưa có giá trị trong localStorage).
 */
import { useState, useEffect } from 'react'
import type { PipelineMode } from '../types'

const STORAGE_KEY = 'pipelineMode'

export function usePipelineMode() {
  const [mode, setMode] = useState<PipelineMode>(() => {
    const stored = localStorage.getItem(STORAGE_KEY)
    return (stored === 'aggregate' ? 'aggregate' : 'session') as PipelineMode
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, mode)
  }, [mode])

  return [mode, setMode] as const
}
