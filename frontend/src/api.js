import axios from 'axios'

/**
 * Автоматическое определение URL бэкенда
 * - Development (localhost): http://localhost:8000
 * - Production: тот же домен, но порт 8000
 */
const getBackendUrl = () => {
  // Если явно задано в .env — используем его
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL
  }

  // Development режим
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000'
  }

  // Production — тот же домен, порт 8000
  const protocol = window.location.protocol
  const hostname = window.location.hostname
  return `${protocol}//${hostname}:8000`
}

const API_BASE_URL = getBackendUrl()

console.log('[API] Backend URL:', API_BASE_URL)

// Основной axios инстанс для JSON запросов
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 секунд
})

// Инстанс для multipart/form-data (загрузка файлов)
export const apiFormData = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data',
  },
  timeout: 60000, // 60 секунд для файлов
})

// Обработчик ошибок (опционально)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
      console.error('[API] Бэкенд недоступен:', API_BASE_URL)
    }
    return Promise.reject(error)
  }
)

export default api
