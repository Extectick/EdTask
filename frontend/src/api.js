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

// ============================================
// Auth API
// ============================================
export const authApi = {
  login(token) {
    return api.post('/auth/login', { token })
  },
}

// ============================================
// File/Image API
// ============================================
export const fileApi = {
  uploadImage(formData) {
    return apiFormData.post('/file/image', formData)
  },
  deleteImage(imageName) {
    return api.delete('/file/image', { data: { image_name: imageName } })
  },
  uploadFile(formData) {
    return apiFormData.post('/file/file', formData)
  },
  deleteFile(fileName) {
    return api.delete('/file/file', { data: { file_name: fileName } })
  },
}

// ============================================
// Master/User API
// ============================================
export const masterUserApi = {
  createUser(userId, fullName, masterToken) {
    return api.post('/master/user/create', {
      user_id: userId,
      full_name: fullName,
      master_token: masterToken,
    })
  },
  deleteUser(userId, masterToken) {
    return api.post('/master/user/delete', {
      user_id: userId,
      master_token: masterToken,
    })
  },
  getStudents(masterToken) {
    return api.get('/master/students', {
      params: { master_token: masterToken },
    })
  },
}

// ============================================
// Master/Task API
// ============================================
export const masterTaskApi = {
  getTasks(params) {
    return api.get('/master/task', { params })
  },
  createTask(title, description, masterToken, userId, imageIds = [], fileIds = []) {
    const data = {
      title,
      description,
      master_token: masterToken,
      user_id: userId,
    }
    // Добавляем image_ids только если массив не пустой
    if (imageIds && imageIds.length > 0) {
      data.image_ids = imageIds
    }
    // Добавляем file_ids только если массив не пустой
    if (fileIds && fileIds.length > 0) {
      data.file_ids = fileIds
    }
    return api.post('/master/task/create', data)
  },
  updateTask(taskId, title, description, masterToken) {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('title', title)
    formData.append('description', description)
    formData.append('master_token', masterToken)
    return api.post('/master/task/update', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteTask(taskId, masterToken) {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('master_token', masterToken)
    return api.post('/master/task/delete', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}

// ============================================
// User/Task API (для учеников)
// ============================================
export const userTaskApi = {
  getTasks(userToken, taskId = null) {
    const params = { user_token: userToken }
    if (taskId) params.task_id = taskId
    return api.get('/user/task', { params })
  },
}

// ============================================
// User/Answer API
// ============================================
export const answerApi = {
  getAnswers(params) {
    return api.get('/user/answer', { params })
  },
  createAnswer(taskId, content, imageId = null) {
    return api.post('/user/answer', {
      task_id: taskId,
      content,
      image_id: imageId,
    })
  },
  updateAnswer(answerId, updates, masterToken) {
    return api.patch('/user/answer', {
      answer_id: answerId,
      ...updates,
      master_token: masterToken,
    })
  },
  deleteAnswer(answerId, masterToken) {
    return api.delete('/user/answer', {
      data: {
        answer_id: answerId,
        master_token: masterToken,
      },
    })
  },
}

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
