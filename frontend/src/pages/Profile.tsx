import { useEffect, useState } from 'react'
import { ProfileAPI, MediaAPI } from '../api/client'
import { useAuthStore } from '../store/auth'
import { Settings, LogOut, Edit3, MapPin, Briefcase, Plus, Trash2, Star } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Profile() {
  const [profile, setProfile] = useState<any>(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState<any>({})
  const logout = useAuthStore(s => s.logout)
  const navigate = useNavigate()

  const load = async () => {
    try {
      const { data } = await ProfileAPI.getMyProfile()
      setProfile(data)
      setForm(data)
    } catch (e) { console.error(e) }
  }

  useEffect(() => { load() }, [])

  const save = async () => {
    try {
      await ProfileAPI.updateProfile({
        display_name: form.display_name,
        bio: form.bio,
        city: form.city,
        job_title: form.job_title,
        school: form.school,
      })
      setEditing(false)
      load()
    } catch (e) { console.error(e) }
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      await MediaAPI.upload(file)
      load()
    } catch (err) { alert('Upload failed') }
  }

  if (!profile) return <div className="p-6">Loading...</div>

  return (
    <div className="max-w-md mx-auto w-full pb-20">
      {/* Photos grid */}
      <div className="p-4">
        <div className="grid grid-cols-3 gap-2">
          {profile.photos?.map((p: any) => (
            <div key={p.id} className="relative aspect-[3/4] rounded-xl overflow-hidden bg-gray-100 group">
              <img src={p.url} className="w-full h-full object-cover" />
              <button onClick={async () => { await MediaAPI.delete(p.id); load() }} className="absolute top-1 right-1 w-6 h-6 bg-black/60 rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100">
                <Trash2 className="w-3 h-3" />
              </button>
              {p.is_primary && <span className="absolute bottom-1 left-1 bg-black/70 text-white text-[10px] px-1.5 py-0.5 rounded">MAIN</span>}
            </div>
          ))}
          {Array.from({ length: Math.max(0, 6 - (profile.photos?.length || 0)) }).map((_, i) => (
            <label key={`empty-${i}`} className="aspect-[3/4] rounded-xl border-2 border-dashed border-gray-300 flex flex-col items-center justify-center cursor-pointer hover:border-[#FF4458] text-gray-400">
              <Plus className="w-6 h-6" />
              <span className="text-xs mt-1">Add Photo</span>
              <input type="file" accept="image/*" className="hidden" onChange={handleUpload} />
            </label>
          ))}
        </div>
      </div>

      <div className="px-6 mt-2 space-y-4">
        {editing ? (
          <>
            <input value={form.display_name || ''} onChange={e => setForm({ ...form, display_name: e.target.value })} placeholder="Name" className="w-full px-4 py-3 rounded-xl border" />
            <textarea value={form.bio || ''} onChange={e => setForm({ ...form, bio: e.target.value })} placeholder="About you" className="w-full px-4 py-3 rounded-xl border h-24" />
            <input value={form.city || ''} onChange={e => setForm({ ...form, city: e.target.value })} placeholder="City" className="w-full px-4 py-3 rounded-xl border" />
            <input value={form.job_title || ''} onChange={e => setForm({ ...form, job_title: e.target.value })} placeholder="Job Title" className="w-full px-4 py-3 rounded-xl border" />
            <input value={form.school || ''} onChange={e => setForm({ ...form, school: e.target.value })} placeholder="School" className="w-full px-4 py-3 rounded-xl border" />
            <div className="flex gap-2">
              <button onClick={save} className="flex-1 py-3 rounded-full bg-[#FF4458] text-white font-semibold">Save</button>
              <button onClick={() => setEditing(false)} className="flex-1 py-3 rounded-full border font-semibold">Cancel</button>
            </div>
          </>
        ) : (
          <>
            <div>
              <h2 className="text-2xl font-bold flex items-center gap-2">{profile.display_name}, {profile.age} {profile.is_verified && <Star className="w-5 h-5 text-blue-500 fill-blue-500" />}</h2>
              {profile.city && <p className="flex items-center gap-1 text-gray-600 text-sm mt-1"><MapPin className="w-4 h-4" />{profile.city}</p>}
              {profile.job_title && <p className="flex items-center gap-1 text-gray-600 text-sm"><Briefcase className="w-4 h-4" />{profile.job_title}</p>}
            </div>
            {profile.bio && <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded-xl">{profile.bio}</p>}

            <button onClick={() => setEditing(true)} className="w-full py-3 rounded-full border flex items-center justify-center gap-2 font-semibold">
              <Edit3 className="w-4 h-4" /> Edit Profile
            </button>

            <div className="bg-gray-50 rounded-xl p-4 text-xs text-gray-600 space-y-1">
              <p className="font-semibold">Preferences</p>
              <p>Age: {profile.preferences?.min_age} - {profile.preferences?.max_age}</p>
              <p>Distance: {profile.preferences?.max_distance_km} km</p>
              <p>Show me: {profile.preferences?.show_me}</p>
            </div>

            <div className="space-y-2 pt-4">
              <button onClick={() => { logout(); navigate('/login') }} className="w-full py-3 rounded-full bg-white border flex items-center justify-center gap-2 text-red-500 font-semibold">
                <LogOut className="w-4 h-4" /> Log Out
              </button>
            </div>

            <div className="text-center text-[11px] text-gray-400 pt-6">
              <p>VibeCodeTinder v1.0.0 • Modular Monolith</p>
              <p>50M users • 1M DAU • Production Ready</p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
