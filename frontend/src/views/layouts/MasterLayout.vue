<template>
  <div class="h-screen flex bg-gray-100 overflow-hidden">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-800 text-white flex flex-col">
      <div class="p-6">
        <h1 class="text-2xl font-bold">Кабинет мастера</h1>
        <p v-if="authStore.user" class="text-sm text-gray-400 mt-1">
          {{ authStore.user.full_name }}
        </p>
      </div>

      <nav class="mt-6 flex-1">
        <router-link
          to="/master/tasks"
          class="flex items-center px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition"
          active-class="bg-gray-700 text-white"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
          </svg>
          Задачи
        </router-link>

        <router-link
          to="/master/students"
          class="flex items-center px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition"
          active-class="bg-gray-700 text-white"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/>
          </svg>
          Ученики
        </router-link>

        <router-link
          to="/master/tasks/new"
          class="flex items-center px-6 py-3 text-gray-300 hover:bg-gray-700 hover:text-white transition"
          active-class="bg-gray-700 text-white"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Создать задачу
        </router-link>
      </nav>

      <div class="p-6 border-t border-gray-700">
        <button
          @click="handleLogout"
          class="flex items-center text-gray-300 hover:text-white transition"
        >
          <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
          </svg>
          Выход
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <main class="flex-1 p-8 overflow-auto">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
