import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Heart, Star } from 'lucide-react'

export default function LikesYou() {
  const [likes, setLikes] = useState<any[]>([])

  useEffect(() => {
    api.get('/explore/likes-you').then(r => setLikes(r.data)).catch(()=>setLikes([
      { swiper_id: 2, swipe_type: 'like', profile: { display_name: 'Alex', age: 24, photo: 'https://i.pravatar.cc/300?img=2' } },
      { swiper_id: 3, swipe_type: 'superlike', profile: { display_name: 'Jordan', age: 26, photo: 'https://i.pravatar.cc/300?img=3' } },
    ]))
  }, [])

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-xl font-bold flex items-center gap-2"><Heart className="fill-[#FF4458] text-[#FF4458]" /> Likes You – Gold</h1>
      <p className="text-xs text-gray-500">Gold feature – see who liked you (production uses Top Picks ML + precomputed daily)</p>

      <div className="grid grid-cols-2 gap-3 mt-4">
        {likes.map(l => (
          <div key={l.swiper_id} className="relative rounded-2xl overflow-hidden aspect-[3/4] bg-gray-100">
            <img src={l.profile?.photo || `https://i.pravatar.cc/300?u=${l.swiper_id}`} className="w-full h-full object-cover blur-sm" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 to-transparent flex flex-col justify-end p-3 text-white">
              <p className="font-semibold">{l.profile?.display_name} • {l.profile?.age || 24}</p>
              {l.swipe_type === 'superlike' && <span className="text-xs bg-blue-500 px-2 py-0.5 rounded-full w-fit flex items-center gap-1"><Star className="w-3 h-3" /> Super Like</span>}
            </div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="bg-white/90 px-3 py-1.5 rounded-full text-xs font-semibold">Gold required to see</div>
            </div>
          </div>
        ))}
      </div>

      {likes.length === 0 && <p className="text-center text-gray-400 mt-20">No likes yet – boost to get more!</p>}
    </div>
  )
}
