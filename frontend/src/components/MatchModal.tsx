import { motion } from 'framer-motion'
import { MessageCircle } from 'lucide-react'

interface Props {
  otherName: string
  otherPhoto?: string
  onClose: () => void
  onMessage: () => void
}

export default function MatchModal({ otherName, otherPhoto, onClose, onMessage }: Props) {
  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6">
      <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="text-center">
        <h1 className="text-6xl font-bold italic bg-gradient-to-r from-[#FF4458] to-[#FD267D] bg-clip-text text-transparent">It's a Match!</h1>
        <p className="text-white/80 mt-2">You and {otherName} have liked each other</p>
        <div className="flex justify-center gap-6 mt-10">
          <img src={otherPhoto || `https://i.pravatar.cc/200?u=${otherName}`} className="w-28 h-28 rounded-full border-4 border-white object-cover" />
          <img src={`https://i.pravatar.cc/200?u=me`} className="w-28 h-28 rounded-full border-4 border-white object-cover" />
        </div>
        <div className="mt-10 flex flex-col gap-3">
          <button onClick={onMessage} className="bg-white text-black px-8 py-4 rounded-full font-semibold flex items-center justify-center gap-2 mx-auto">
            <MessageCircle className="w-5 h-5" /> Send a Message
          </button>
          <button onClick={onClose} className="text-white/70 py-2">Keep Swiping</button>
        </div>
      </motion.div>
    </div>
  )
}
