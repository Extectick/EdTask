<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'
import { useRouter } from 'vue-router'
import MasterNav from '../components/MasterNav.vue'

const router = useRouter()
const masterToken = Cookies.get('user_token')

const tasks = ref([])
const isLoading = ref(false)
const editingTask = ref(null)
const editForm = ref({ title: '', description: '' })
const uploadImageTaskId = ref(null)
const uploadImageFile = ref(null)
const accessTaskId = ref(null)
const accessUsers = ref([])
const accessRoles = ref([])
const selectedUserId = ref('')
const selectedRoleId = ref('')
const allUsers = ref([])
const allRoles = ref([])

// Получить все задачи мастера
const fetchTasks = async () => {
  try {
    isLoading.value = true
    const formData = new FormData()
    formData.append('master_token', masterToken)
    
    const res = await axios.post('http://127.0.0.1:8000/master/task/get_tasks', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    tasks.value = res.data.tasks
  } catch (e) {
    console.error("Ошибка загрузки задач", e)
    alert(e.response?.data?.detail || 'Ошибка при загрузке задач')
  } finally {
    isLoading.value = false
  }
}

// Переключить статус задачи
const toggleActive = async (taskId) => {
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('master_token', masterToken)
    
    await axios.post('http://127.0.0.1:8000/master/task/toggle_active', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    fetchTasks()
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

// Удалить задачу
const deleteTask = async (taskId, taskTitle) => {
  if (!confirm(`Удалить задачу "${taskTitle}"? Это действие нельзя отменить!`)) return
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('master_token', masterToken)
    
    await axios.post('http://127.0.0.1:8000/master/task/delete_task', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    fetchTasks()
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка при удалении')
  }
}

// Начать редактирование задачи
const startEdit = (task) => {
  editingTask.value = task.id
  editForm.value = {
    title: task.title,
    description: task.description
  }
}

// Сохранить редактирование
const saveEdit = async (taskId) => {
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('title', editForm.value.title)
    formData.append('description', editForm.value.description)
    formData.append('master_token', masterToken)
    
    await axios.post('http://127.0.0.1:8000/master/task/edit_task', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    editingTask.value = null
    fetchTasks()
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка при сохранении')
  }
}

// Отменить редактирование
const cancelEdit = () => {
  editingTask.value = null
  editForm.value = { title: '', description: '' }
}

// Удалить изображение
const deleteImage = async (taskId, imageId) => {
  if (!confirm('Удалить это изображение?')) return
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('image_id', imageId)
    formData.append('master_token', masterToken)
    
    await axios.post('http://127.0.0.1:8000/master/task/delete_image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    fetchTasks()
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка при удалении')
  }
}

// Поменять местами главное и маленькое изображение
const swapImage = (task, index) => {
  const mainImage = task.images[0]
  const smallImage = task.images[index + 1]
  
  task.images[0] = smallImage
  task.images[index + 1] = mainImage
}

// Открыть форму загрузки изображения
const openUploadForm = (taskId) => {
  uploadImageTaskId.value = taskId
  uploadImageFile.value = null
}

// Загрузить изображение
const uploadImage = async (taskId) => {
  if (!uploadImageFile.value) {
    alert('Выберите файл')
    return
  }
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('master_token', masterToken)
    formData.append('image', uploadImageFile.value)
    
    await axios.post('http://127.0.0.1:8000/master/task/upload_image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    uploadImageTaskId.value = null
    uploadImageFile.value = null
    fetchTasks()
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка при загрузке')
  }
}

// Закрыть форму загрузки
const closeUploadForm = () => {
  uploadImageTaskId.value = null
  uploadImageFile.value = null
}

// Загрузить списки пользователей и ролей
const loadUsersAndRoles = async () => {
  try {
    const usersRes = await axios.post('http://127.0.0.1:8000/master/get_users', {
      master_token: masterToken
    })
    allUsers.value = usersRes.data.users || []
    
    const rolesRes = await axios.post('http://127.0.0.1:8000/master/get_roles', {
      master_token: masterToken
    })
    allRoles.value = rolesRes.data.roles || []
  } catch (e) {
    console.error('Ошибка загрузки списков', e)
  }
}

// Открыть управление доступом
const openAccessForm = async (task) => {
  accessTaskId.value = task.id
  await loadUsersAndRoles()
  await loadAccess(task.id)
}

// Загрузить текущий доступ
const loadAccess = async (taskId) => {
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('master_token', masterToken)
    
    const res = await axios.post('http://127.0.0.1:8000/master/task/get_access', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    accessUsers.value = res.data.users || []
    accessRoles.value = res.data.roles || []
  } catch (e) {
    console.error('Ошибка загрузки доступа', e)
  }
}

// Дать доступ пользователю
const grantUserAccess = async (taskId) => {
  if (!selectedUserId.value) {
    alert('Выберите пользователя')
    return
  }
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('user_id', selectedUserId.value)
    formData.append('master_token', masterToken)
    
    await axios.post('http://127.0.0.1:8000/master/task/grant_user_access', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    selectedUserId.value = ''
    await loadAccess(taskId)
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

// Дать доступ роли
const grantRoleAccess = async (taskId) => {
  if (!selectedRoleId.value) {
    alert('Выберите роль')
    return
  }
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('role_id', selectedRoleId.value)
    formData.append('master_token', masterToken)
    
    await axios.post('http://127.0.0.1:8000/master/task/grant_role_access', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    selectedRoleId.value = ''
    await loadAccess(taskId)
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

// Отозвать доступ у пользователя
const revokeUserAccess = async (taskId, accessId) => {
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('access_id', accessId)
    formData.append('master_token', masterToken)
    
    await axios.post('http://127.0.0.1:8000/master/task/revoke_user_access', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await loadAccess(taskId)
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

// Отозвать доступ у роли
const revokeRoleAccess = async (taskId, accessId) => {
  try {
    const formData = new FormData()
    formData.append('task_id', taskId)
    formData.append('access_id', accessId)
    formData.append('master_token', masterToken)
    
    await axios.post('http://127.0.0.1:8000/master/task/revoke_role_access', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    await loadAccess(taskId)
  } catch (e) {
    alert(e.response?.data?.detail || 'Ошибка')
  }
}

// Закрыть форму доступа
const closeAccessForm = () => {
  accessTaskId.value = null
  accessUsers.value = []
  accessRoles.value = []
}

// Перейти к созданию задачи
const goToCreateTask = () => {
  router.push('/master/tasks/new')
}

onMounted(() => {
  fetchTasks()
})
</script>

<template>
  <div class="master-tasks-page">
    <MasterNav />
    
    <div class="page-content">
      <div class="content-header">
        <h1>Мои задачи</h1>
        <button @click="goToCreateTask" class="btn-new">➕ Новая задача</button>
      </div>

      <div v-if="isLoading" class="loading">Загрузка...</div>

      <div v-else-if="tasks.length === 0" class="empty-state">
        <p>У вас пока нет задач</p>
        <button @click="goToCreateTask" class="btn-new">Создать первую задачу</button>
      </div>

      <div v-else class="tasks-list">
        <div v-for="task in tasks" :key="task.id" class="task-card" :class="{ inactive: !task.is_active }">
          
          <!-- Режим просмотра -->
          <template v-if="editingTask !== task.id">
            <div class="task-header">
              <h3>{{ task.title }}</h3>
              <div class="header-actions">
                <span class="status-badge" :class="{ active: task.is_active }">
                  {{ task.is_active ? 'Активна' : 'Неактивна' }}
                </span>
                <button @click="startEdit(task)" class="btn-edit-sm">✏️</button>
              </div>
            </div>

            <div v-if="task.images.length > 0" class="task-main-image">
              <img
                :src="`http://127.0.0.1:8000/data/img/${task.images[0].image_name}`"
                :alt="task.images[0].image_name"
                class="main-image"
              />
              <button @click="deleteImage(task.id, task.images[0].id)" class="delete-image-btn">×</button>
            </div>

            <p class="task-description">{{ task.description }}</p>

            <div v-if="task.images.length > 1" class="task-images">
              <div v-for="(img, idx) in task.images.slice(1)" :key="img.id" class="thumb-wrapper">
                <img
                  :src="`http://127.0.0.1:8000/data/img/${img.image_name}`"
                  :alt="img.image_name"
                  class="task-image-thumb"
                  @click="swapImage(task, idx)"
                  title="Нажмите, чтобы сделать главным"
                />
                <button @click="deleteImage(task.id, img.id)" class="delete-thumb-btn">×</button>
              </div>
            </div>
          </template>

          <!-- Режим редактирования -->
          <template v-else>
            <div class="edit-form">
              <div class="form-group">
                <label>Заголовок</label>
                <input v-model="editForm.title" type="text" />
              </div>
              <div class="form-group">
                <label>Описание</label>
                <textarea v-model="editForm.description" rows="4"></textarea>
              </div>
              <div class="edit-actions">
                <button @click="saveEdit(task.id)" class="btn-save">💾 Сохранить</button>
                <button @click="cancelEdit" class="btn-cancel-edit">Отмена</button>
              </div>
            </div>
          </template>

          <!-- Статистика и действия (всегда видны) -->
          <div class="task-stats">
            <span class="answers-count">
              💬 Ответов: {{ task.answers?.length || 0 }}
            </span>
            <span class="created-at">
              📅 {{ new Date(task.created_at).toLocaleDateString('ru-RU') }}
            </span>
          </div>

          <!-- Ответы учеников -->
          <div v-if="task.answers && task.answers.length > 0" class="answers-section">
            <h4>Ответы учеников:</h4>
            <div v-for="answer in task.answers" :key="answer.id" class="answer-card">
              <div class="answer-header">
                <span class="answer-user">{{ answer.user_id }}</span>
                <span class="answer-date">{{ new Date(answer.created_at).toLocaleString('ru-RU') }}</span>
              </div>
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
            </div>
          </div>

          <div class="task-actions">
            <button @click="toggleActive(task.id)" class="btn-toggle">
              {{ task.is_active ? '⏸️ Деактивировать' : '▶️ Активировать' }}
            </button>
            <button @click="openUploadForm(task.id)" class="btn-upload">📷 Фото</button>
            <button @click="openAccessForm(task)" class="btn-access">🔐 Доступ</button>
            <button @click="deleteTask(task.id, task.title)" class="btn-delete">
              🗑️ Удалить
            </button>
          </div>

          <!-- Модальное окно загрузки изображения -->
          <div v-if="uploadImageTaskId === task.id" class="upload-modal">
            <div class="upload-content">
              <h4>Загрузить изображение</h4>
              <input type="file" accept="image/*" @change="uploadImageFile = $event.target.files[0]" />
              <div class="upload-actions">
                <button @click="uploadImage(task.id)" class="btn-upload-confirm">Загрузить</button>
                <button @click="closeUploadForm" class="btn-upload-cancel">Отмена</button>
              </div>
            </div>
          </div>

          <!-- Модальное окно управления доступом -->
          <div v-if="accessTaskId === task.id" class="upload-modal">
            <div class="upload-content access-content">
              <h4>Управление доступом</h4>
              
              <div class="access-section">
                <h5>Пользователи</h5>
                <div class="access-add">
                  <select v-model="selectedUserId">
                    <option value="" disabled>Выберите пользователя</option>
                    <option v-for="u in allUsers" :key="u.user_id" :value="u.user_id">
                      {{ u.full_name }} ({{ u.user_id }})
                    </option>
                  </select>
                  <button @click="grantUserAccess(task.id)" class="btn-add">➕</button>
                </div>
                <div class="access-list">
                  <div v-for="u in accessUsers" :key="u.id" class="access-item">
                    <span>{{ u.full_name || u.user_id }}</span>
                    <button @click="revokeUserAccess(task.id, u.id)" class="btn-revoke">×</button>
                  </div>
                </div>
              </div>
              
              <div class="access-section">
                <h5>Роли</h5>
                <div class="access-add">
                  <select v-model="selectedRoleId">
                    <option value="" disabled>Выберите роль</option>
                    <option v-for="r in allRoles" :key="r.role_id" :value="r.role_id">
                      {{ r.role_name }} ({{ r.role_id }})
                    </option>
                  </select>
                  <button @click="grantRoleAccess(task.id)" class="btn-add">➕</button>
                </div>
                <div class="access-list">
                  <div v-for="r in accessRoles" :key="r.id" class="access-item">
                    <span>{{ r.role_name || r.role_id }}</span>
                    <button @click="revokeRoleAccess(task.id, r.id)" class="btn-revoke">×</button>
                  </div>
                </div>
              </div>
              
              <div class="upload-actions">
                <button @click="closeAccessForm" class="btn-upload-cancel">Закрыть</button>
              </div>
            </div>
          </div>

        </div>  <!-- Закрывает task-card -->
      </div>  <!-- Закрывает tasks-list -->
    </div>  <!-- Закрывает page-content -->
  </div>  <!-- Закрывает master-tasks-page -->
</template>

<style scoped>
.master-tasks-page {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.page-content {
  padding: 30px;
  max-width: 1000px;
  margin: 0 auto;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.content-header h1 {
  margin: 0;
  color: #333;
}

.btn-new {
  background: #42b883;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 0.95rem;
}

.btn-new:hover {
  background: #3aa876;
}

.loading, .empty-state {
  text-align: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  color: #666;
}

.empty-state button {
  margin-top: 20px;
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
  overflow: hidden;
}

.task-card.inactive {
  opacity: 0.7;
  background: #f5f5f5;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.task-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-edit-sm {
  background: #e3f2fd;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-edit-sm:hover {
  background: #bbdefb;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  background: #ffebee;
  color: #c62828;
}

.status-badge.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.task-main-image {
  width: 100%;
  margin-bottom: 20px;
  position: relative;
}

.main-image {
  width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
  border-radius: 8px;
}

.delete-image-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(255, 0, 0, 0.8);
  color: white;
  border: none;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
}

.delete-image-btn:hover {
  background: rgba(255, 0, 0, 1);
}

.thumb-wrapper {
  position: relative;
  display: inline-block;
}

.delete-thumb-btn {
  position: absolute;
  top: -5px;
  right: -5px;
  background: rgba(255, 0, 0, 0.8);
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.9rem;
  line-height: 1;
}

.delete-thumb-btn:hover {
  background: rgba(255, 0, 0, 1);
}

.task-image-thumb {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  border: 2px solid #e0e0e0;
  cursor: pointer;
  transition: border-color 0.2s, transform 0.2s;
}

.task-image-thumb:hover {
  border-color: #2196f3;
  transform: scale(1.05);
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

/* Форма редактирования */
.edit-form {
  margin-bottom: 20px;
}

.edit-form .form-group {
  margin-bottom: 15px;
}

.edit-form label {
  display: block;
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}

.edit-form input,
.edit-form textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
  box-sizing: border-box;
}

.edit-form textarea {
  resize: vertical;
}

.edit-actions {
  display: flex;
  gap: 10px;
}

.btn-save {
  background: #42b883;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-save:hover {
  background: #3aa876;
}

.btn-cancel-edit {
  background: #e0e0e0;
  color: #333;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-cancel-edit:hover {
  background: #d0d0d0;
}

.task-stats {
  display: flex;
  gap: 20px;
  color: #888;
  font-size: 0.9rem;
  margin-bottom: 15px;
}

.task-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.btn-toggle {
  background: #2196f3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-toggle:hover {
  background: #1976d2;
}

.btn-delete {
  background: #ff4444;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-delete:hover {
  background: #cc0000;
}

.btn-upload {
  background: #2196f3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-upload:hover {
  background: #1976d2;
}

.btn-access {
  background: #9c27b0;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-access:hover {
  background: #7b1fa2;
}

/* Модальное окно */
.upload-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.upload-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  max-width: 400px;
  width: 90%;
}

.upload-content h4 {
  margin: 0 0 20px 0;
  color: #333;
}

.upload-content input[type="file"] {
  width: 100%;
  margin-bottom: 20px;
}

.upload-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn-upload-confirm {
  background: #42b883;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-upload-confirm:hover {
  background: #3aa876;
}

.btn-upload-cancel {
  background: #e0e0e0;
  color: #333;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.btn-upload-cancel:hover {
  background: #d0d0d0;
}

/* Управление доступом */
.access-content {
  max-width: 500px;
}

.access-section {
  margin-bottom: 20px;
}

.access-section h5 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 0.95rem;
}

.access-add {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.access-add select {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
}

.btn-add {
  background: #42b883;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
}

.btn-add:hover {
  background: #3aa876;
}

.access-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 150px;
  overflow-y: auto;
}

.access-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 6px;
}

.btn-revoke {
  background: #ff4444;
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}

.btn-revoke:hover {
  background: #cc0000;
}

/* Ответы учеников */
.answers-section {
  margin: 20px 0;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.answers-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 1rem;
}

.answer-card {
  background: white;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 15px;
  border-left: 3px solid #42b883;
}

.answer-card:last-child {
  margin-bottom: 0;
}

.answer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.answer-user {
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
}

.answer-date {
  color: #999;
  font-size: 0.85rem;
}

.answer-text {
  margin: 0 0 10px 0;
  color: #333;
  line-height: 1.5;
  white-space: pre-wrap;
}

.answer-images {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.answer-image-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ddd;
}
</style>
