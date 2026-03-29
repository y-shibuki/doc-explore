import { useCallback, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import type { TreeNode } from '../types'

export function useTree(path?: string) {
  return useQuery({
    queryKey: ['tree', path ?? null],
    queryFn: () => api.getTree(path),
    staleTime: 30_000,
  })
}

export function useTreeState() {
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [highlighted, setHighlighted] = useState<string | null>(null)

  const toggle = useCallback((path: string) => {
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(path)) next.delete(path)
      else next.add(path)
      return next
    })
  }, [])

  const expandPath = useCallback((paths: string[]) => {
    setExpanded((prev) => {
      const next = new Set(prev)
      paths.forEach((p) => next.add(p))
      return next
    })
  }, [])

  const highlight = useCallback((path: string) => {
    setHighlighted(path)
    setTimeout(() => setHighlighted(null), 2000)
  }, [])

  return { expanded, highlighted, toggle, expandPath, highlight }
}

export type TreeState = ReturnType<typeof useTreeState>
