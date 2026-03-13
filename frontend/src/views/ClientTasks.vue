<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'
import MasterNav from '../components/MasterNav.vue'

const userToken = Cookies.get('user_token')
const tasks = ref([])
const isLoading = ref(false)
const submittingAnswer = ref(null)
const answerText = ref('')
const uploadImageAnswerId = ref(null)
const uploadImageFile = ref(null)

// Получить все доступные задачи
const fetchTasks = async () => {
  try {
    isLoading.value = true
    const res = await axios.post('http://127.0.0.1:8000/master/task/client/get_tasks', {
      user_id: userToken
    })
    tasks.value = res.data.tasks
  } catch (e) {
    console.error("Ошибка загрузки задач", e)
    alert(e.response?.data?.detail || 'Ошибка при загрузке задач')
  } finally {
    isLoading.value = false
  }
}

// Отправить ответ
const submitAnswer = async (taskId) => {
  if (!answerText.value.trim()) {
    alert('Введите текст ответа')
    return
  }
  
  try {
    submittingAnswer.value = taskId
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('user_id', userToken)
    formData.append('text', answerText.value)
    
    const res = await axios.post('http://127.0.0.1:8000/master/task/client/submit_answer', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    answerText.value = ''
    
    // Если есть изображение для загрузки
    if (uploadImageFile.value) {
      const imgFormData = new FormData()
      imgFormData.append('task_id', taskId)
      imgFormData.append('answer_id', res.data.answer_id)
      imgFormData.append('user_id', userToken)
      imgFormData.append('image', uploadImageFile.value)
      
      await axios.post('http://127.0.0.1:8000/master/task/client/upload_answer_image', imgFormData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    
    uploadImageFile.value = null
    uploadImageAnswerId.value = null
    fetchTasks()
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка при отправке ответа')
  } finally {
    submittingAnswer.value = null
  }
}

// Открыть форму отправки ответа
const openAnswerForm = (taskId) => {
  submittingAnswer.value = taskId
  answerText.value = ''
  uploadImageFile.value = null
}

// Закрыть форму ответа
const closeAnswerForm = () => {
  submittingAnswer.value = null
  answerText.value = ''
  uploadImageFile.value = null
}

// Выбрать файл для загрузки
const handleFileChange = (event) => {
  uploadImageFile.value = event.target.files[0]
}

onMounted(() => {
  fetchTasks()
})
</script>

<template>
  <div class="client-tasks-page">
    <MasterNav />
    
    <div class="page-content">
      <div class="content-header">
        <h1>Мои задачи</h1>
      </div>

      <div v-if="isLoading" class="loading">Загрузка...</div>

      <div v-else-if="tasks.length === 0" class="empty-state">
        <p>Нет доступных задач</p>
        <p class="hint">Обратитесь к учителю для предоставления доступа</p>
      </div>

      <div v-else class="tasks-list">
        <div v-for="task in tasks" :key="task.id" class="task-card">
          <div class="task-header">
            <h3>{{ task.title }}</h3>
          </div>

          <div v-if="task.images.length > 0" class="task-main-image">
            <img
              :src="`http://127.0.0.1:8000/data/img/${task.images[0].image_name}`"
              :alt="task.images[0].image_name"
              class="main-image"
            />
          </div>

          <p class="task-description">{{ task.description }}</p>

          <div v-if="task.images.length > 1" class="task-images">
            <img
              v-for="img in task.images.slice(1)"
              :key="img.id"
              :src="`http://127.0.0.1:8000/data/img/${img.image_name}`"
              :alt="img.image_name"
              class="task-image-thumb"
            />
          </div>

          <div class="task-stats">
            <span class="answers-count">
              📅 {{ new Date(task.created_at).toLocaleDateString('ru-RU') }}
            </span>
            <span class="my-answers-count">
              💬 Мои ответы: {{ task.my_answers?.length || 0 }}
            </span>
          </div>

          <!-- Мои ответы -->
          <div v-if="task.my_answers && task.my_answers.length > 0" class="my-answers">
            <h4>Мои ответы:</h4>
            <div v-for="answer in task.my_answers" :key="answer.id" class="answer-item">
              <p class="answer-text">{{ answer.text }}</p>
              <div v-if="answer.images && answer.images.length > 0" class="answer-images">
                <img
                  v-for="img in answer.images"
                  :key="img.id"
                  :src="`http://127.0.0.1:8000/data/img/${img.image_name}`"
                  :alt="img.image_name"
                  class="answer-image-thumb"
                />
              </div>
              <span class="answer-date">{{ new Date(answer.created_at).toLocaleString('ru-RU') }}</span>
            </div>
          </div>

          <!-- Форма отправки ответа -->
          <div v-if="submittingAnswer === task.id" class="answer-form">
            <h4>Ваш ответ:</h4>
            <textarea
              v-model="answerText"
              placeholder="Введите текст ответа..."
              rows="4"
            ></textarea>
            
            <div class="file-upload">
              <label for="file-upload">📎 Прикрепить изображение (необязательно)</label>
              <input
                id="file-upload"
                type="file"
                accept="image/*"
                capture="environment"
                @change="handleFileChange"
              />
              <span v-if="uploadImageFile" class="file-name">{{ uploadImageFile.name }}</span>
            </div>

            <div class="form-actions">
              <button @click="submitAnswer(task.id)" class="btn-submit">
                {{ uploadImageFile ? 'Отправить с фото' : 'Отправить' }}
              </button>
              <button @click="closeAnswerForm" class="btn-cancel">Отмена</button>
            </div>
          </div>

          <button v-else @click="openAnswerForm(task.id)" class="btn-answer">
            ✍️ Дать ответ
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.client-tasks-page {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.page-content {
  padding: 30px;
  max-width: 1000px;
  margin: 0 auto;
}

.content-header {
  margin-bottom: 30px;
}

.content-header h1 {
  margin: 0;
  color: #333;
}

.loading, .empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  color: #666;
}

.empty-state .hint {
  color: #999;
  font-size: 0.9rem;
  margin-top: 10px;
}

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.task-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.task-header {
  margin-bottom: 20px;
}

.task-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
}

.task-main-image {
  width: 100%;
  margin-bottom: 20px;
}

.main-image {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 8px;
}

.task-description {
  color: #555;
  margin-bottom: 20px;
  line-height: 1.6;
  font-size: 1rem;
}

.task-images {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.task-image-thumb {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  border: 2px solid #e0e0e0;
}

.task-stats {
  display: flex;
  gap: 20px;
  color: #888;
  font-size: 0.9rem;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

/* Мои ответы */
.my-answers {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.my-answers h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1rem;
}

.answer-item {
  padding: 12px;
  background: white;
  border-radius: 6px;
  margin-bottom: 10px;
}

.answer-item:last-child {
  margin-bottom: 0;
}

.answer-text {
  margin: 0 0 10px 0;
  color: #333;
  line-height: 1.5;
}

.answer-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}

.answer-image-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.answer-date {
  font-size: 0.85rem;
  color: #999;
}

/* Форма ответа */
.answer-form {
  margin-top: 20px;
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.answer-form h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.answer-form textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.file-upload {
  margin-top: 15px;
}

.file-upload label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-size: 0.9rem;
}

.file-upload input[type="file"] {
  display: block;
  margin-bottom: 5px;
}

.file-name {
  font-size: 0.85rem;
  color: #666;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.btn-submit {
  background: #42b883;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-submit:hover {
  background: #3aa876;
}

.btn-cancel {
  background: #e0e0e0;
  color: #333;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-cancel:hover {
  background: #d0d0d0;
}

.btn-answer {
  width: 100%;
  background: #42b883;
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
}

.btn-answer:hover {
  background: #3aa876;
}
</style>
