import { useState } from 'react'
import { RiExternalLinkLine, RiDeleteBinLine } from 'react-icons/ri'
import { useFileActions, useFileDetail } from '../../hooks/useFileActions'
import { TagBadge } from '../tags/TagBadge'
import { TagSelector } from '../tags/TagSelector'
import { ConfirmDialog } from '../common/ConfirmDialog'
import { Spinner } from '../common/Spinner'

interface Props {
  fileId: number | null
  onDeleted: () => void
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

export function DetailPanel({ fileId, onDeleted }: Props) {
  const [confirmDelete, setConfirmDelete] = useState(false)
  const { data: file, isLoading } = useFileDetail(fileId)
  const { openFile, deleteFile, addTag, removeTag } = useFileActions(fileId)

  if (!fileId) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400 text-sm">
        ファイルを選択してください
      </div>
    )
  }

  if (isLoading) return <div className="flex justify-center p-8"><Spinner /></div>
  if (!file) return <div className="p-4 text-sm text-red-500">読み込みエラー</div>

  const handleDelete = async () => {
    await deleteFile.mutateAsync()
    setConfirmDelete(false)
    onDeleted()
  }

  return (
    <div className="p-4 h-full overflow-y-auto">
      <div className="flex items-start justify-between gap-2 mb-4">
        <h2 className="text-base font-semibold text-gray-900 break-all">{file.filename}</h2>
        <div className="flex gap-2 shrink-0">
          <button
            onClick={() => openFile.mutate()}
            className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 border border-blue-300 rounded px-2 py-1"
          >
            <RiExternalLinkLine />
            開く
          </button>
          <button
            onClick={() => setConfirmDelete(true)}
            className="flex items-center gap-1 text-xs text-red-500 hover:text-red-700 border border-red-300 rounded px-2 py-1"
          >
            <RiDeleteBinLine />
            削除
          </button>
        </div>
      </div>

      <dl className="text-xs text-gray-500 space-y-1 mb-4">
        <div className="flex gap-2">
          <dt className="w-16 shrink-0">パス</dt>
          <dd className="break-all text-gray-700">{file.path}</dd>
        </div>
        <div className="flex gap-2">
          <dt className="w-16 shrink-0">サイズ</dt>
          <dd>{formatSize(file.size)}</dd>
        </div>
        <div className="flex gap-2">
          <dt className="w-16 shrink-0">更新日時</dt>
          <dd>{new Date(file.mtime * 1000).toLocaleString('ja-JP')}</dd>
        </div>
        <div className="flex gap-2">
          <dt className="w-16 shrink-0">種別</dt>
          <dd>{file.ext}</dd>
        </div>
      </dl>

      <div className="mb-4">
        <div className="text-xs font-medium text-gray-500 mb-2">タグ</div>
        <div className="flex flex-wrap gap-1 mb-2">
          {file.tags.map((tag) => (
            <TagBadge key={tag.id} tag={tag} onRemove={(id) => removeTag.mutate(id)} />
          ))}
        </div>
        <TagSelector
          fileTags={file.tags}
          onAdd={(name) => addTag.mutate(name)}
          onRemove={(id) => removeTag.mutate(id)}
        />
      </div>

      {file.preview && (
        <div>
          <div className="text-xs font-medium text-gray-500 mb-2">テキストプレビュー</div>
          <pre className="text-xs text-gray-600 bg-gray-50 rounded p-3 whitespace-pre-wrap break-all max-h-64 overflow-y-auto">
            {file.preview}
          </pre>
        </div>
      )}

      {confirmDelete && (
        <ConfirmDialog
          message={`「${file.filename}」を削除しますか？この操作は元に戻せません。`}
          onConfirm={handleDelete}
          onCancel={() => setConfirmDelete(false)}
        />
      )}
    </div>
  )
}
