import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '../api/client'

export function useFileDetail(id: number | null) {
  return useQuery({
    queryKey: ['file', id],
    queryFn: () => api.getFile(id!),
    enabled: id !== null,
    staleTime: 30_000,
  })
}

export function useFileActions(fileId: number | null) {
  const qc = useQueryClient()

  const openFile = useMutation({
    mutationFn: () => api.openFile(fileId!),
    onError: () => toast.error('ファイルを開けませんでした'),
  })

  const deleteFile = useMutation({
    mutationFn: () => api.deleteFile(fileId!),
    onSuccess: () => {
      toast.success('ファイルを削除しました')
      qc.invalidateQueries({ queryKey: ['tree'] })
      qc.removeQueries({ queryKey: ['file', fileId] })
    },
    onError: () => toast.error('削除に失敗しました'),
  })

  const addTag = useMutation({
    mutationFn: (name: string) => api.addFileTag(fileId!, name),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['file', fileId] })
      qc.invalidateQueries({ queryKey: ['tags'] })
    },
    onError: () => toast.error('タグの追加に失敗しました'),
  })

  const removeTag = useMutation({
    mutationFn: (tagId: number) => api.removeFileTag(fileId!, tagId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['file', fileId] })
      qc.invalidateQueries({ queryKey: ['tags'] })
    },
    onError: () => toast.error('タグの削除に失敗しました'),
  })

  return { openFile, deleteFile, addTag, removeTag }
}
