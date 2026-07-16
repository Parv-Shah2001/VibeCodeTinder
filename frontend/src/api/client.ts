import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      const refresh = localStorage.getItem('refresh_token')
      if (refresh && error.config && !error.config._retry) {
        error.config._retry = true
        try {
          const { data } = await axios.post(`${API_BASE}/auth/refresh`, { refresh_token: refresh })
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          error.config.headers.Authorization = `Bearer ${data.access_token}`
          return api(error.config)
        } catch {
          localStorage.clear()
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export const AuthAPI = {
  register: (email: string, password: string, name?: string) => api.post('/auth/register', { email, password, name }),
  login: (email: string, password: string) => api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
}

export const ProfileAPI = {
  getMyProfile: () => api.get('/users/me/profile'),
  createProfile: (data: any) => api.post('/users/me/profile', data),
  updateProfile: (data: any) => api.patch('/users/me/profile', data),
  updatePrefs: (data: any) => api.patch('/users/me/preferences', data),
}

export const MediaAPI = {
  list: () => api.get('/media/me'),
  upload: (file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return api.post('/media/me/upload', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
  },
  delete: (id: number) => api.delete(`/media/me/${id}`),
  setPrimary: (id: number) => api.post(`/media/me/${id}/primary`),
}

export const DiscoveryAPI = {
  feed: (limit = 20, params?: any) => api.get('/discovery/feed', { params: { limit, ...params } }),
  boost: () => api.get('/discovery/boost'),
}

export const SwipeAPI = {
  swipe: (swiped_id: number, swipe_type: 'like' | 'dislike' | 'superlike') => api.post('/swipes', { swiped_id, swipe_type }),
  history: () => api.get('/swipes/history'),
}

export const MatchAPI = {
  list: () => api.get('/matches'),
  unmatch: (id: number) => api.delete(`/matches/${id}`),
}

export const MessagingAPI = {
  conversations: () => api.get('/messaging/conversations'),
  startConversation: (otherUserId: number) => api.post(`/messaging/conversations/with/${otherUserId}`),
  messages: (convId: number, limit = 50, beforeId?: number) => api.get(`/messaging/conversations/${convId}/messages`, { params: { limit, before_id: beforeId } }),
  send: (convId: number, content: string, media_asset_id?: number) => api.post(`/messaging/conversations/${convId}/messages`, { content, media_asset_id, message_type: content ? 'text' : 'image' }),
  typing: (convId: number, isTyping: boolean) => api.post(`/messaging/conversations/${convId}/typing?is_typing=${isTyping}`),
}
