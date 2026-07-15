import { useState } from 'react'
import { motion, PanInfo } from 'framer-motion'
import { MapPin, Briefcase, GraduationCap, BadgeCheck, X, Heart, Star } from 'lucide-react'
import { Profile } from '../types'

interface Props {
  profile: Profile
  onSwipe: (type: 'like' | 'dislike' | 'superlike') => void
  active?: boolean
}

export default function SwipeCard({ profile, onSwipe, active = true }: Props) {
  const [currentPhotoIdx, setCurrentPhotoIdx] = useState(0)
  const photos = profile.photos || []
  const photo = photos[currentPhotoIdx]?.url || `https://i.pravatar.cc/400?u=${profile.user_id}`

  const handleDragEnd = (_: any, info: PanInfo) => {
    if (!active) return
    const threshold = 100
    if (info.offset.x > threshold) onSwipe('like')
    else if (info.offset.x < -threshold) onSwipe('dislike')
    else if (info.offset.y < -threshold) onSwipe('superlike')
  }

  const nextPhoto = () => setCurrentPhotoIdx((i) => (i + 1) % Math.max(photos.length, 1))
  const prevPhoto = () => setCurrentPhotoIdx((i) => (i - 1 + Math.max(photos.length, 1)) % Math.max(photos.length, 1))

  return (
    <motion.div
      drag={active}
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      onDragEnd={handleDragEnd}
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.8, opacity: 0 }}
      className="absolute inset-0 w-full h-full rounded-3xl overflow-hidden bg-gray-900 shadow-2xl select-none"
      style={{ touchAction: 'none' }}
    >
      <img src={photo} alt={profile.display_name} className="w-full h-full object-cover" draggable={false} />
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black via-black/20 to-transparent" />

      {/* Top indicators */}
      <div className="absolute top-3 left-3 right-3 flex gap-1">
        {photos.map((_, idx) => (
          <div key={idx} className={`h-1 flex-1 rounded-full ${idx === currentPhotoIdx ? 'bg-white' : 'bg-white/40'}`} />
        ))}
      </div>
      {/* Photo tap areas */}
      <div className="absolute top-0 left-0 w-1/3 h-3/4" onClick={prevPhoto} />
      <div className="absolute top-0 right-0 w-1/3 h-3/4" onClick={nextPhoto} />

      {/* Info */}
      <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
        <div className="flex items-center gap-2">
          <h2 className="text-3xl font-bold">{profile.display_name}</h2>
          {profile.age && <span className="text-2xl font-light">{profile.age}</span>}
          {profile.is_verified && <BadgeCheck className="w-6 h-6 text-blue-400" />}
          {profile.is_boosted && <span className="bg-purple-500 text-xs px-2 py-0.5 rounded-full">BOOSTED</span>}
        </div>
        {profile.job_title && (
          <div className="flex items-center gap-1.5 mt-1 text-white/90">
            <Briefcase className="w-4 h-4" /> <span className="text-sm">{profile.job_title}</span>
          </div>
        )}
        {profile.school && (
          <div className="flex items-center gap-1.5 mt-1 text-white/90">
            <GraduationCap className="w-4 h-4" /> <span className="text-sm">{profile.school}</span>
          </div>
        )}
        {profile.city && (
          <div className="flex items-center gap-1.5 mt-1 text-white/90">
            <MapPin className="w-4 h-4" /> <span className="text-sm">{profile.city} {profile.distance_km ? `• ${profile.distance_km} km away` : ''}</span>
          </div>
        )}
        {profile.bio && <p className="mt-3 text-sm text-white/90 line-clamp-3">{profile.bio}</p>}
      </div>

      {/* Action buttons - only on active card */}
      {active && (
        <div className="absolute -bottom-2 left-0 right-0 flex justify-center gap-4 pb-6 md:pb-8 pointer-events-none">
          <button onClick={() => onSwipe('dislike')} className="pointer-events-auto w-14 h-14 rounded-full bg-white shadow-xl flex items-center justify-center border border-gray-100 hover:scale-110 transition">
            <X className="w-7 h-7 text-[#FF4458]" />
          </button>
          <button onClick={() => onSwipe('superlike')} className="pointer-events-auto w-12 h-12 rounded-full bg-white shadow-xl flex items-center justify-center border border-gray-100 hover:scale-110 transition">
            <Star className="w-6 h-6 text-[#0AB0F0]" />
          </button>
          <button onClick={() => onSwipe('like')} className="pointer-events-auto w-14 h-14 rounded-full bg-white shadow-xl flex items-center justify-center border border-gray-100 hover:scale-110 transition">
            <Heart className="w-7 h-7 text-[#4DDB92] fill-[#4DDB92]" />
          </button>
        </div>
      )}
    </motion.div>
  )
}
