<template>
  <div>
    <button @click="$router.back()" class="mb-4 flex items-center text-gray-600 hover:text-gray-800">
      <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
      </svg>
      Назад
    </button>

    <div class="max-w-2xl">
      <h1 class="text-3xl font-bold text-gray-800 mb-8">Создание задачи</h1>

      <div class="bg-white rounded-lg shadow p-6">
        <form @submit.prevent="handleSubmit">
          <!-- Заголовок -->
          <div class="mb-6">
            <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
              Заголовок *
            </label>
            <input
              id="title"
              v-model="form.title"
              type="text"
              required
              placeholder="Введите заголовок задачи"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <!-- Описание -->
          <div class="mb-6">
            <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
              Описание *
            </label>
            <textarea
              id="description"
              v-model="form.description"
              required
              rows="5"
              placeholder="Введите описание задачи"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            ></textarea>
          </div>

          <!-- Выбор ученика -->
          <div class="mb-6">
            <label for="user_id" class="block text-sm font-medium text-gray-700 mb-2">
              Ученик *
            </label>
            <select
              id="user_id"
              v-model="form.user_id"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Выберите ученика</option>
              <option v-for="student in students" :key="student.user_id" :value="student.user_id">
                {{ student.full_name }} ({{ student.user_id }})
              </option>
            </select>
          </div>

          <!-- Чекбокс is_material -->
          <div class="mb-6">
            <label class="flex items-center">
              <input
                v-model="form.is_material"
                type="checkbox"
                class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span class="ml-2 text-gray-700">
                Это учебный материал (без приёма ответов)
              </span>
            </label>
          </div>

          <!-- Загрузка изображений -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Изображения
            </label>
            <div
              class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition"
              @dragover.prevent
              @drop.prevent="handleDrop"
            >
              <input
                ref="fileInput"
                type="file"
                accept="image/*"
                multiple
                class="hidden"
                @change="handleFileSelect"
              />
              <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <p class="mt-2 text-sm text-gray-600">
                Перетащите файлы сюда или <button type="button" @click="$refs.fileInput.click()" class="text-blue-600 hover:underline">выберите</button>
              </p>
              <p class="mt-1 text-xs text-gray-500">PNG, JPG, GIF до 10MB</p>
            </div>

            <!-- Превью загруженных изображений -->
            <div v-if="uploadedImages.length" class="mt-4 grid grid-cols-3 gap-4">
              <div
                v-for="(img, index) in uploadedImages"
                :key="index"
                class="relative group"
              >
                <img
                  :src="img.preview"
                  :alt="img.name"
                  class="w-full h-32 object-cover rounded-lg"
                />
                <button
                  type="button"
                  @click="removeImage(index)"
                  class="absolute top-1 right-1 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Загрузка файлов -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Файлы (документы)
            </label>
            <div
              class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-green-500 transition"
              @dragover.prevent
              @drop.prevent="handleFileDrop"
            >
              <input
                ref="fileFilesInput"
                type="file"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.zip,.rar"
                multiple
                class="hidden"
                @change="handleFilesSelect"
              />
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <p class="mt-2 text-sm text-gray-600">
                Перетащите файлы сюда или <button type="button" @click="$refs.fileFilesInput.click()" class="text-green-600 hover:underline">выберите</button>
              </p>
              <p class="mt-1 text-xs text-gray-500">PDF, DOC, XLS, TXT, ZIP до 50MB</p>
            </div>

            <!-- Список загруженных файлов -->
            <div v-if="uploadedFiles.length" class="mt-4 space-y-2">
              <div
                v-for="(file, index) in uploadedFiles"
                :key="index"
                class="flex items-center justify-between bg-gray-50 rounded-lg p-3"
              >
                <div class="flex items-center">
                  <svg class="w-6 h-6 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                  <span class="text-sm text-gray-700">{{ file.name }}</span>
                </div>
                <button
                  type="button"
                  @click="removeFile(index)"
                  class="text-red-500 hover:text-red-700"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>

          <!-- Кнопки -->
          <div class="flex gap-4">
            <button
              type="submit"
              :disabled="submitting || uploading"
              class="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ submitting ? 'Создание...' : 'Создать задачу' }}
            </button>
            <button
              type="button"
              @click="$router.back()"
              class="px-6 py-3 border border-gray-300 rounded-lg font-semibold text-gray-700 hover:bg-gray-50 transition"
            >
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { masterTaskApi, fileApi, masterUserApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  title: '',
  description: '',
  user_id: '',  // Токен ученика
  is_material: false,
})

