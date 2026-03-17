<template>
  <div>
    <button @click="$router.back()" class="mb-4 flex items-center text-gray-600 hover:text-gray-800">
      <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      Назад
    </button>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="!task" class="bg-white rounded-lg shadow p-12 text-center">
      <p class="text-gray-600">Задача не найдена</p>
    </div>

    <div v-else class="grid lg:grid-cols-3 gap-6">
      <!-- Модальное окно подтверждения удаления -->
      <div
        v-if="showDeleteConfirm"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      >
        <div class="bg-white rounded-lg p-6 max-w-md">
          <h3 class="text-lg font-bold mb-4">Удалить задачу?</h3>
          <p class="text-gray-600 mb-6">Это действие нельзя отменить. Все файлы и ответы будут удалены.</p>
          <div class="flex gap-4">
            <button
              @click="confirmDelete"
              :disabled="deleting"
              class="flex-1 bg-red-600 text-white py-2 rounded-lg hover:bg-red-700 transition disabled:opacity-50"
            >
              {{ deleting ? 'Удаление...' : 'Удалить' }}
            </button>
            <button
              @click="showDeleteConfirm = false"
              class="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300 transition"
            >
              Отмена
            </button>
          </div>
        </div>
      </div>

      <!-- Модальное окно редактирования -->
      <div
        v-if="showEditModal"
        class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      >
        <div class="bg-white rounded-lg p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto">
          <h3 class="text-lg font-bold mb-4">Редактировать задачу</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Заголовок</label>
              <input
                v-model="editForm.title"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Описание</label>
              <textarea
                v-model="editForm.description"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              ></textarea>
            </div>
          </div>
          <div class="flex gap-4 mt-6">
            <button
              @click="confirmEdit"
              :disabled="saving"
              class="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
            >
              {{ saving ? 'Сохранение...' : 'Сохранить' }}
            </button>
            <button
              @click="showEditModal = false"
              class="flex-1 bg-gray-200 text-gray-800 py-2 rounded-lg hover:bg-gray-300 transition"
            >
              Отмена
            </button>
          </div>
        </div>
      </div>

      <!-- Изображение в полном размере (модальное окно) -->
      <div
        v-if="selectedImage"
        class="fixed inset-0 bg-black bg-opacity-75 z-50 flex items-center justify-center p-4"
        @click="selectedImage = null"
      >
        <div class="relative max-w-6xl max-h-screen">
          <button
            @click="selectedImage = null"
            class="absolute -top-10 right-0 text-white hover:text-gray-300"
          >
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
          <img
            :src="selectedImage"
            alt="Full size"
            class="max-w-full max-h-[90vh] object-contain"
          />
        </div>
      </div>

      <!-- Описание задачи -->
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-start justify-between mb-4">
            <h1 class="text-2xl font-bold text-gray-800">{{ task.title }}</h1>
            <div class="flex gap-2">
              <button
                @click="showEditModal = true"
                class="text-blue-600 hover:text-blue-800 p-2"
                title="Редактировать"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <button
                @click="showDeleteConfirm = true"
                class="text-red-600 hover:text-red-800 p-2"
                title="Удалить"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
          <p class="text-gray-600">{{ task.description }}</p>

          <!-- Изображения задачи -->
          <div v-if="task.images?.length" class="mt-6 grid grid-cols-2 gap-4">
            <div
              v-for="img in task.images"
              :key="img.id"
              class="relative cursor-pointer group"
              @click="selectedImage = img.image_url"
            >
              <img
                :src="img.image_url"
                :alt="img.id"
                class="w-full h-48 object-cover rounded-lg group-hover:opacity-75 transition"
              />
              <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
                <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- Файлы задачи -->
          <div v-if="task.files?.length" class="mt-6 space-y-2">
            <h3 class="text-lg font-semibold text-gray-800">Файлы</h3>
            <div
              v-for="file in task.files"
              :key="file.id"
              class="flex items-center justify-between bg-gray-50 rounded-lg p-3"
            >
              <div class="flex items-center">
                <svg class="w-6 h-6 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <span class="text-sm text-gray-700">{{ file.original_name || file.file_name }}</span>
              </div>
              <a
                :href="`${API_URL}/data/files/${file.file_name}`"
                download
                class="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Скачать
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Ответы учеников -->
      <div class="space-y-4">
        <h2 class="text-xl font-bold text-gray-800">Ответы учеников</h2>

        <div v-if="!task.answers?.length" class="bg-white rounded-lg shadow p-6 text-center">
          <p class="text-gray-600">Нет ответов</p>
        </div>

        <div
          v-for="answer in task.answers"
          :key="answer.id"
          class="bg-white rounded-lg shadow p-6"
        >
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm text-gray-500">{{ formatDate(answer.created_at) }}</span>
            <span
              class="px-2 py-1 text-xs font-medium rounded"
              :class="{
                'bg-yellow-100 text-yellow-800': answer.comment_grade === 0,
                'bg-orange-100 text-orange-800': answer.comment_grade === 1,
                'bg-green-100 text-green-800': answer.comment_grade === 2,
              }"
            >
              {{ gradeText(answer.comment_grade) }}
            </span>
          </div>

          <p class="text-gray-800 mb-3">{{ answer.content }}</p>

          <!-- Изображение ответа -->
          <div v-if="answer.image" class="mb-3">
            <img
              :src="answer.image.image_url"
              alt="Ответ"
              class="w-full h-48 object-cover rounded-lg cursor-pointer hover:opacity-75 transition"
              @click="selectedImage = answer.image.image_url"
            />
          </div>

          <!-- Форма проверки -->
          <div class="border-t pt-3 mt-3">
            <label class="block text-sm font-medium text-gray-700 mb-2">Комментарий и оценка</label>
            <textarea
              v-model="answer.comment"
              rows="2"
              placeholder="Введите комментарий..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm mb-2"
            ></textarea>
            <select
              v-model.number="answer.comment_grade"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm mb-3"
            >
              <option :value="0">Новый (0)</option>
              <option :value="1">На доработку (1)</option>
              <option :value="2">Решено (2)</option>
            </select>
            <button
              @click="submitReview(answer)"
              :disabled="submitting"
              class="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50"
            >
              {{ submitting ? 'Сохранение...' : 'Сохранить' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { masterTaskApi, answerApi, api } from '@/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const task = ref(null)
const loading = ref(true)
const submitting = ref(false)
const selectedImage = ref(null)
const showDeleteConfirm = ref(false)
const showEditModal = ref(false)
const deleting = ref(false)
const saving = ref(false)

const editForm = ref({
  title: '',
  description: ''
})

const loadTask = async () => {
  loading.value = true
  try {
    const response = await masterTaskApi.getTasks({
      master_token: authStore.token,
      task_id: route.params.taskId,
    })
    task.value = response.data.task
    editForm.value = {
      title: task.value.title,
      description: task.value.description
    }
  } catch (error) {
    console.error('Failed to load task:', error)
    alert('Ошибка загрузки задачи')
  } finally {
    loading.value = false
  }
}

const confirmDelete = async () => {
  deleting.value = true
  try {
    const formData = new FormData()
    formData.append('task_id', route.params.taskId)
    formData.append('master_token', authStore.token)
    
    await api.post('/master/task/delete', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    router.push('/master/tasks')
  } catch (error) {
    console.error('Failed to delete task:', error)
    alert('Ошибка удаления задачи')
  } finally {
    deleting.value = false
    showDeleteConfirm.value = false
  }
}

const confirmEdit = async () => {
  saving.value = true
  try {
    const formData = new FormData()
    formData.append('task_id', route.params.taskId)
    formData.append('title', editForm.value.title)
    formData.append('description', editForm.value.description)
    formData.append('master_token', authStore.token)
    
    await api.post('/master/task/update', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    task.value.title = editForm.value.title
    task.value.description = editForm.value.description
    showEditModal.value = false
  } catch (error) {
    console.error('Failed to update task:', error)
    alert('Ошибка обновления задачи')
  } finally {
    saving.value = false
  }
}

const submitReview = async (answer) => {
  submitting.value = true
  try {
    await answerApi.updateAnswer(answer.id, {
      comment: answer.comment,
      comment_grade: answer.comment_grade,
    }, authStore.token)
  } catch (error) {
    console.error('Failed to submit review:', error)
    alert('Ошибка сохранения рецензии')
  } finally {
    submitting.value = false
  }
}

const gradeText = (grade) => {
  const texts = {
    0: 'Новый',
    1: 'На доработку',
    2: 'Решено',
  }
  return texts[grade] || 'Неизвестно'
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadTask()
})
</script>
