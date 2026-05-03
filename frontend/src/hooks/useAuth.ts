import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import apiClient from '@/services/api'

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  current_degree: string
  current_cgpa: number
  work_experience_years: number
  annual_income: number
  preferred_countries: string[]
  preferred_fields: string[]
  engagement_segment?: string
  engagement_score?: number
}

interface AuthState {
  user: User | null
  isLoading: boolean
  error: string | null
  isAuthenticated: boolean

  // Actions
  signup: (data: any) => Promise<void>
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  fetchProfile: () => Promise<void>
  updateProfile: (data: any) => Promise<void>
  clearError: () => void
}

export const useAuth = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isLoading: false,
      error: null,
      isAuthenticated: false,

      signup: async (data) => {
        try {
          set({ isLoading: true, error: null })
          const response = await apiClient.signup(data)
          localStorage.setItem('refresh_token', response.refresh_token)
          
          // Fetch profile after signup
          await get().fetchProfile()
          set({ isAuthenticated: true })
        } catch (error: any) {
          set({ error: error.message || 'Signup failed' })
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      login: async (email, password) => {
        try {
          set({ isLoading: true, error: null })
          const response = await apiClient.login(email, password)
          localStorage.setItem('refresh_token', response.refresh_token)
          
          // Fetch profile after login
          await get().fetchProfile()
          set({ isAuthenticated: true })
        } catch (error: any) {
          set({ error: error.message || 'Login failed' })
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      logout: async () => {
        try {
          await apiClient.logout()
          set({ user: null, isAuthenticated: false })
          localStorage.removeItem('refresh_token')
        } catch (error: any) {
          console.error('Logout error:', error)
        }
      },

      fetchProfile: async () => {
        try {
          const profile = await apiClient.getProfile()
          set({ user: profile, isAuthenticated: true })
        } catch (error: any) {
          set({ error: error.message || 'Failed to fetch profile' })
        }
      },

      updateProfile: async (data) => {
        try {
          set({ isLoading: true, error: null })
          const updated = await apiClient.updateProfile(data)
          set({ user: updated })
        } catch (error: any) {
          set({ error: error.message || 'Update failed' })
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
