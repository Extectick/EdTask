import { defineStore } from 'pinia'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('user_token') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    isMaster: (state) => state.user?.type === 'master',
    isStudent: (state) => state.user?.type === 'student',
  },

  actions: {
    async login(token) {
      try {
        const response = await authApi.login(token)
        this.user = response.data.user
        this.token = token
        
        // Сохраняем в localStorage
        localStorage.setItem('user_token', token)
        localStorage.setItem('user_data', JSON.stringify(this.user))
        
        return { success: true }
      } catch (error) {
        console.error('Login failed:', error)
        return {
          success: false,
          error: error.response?.data?.detail || 'Ошибка входа',
        }
      }
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('user_token')
      localStorage.removeItem('user_data')
    },

    // Загрузка данных из localStorage при инициализации
    initAuth() {
      const savedUser = localStorage.getItem('user_data')
      if (this.token && savedUser) {
        try {
          this.user = JSON.parse(savedUser)
        } catch (e) {
          this.logout()
        }
      }
    },
  },
})
