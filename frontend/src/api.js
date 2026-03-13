import axios from 'axios'

// Базовый URL из переменных окружения
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Создаём настроенный axios инстанс
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Для multipart/form-data (загрузка файлов) заголовок установится автоматически
export const apiFormData = axios.create({
  baseURL: API_BASE_URL,
})

export default api
