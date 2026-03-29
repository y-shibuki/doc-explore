export interface Tag {
  id: number
  name: string
}

export interface TagWithCount extends Tag {
  file_count: number
}

export interface FileItem {
  id: number
  path: string
  filename: string
  mtime: number
  size: number
  ext: string
  indexed_at: string
  tags: Tag[]
}

export interface FileDetail extends FileItem {
  preview: string
}

export interface SearchResult {
  id: number
  path: string
  filename: string
  ext: string
  indexed_at: string
  tags: Tag[]
  snippet: string
}

export interface SearchResponse {
  total: number
  items: SearchResult[]
}

export interface TreeNode {
  name: string
  path: string
  type: 'folder' | 'file'
  file_id: number | null
  ext: string | null
  has_children: boolean
}

export interface ScanStatus {
  status: 'idle' | 'running' | 'completed' | 'failed'
  started_at: string | null
  finished_at: string | null
  files_added: number
  files_updated: number
  files_deleted: number
}

export interface ConfigResponse {
  scan_folders: string[]
  target_extensions: string[]
  db_path: string
  auto_scan_on_startup: boolean
}
