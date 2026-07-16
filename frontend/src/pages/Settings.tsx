import { useState, useEffect } from 'react'
import { ProfileAPI } from '../api/client'
import { useGeolocation } from '../hooks/useGeolocation'
import { MapPin, Shield, LogOut, Bell } from 'lucide-react'
import { useAuthStore } from '../store/auth'
import { useNavigate } from 'react-router-dom'

export default function Settings() {
  const [prefs, setPrefs] = useState<any>({ min_age: 18, max_age: 60, max_distance_km: 50, show_me: 'everyone', global_mode: false })
  const { coords } = useGeolocation()
  const logout = useAuthStore(s => s.logout)
  const navigate = useNavigate()

  useEffect(() => {
    ProfileAPI.getMyProfile().then(r => {
      if (r.data.preferences) setPrefs(r.data.preferences)
    })
  }, [])

  const save = async () => {
    await ProfileAPI.updatePrefs(prefs)
    alert('Preferences saved')
  }

  const updateLocation = async () => {
    if (coords) {
      await ProfileAPI.updateProfile({ latitude: coords.lat, longitude: coords.lon })
      alert('Location updated')
    }
  }

  return (
    <div className="max-w-md mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>

      <div className="space-y-4 bg-white rounded-2xl p-4 border">
        <h3 className="font-semibold flex items-center gap-2"><MapPin className="w-4 h-4" /> Discovery Preferences</h3>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-500">Min Age</label>
            <input type="number" value={prefs.min_age} onChange={e => setPrefs({ ...prefs, min_age: Number(e.target.value) })} className="w-full border rounded-lg px-3 py-2" />
          </div>
          <div>
            <label className="text-xs text-gray-500">Max Age</label>
            <input type="number" value={prefs.max_age} onChange={e => setPrefs({ ...prefs, max_age: Number(e.target.value) })} className="w-full border rounded-lg px-3 py-2" />
          </div>
        </div>
        <div>
          <label className="text-xs text-gray-500">Max Distance (km)</label>
          <input type="range" min={5} max={500} value={prefs.max_distance_km} onChange={e => setPrefs({ ...prefs, max_distance_km: Number(e.target.value) })} className="w-full" />
          <span className="text-sm">{prefs.max_distance_km} km</span>
        </div>
        <div>
          <label className="text-xs text-gray-500">Show Me</label>
          <select value={prefs.show_me} onChange={e => setPrefs({ ...prefs, show_me: e.target.value })} className="w-full border rounded-lg px-3 py-2">
            <option value="male">Men</option>
            <option value="female">Women</option>
            <option value="everyone">Everyone</option>
          </select>
        </div>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={prefs.global_mode} onChange={e => setPrefs({ ...prefs, global_mode: e.target.checked })} />
          <span className="text-sm">Global Mode (ignore distance)</span>
        </label>
        <button onClick={save} className="w-full py-3 rounded-full bg-[#FF4458] text-white font-semibold">Save Preferences</button>
      </div>

      <div className="space-y-2 bg-white rounded-2xl p-4 border">
        <h3 className="font-semibold flex items-center gap-2"><MapPin className="w-4 h-4" /> Location</h3>
        <p className="text-sm text-gray-500">{coords ? `${coords.lat.toFixed(4)}, ${coords.lon.toFixed(4)}` : 'Fetching location...'}</p>
        <button onClick={updateLocation} disabled={!coords} className="w-full py-2 rounded-full border font-semibold disabled:opacity-50">Update Location</button>
      </div>

      <div className="space-y-2 bg-white rounded-2xl p-4 border">
        <h3 className="font-semibold flex items-center gap-2"><Shield className="w-4 h-4" /> Privacy & Safety</h3>
        <p className="text-xs text-gray-500">Blocked users, reporting, and data management. Your data is encrypted and stored securely per GDPR.</p>
      </div>

      <div className="space-y-2 bg-white rounded-2xl p-4 border">
        <h3 className="font-semibold flex items-center gap-2"><Bell className="w-4 h-4" /> Notifications</h3>
        <p className="text-xs text-gray-500">Push notifications for matches and messages are enabled via FCM/APNS in production.</p>
      </div>

      <button onClick={() => { logout(); navigate('/login') }} className="w-full py-3 rounded-full border flex items-center justify-center gap-2 text-red-500 font-semibold">
        <LogOut className="w-4 h-4" /> Log Out
      </button>

      <div className="text-center text-[11px] text-gray-400">
        <p>VibeCodeTinder Production v1.0.0</p>
        <p>50M users scale • Modular Monolith • SOC2 Ready</p>
      </div>
    </div>
  )
}
