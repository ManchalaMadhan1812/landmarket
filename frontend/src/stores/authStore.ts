import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  phone?: string
  role: 'buyer' | 'vendor' | 'broker' | 'admin' | 'super_admin'
  isVerified: boolean
  avatar?: string
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isInitialized: boolean
  
  // Actions
  login: (token: string, refreshToken: string, user: User) => void
  logout: () => void
  updateUser: (user: Partial<User>) => void
  initialize: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isInitialized: false,

      login: (token: string, refreshToken: string, user: User) => {
        set({
          token,
          refreshToken,
          user,
          isAuthenticated: true,
          isInitialized: true,
        })
      },

      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },

      updateUser: (userData: Partial<User>) => {
        const currentUser = get().user
        if (currentUser) {
          set({
            user: { ...currentUser, ...userData }
          })
        }
      },

      initialize: () => {
        const state = get()
        set({
          isInitialized: true,
          isAuthenticated: !!(state.token && state.user)
        })
      },
    }),
    {
      name: 'landmarket-auth',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
      }),
    }
  )
)