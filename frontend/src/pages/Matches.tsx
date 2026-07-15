import { useEffect, useState } from 'react'
import { MatchAPI, MessagingAPI } from '../api/client'
import { Match, Conversation } from '../types'
import { MessageCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function Matches() {
  const [matches, setMatches] = useState<Match[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [tab, setTab] = useState<'matches' | 'messages'>('matches')
  const navigate = useNavigate()

  useEffect(() => {
    MatchAPI.list().then(r => setMatches(r.data)).catch(console.error)
    MessagingAPI.conversations().then(r => setConversations(r.data)).catch(console.error)
  }, [])

  return (
    <div className="max-w-md mx-auto w-full">
      <div className="flex border-b">
        <button onClick={() => setTab('matches')} className={`flex-1 py-3 font-semibold ${tab === 'matches' ? 'border-b-2 border-[#FF4458] text-[#FF4458]' : 'text-gray-400'}`}>Matches ({matches.length})</button>
        <button onClick={() => setTab('messages')} className={`flex-1 py-3 font-semibold ${tab === 'messages' ? 'border-b-2 border-[#FF4458] text-[#FF4458]' : 'text-gray-400'}`}>Messages</button>
      </div>

      {tab === 'matches' ? (
        <div>
          <div className="p-4 grid grid-cols-3 gap-4">
            {matches.map(m => (
              <div key={m.id} className="flex flex-col items-center cursor-pointer" onClick={async () => {
                try {
                  const { data } = await MessagingAPI.startConversation(m.other_user.user_id)
                  navigate(`/chat/${data.id}`)
                } catch { navigate(`/chat/${m.id}`) }
              }}>
                <img src={m.other_user.photo || `https://i.pravatar.cc/200?u=${m.other_user.user_id}`} className="w-20 h-20 rounded-full object-cover border-2 border-white shadow-md" />
                <span className="text-xs mt-1 font-medium">{m.other_user.display_name}</span>
              </div>
            ))}
          </div>
          {matches.length === 0 && <p className="text-center text-gray-400 mt-20">No matches yet. Keep swiping!</p>}
        </div>
      ) : (
        <div className="divide-y">
          {conversations.map(c => (
            <div key={c.id} className="flex items-center gap-3 p-4 hover:bg-gray-50 cursor-pointer" onClick={() => navigate(`/chat/${c.id}`)}>
              <img src={c.other_user.photo || `https://i.pravatar.cc/100?u=${c.other_user.user_id}`} className="w-12 h-12 rounded-full object-cover" />
              <div className="flex-1 min-w-0">
                <div className="flex justify-between">
                  <span className="font-semibold">{c.other_user.display_name}</span>
                  {c.unread_count > 0 && <span className="bg-[#FF4458] text-white text-xs px-2 py-0.5 rounded-full">{c.unread_count}</span>}
                </div>
                <p className="text-sm text-gray-500 truncate">{c.last_message_text || 'Start a conversation'}</p>
              </div>
            </div>
          ))}
          {conversations.length === 0 && (
            <div className="text-center mt-20 text-gray-400">
              <MessageCircle className="w-12 h-12 mx-auto mb-2" />
              <p>No conversations yet</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
