import { Flame, MessageCircle, User } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

export default function TopBar() {
  const loc = useLocation()
  return (
    <div className="h-14 w-full flex items-center justify-between px-6 bg-white shadow-sm border-b">
      <Link to="/profile" className={`p-2 rounded-full ${loc.pathname.startsWith('/profile') ? 'bg-gray-100' : ''}`}>
        <User className="w-6 h-6 text-gray-400" />
      </Link>
      <Link to="/" className="flex items-center gap-1">
        <Flame className="w-8 h-8 text-[#FF4458]" />
        <span className="font-bold text-xl text-gray-800 tracking-tight">vibe</span>
      </Link>
      <Link to="/matches" className={`p-2 rounded-full ${loc.pathname.startsWith('/matches') ? 'bg-gray-100' : ''}`}>
        <MessageCircle className="w-6 h-6 text-gray-400" />
      </Link>
    </div>
  )
}
