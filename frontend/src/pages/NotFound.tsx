import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-[70vh] text-center p-6">
      <h1 className="text-6xl font-bold text-gray-200">404</h1>
      <h2 className="text-xl font-semibold mt-2">Page not found</h2>
      <p className="text-gray-500 text-sm mt-1">Looks like you swiped left on this page</p>
      <Link to="/" className="mt-6 px-6 py-3 rounded-full bg-[#FF4458] text-white font-semibold">Back to Feed</Link>
    </div>
  )
}
