<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Connexion à votre compte
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Ou
          <router-link to="/register" class="font-medium text-primary-600 hover:text-primary-500">
            créez un nouveau compte
          </router-link>
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="card space-y-4">
          <div>
            <label for="login" class="block text-sm font-medium text-gray-700">
              Nom d'utilisateur ou Email
            </label>
            <input
              id="login"
              v-model="form.login"
              type="text"
              required
              class="input-field mt-1"
              placeholder="jeff ou jeff@example.com"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              Mot de passe
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="input-field mt-1"
              placeholder="Votre mot de passe"
            />
          </div>
          
          <div class="flex items-center justify-between">
            <div class="text-sm">
              <router-link to="/forgot-password" class="font-medium text-primary-600 hover:text-primary-500">
                Mot de passe oublié ?
              </router-link>
            </div>
          </div>
          
          <div v-if="authStore.error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ authStore.error }}
          </div>
          
          <button
            type="submit"
            :disabled="authStore.loading"
            class="btn-primary w-full flex justify-center"
          >
            <span v-if="authStore.loading" class="mr-2">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ authStore.loading ? 'Connexion...' : 'Se connecter' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  login: '',
  password: ''
})

const handleLogin = async () => {
  const result = await authStore.login(form.value)
  
  if (result.success) {
    router.push('/')
  }
}
</script> 