import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'

export function useTags() {
  const qc = useQueryClient()

  const tags = useQuery({
    queryKey: ['tags'],
    queryFn: api.listTags,
    staleTime: 60_000,
  })

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ['tags'] })
  }

  const createTag = useMutation({
    mutationFn: (name: string) => api.createTag(name),
    onSuccess: invalidate,
  })

  const updateTag = useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) => api.updateTag(id, name),
    onSuccess: invalidate,
  })

  const deleteTag = useMutation({
    mutationFn: (id: number) => api.deleteTag(id),
    onSuccess: invalidate,
  })

  return { tags, createTag, updateTag, deleteTag }
}
