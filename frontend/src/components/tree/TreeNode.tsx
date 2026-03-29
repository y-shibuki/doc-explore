import { RiFile2Line, RiFilePdf2Line, RiFileExcel2Line, RiFileWord2Line, RiFolderLine, RiFolderOpenLine } from 'react-icons/ri'
import { useTree } from '../../hooks/useTree'
import type { TreeNode as TreeNodeType } from '../../types'
import { Spinner } from '../common/Spinner'
import { useTreeContext } from './TreeContext'

function FileIcon({ ext }: { ext: string | null }) {
  if (ext === '.pdf') return <RiFilePdf2Line className="text-red-500 shrink-0" />
  if (ext === '.docx') return <RiFileWord2Line className="text-blue-500 shrink-0" />
  if (ext === '.xlsx' || ext === '.xls') return <RiFileExcel2Line className="text-green-600 shrink-0" />
  return <RiFile2Line className="text-gray-400 shrink-0" />
}

function FolderChildren({ path }: { path: string }) {
  const { data, isLoading } = useTree(path)
  if (isLoading) return <div className="pl-4 py-1"><Spinner size="sm" /></div>
  if (!data?.length) return <div className="pl-6 py-1 text-xs text-gray-400">空のフォルダ</div>
  return (
    <ul>
      {data.map((node) => (
        <TreeNodeItem key={node.path} node={node} depth={1} />
      ))}
    </ul>
  )
}

interface Props {
  node: TreeNodeType
  depth?: number
}

export function TreeNodeItem({ node, depth = 0 }: Props) {
  const { expanded, highlighted, toggle, selectedFileId, onSelectFile } = useTreeContext()
  const isExpanded = expanded.has(node.path)
  const isHighlighted = highlighted === node.path
  const isSelected = node.file_id !== null && selectedFileId === node.file_id
  const indent = `pl-${4 + depth * 4}`

  if (node.type === 'folder') {
    return (
      <li>
        <button
          onClick={() => toggle(node.path)}
          className={`flex items-center gap-1.5 w-full text-left text-sm py-1 px-2 ${indent} hover:bg-gray-100 rounded ${isHighlighted ? 'bg-yellow-100' : ''}`}
        >
          {isExpanded
            ? <RiFolderOpenLine className="text-yellow-500 shrink-0" />
            : <RiFolderLine className="text-yellow-500 shrink-0" />
          }
          <span className="truncate">{node.name}</span>
        </button>
        {isExpanded && <FolderChildren path={node.path} />}
      </li>
    )
  }

  return (
    <li>
      <button
        onClick={() => node.file_id !== null && onSelectFile(node.file_id, node.path)}
        className={`flex items-center gap-1.5 w-full text-left text-sm py-1 px-2 ${indent} hover:bg-gray-100 rounded
          ${isSelected ? 'bg-blue-50 font-medium' : ''}
          ${isHighlighted ? 'bg-yellow-100' : ''}
          ${node.file_id === null ? 'opacity-50' : ''}`}
      >
        <FileIcon ext={node.ext} />
        <span className="truncate">{node.name}</span>
      </button>
    </li>
  )
}
