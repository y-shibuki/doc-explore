import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function useSearch() {
  const [query, setQuery] = useState('')
  const [tagFilters, setTagFilters] = useState<number[]>([])
  const [debouncedQuery, setDebouncedQuery] = useState('')

  const updateQuery = (q: string) => {
    setQuery(q)
    const timer = setTimeout(() => setDebouncedQuery(q), 300)
    return () => clearTimeout(timer)
  }

  const results = useQuery({
    queryKey: ['search', debouncedQuery, tagFilters],
    queryFn: () => api.search(debouncedQuery, tagFilters),
    enabled: debouncedQuery.length > 0,
    staleTime: 10_000,
  })

  return {
    query,
    tagFilters,
    setTagFilters,
    updateQuery,
    results,
    isSearchMode: debouncedQuery.length > 0,
  }
}
