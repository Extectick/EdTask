<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

// Состояния для данных
const masters = ref([])
const isLoading = ref(false)
const errorMsg = ref('')

// Состояние для формы создания учителя
const newMaster = ref({
  name: '',
  full_name: ''
})

// 1. Загрузка всех учителей и их учеников
const fetchMasters = async () => {
  errorMsg.value = ''
  try {
    const response = await axios.post(`${API_URL}/admin/get_masters`)
    if (response.data.status === 'success') {
      masters.value = response.data.masters
    }
  } catch (err) {
    console.error(err)
    errorMsg.value = 'Ошибка загрузки данных. Проверьте соединение с сервером.'
  }
}

// 2. Создание нового учителя
const handleCreateMaster = async () => {
  if (!newMaster.value.name || !newMaster.value.full_name) {
    alert('Заполните все поля')
    return
  }

  isLoading.value = true
  try {
    const response = await axios.post('http://127.0.0.1:8000/admin/new_user', {
      name: newMaster.value.name,
      full_name: newMaster.value.full_name
    })

    if (response.data.status === 'success') {
      alert(`Учитель ${response.data.full_name} успешно создан!`)
      // Очищаем форму
      newMaster.value.name = ''
      newMaster.value.full_name = ''
      // Обновляем список
      await fetchMasters()
    }
  } catch (err) {
    alert(err.response?.data?.detail || 'Ошибка при создании')
  } finally {
    isLoading.value = false
  }
}

// Запускаем загрузку при открытии страницы
onMounted(() => {
  fetchMasters()
})
</script>

<template>
  <div class="admin-container">
    <header class="admin-header">
      <h1>Панель управления</h1>
      <button @click="fetchMasters" class="refresh-btn">🔄 Обновить данные</button>
    </header>

    <section class="card creation-form">
      <h2>➕ Регистрация нового учителя</h2>
      <div class="inputs">
        <input 
          v-model="newMaster.name" 
          type="text" 
          placeholder="Логин (например: ivan#123)"
        />
        <input 
          v-model="newMaster.full_name" 
          type="text" 
          placeholder="Полное имя (Иванов Иван)"
        />
        <button @click="handleCreateMaster" :disabled="isLoading">
          {{ isLoading ? 'Создание...' : 'Добавить учителя' }}
        </button>
      </div>
    </section>

    <p v-if="errorMsg" class="error-banner">{{ errorMsg }}</p>

    <section class="masters-list">
      <h2>📋 Список учителей и учеников</h2>
      <div v-if="masters.length === 0" class="empty-state">Учителей пока нет</div>
      
      <div v-for="master in masters" :key="master.master_id" class="master-card">
        <div class="master-info">
          <h3>{{ master.full_name }}</h3>
          <span class="badge">Логин: {{ master.name }}</span>
          <span class="id-label">ID: {{ master.master_id }}</span>
        </div>

        <div class="apprentices-section">
          <h4>Ученики:</h4>
          <ul v-if="master.apprentices && master.apprentices.length > 0">
            <li v-for="student in master.apprentices" :key="student.id" class="student-item">
              <span class="student-name">{{ student.full_name || 'Без имени' }}</span>
              <span class="student-id">ID: {{ student.user_id }}</span>
            </li>
          </ul>
          <p v-else class="no-students">У этого учителя пока нет учеников</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.admin-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.card {
  background: #fff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  margin-bottom: 30px;
  border: 1px solid #eee;
}

.inputs {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
}

button {
  padding: 10px 20px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

button:hover { background-color: #3aa876; }
button:disabled { background-color: #a7d9c1; cursor: not-allowed; }

.refresh-btn { background-color: #35495e; }

.master-card {
  background: white;
  border-left: 5px solid #42b883;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.master-info h3 { margin: 0; color: #2c3e50; }
.badge {
  background: #e1f5fe;
  color: #0288d1;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  margin-right: 10px;
}

.apprentices-section {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.student-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px dashed #eee;
}

.student-name { font-weight: 500; }
.student-id { color: #888; font-size: 0.9rem; }
.no-students { color: #999; font-style: italic; }
.error-banner { background: #fee2e2; color: #dc2626; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
</style>