import { useEffect, useState } from 'react'
import { DiscoveryAPI, SwipeAPI, MediaAPI } from '../api/client'
import { Profile } from '../types'
import SwipeCard from '../components/SwipeCard'
import MatchModal from '../components/MatchModal'
import { Flame, RotateCcw, Zap } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Feed() {
  const [profiles, setProfiles] = useState<Profile[]>([])
  const [loading, setLoading] = useState(true)
  const [matchInfo, setMatchInfo] = useState<{ name: string, photo?: string } | null>(null)
  const navigate = useNavigate()

  const loadFeed = async () => {
    setLoading(true)
    try {
      const { data } = await DiscoveryAPI.feed(20)
      setProfiles(data)
    } catch (e) {
      console.error(e)
    } finally { setLoading(false) }
  }

  useEffect(() => { loadFeed() }, [])

  const handleSwipe = async (type: 'like' | 'dislike' | 'superlike') => {
    const current = profiles[0]
    if (!current) return
    const nextProfiles = profiles.slice(1)
    setProfiles(nextProfiles)
    try {
      const { data } = await SwipeAPI.swipe(current.user_id, type)
      if (data.is_match) {
        setMatchInfo({ name: current.display_name, photo: current.photos[0]?.url })
      }
    } catch (err: any) {
      console.error(err)
    }
    if (nextProfiles.length < 5) {
      try {
        const { data } = await DiscoveryAPI.feed(15)
        // avoid duplicates
        setProfiles(prev => [...prev, ...data.filter((p: Profile) => !prev.some(x => x.user_id === p.user_id))])
      } catch {}
    }
  }

  if (loading) return <div className="flex items-center justify-center h-[80vh]"><Flame className="w-8 h-8 animate-pulse text-[#FF4458]" /></div>

  if (profiles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] text-center px-6">
        <Flame className="w-16 h-16 text-gray-300 mb-4" />
        <h2 className="text-xl font-semibold">No more profiles nearby</h2>
        <p className="text-gray-500 text-sm mt-2">Check back later or expand your distance</p>
        <button onClick={loadFeed} className="mt-6 px-6 py-3 rounded-full bg-gradient-to-r from-[#FF4458] to-[#FD267D] text-white font-semibold flex items-center gap-2">
          <RotateCcw className="w-4 h-4" /> Reload
        </button>
      </div>
    )
  }

  return (
    <div className="relative w-full max-w-sm mx-auto h-[calc(100vh-56px)] md:h-[700px] mt-2">
      <div className="relative w-full h-full">
        {/* Stack: render next 2 underneath */}
        {profiles.slice(0, 3).reverse().map((p, idx) => {
          const isTop = idx === profiles.slice(0,3).length-1
          return (
            <SwipeCard key={p.user_id} profile={p} active={isTop} onSwipe={handleSwipe} />
          )
        })}
      </div>

      {/* Boost button */}
      <button onClick={async () => { await DiscoveryAPI.boost(); alert('Boosted for 30 mins! +200 score'); }} className="absolute top-3 right-3 z-10 bg-purple-600 text-white text-xs px-3 py-1.5 rounded-full flex items-center gap-1 shadow-lg">
        <Zap className="w-4 h-4" /> BOOST
      </button>

      {matchInfo && (
        <MatchModal
          otherName={matchInfo.name}
          otherPhoto={matchInfo.photo}
          onClose={() => setMatchInfo(null)}
          onMessage={() => { setMatchInfo(null); navigate('/matches') }}
        />
      )}
    </div>
  )
}
