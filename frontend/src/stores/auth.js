import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Configuration axios
  axios.defaults.baseURL = 'http://localhost:8000'
  axios.defaults.withCredentials = true

  // Intercepteur pour ajouter le token
  axios.interceptors.request.use(config => {
    if (token.value) {
      config.headers.Authorization = `Bearer ${token.value}`
    }
    return config
  })

  const login = async (credentials) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/auth/api/login/', credentials)
      
      if (response.data.success) {
        user.value = response.data.user
        token.value = response.data.token || 'session-token'
        localStorage.setItem('token', token.value)
        return { success: true }
      } else {
        error.value = response.data.message
        return { success: false, message: response.data.message }
      }
    } catch (err) {
      error.value = err.response?.data?.message || 'Erreur de connexion'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }

  const register = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/auth/api/signup/', userData)
      
      if (response.data.success) {
        user.value = response.data.user
        token.value = response.data.token || 'session-token'
        localStorage.setItem('token', token.value)
        return { success: true }
      } else {
        error.value = response.data.message
        return { success: false, message: response.data.message }
      }
    } catch (err) {
      error.value = err.response?.data?.message || 'Erreur d\'inscription'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await axios.post('/auth/api/logout/')
    } catch (err) {
      console.error('Erreur lors de la déconnexion:', err)
    } finally {
      user.value = null
      token.value = null
      localStorage.removeItem('token')
    }
  }

  const getProfile = async () => {
    loading.value = true
    error.value = null
    
    if (!token.value) {
      error.value = 'Utilisateur non connecté'
      loading.value = false
      return
    }
    
    try {
      const response = await axios.get('/auth/api/profile/')
      if (response.data.success) {
        user.value = response.data.user
      }
    } catch (err) {
      error.value = err.response?.data?.message || 'Erreur lors de la récupération du profil'
      user.value = null
      logout()
    } finally {
      loading.value = false
    }
  }

  const forgotPassword = async (email) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/auth/api/forgot-password/', { email })
      return { success: response.data.success, message: response.data.message }
    } catch (err) {
      error.value = err.response?.data?.message || 'Erreur lors de la récupération'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }

  const verifyEmail = async (token) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await axios.post('/auth/api/verify-email/', { token })
      return { success: response.data.success, message: response.data.message }
    } catch (err) {
      error.value = err.response?.data?.message || 'Erreur lors de la vérification'
      return { success: false, message: error.value }
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  // Initialiser l'utilisateur au démarrage
  if (token.value) {
    getProfile()
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    getProfile,
    forgotPassword,
    verifyEmail,
    clearError
  }
}) 