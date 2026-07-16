import { create } from 'zustand'
import { AuthAPI } from '../api/client'

interface AuthState {
  token: string | null
  userId: number | null
  email: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name?: string) => Promise<void>
  logout: () => void
  init: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  userId: null,
  email: null,
  isAuthenticated: false,
  init: () => {
    const token = localStorage.getItem('access_token')
    const userId = localStorage.getItem('user_id')
    const email = localStorage.getItem('email')
    if (token && userId) {
      set({ token, userId: Number(userId), email, isAuthenticated: true })
    }
  },
  login: async (email, password) => {
    const { data } = await AuthAPI.login(email, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user_id', String(data.user_id))
    localStorage.setItem('email', data.email)
    set({ token: data.access_token, userId: data.user_id, email: data.email, isAuthenticated: true })
  },
  register: async (email, password, name) => {
    const { data } = await AuthAPI.register(email, password, name)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('user_id', String(data.user_id))
    localStorage.setItem('email', data.email)
    set({ token: data.access_token, userId: data.user_id, email: data.email, isAuthenticated: true })
  },
  logout: () => {
    localStorage.clear()
    set({ token: null, userId: null, email: null, isAuthenticated: false })
  },
}))
