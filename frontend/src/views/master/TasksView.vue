<template>
  <div>
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-800">Задачи</h1>
      <p class="text-gray-600 mt-2">Управление задачами и проверка ответов</p>
    </div>

    <!-- Фильтры -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
      <div class="flex flex-wrap gap-4">
        <!-- Быстрый поиск по статусу -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Статус</label>
          <select
            v-model="filters.filter_status"
            @change="loadTasks"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Все задачи</option>
            <option value="unreviewed">Требуют проверки</option>
            <option value="no_answers">Без ответов</option>
            <option value="in_revision">На доработке</option>
            <option value="solved">Решённые</option>
          </select>
        </div>

        <!-- Поиск по ученику -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Ученик</label>
          <select
            v-model="filters.student_id"
            @change="loadTasks"
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Все ученики</option>
            <option v-for="student in students" :key="student.user_id" :value="student.user_id">
              {{ student.full_name }}
            </option>
          </select>
        </div>

        <!-- Кнопка сброса -->
        <div class="flex items-end">
          <button
            @click="resetFilters"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition"
          >
            Сбросить
          </button>
        </div>
      </div>
    </div>

    <!-- Список задач -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="tasks.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
      </svg>
      <p class="mt-4 text-gray-600">Задач не найдено</p>
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer"
        @click="goToTask(task.id)"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-800">{{ task.title }}</h3>
            <span
              class="px-2 py-1 text-xs font-medium rounded"
              :class="{
                'bg-green-100 text-green-800': task.is_active,
                'bg-gray-100 text-gray-800': !task.is_active,
              }"
            >
              {{ task.is_active ? 'Активна' : 'Архив' }}
            </span>
          </div>

          <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ task.description }}</p>

          <!-- Ученик -->
          <div v-if="task.assigned_to_name" class="mb-3 flex items-center text-sm">
            <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            <span class="text-gray-700 font-medium">{{ task.assigned_to_name }}</span>
            <span class="text-gray-500 ml-2">({{ task.assigned_to }})</span>
          </div>

          <div class="flex items-center justify-between text-sm text-gray-500">
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              {{ formatDate(task.created_at) }}
            </span>
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              {{ task.answers_count }} ответов
            </span>
          </div>

          <!-- Индикаторы статусов -->
          <div v-if="hasSolvedAnswer(task)" class="mt-3 flex items-center text-green-600 text-xs">
            <span class="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
            Решено
          </div>
          <div v-else-if="hasAnswersWithGrade(task, 0)" class="mt-3 flex items-center text-yellow-600 text-xs">
            <span class="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
            Требует проверки
          </div>
          <div v-else-if="hasAnswersWithGrade(task, 1)" class="mt-1 flex items-center text-orange-600 text-xs">
            <span class="w-2 h-2 bg-orange-500 rounded-full mr-2"></span>
            На доработке
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { masterTaskApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const tasks = ref([])
const students = ref([])
const loading = ref(false)

const filters = reactive({
  filter_status: '',
  student_id: '',
})

const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      master_token: authStore.token,
      ...(filters.filter_status && { filter_status: filters.filter_status }),
      ...(filters.student_id && { student_id: filters.student_id }),
    }

    const response = await masterTaskApi.getTasks(params)
    tasks.value = response.data.tasks || []
  } catch (error) {
    console.error('Failed to load tasks:', error)
    alert('Ошибка загрузки задач')
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.filter_status = ''
  filters.student_id = ''
  loadTasks()
}

const goToTask = (taskId) => {
  router.push(`/master/tasks/${taskId}`)
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

const hasAnswersWithGrade = (task, grade) => {
  // grade 0 = новые (comment_grade === 0 или null/undefined)
  if (grade === 0) {
    return task.answers?.some(a => a.comment_grade === 0 || a.comment_grade === null || a.comment_grade === undefined)
  }
  return task.answers?.some(a => a.comment_grade === grade)
}

const hasSolvedAnswer = (task) => {
  // Есть хотя бы один ответ со статусом "Решено" (grade 2)
  return task.answers?.some(a => a.comment_grade === 2)
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
