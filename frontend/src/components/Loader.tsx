import { Flame } from 'lucide-react'

export default function Loader({ text = 'Loading...' }: { text?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-10 gap-3">
      <Flame className="w-10 h-10 text-[#FF4458] animate-pulse" />
      <span className="text-sm text-gray-500">{text}</span>
    </div>
  )
}
