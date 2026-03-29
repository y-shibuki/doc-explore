import { useState } from 'react'
import { DetailPanel } from './components/layout/DetailPanel'
import { Sidebar } from './components/layout/Sidebar'
import { TreeContext } from './components/tree/TreeContext'
import { useTreeState } from './hooks/useTree'

export default function App() {
  const [selectedFileId, setSelectedFileId] = useState<number | null>(null)
  const treeState = useTreeState()

  const handleSelectFile = (id: number, path: string) => {
    setSelectedFileId(id)
    treeState.highlight(path)
  }

  const handleSelectFromSearch = (id: number) => {
    setSelectedFileId(id)
  }

  return (
    <TreeContext.Provider
      value={{ ...treeState, selectedFileId, onSelectFile: handleSelectFile }}
    >
      <div className="flex h-screen bg-white">
        <aside className="w-72 border-r flex-shrink-0 overflow-hidden flex flex-col">
          <Sidebar selectedFileId={selectedFileId} onSelectFile={handleSelectFromSearch} />
        </aside>
        <main className="flex-1 overflow-hidden">
          <DetailPanel fileId={selectedFileId} onDeleted={() => setSelectedFileId(null)} />
        </main>
      </div>
    </TreeContext.Provider>
  )
}
