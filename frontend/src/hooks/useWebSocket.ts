import { useEffect, useRef, useState, useCallback } from 'react'

interface WSMessage {
  type: string
  [key: string]: any
}

export function useWebSocket(token: string | null, onMessage?: (msg: WSMessage) => void) {
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null)

  const connect = useCallback(() => {
    if (!token) return
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_API_URL ? new URL(import.meta.env.VITE_API_URL).host : 'localhost:8000'
    const url = `${proto}//${host}/api/v1/messaging/ws?token=${token}`

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => setIsConnected(true)
    ws.onclose = () => {
      setIsConnected(false)
      // reconnect after 3s
      setTimeout(connect, 3000)
    }
    ws.onerror = () => setIsConnected(false)
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data)
        setLastMessage(data)
        onMessage?.(data)
      } catch {}
    }
  }, [token, onMessage])

  useEffect(() => {
    connect()
    return () => wsRef.current?.close()
  }, [connect])

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  return { isConnected, lastMessage, send, ws: wsRef.current }
}
