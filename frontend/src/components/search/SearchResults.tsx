import type { SearchResult } from '../../types'
import { Spinner } from '../common/Spinner'
import { TagBadge } from '../tags/TagBadge'

interface Props {
  results: SearchResult[]
  total: number
  isLoading: boolean
  selectedId: number | null
  onSelect: (id: number) => void
}

export function SearchResults({ results, total, isLoading, selectedId, onSelect }: Props) {
  if (isLoading) return <div className="p-4"><Spinner /></div>
  if (!results.length) return <div className="p-4 text-sm text-gray-400">結果が見つかりません</div>

  return (
    <div>
      <div className="px-3 py-1.5 text-xs text-gray-500 border-b">{total}件</div>
      <ul>
        {results.map((r) => (
          <li key={r.id}>
            <button
              onClick={() => onSelect(r.id)}
              className={`w-full text-left px-3 py-2 hover:bg-gray-50 border-b ${
                selectedId === r.id ? 'bg-blue-50' : ''
              }`}
            >
              <div className="text-sm font-medium truncate">{r.filename}</div>
              {r.snippet && (
                <div
                  className="text-xs text-gray-500 mt-0.5 line-clamp-2"
                  dangerouslySetInnerHTML={{ __html: r.snippet }}
                />
              )}
              {r.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1">
                  {r.tags.map((t) => (
                    <TagBadge key={t.id} tag={t} />
                  ))}
                </div>
              )}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