const students = ref([])

const uploadedImages = ref([])
const imageIds = ref([])  // Храним ID изображений (числа)

const uploadedFiles = ref([])
const fileIds = ref([])  // Храним ID файлов (числа)

const submitting = ref(false)
const uploading = ref(false)

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  uploadFiles(files)
}

const handleDrop = (event) => {
  const files = Array.from(event.dataTransfer.files)
  uploadFiles(files)
}

// Загрузка изображений
const uploadFiles = async (files) => {
  uploading.value = true
  for (const file of files) {
    if (!file.type.startsWith('image/')) continue

    try {
      const formData = new FormData()
      formData.append('image', file)

      const response = await fileApi.uploadImage(formData)
      uploadedImages.value.push({
        id: response.data.image_id,  // Сохраняем ID изображения
        preview: URL.createObjectURL(file),
      })
      imageIds.value.push(response.data.image_id)  // Добавляем ID в массив
    } catch (error) {
      console.error('Failed to upload image:', error)
      alert(`Ошибка загрузки изображения: ${file.name}`)
    }
  }
  uploading.value = false
}

// Загрузка файлов (документов)
const handleFilesSelect = (event) => {
  const files = Array.from(event.target.files)
  uploadDocumentFiles(files)
}

const handleFileDrop = (event) => {
  const files = Array.from(event.dataTransfer.files)
  uploadDocumentFiles(files)
}

const uploadDocumentFiles = async (files) => {
  uploading.value = true
  for (const file of files) {
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fileApi.uploadFile(formData)
      uploadedFiles.value.push({
        id: response.data.file_id,
        name: response.data.original_name || file.name,
      })
      fileIds.value.push(response.data.file_id)
    } catch (error) {
      console.error('Failed to upload file:', error)
      alert(`Ошибка загрузки файла: ${file.name}`)
    }
  }
  uploading.value = false
}

const removeImage = (index) => {
  uploadedImages.value.splice(index, 1)
  imageIds.value.splice(index, 1)
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
  fileIds.value.splice(index, 1)
}

const handleSubmit = async () => {
  submitting.value = true
  try {
    if (!form.user_id) {
      alert('Выберите ученика!')
      submitting.value = false
      return
    }
    await masterTaskApi.createTask(
      form.title,
      form.description,
      authStore.token,
      form.user_id,  // Передаём токен ученика
      imageIds.value,  // Передаём ID изображений
      fileIds.value  // Передаём ID файлов
    )
    router.push('/master/tasks')
  } catch (error) {
    console.error('Failed to create task:', error)
    console.error('Response data:', error.response?.data)
    const detail = error.response?.data?.detail
    if (Array.isArray(detail)) {
      // Валидационная ошибка - показать первое сообщение
      alert('Ошибка: ' + detail[0]?.msg)
    } else if (typeof detail === 'string') {
      alert('Ошибка: ' + detail)
    } else {
      alert('Ошибка создания задачи')
    }
  } finally {
    submitting.value = false
  }
}

// Загрузка списка учеников при монтировании
onMounted(async () => {
  try {
    const response = await masterUserApi.getStudents(authStore.token)
    students.value = response.data.students || []
  } catch (error) {
    console.error('Failed to load students:', error)
  }
})
</script>
