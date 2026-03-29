import { createContext, useContext } from 'react'
import type { TreeState } from '../../hooks/useTree'

interface TreeContextValue extends TreeState {
  selectedFileId: number | null
  onSelectFile: (id: number, path: string) => void
}

export const TreeContext = createContext<TreeContextValue | null>(null)

export function useTreeContext() {
  const ctx = useContext(TreeContext)
  if (!ctx) throw new Error('useTreeContext must be used within TreeContext.Provider')
  return ctx
}
