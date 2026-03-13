<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'
import { useRouter } from 'vue-router'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const tokenInput = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const router = useRouter()

const handleLogin = async () => {
  try {
    const response = await axios.post(`${API_URL}/login`, {
      token: tokenInput.value
    })

    if (response.data.status === 'success') {
      Cookies.set('user_token', response.data.user, { expires: 1 })
      Cookies.set('user_role', response.data.type, { expires: 1 })

      // Редирект в зависимости от роли
      if (response.data.type === 'admin') {
        router.push('/admin')
      } else if (response.data.type === 'master') {
        router.push('/master/students')
      } else if (response.data.type === 'user') {
        router.push('/client/tasks')
      }
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || 'Ошибка входа'
  }
}
</script>

<template>
  <div class="login-wrapper">
    <form @submit.prevent="handleLogin" class="login-card">
      <h2>Вход</h2>
      
      <input 
        v-model="tokenInput" 
        type="text" 
        placeholder="Введите токен (name#id)"
        :disabled="isLoading"
      />
      
      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Проверка...' : 'Войти' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
/* Стили можно оставить те же, что были раньше */
.login-wrapper { display: flex; justify-content: center; padding-top: 100px; }
.login-card { border: 1px solid #ccc; padding: 20px; border-radius: 8px; width: 300px; }
input { width: 100%; margin-bottom: 10px; padding: 8px; box-sizing: border-box; }
.error-text { color: red; font-size: 0.8rem; }
button { width: 100%; padding: 10px; background: #42b883; color: white; border: none; cursor: pointer; }
button:disabled { background: #ccc; }
</style>