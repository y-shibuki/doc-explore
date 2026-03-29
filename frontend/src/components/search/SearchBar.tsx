import { RiSearchLine } from 'react-icons/ri'
import { useTags } from '../../hooks/useTags'

interface Props {
  query: string
  tagFilters: number[]
  onChange: (q: string) => void
  onTagFilterChange: (ids: number[]) => void
}

export function SearchBar({ query, tagFilters, onChange, onTagFilterChange }: Props) {
  const { tags } = useTags()

  const toggleTag = (id: number) => {
    onTagFilterChange(
      tagFilters.includes(id) ? tagFilters.filter((t) => t !== id) : [...tagFilters, id],
    )
  }

  return (
    <div className="p-3 border-b">
      <div className="flex items-center gap-2 bg-gray-100 rounded px-3 py-1.5">
        <RiSearchLine className="text-gray-400 shrink-0" />
        <input
          value={query}
          onChange={(e) => onChange(e.target.value)}
          placeholder="ファイルを検索..."
          className="bg-transparent text-sm w-full outline-none"
        />
      </div>
      {tags.data && tags.data.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {tags.data.map((tag) => (
            <button
              key={tag.id}
              onClick={() => toggleTag(tag.id)}
              className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                tagFilters.includes(tag.id)
                  ? 'bg-blue-500 text-white border-blue-500'
                  : 'text-gray-600 border-gray-300 hover:border-blue-400'
              }`}
            >
              {tag.name}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
