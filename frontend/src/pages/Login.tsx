import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/auth'
import { Flame } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('test@example.com')
  const [password, setPassword] = useState('password123')
  const [isRegister, setIsRegister] = useState(false)
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const login = useAuthStore(s => s.login)
  const register = useAuthStore(s => s.register)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      if (isRegister) await register(email, password, name)
      else await login(email, password)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed, try again')
    } finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#FF4458] via-[#FD267D] to-[#FF8A00] flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl w-full max-w-sm p-8 shadow-2xl">
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-[#FF4458] to-[#FD267D] flex items-center justify-center">
            <Flame className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold mt-4">VibeCodeTinder</h1>
          <p className="text-gray-500 text-sm mt-1">Production Tinder Replica • Modular Monolith</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <input value={name} onChange={e=>setName(e.target.value)} placeholder="Display Name" className="w-full px-4 py-3 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#FF4458]" />
          )}
          <input value={email} onChange={e=>setEmail(e.target.value)} type="email" placeholder="Email" className="w-full px-4 py-3 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#FF4458]" required />
          <input value={password} onChange={e=>setPassword(e.target.value)} type="password" placeholder="Password" className="w-full px-4 py-3 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#FF4458]" required />
          {error && <p className="text-red-500 text-sm text-center">{error}</p>}
          <button disabled={loading} className="w-full py-3 rounded-full bg-gradient-to-r from-[#FF4458] to-[#FD267D] text-white font-semibold shadow-lg disabled:opacity-50">
            {loading ? '...' : isRegister ? 'Create Account' : 'Log In'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button onClick={()=>setIsRegister(!isRegister)} className="text-sm text-gray-600">
            {isRegister ? 'Already have account? Log in' : "Don't have account? Sign up"}
          </button>
        </div>

        <div className="mt-8 p-3 bg-gray-50 rounded-xl text-xs text-gray-500">
          <p className="font-semibold mb-1">Scale Design:</p>
          <p>• 50M users • 1M DAU • 500k new/day</p>
          <p>• 1B matches/day • 200M msgs/day</p>
          <p>• Modular monolith + Redis + S3</p>
        </div>
      </div>
    </div>
  )
}
