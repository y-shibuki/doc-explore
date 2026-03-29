import { useState } from 'react'
import { RiRefreshLine } from 'react-icons/ri'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '../../api/client'
import { useSearch } from '../../hooks/useSearch'
import { SearchBar } from '../search/SearchBar'
import { SearchResults } from '../search/SearchResults'
import { FolderTree } from '../tree/FolderTree'
import { Spinner } from '../common/Spinner'

interface Props {
  selectedFileId: number | null
  onSelectFile: (id: number) => void
}

export function Sidebar({ selectedFileId, onSelectFile }: Props) {
  const { query, tagFilters, setTagFilters, updateQuery, results, isSearchMode } = useSearch()
  const qc = useQueryClient()
  const [scanning, setScanning] = useState(false)

  const handleScan = async () => {
    setScanning(true)
    try {
      await api.startScan()
      const poll = setInterval(async () => {
        const status = await api.getScanStatus()
        if (status.status !== 'running') {
          clearInterval(poll)
          setScanning(false)
          if (status.status === 'completed') {
            toast.success(
              `スキャン完了: 追加${status.files_added} 更新${status.files_updated} 削除${status.files_deleted}`,
            )
            qc.invalidateQueries({ queryKey: ['tree'] })
          } else {
            toast.error('スキャンに失敗しました')
          }
        }
      }, 2000)
    } catch {
      setScanning(false)
      toast.error('スキャンの開始に失敗しました')
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 py-2 border-b">
        <span className="font-semibold text-sm text-gray-700">doc-explore</span>
        <button
          onClick={handleScan}
          disabled={scanning}
          className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-800 disabled:opacity-50"
          title="インデックス更新"
        >
          {scanning ? <Spinner size="sm" /> : <RiRefreshLine />}
          スキャン
        </button>
      </div>
      <SearchBar
        query={query}
        tagFilters={tagFilters}
        onChange={updateQuery}
        onTagFilterChange={setTagFilters}
      />
      <div className="flex-1 overflow-y-auto">
        {isSearchMode ? (
          <SearchResults
            results={results.data?.items ?? []}
            total={results.data?.total ?? 0}
            isLoading={results.isLoading}
            selectedId={selectedFileId}
            onSelect={onSelectFile}
          />
        ) : (
          <FolderTree />
        )}
      </div>
    </div>
  )
}
