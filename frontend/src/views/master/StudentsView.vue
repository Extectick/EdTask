<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-800 mb-8">Ученики</h1>

    <div class="grid lg:grid-cols-3 gap-6">
      <!-- Форма создания -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-lg shadow p-6 sticky top-6">
          <h2 class="text-xl font-bold text-gray-800 mb-4">Добавить ученика</h2>

          <form @submit.prevent="handleCreate">
            <div class="mb-4">
              <label for="user_id" class="block text-sm font-medium text-gray-700 mb-2">
                Токен пользователя *
              </label>
              <input
                id="user_id"
                v-model="form.user_id"
                type="text"
                required
                placeholder="user123"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div class="mb-6">
              <label for="full_name" class="block text-sm font-medium text-gray-700 mb-2">
                Полное имя *
              </label>
              <input
                id="full_name"
                v-model="form.full_name"
                type="text"
                required
                placeholder="Иван Петров"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              :disabled="creating"
              class="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50"
            >
              {{ creating ? 'Создание...' : 'Создать' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Список учеников -->
      <div class="lg:col-span-2">
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>

        <div v-else-if="students.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
          <p class="text-gray-600">Учеников пока нет</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="student in students"
            :key="student.user_id"
            class="bg-white rounded-lg shadow p-6 flex items-center justify-between"
          >
            <div>
              <h3 class="font-semibold text-gray-800">{{ student.full_name }}</h3>
              <p class="text-sm text-gray-500">{{ student.user_id }}</p>
            </div>

            <button
              @click="handleDelete(student)"
              :disabled="deleting === student.user_id"
              class="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition disabled:opacity-50"
            >
              {{ deleting === student.user_id ? 'Удаление...' : 'Удалить' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { masterUserApi } from '@/api'

const authStore = useAuthStore()

const students = ref([])
const loading = ref(false)
const creating = ref(false)
const deleting = ref(null)

const form = reactive({
  user_id: '',
  full_name: '',
})

const loadStudents = async () => {
  loading.value = true
  try {
    const response = await masterUserApi.getStudents(authStore.token)
    students.value = response.data.students || []
  } catch (error) {
    console.error('Failed to load students:', error)
    alert('Ошибка загрузки списка учеников')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  creating.value = true
  try {
    await masterUserApi.createUser(form.user_id, form.full_name, authStore.token)
    form.user_id = ''
    form.full_name = ''
    loadStudents()
  } catch (error) {
    console.error('Failed to create student:', error)
    alert('Ошибка: ' + (error.response?.data?.detail || error.message))
  } finally {
    creating.value = false
  }
}

const handleDelete = async (student) => {
  if (!confirm(`Удалить ученика "${student.full_name}"?`)) return

  deleting.value = student.user_id
  try {
    await masterUserApi.deleteUser(student.user_id, authStore.token)
    loadStudents()
  } catch (error) {
    console.error('Failed to delete student:', error)
    alert('Ошибка: ' + (error.response?.data?.detail || error.message))
  } finally {
    deleting.value = null
  }
}

onMounted(() => {
  loadStudents()
})
</script>
