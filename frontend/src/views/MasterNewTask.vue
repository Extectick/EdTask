<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'
import { useRouter } from 'vue-router'
import MasterNav from '../components/MasterNav.vue'

const router = useRouter()
const masterToken = Cookies.get('user_token')

const title = ref('')
const description = ref('')
const images = ref([])
const previewImages = ref([])
const isSubmitting = ref(false)

// Обработка выбора файлов
const handleFileChange = (event) => {
  const files = event.target.files
  images.value = Array.from(files)
  
  // Создаём превью
  previewImages.value = []
  Array.from(files).forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      previewImages.value.push(e.target.result)
    }
    reader.readAsDataURL(file)
  })
}

// Создание задачи
const createTask = async () => {
  if (!title.value.trim()) {
    alert('Введите заголовок задачи!')
    return
  }
  
  try {
    isSubmitting.value = true
    
    // 1. Создаём задачу
    const createResponse = await axios.post('http://127.0.0.1:8000/master/task/create', {
      title: title.value,
      description: description.value,
      master_token: masterToken
    })
    
    const taskId = createResponse.data.task_id
    
    // 2. Загружаем изображения (если есть)
    if (images.value.length > 0) {
      for (const image of images.value) {
        const formData = new FormData()
        formData.append('task_id', taskId)
        formData.append('master_token', masterToken)
        formData.append('image', image)
        
        await axios.post('http://127.0.0.1:8000/master/task/upload_image', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      }
    }
    
    alert('Задача успешно создана!')
    router.push('/master/tasks')
  } catch (e) {
    console.error(e)
    alert(e.response?.data?.detail || 'Ошибка при создании задачи')
  } finally {
    isSubmitting.value = false
  }
}

// Отмена
const cancel = () => {
  router.push('/master/tasks')
}
</script>

<template>
  <div class="new-task-page">
    <MasterNav />

    <div class="page-content">
      <div class="header-left">
        <button @click="cancel" class="btn-back">← Назад</button>
        <h1>Новая задача</h1>
      </div>

      <div class="form-card">
      <div class="form-group">
        <label for="title">Заголовок *</label>
        <input
          id="title"
          v-model="title"
          type="text"
          placeholder="Например: Домашнее задание №1"
          :disabled="isSubmitting"
        />
      </div>

      <div class="form-group">
        <label for="description">Описание</label>
        <textarea
          id="description"
          v-model="description"
          placeholder="Опишите задание подробно..."
          rows="6"
          :disabled="isSubmitting"
        ></textarea>
      </div>

      <div class="form-group">
        <label for="images">Изображения</label>
        <input
          id="images"
          type="file"
          accept="image/*"
          multiple
          @change="handleFileChange"
          :disabled="isSubmitting"
        />
        <p class="hint">Можно выбрать несколько файлов</p>
      </div>

      <div v-if="previewImages.length > 0" class="preview-section">
        <h4>Предпросмотр:</h4>
        <div class="preview-grid">
          <div v-for="(img, idx) in previewImages" :key="idx" class="preview-item">
            <img :src="img" :alt="`Preview ${idx}`" />
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button @click="cancel" class="btn-cancel" :disabled="isSubmitting">
          Отмена
        </button>
        <button @click="createTask" class="btn-submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Создание...' : 'Создать задачу' }}
        </button>
      </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.new-task-page {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.page-content {
  padding: 30px;
  max-width: 800px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.header-left h1 {
  margin: 0;
  color: #333;
}

.btn-back {
  background: #e0e0e0;
  color: #333;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-back:hover {
  background: #d0d0d0;
}

.form-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.form-group input[type="text"],
.form-group textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  box-sizing: border-box;
}

.form-group input[type="text"]:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 3px rgba(66, 184, 131, 0.1);
}

.form-group input[type="file"] {
  padding: 10px 0;
}

.hint {
  color: #888;
  font-size: 0.85rem;
  margin-top: 5px;
}

.preview-section {
  margin-bottom: 25px;
}

.preview-section h4 {
  margin-bottom: 15px;
  color: #555;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
}

.preview-item img {
  width: 100%;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  border: 2px solid #e0e0e0;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
}

.form-actions button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
  transition: opacity 0.2s;
}

.btn-cancel {
  background: #e0e0e0;
  color: #333;
}

.btn-submit {
  background: #42b883;
  color: white;
}

.btn-submit:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.form-actions button:hover:not(:disabled) {
  opacity: 0.9;
}
</style>
