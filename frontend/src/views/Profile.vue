<template>
  <div class="py-12">
    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="card">
        <div class="flex items-center justify-between mb-6">
          <h1 class="text-2xl font-bold text-gray-900">Profil utilisateur</h1>
          <router-link to="/" class="btn-secondary">
            Retour à l'accueil
          </router-link>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700">Nom d'utilisateur</label>
            <p class="mt-1 text-lg text-gray-900">{{ authStore.user?.username }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <p class="mt-1 text-lg text-gray-900">{{ authStore.user?.email }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">ID utilisateur</label>
            <p class="mt-1 text-lg text-gray-900">{{ authStore.user?.id }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Statut email</label>
            <p class="mt-1 text-lg">
              <span v-if="authStore.user?.is_verified" class="text-green-600 font-medium">
                Email vérifié
              </span>
              <span v-else class="text-red-600 font-medium">
                Email non vérifié
              </span>
            </p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Date de création</label>
            <p class="mt-1 text-lg text-gray-900">
              {{ formatDate(authStore.user?.created_at) }}
            </p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">Sécurité</label>
            <p class="mt-1 text-lg text-green-600 font-medium">
              Hachage Argon2
            </p>
          </div>
        </div>
        
        <div class="mt-8 pt-6 border-t border-gray-200">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Actions</h3>
          <div class="flex space-x-4">
            <button @click="logout" class="btn-secondary">
              Se déconnecter
            </button>
            <router-link to="/forgot-password" class="btn-primary">
              Changer le mot de passe
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const formatDate = (dateString) => {
  if (!dateString) return 'Non disponible'
  return new Date(dateString).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script> 