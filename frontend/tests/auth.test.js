/**
 * Tests pour l'authentification frontend
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useAuthStore } from '../src/stores/auth'
import axios from 'axios'

// Mock axios
vi.mock('axios')

describe('Auth Store', () => {
  let authStore

  beforeEach(() => {
    // Créer une nouvelle instance de Pinia pour chaque test
    setActivePinia(createPinia())
    authStore = useAuthStore()
    
    // Reset des mocks
    vi.clearAllMocks()
  })

  describe('État initial', () => {
    it('devrait avoir un état initial correct', () => {
      expect(authStore.user).toBeNull()
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBeNull()
      // Le token peut être null, undefined (localStorage mocké) ou une valeur du localStorage
      expect(authStore.token === null || authStore.token === undefined || typeof authStore.token === 'string').toBe(true)
    })
  })

  describe('Login', () => {
    it('devrait se connecter avec succès', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com'
      }

      const mockResponse = {
        data: {
          success: true,
          message: 'Authentification réussie',
          user: mockUser
        }
      }

      axios.post.mockResolvedValue(mockResponse)

      await authStore.login({
        login: 'testuser',
        password: 'password123'
      })

      expect(axios.post).toHaveBeenCalledWith('/auth/api/login/', {
        login: 'testuser',
        password: 'password123'
      })
      expect(authStore.user).toEqual(mockUser)
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBeNull()
    })

    it('devrait gérer les erreurs de connexion', async () => {
      const mockError = {
        response: {
          data: {
            success: false,
            message: 'Nom d\'utilisateur ou mot de passe invalide'
          },
          status: 401
        }
      }

      axios.post.mockRejectedValue(mockError)

      await authStore.login({
        login: 'wronguser',
        password: 'wrongpass'
      })

      expect(authStore.user).toBeNull()
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBe('Nom d\'utilisateur ou mot de passe invalide')
    })

    it('devrait gérer les erreurs réseau', async () => {
      const mockError = new Error('Network Error')
      axios.post.mockRejectedValue(mockError)

      await authStore.login({
        login: 'testuser',
        password: 'password123'
      })

      expect(authStore.user).toBeNull()
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBe('Erreur de connexion')
    })
  })

  describe('Register', () => {
    it('devrait s\'inscrire avec succès', async () => {
      const mockUser = {
        id: 1,
        username: 'newuser',
        email: 'new@example.com'
      }

      const mockResponse = {
        data: {
          success: true,
          message: 'Utilisateur créé avec succès',
          user: mockUser,
          email_verification_sent: true
        }
      }

      axios.post.mockResolvedValue(mockResponse)

      await authStore.register({
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      })

      expect(axios.post).toHaveBeenCalledWith('/auth/api/signup/', {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      })
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBeNull()
    })

    it('devrait gérer les erreurs d\'inscription', async () => {
      const mockError = {
        response: {
          data: {
            success: false,
            message: 'Ce nom d\'utilisateur est déjà utilisé'
          },
          status: 400
        }
      }

      axios.post.mockRejectedValue(mockError)

      await authStore.register({
        username: 'existinguser',
        email: 'existing@example.com',
        password: 'password123'
      })

      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBe('Ce nom d\'utilisateur est déjà utilisé')
    })
  })

  describe('Logout', () => {
    it('devrait se déconnecter avec succès', async () => {
      // Simuler un utilisateur connecté
      authStore.user = { id: 1, username: 'testuser' }
      authStore.token = 'mock-token'

      const mockResponse = {
        data: {
          success: true,
          message: 'Déconnexion réussie'
        }
      }

      axios.post.mockResolvedValue(mockResponse)

      await authStore.logout()

      expect(axios.post).toHaveBeenCalledWith('/auth/api/logout/')
      expect(authStore.user).toBeNull()
      expect(authStore.token).toBeNull()
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBeNull()
    })
  })

  describe('Get Profile', () => {
    it('devrait récupérer le profil avec succès', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        is_verified: true
      }

      const mockResponse = {
        data: {
          success: true,
          user: mockUser
        }
      }

      // Simuler un token existant
      authStore.token = 'mock-token'
      axios.get.mockResolvedValue(mockResponse)

      await authStore.getProfile()

      expect(axios.get).toHaveBeenCalledWith('/auth/api/profile/')
      expect(authStore.user).toEqual(mockUser)
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBeNull()
    })

    it('devrait gérer les erreurs de récupération de profil', async () => {
      const mockError = {
        response: {
          data: {
            success: false,
            message: 'Utilisateur non connecté'
          },
          status: 401
        }
      }

      // Simuler un token existant pour que l'appel API soit fait
      authStore.token = 'mock-token'
      axios.get.mockRejectedValue(mockError)

      await authStore.getProfile()

      expect(authStore.user).toBeNull()
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBe('Utilisateur non connecté')
    })

    it('devrait gérer le cas sans token', async () => {
      // S'assurer qu'il n'y a pas de token
      authStore.token = null

      await authStore.getProfile()

      expect(authStore.user).toBeNull()
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBe('Utilisateur non connecté')
      expect(axios.get).not.toHaveBeenCalled()
    })
  })

  describe('Forgot Password', () => {
    it('devrait envoyer l\'email de récupération avec succès', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Email de récupération envoyé'
        }
      }

      axios.post.mockResolvedValue(mockResponse)

      await authStore.forgotPassword('test@example.com')

      expect(axios.post).toHaveBeenCalledWith('/auth/api/forgot-password/', {
        email: 'test@example.com'
      })
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBeNull()
    })

    it('devrait gérer les erreurs d\'envoi d\'email', async () => {
      const mockError = {
        response: {
          data: {
            success: false,
            message: 'Aucun utilisateur trouvé avec cet email'
          },
          status: 404
        }
      }

      axios.post.mockRejectedValue(mockError)

      await authStore.forgotPassword('nonexistent@example.com')

      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBe('Aucun utilisateur trouvé avec cet email')
    })
  })

  describe('Verify Email', () => {
    it('devrait vérifier l\'email avec succès', async () => {
      const mockResponse = {
        data: {
          success: true,
          message: 'Email vérifié avec succès'
        }
      }

      axios.post.mockResolvedValue(mockResponse)

      await authStore.verifyEmail('mock-token')

      expect(axios.post).toHaveBeenCalledWith('/auth/api/verify-email/', {
        token: 'mock-token'
      })
      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBeNull()
    })

    it('devrait gérer les erreurs de vérification', async () => {
      const mockError = {
        response: {
          data: {
            success: false,
            message: 'Token invalide ou expiré'
          },
          status: 400
        }
      }

      axios.post.mockRejectedValue(mockError)

      await authStore.verifyEmail('invalid-token')

      expect(authStore.loading).toBe(false)
      expect(authStore.error).toBe('Token invalide ou expiré')
    })
  })

  describe('Clear Error', () => {
    it('devrait effacer l\'erreur', () => {
      authStore.error = 'Une erreur'
      authStore.clearError()
      expect(authStore.error).toBeNull()
    })
  })
}) 