import { useEffect, useState, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { MessagingAPI } from '../api/client'
import { Message } from '../types'
import { Send, ArrowLeft, Image as ImageIcon } from 'lucide-react'

export default function Chat() {
  const { id } = useParams()
  const convId = Number(id)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [ws, setWs] = useState<WebSocket | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const currentUserId = Number(localStorage.getItem('user_id'))

  const loadMessages = async () => {
    try {
      const { data } = await MessagingAPI.messages(convId, 100)
      setMessages(data)
    } catch (e) { console.error(e) }
  }

  useEffect(() => {
    loadMessages()
    // Setup WS
    const token = localStorage.getItem('access_token')
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_API_URL ? new URL(import.meta.env.VITE_API_URL).host : 'localhost:8000'
    const apiHost = host
    const wsUrl = `${proto}//${apiHost}/api/v1/messaging/ws?token=${token}`
    try {
      const socket = new WebSocket(wsUrl)
      socket.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data)
          if (msg.type === 'new_message' && msg.conversation_id === convId) {
            setMessages(prev => [...prev, {
              id: msg.message.id,
              conversation_id: msg.conversation_id,
              sender_id: msg.message.sender_id,
              content: msg.message.content,
              message_type: msg.message.message_type,
              is_read: false,
              created_at: msg.message.created_at,
            }])
          }
        } catch {}
      }
      setWs(socket)
      return () => socket.close()
    } catch {}
  }, [convId])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async () => {
    if (!input.trim()) return
    try {
      const { data } = await MessagingAPI.send(convId, input)
      setMessages(prev => [...prev, {
        id: data.id,
        conversation_id: data.conversation_id,
        sender_id: data.sender_id,
        content: data.content,
        message_type: data.message_type,
        is_read: false,
        created_at: data.created_at,
      }])
      setInput('')
    } catch (e) { console.error(e) }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-56px)] max-w-md mx-auto w-full bg-white">
      <div className="flex items-center gap-3 p-3 border-b">
        <Link to="/matches" className="p-2"><ArrowLeft className="w-5 h-5" /></Link>
        <span className="font-semibold">Chat</span>
      </div>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
        {messages.map(m => {
          const isMe = m.sender_id === currentUserId
          return (
            <div key={m.id} className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[75%] rounded-2xl px-4 py-2 text-sm ${isMe ? 'bg-gradient-to-r from-[#FF4458] to-[#FD267D] text-white rounded-br-sm' : 'bg-white border shadow-sm rounded-bl-sm'}`}>
                {m.media_url && <img src={m.media_url} className="rounded-lg mb-1 max-w-full" />}
                {m.content && <p>{m.content}</p>}
                <span className={`text-[10px] mt-1 block ${isMe ? 'text-white/70' : 'text-gray-400'}`}>{new Date(m.created_at).toLocaleTimeString()}</span>
              </div>
            </div>
          )
        })}
        <div ref={bottomRef} />
      </div>
      <div className="p-3 border-t flex items-center gap-2 bg-white">
        <button className="p-2 text-gray-400"><ImageIcon className="w-5 h-5" /></button>
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && send()} placeholder="Type a message" className="flex-1 px-4 py-2.5 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-[#FF4458] text-sm" />
        <button onClick={send} className="w-10 h-10 rounded-full bg-gradient-to-r from-[#FF4458] to-[#FD267D] text-white flex items-center justify-center shadow-md">
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
