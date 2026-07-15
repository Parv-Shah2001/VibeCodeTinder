export interface User {
  id: number
  email: string
}

export interface Photo {
  id: number
  url: string
  thumbnail_url?: string
  is_primary: boolean
  order?: number
}

export interface Profile {
  id: number
  user_id: number
  display_name: string
  bio?: string
  age?: number
  gender?: string
  city?: string
  distance_km?: number
  job_title?: string
  school?: string
  elo_score: number
  photos: Photo[]
  is_verified: boolean
  is_boosted?: boolean
  score?: number
}

export interface Match {
  id: number
  user1_id: number
  user2_id: number
  other_user: {
    user_id: number
    display_name: string
    photo?: string
    age?: number
  }
  created_at: string
  last_message_at?: string
  last_message?: {
    content: string
    created_at: string
    sender_id: number
  }
}

export interface Message {
  id: number
  conversation_id: number
  sender_id: number
  content?: string
  media_url?: string
  media_asset_id?: number
  message_type: string
  is_read: boolean
  created_at: string
}

export interface Conversation {
  id: number
  user1_id: number
  user2_id: number
  other_user: {
    user_id: number
    display_name: string
    photo?: string
  }
  last_message_at?: string
  last_message_text?: string
  unread_count: number
  created_at: string
}
