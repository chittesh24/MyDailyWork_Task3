import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import Cookies from 'js-cookie'

interface AuthState {
  isAuthenticated: boolean
  user: { email: string } | null
  token: string | null
  apiKey: string | null
  login: (token: string, email: string) => void
  logout: () => void
  setApiKey: (apiKey: string) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      isAuthenticated: false,
      user: null,
      token: null,
      apiKey: null,
      
      login: (token: string, email: string) => {
        // Store token in HTTP-only cookie (in production)
        Cookies.set('auth_token', token, { 
          expires: 7,
          sameSite: 'strict',
          secure: process.env.NODE_ENV === 'production'
        })
        
        set({ 
          isAuthenticated: true, 
          user: { email },
          token 
        })
      },
      
      logout: () => {
        Cookies.remove('auth_token')
        set({ 
          isAuthenticated: false, 
          user: null, 
          token: null,
          apiKey: null
        })
      },
      
      setApiKey: (apiKey: string) => {
        set({ apiKey })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
