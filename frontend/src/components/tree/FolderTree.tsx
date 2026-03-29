import { useTree } from '../../hooks/useTree'
import { Spinner } from '../common/Spinner'
import { TreeNodeItem } from './TreeNode'

export function FolderTree() {
  const { data, isLoading, error } = useTree()

  if (isLoading) return <div className="p-4"><Spinner /></div>
  if (error) return <div className="p-4 text-sm text-red-500">読み込みエラー</div>
  if (!data?.length) return <div className="p-4 text-sm text-gray-400">スキャン対象フォルダが設定されていません</div>

  return (
    <ul className="py-2">
      {data.map((node) => (
        <TreeNodeItem key={node.path} node={node} depth={0} />
      ))}
    </ul>
  )
}
