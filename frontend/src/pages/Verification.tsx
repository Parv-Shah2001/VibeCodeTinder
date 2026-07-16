import { useState } from 'react'
import { api } from '../api/client'
import { BadgeCheck, Camera, Upload } from 'lucide-react'

export default function Verification() {
  const [status, setStatus] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const fetchStatus = async () => {
    const { data } = await api.get('/verification/status')
    setStatus(data)
  }

  const submitMock = async () => {
    setLoading(true)
    try {
      // In prod upload selfie via media then submit id
      const { data } = await api.post('/verification/submit', { selfie_asset_id: 1 })
      setStatus(data)
    } catch (e) {
      // mock for demo
      setStatus({ status: 'approved', confidence_score: 0.95 })
    } finally { setLoading(false) }
  }

  return (
    <div className="max-w-md mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2"><BadgeCheck className="text-blue-500" /> Photo Verification</h1>
      <div className="bg-blue-50 border border-blue-200 rounded-2xl p-4">
        <h3 className="font-semibold">Get Verified – 30% more matches</h3>
        <p className="text-sm text-gray-600 mt-1">Take a selfie mimicking a pose. We compare with your profile photos using AWS Rekognition (mock in dev). Production auto-approves confidence &gt;0.9 else manual review.</p>
      </div>

      <div className="bg-white border rounded-2xl p-6 text-center">
        <Camera className="w-16 h-16 mx-auto text-gray-300 mb-4" />
        <p className="text-sm text-gray-500 mb-4">Upload a selfie for verification</p>
        <button onClick={submitMock} disabled={loading} className="px-6 py-3 rounded-full bg-blue-500 text-white font-semibold flex items-center gap-2 mx-auto">
          <Upload className="w-4 h-4" /> {loading ? 'Verifying...' : 'Submit Selfie'}
        </button>
      </div>

      <button onClick={fetchStatus} className="w-full py-2 rounded-full border">Check Status</button>

      {status && (
        <div className="bg-white border rounded-2xl p-4">
          <p className="font-semibold">Status: {status.status}</p>
          {status.confidence_score && <p className="text-sm">Confidence: {(status.confidence_score * 100).toFixed(1)}%</p>}
          {status.status === 'approved' && <p className="text-green-600 text-sm mt-2">✅ You are verified! Blue tick added.</p>}
        </div>
      )}
    </div>
  )
}
