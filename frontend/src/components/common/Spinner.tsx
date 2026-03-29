export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' }) {
  const cls = size === 'sm' ? 'w-4 h-4 border-2' : 'w-6 h-6 border-2'
  return (
    <span
      className={`${cls} inline-block rounded-full border-gray-300 border-t-blue-500 animate-spin`}
    />
  )
}
