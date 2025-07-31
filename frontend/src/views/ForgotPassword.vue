<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Mot de passe oublié
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Entrez votre email pour recevoir un lien de récupération
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleForgotPassword">
        <div class="card space-y-4">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="input-field mt-1"
              placeholder="jeff@example.com"
            />
          </div>
          
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ error }}
          </div>
          
          <div v-if="success" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            {{ success }}
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
            {{ authStore.loading ? 'Envoi...' : 'Envoyer le lien de récupération' }}
          </button>
          
          <div class="text-center">
            <router-link to="/login" class="text-sm text-primary-600 hover:text-primary-500">
              Retour à la connexion
            </router-link>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const form = ref({
  email: ''
})

const error = ref('')
const success = ref('')

const handleForgotPassword = async () => {
  error.value = ''
  success.value = ''
  
  const result = await authStore.forgotPassword(form.value.email)
  
  if (result.success) {
    success.value = 'Email de récupération envoyé ! Vérifiez votre boîte de réception.'
  } else {
    error.value = result.message
  }
}
</script> 