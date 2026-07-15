import { Flame, MessageCircle, User, Settings } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'

export default function BottomNav() {
  const loc = useLocation()
  const isActive = (p: string) => loc.pathname === p
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-2 md:hidden max-w-md mx-auto">
      <Link to="/" className={`p-2 ${isActive('/') ? 'text-[#FF4458]' : 'text-gray-400'}`}><Flame className="w-6 h-6" /></Link>
      <Link to="/matches" className={`p-2 ${isActive('/matches') ? 'text-[#FF4458]' : 'text-gray-400'}`}><MessageCircle className="w-6 h-6" /></Link>
      <Link to="/profile" className={`p-2 ${isActive('/profile') ? 'text-[#FF4458]' : 'text-gray-400'}`}><User className="w-6 h-6" /></Link>
      <Link to="/settings" className={`p-2 ${isActive('/settings') ? 'text-[#FF4458]' : 'text-gray-400'}`}><Settings className="w-6 h-6" /></Link>
    </div>
  )
}
