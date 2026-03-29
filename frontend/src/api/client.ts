import type {
  ConfigResponse,
  FileDetail,
  ScanStatus,
  SearchResponse,
  Tag,
  TagWithCount,
  TreeNode,
} from '../types'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(path, options)
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`${res.status}: ${text}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  getConfig: () => request<ConfigResponse>('/api/config'),

  getTree: (path?: string) => {
    const url = path ? `/api/tree?path=${encodeURIComponent(path)}` : '/api/tree'
    return request<TreeNode[]>(url)
  },

  search: (q: string, tags: number[] = [], limit = 20, offset = 0) => {
    const params = new URLSearchParams({ q, limit: String(limit), offset: String(offset) })
    tags.forEach((t) => params.append('tags', String(t)))
    return request<SearchResponse>(`/api/search?${params}`)
  },

  getFile: (id: number) => request<FileDetail>(`/api/files/${id}`),

  deleteFile: (id: number) =>
    request<void>(`/api/files/${id}`, { method: 'DELETE' }),

  openFile: (id: number) =>
    request<void>(`/api/files/${id}/open`, { method: 'POST' }),

  listTags: () => request<TagWithCount[]>('/api/tags'),

  createTag: (name: string) =>
    request<Tag>('/api/tags', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    }),

  updateTag: (id: number, name: string) =>
    request<Tag>(`/api/tags/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    }),

  deleteTag: (id: number) =>
    request<void>(`/api/tags/${id}`, { method: 'DELETE' }),

  addFileTag: (fileId: number, name: string) =>
    request<Tag>(`/api/files/${fileId}/tags`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name }),
    }),

  removeFileTag: (fileId: number, tagId: number) =>
    request<void>(`/api/files/${fileId}/tags/${tagId}`, { method: 'DELETE' }),

  startScan: () => request<ScanStatus>('/api/index/scan', { method: 'POST' }),

  getScanStatus: () => request<ScanStatus>('/api/index/status'),
}
