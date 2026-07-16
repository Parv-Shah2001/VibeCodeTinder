import { Shield, Flag, Lock, EyeOff } from 'lucide-react'

export default function Safety() {
  return (
    <div className="max-w-md mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2"><Shield className="w-6 h-6" /> Safety Center</h1>

      <div className="grid grid-cols-2 gap-3">
        <div className="bg-white border rounded-2xl p-4">
          <Flag className="w-6 h-6 text-red-500 mb-2" />
          <h3 className="font-semibold text-sm">Report</h3>
          <p className="text-xs text-gray-500">Report suspicious behavior. Our moderation AI + human review within 24h.</p>
        </div>
        <div className="bg-white border rounded-2xl p-4">
          <EyeOff className="w-6 h-6 text-gray-500 mb-2" />
          <h3 className="font-semibold text-sm">Block</h3>
          <p className="text-xs text-gray-500">Block prevents them from seeing you or messaging.</p>
        </div>
        <div className="bg-white border rounded-2xl p-4">
          <Lock className="w-6 h-6 text-blue-500 mb-2" />
          <h3 className="font-semibold text-sm">Photo Verification</h3>
          <p className="text-xs text-gray-500">Blue tick ensures real people.</p>
        </div>
        <div className="bg-white border rounded-2xl p-4">
          <Shield className="w-6 h-6 text-green-500 mb-2" />
          <h3 className="font-semibold text-sm">GDPR Delete</h3>
          <p className="text-xs text-gray-500">Delete all data cascades profiles/media/swipes/matches/messages per privacy law.</p>
        </div>
      </div>

      <div className="bg-gray-50 rounded-xl p-4 text-xs space-y-2">
        <p className="font-semibold">How we handle 50M users safety:</p>
        <p>• Media pipeline NSFW detection (Rekognition) + virus scan</p>
        <p>• Text toxicity detection Perspective API placeholder</p>
        <p>• Rate limiting prevents spam 60 msg/min 100 swipes/min</p>
        <p>• Block filters discovery + messaging + search</p>
        <p>• Report queue with admin review /reports endpoint</p>
        <p>• Analytics anomaly detection swipe velocity &gt;1000/min flagged bot</p>
      </div>
    </div>
  )
}
