import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { Music, Gamepad2, Plane, Dumbbell } from 'lucide-react'

const icons: any = { Music, Gaming: Gamepad2, Travel: Plane, Fitness: Dumbbell }

export default function Explore() {
  const [data, setData] = useState<any>({})
  const [selectedInterest, setSelectedInterest] = useState<string | null>(null)

  useEffect(() => {
    api.get('/explore').then(r => setData(r.data)).catch(()=>{
      setData({
        Music: [{ user_id: 1, display_name: 'Alex', photo: 'https://i.pravatar.cc/200?img=1' }],
        Travel: [{ user_id: 2, display_name: 'Jordan', photo: 'https://i.pravatar.cc/200?img=2' }],
      })
    })
  }, [])

  const interests = Object.keys(data)

  return (
    <div className="max-w-md mx-auto p-4">
      <h1 className="text-xl font-bold">Explore</h1>
      <p className="text-xs text-gray-500">Find people by interests – precomputed daily for 1M DAU</p>

      <div className="flex gap-2 mt-3 overflow-x-auto pb-2">
        {interests.map(interest => {
          const Icon = icons[interest] || Music
          return (
            <button key={interest} onClick={() => setSelectedInterest(interest === selectedInterest ? null : interest)} className={`flex flex-col items-center gap-1 px-4 py-3 rounded-2xl border min-w-[80px] ${selectedInterest === interest ? 'bg-[#FF4458] text-white border-[#FF4458]' : 'bg-white'}`}>
              <Icon className="w-6 h-6" />
              <span className="text-xs font-semibold">{interest}</span>
            </button>
          )
        })}
      </div>

      <div className="mt-6 space-y-6">
        {(selectedInterest ? [selectedInterest] : interests).map(interest => (
          <div key={interest}>
            <h3 className="font-bold mb-2">{interest}</h3>
            <div className="grid grid-cols-3 gap-2">
              {(data[interest] || []).map((p: any) => (
                <div key={p.user_id} className="rounded-xl overflow-hidden aspect-square bg-gray-100 relative">
                  <img src={p.photo} className="w-full h-full object-cover" />
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-1.5">
                    <p className="text-white text-xs font-semibold truncate">{p.display_name}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
