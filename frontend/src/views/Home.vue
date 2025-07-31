<template>
  <div class="py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">
          Bienvenue sur NAIRA
        </h1>
        <p class="text-xl text-gray-600 mb-8">
          Votre système d'authentification sécurisé avec Argon2
        </p>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
        <div class="card">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">Profil</h3>
              <p class="text-gray-600">Gérez vos informations personnelles</p>
            </div>
          </div>
          <div class="mt-4">
            <router-link to="/profile" class="btn-primary">
              Voir le profil
            </router-link>
          </div>
        </div>
        
        <div class="card">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">Sécurité</h3>
              <p class="text-gray-600">Hachage Argon2 pour vos mots de passe</p>
            </div>
          </div>
          <div class="mt-4">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
              Sécurisé
            </span>
          </div>
        </div>
        
        <div class="card">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <div class="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
            </div>
            <div class="ml-4">
              <h3 class="text-lg font-medium text-gray-900">Performance</h3>
              <p class="text-gray-600">API REST rapide et moderne</p>
            </div>
          </div>
          <div class="mt-4">
            <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
              Rapide
            </span>
          </div>
        </div>
      </div>
      
      <div class="mt-12 card">
        <h2 class="text-2xl font-bold text-gray-900 mb-4">Informations utilisateur</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">Nom d'utilisateur</label>
            <p class="mt-1 text-sm text-gray-900">{{ authStore.user?.username }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Email</label>
            <p class="mt-1 text-sm text-gray-900">{{ authStore.user?.email }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">ID utilisateur</label>
            <p class="mt-1 text-sm text-gray-900">{{ authStore.user?.id }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700">Email vérifié</label>
            <p class="mt-1 text-sm text-gray-900">
                              <span v-if="authStore.user?.is_verified" class="text-green-600">Vérifié</span>
                <span v-else class="text-red-600">Non vérifié</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
</script> 