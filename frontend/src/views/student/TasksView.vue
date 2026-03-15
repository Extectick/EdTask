<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-800 mb-8">Мои задачи</h1>

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>

    <div v-else-if="tasks.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
      </svg>
      <p class="mt-4 text-gray-600">Задач пока нет</p>
    </div>

    <div v-else class="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="task in tasks"
        :key="task.id"
        class="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer"
        @click="goToAnswer(task)"
      >
        <div class="p-6">
          <div class="flex items-start justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-800">{{ task.title }}</h3>
            <!-- Статус на основе comment_grade -->
            <span
              class="px-2 py-1 text-xs font-medium rounded"
              :class="{
                'bg-gray-100 text-gray-800': !task.my_answers?.length,
                'bg-yellow-100 text-yellow-800': hasUnreviewedAnswer(task),
                'bg-orange-100 text-orange-800': hasRevisionAnswer(task),
                'bg-green-100 text-green-800': hasSolvedAnswer(task),
              }"
            >
              {{ getStatusText(task) }}
            </span>
          </div>

          <p class="text-gray-600 text-sm mb-4 line-clamp-2">{{ task.description }}</p>

          <div class="flex items-center justify-between text-sm text-gray-500">
            <span class="flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              {{ formatDate(task.created_at) }}
            </span>
            <span v-if="task.my_answers?.length" class="text-gray-400">
              {{ task.my_answers.length }} ответ{{ task.my_answers.length === 1 ? '' : 'а' }}
            </span>
          </div>

          <!-- Комментарии мастера -->
          <div v-if="task.my_answers?.length" class="mt-4 pt-4 border-t">
            <div
              v-for="answer in task.my_answers"
              :key="answer.id"
              class="text-sm"
            >
              <div v-if="answer.comment" class="text-gray-700 mb-1">
                <span class="font-medium">Комментарий:</span> {{ answer.comment }}
              </div>
              <div v-if="answer.comment_grade !== null" class="flex items-center">
                <span
                  class="w-2 h-2 rounded-full mr-2"
                  :class="{
                    'bg-yellow-500': answer.comment_grade === 0,
                    'bg-orange-500': answer.comment_grade === 1,
                    'bg-green-500': answer.comment_grade === 2,
                  }"
                ></span>
                <span class="text-xs" :class="{
                  'text-yellow-600': answer.comment_grade === 0,
                  'text-orange-600': answer.comment_grade === 1,
                  'text-green-600': answer.comment_grade === 2,
                }">
                  {{ gradeText(answer.comment_grade) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { userTaskApi } from '@/api'

const router = useRouter()
const authStore = useAuthStore()

const tasks = ref([])
const loading = ref(false)

const loadTasks = async () => {
  loading.value = true
  try {
    const response = await userTaskApi.getTasks(authStore.token)
    tasks.value = response.data.tasks || []
  } catch (error) {
    console.error('Failed to load tasks:', error)
    alert('Ошибка загрузки задач')
  } finally {
    loading.value = false
  }
}

const goToAnswer = (task) => {
  router.push(`/student/tasks/${task.id}/answer`)
}

const getStatusText = (task) => {
  if (!task.my_answers?.length) return 'Нет ответов'
  if (hasSolvedAnswer(task)) return 'Решено'
  if (hasRevisionAnswer(task)) return 'На доработке'
  if (hasUnreviewedAnswer(task)) return 'На проверке'
  return 'Нет ответов'
}

const hasUnreviewedAnswer = (task) => {
  return task.my_answers?.some(a => a.comment_grade === 0)
}

const hasRevisionAnswer = (task) => {
  return task.my_answers?.some(a => a.comment_grade === 1)
}

const hasSolvedAnswer = (task) => {
  return task.my_answers?.some(a => a.comment_grade === 2)
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
    year: 'numeric',
  })
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
