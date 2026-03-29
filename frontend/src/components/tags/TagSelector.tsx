import { useState } from 'react'
import { useTags } from '../../hooks/useTags'
import type { Tag } from '../../types'

interface Props {
  fileTags: Tag[]
  onAdd: (name: string) => void
  onRemove: (id: number) => void
}

export function TagSelector({ fileTags, onAdd, onRemove }: Props) {
  const [input, setInput] = useState('')
  const [open, setOpen] = useState(false)
  const { tags } = useTags()

  const fileTagIds = new Set(fileTags.map((t) => t.id))
  const available = (tags.data ?? []).filter((t) => !fileTagIds.has(t.id))
  const filtered = available.filter((t) =>
    t.name.toLowerCase().includes(input.toLowerCase()),
  )

  const handleAdd = (name: string) => {
    if (!name.trim()) return
    onAdd(name.trim())
    setInput('')
    setOpen(false)
  }

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="text-xs text-blue-600 hover:text-blue-800 border border-blue-300 rounded px-2 py-0.5"
      >
        + タグ追加
      </button>
      {open && (
        <div className="absolute left-0 top-6 z-20 bg-white border rounded shadow-lg w-48">
          <input
            autoFocus
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleAdd(input)
              if (e.key === 'Escape') setOpen(false)
            }}
            placeholder="タグ名を入力..."
            className="w-full px-3 py-2 text-sm border-b outline-none"
          />
          <ul className="max-h-40 overflow-y-auto">
            {filtered.map((t) => (
              <li key={t.id}>
                <button
                  onClick={() => handleAdd(t.name)}
                  className="w-full text-left px-3 py-1.5 text-sm hover:bg-gray-100"
                >
                  {t.name}
                </button>
              </li>
            ))}
            {input && !filtered.some((t) => t.name === input) && (
              <li>
                <button
                  onClick={() => handleAdd(input)}
                  className="w-full text-left px-3 py-1.5 text-sm text-blue-600 hover:bg-gray-100"
                >
                  「{input}」を新規作成
                </button>
              </li>
            )}
          </ul>
        </div>
      )}
    </div>
  )
}
