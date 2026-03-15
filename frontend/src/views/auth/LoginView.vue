<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-center text-gray-800 mb-8">Вход в систему</h1>
      
      <form @submit.prevent="handleLogin">
        <div class="mb-6">
          <label for="token" class="block text-sm font-medium text-gray-700 mb-2">
            Токен доступа
          </label>
          <input
            id="token"
            v-model="token"
            type="text"
            placeholder="Введите ваш токен"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
            required
          />
        </div>

        <div v-if="error" class="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg">
          {{ error }}
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? 'Вход...' : 'Войти' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const token = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!token.value.trim()) {
    error.value = 'Введите токен'
    return
  }

  loading.value = true
  error.value = ''

  const result = await authStore.login(token.value.trim())

  loading.value = false

  if (result.success) {
    router.push(authStore.isMaster ? '/master/tasks' : '/student/tasks')
  } else {
    error.value = result.error
  }
}
</script>
