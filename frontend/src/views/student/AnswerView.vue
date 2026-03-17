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

    <div v-else class="max-w-3xl">
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

      <h1 class="text-3xl font-bold text-gray-800 mb-6">{{ task.title }}</h1>

      <!-- Описание задачи -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-3">Описание</h2>
        <p class="text-gray-700 whitespace-pre-line">{{ task.description }}</p>

        <!-- Изображения задачи -->
        <div v-if="task.images?.length" class="mt-4 grid grid-cols-2 gap-4">
          <div
            v-for="img in task.images"
            :key="img.id"
            class="relative cursor-pointer group"
            @click="selectedImage = img.image_url"
          >
            <img
              :src="img.image_url"
              alt="Задача"
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
        <div v-if="task.files?.length" class="mt-4 space-y-2">
          <h3 class="text-lg font-semibold text-gray-800">Файлы</h3>
          <div
            v-for="(file, index) in uniqueFiles"
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

      <!-- Мои ответы -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Мои ответы</h2>

        <div v-if="!task.my_answers?.length" class="text-gray-600 text-center py-8">
          У вас ещё нет ответов на эту задачу
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="answer in task.my_answers"
            :key="answer.id"
            class="border rounded-lg p-4"
          >
            <div class="flex items-center justify-between mb-2">
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

            <p class="text-gray-800 mb-2">{{ answer.content }}</p>

            <div v-if="answer.image" class="mb-3">
              <img
                :src="answer.image.image_url"
                alt="Ответ"
                class="w-full h-48 object-cover rounded-lg cursor-pointer hover:opacity-75 transition"
                @click="selectedImage = answer.image.image_url"
              />
            </div>

            <div v-if="answer.comment" class="bg-gray-50 rounded p-3 mt-2">
              <p class="text-sm font-medium text-gray-700 mb-1">Комментарий мастера:</p>
              <p class="text-gray-600">{{ answer.comment }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Форма нового ответа -->
      <div class="bg-white rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Отправить ответ</h2>

        <form @submit.prevent="handleSubmit">
          <div class="mb-4">
            <label for="content" class="block text-sm font-medium text-gray-700 mb-2">
              Текст ответа *
            </label>
            <textarea
              id="content"
              v-model="form.content"
              required
              rows="5"
              placeholder="Введите ваш ответ..."
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            ></textarea>
          </div>

          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Изображение ответа
            </label>
            
            <!-- Кнопки загрузки -->
            <div class="flex gap-3 mb-4">
              <button
                type="button"
                @click="$refs.cameraInput.click()"
                class="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                Камера
              </button>
              <button
                type="button"
                @click="$refs.galleryInput.click()"
                class="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                Галерея
              </button>
            </div>
            
            <!-- Скрытые инпуты -->
            <input
              ref="cameraInput"
              type="file"
              accept="image/*"
              capture="environment"
              class="hidden"
              @change="handleFileSelect"
            />
            <input
              ref="galleryInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="handleFileSelect"
            />

            <!-- Превью -->
            <div v-if="uploadedImage" class="relative inline-block">
              <img :src="uploadedImage.preview" class="h-32 rounded-lg" />
              <button
                type="button"
                @click="uploadedImage = null"
                class="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>

          <button
            type="submit"
            :disabled="submitting || uploading"
            class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
          >
            {{ submitting ? 'Отправка...' : 'Отправить ответ' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { userTaskApi, answerApi, fileApi } from '@/api'

const route = useRoute()
const authStore = useAuthStore()
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

const task = ref(null)
const loading = ref(true)
const selectedImage = ref(null)

const form = reactive({
  content: '',
})

const uploadedImage = ref(null)
const imageId = ref(null)
const submitting = ref(false)
const uploading = ref(false)

const loadTask = async () => {
  loading.value = true
  try {
    const response = await userTaskApi.getTasks(authStore.token, route.params.taskId)
    task.value = response.data.task
  } catch (error) {
    console.error('Failed to load task:', error)
    alert('Ошибка загрузки задачи')
  } finally {
    loading.value = false
  }
}

// Убираем дубликаты файлов
const uniqueFiles = computed(() => {
  if (!task.value?.files) return []
  const seen = new Set()
  return task.value.files.filter(f => {
    if (seen.has(f.id)) return false
    seen.add(f.id)
    return true
  })
})

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) uploadFile(file)
}

const handleDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file) uploadFile(file)
}

const uploadFile = async (file) => {
  if (!file.type.startsWith('image/')) {
    alert('Пожалуйста, загрузите изображение')
    return
  }

  uploading.value = true
  try {
    const formData = new FormData()
    formData.append('image', file)

    const response = await fileApi.uploadImage(formData)
    uploadedImage.value = {
      id: response.data.image_id,
      preview: URL.createObjectURL(file),
    }
    imageId.value = response.data.image_id
  } catch (error) {
    console.error('Failed to upload image:', error)
    alert('Ошибка загрузки изображения')
  } finally {
    uploading.value = false
  }
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    await answerApi.createAnswer(
      route.params.taskId,
      form.content,
      imageId.value
    )
    form.content = ''
    uploadedImage.value = null
    imageId.value = null
    loadTask()
  } catch (error) {
    console.error('Failed to submit answer:', error)
    alert('Ошибка отправки ответа')
  } finally {
    submitting.value = false
  }
}

const gradeText = (grade) => {
  const texts = {
    0: 'На проверке',
    1: 'На доработку',
    2: 'Решено',
  }
  return texts[grade] || ''
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
