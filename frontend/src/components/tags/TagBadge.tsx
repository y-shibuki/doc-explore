import type { Tag } from '../../types'

interface Props {
  tag: Tag
  onRemove?: (id: number) => void
}

export function TagBadge({ tag, onRemove }: Props) {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs bg-blue-100 text-blue-700 rounded-full">
      {tag.name}
      {onRemove && (
        <button
          onClick={() => onRemove(tag.id)}
          className="hover:text-blue-900 leading-none"
          aria-label={`${tag.name}を削除`}
        >
          ×
        </button>
      )}
    </span>
  )
}
