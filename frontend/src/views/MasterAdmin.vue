<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Cookies from 'js-cookie'
import MasterNav from '../components/MasterNav.vue'

const masterToken = Cookies.get('user_token')

console.log('[DEBUG] masterToken:', masterToken)

// Данные с сервера
const users = ref([])
const roles = ref([])

// Состояния форм
const newUser = ref({ user_id: '', full_name: '' })
const newRole = ref({ role_id: '', role_name: '' })
const assignData = ref({ user_id: '', role_id: '' })

// 1. Получить всех учеников и их роли
const fetchUsers = async () => {
  try {
    console.log('[DEBUG] fetchUsers вызван с master_token:', masterToken)
    const res = await axios.post('http://127.0.0.1:8000/master/get_users', {
      master_token: masterToken
    })
    users.value = res.data.users
    console.log('[DEBUG] Ученики загружены:', users.value)
  } catch (e) {
    console.error("Ошибка загрузки учеников", e)
    console.error("Response data:", e.response?.data)
  }
}

// 2. Создать ученика
const createUser = async () => {
  if (!newUser.value.user_id || !newUser.value.full_name) {
    alert('Заполните все поля!')
    return
  }
  try {
    await axios.post('http://127.0.0.1:8000/master/new_user', {
      ...newUser.value, master_token: masterToken
    })
    newUser.value = { user_id: '', full_name: '' }
    fetchUsers()
  } catch (e) { alert(e.response?.data?.detail || 'Ошибка при создании') }
}

// 3. Создать роль (с автогенерацией ID если не указан)
const createRole = async () => {
  if (!newRole.value.role_name) {
    alert('Введите название роли!')
    return
  }
  try {
    const roleId = newRole.value.role_id || generateRoleId(newRole.value.role_name)
    
    await axios.post('http://127.0.0.1:8000/master/new_role', {
      role_id: roleId,
      role_name: newRole.value.role_name,
      master_token: masterToken
    })
    newRole.value = { role_id: '', role_name: '' }
    fetchRoles()
  } catch (e) { alert(e.response?.data?.detail || 'Ошибка при создании') }
}

// Генерация ID роли из названия
const generateRoleId = (name) => {
  if (!name) return ''
  return name
    .toLowerCase()
    .replace(/[^а-яa-z0-9]/gi, '_')
    .slice(0, 20)
}

// Получить все роли мастера
const fetchRoles = async () => {
  try {
    const res = await axios.post('http://127.0.0.1:8000/master/get_roles', {
      master_token: masterToken
    })
    roles.value = res.data.roles
  } catch (e) { console.error("Ошибка загрузки ролей", e) }
}

// 4. Назначить роль
const assignRole = async () => {
  if (!assignData.value.user_id || !assignData.value.role_id) {
    alert('Выберите ученика и роль!')
    return
  }
  try {
    await axios.post('http://127.0.0.1:8000/master/assign_role', {
      ...assignData.value, master_token: masterToken
    })
    fetchUsers()
    fetchRoles()
  } catch (e) { alert(e.response?.data?.detail || 'Ошибка при назначении') }
}

// 5. Удалить роль у пользователя
const removeRoleFromUser = async (u_id, r_id) => {
  try {
    await axios.post('http://127.0.0.1:8000/master/remove_role', {
      user_id: u_id, role_id: r_id, master_token: masterToken
    })
    fetchUsers()
  } catch (e) { alert(e.response?.data?.detail || 'Ошибка') }
}

// 6. Удалить роль
const deleteRole = async (roleId) => {
  if (!confirm(`Удалить роль "${roleId}"? Это удалит её у всех учеников.`)) return
  try {
    await axios.post('http://127.0.0.1:8000/master/delete_role', {
      role_id: roleId, master_token: masterToken
    })
    fetchRoles()
    fetchUsers()
  } catch (e) { alert(e.response?.data?.detail || 'Ошибка при удалении') }
}

// 7. Удалить пользователя
const deleteUser = async (userId, userName) => {
  if (!confirm(`Вы уверены, что хотите удалить ученика "${userName}"?\nЭто действие нельзя отменить!`)) return
  try {
    await axios.post('http://127.0.0.1:8000/master/delete_user', {
      user_id: userId, master_token: masterToken
    })
    fetchUsers()
  } catch (e) { alert(e.response?.data?.detail || 'Ошибка при удалении') }
}

onMounted(() => {
  fetchUsers()
  fetchRoles()
})
</script>

<template>
  <div class="master-panel">
    <MasterNav />
    
    <div class="panel-content">

    <div class="level-1-grid">
      <section class="card action-card">
        <div class="card-icon">👤</div>
        <h3>Новый ученик</h3>
        <div class="form-body">
          <input v-model="newUser.user_id" placeholder="ID (ivan#123)" />
          <input v-model="newUser.full_name" placeholder="ФИО ученика" />
          <button @click="createUser" class="btn-primary">Зарегистрировать</button>
        </div>
      </section>

      <section class="card action-card">
        <div class="card-icon">🎭</div>
        <h3>Создать роль</h3>
        <div class="form-body">
          <input v-model="newRole.role_id" placeholder="ID (оставь пустым для авто)" />
          <input v-model="newRole.role_name" placeholder="Название (Староста)" />
          <button @click="createRole" class="btn-secondary">Создать роль</button>
        </div>
      </section>

      <section class="card action-card">
        <div class="card-icon">🔗</div>
        <h3>Назначить роль</h3>
        <div class="form-body">
          <select v-model="assignData.user_id">
            <option value="" disabled selected>Выберите ученика</option>
            <option v-for="u in users" :key="u.user_id" :value="u.user_id">
              {{ u.full_name }}
            </option>
          </select>
          <select v-model="assignData.role_id">
            <option value="" disabled selected>Выберите роль</option>
            <option v-for="r in roles" :key="r.role_id" :value="r.role_id">
              {{ r.role_name }} ({{ r.role_id }})
            </option>
          </select>
          <button @click="assignRole" class="btn-accent">Выдать роль</button>
        </div>
      </section>
    </div>

    <section class="level-2-roles">
      <div class="section-title">
        <h3>Доступные роли</h3>
        <span class="count-badge">{{ roles.length }}</span>
      </div>
      <div class="roles-container">
        <div v-if="roles.length === 0" class="empty-text">Роли еще не созданы</div>
        <div v-for="role in roles" :key="role.role_id" class="role-chip">
          <span class="role-id">#{{ role.role_id }}</span>
          <span class="role-name">{{ role.role_name }}</span>
          <button @click="deleteRole(role.role_id)" class="role-delete">×</button>
        </div>
      </div>
    </section>

    <section class="level-3-users">
      <div class="section-title">
        <h3>Список учеников</h3>
        <span class="count-badge">{{ users.length }}</span>
      </div>
      <div class="table-wrapper">
        <table class="modern-table">
          <thead>
            <tr>
              <th>ФИО Ученика</th>
              <th>Токен (ID)</th>
              <th>Активные роли</th>
              <th>Действия</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.user_id">
              <td class="user-name-cell">
                <div class="user-avatar">{{ user.full_name[0] }}</div>
                {{ user.full_name }}
              </td>
              <td><code>{{ user.user_id }}</code></td>
              <td>
                <div class="user-tags">
                  <span v-for="role in user.roles" :key="role" class="tag-pill">
                    {{ role }}
                    <button @click="removeRoleFromUser(user.user_id, role)" class="tag-remove">×</button>
                  </span>
                </div>
              </td>
              <td>
                <button @click="deleteUser(user.user_id, user.full_name)" class="delete-user-btn">
                  🗑️ Удалить
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    </div>
  </div>
</template>

<style scoped>
/* Глобальные настройки */
.master-panel {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.panel-content {
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Уровень 1: Сетка блоков */
.level-1-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 25px;
  margin-bottom: 50px;
}

.card {
  background: white;
  padding: 25px;
  border-radius: 15px;
  box-shadow: 0 10px 20px rgba(0,0,0,0.05);
}

.card-icon { font-size: 2rem; margin-bottom: 10px; }

.form-body input, .form-body select {
  width: 100%;
  padding: 12px;
  margin-bottom: 15px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.95rem;
  box-sizing: border-box;
}

/* Уровень 2: Роли */
.level-2-roles {
  margin-bottom: 50px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.count-badge {
  background: #42b883;
  color: white;
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 0.8rem;
}

.roles-container {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  border: 1px dashed #ced4da;
}

.role-chip {
  background: #f1f3f5;
  padding: 8px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #e9ecef;
}

.role-id { font-weight: bold; color: #42b883; font-size: 0.8rem; }
.role-delete {
  background: none;
  border: none;
  color: #ff6b6b;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0;
}

/* Уровень 3: Бесконечный список */
.level-3-users {
  background: white;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
  padding: 20px;
}

.table-wrapper {
  max-height: 500px; /* Ограничиваем высоту для эффекта бесконечного списка */
  overflow-y: auto;
  border-radius: 10px;
}

.modern-table {
  width: 100%;
  border-collapse: collapse;
}

.modern-table thead th {
  position: sticky;
  top: 0;
  background: #f8f9fa;
  padding: 15px;
  text-align: left;
  z-index: 10;
}

.modern-table td { padding: 15px; border-bottom: 1px solid #f1f3f5; }

.user-name-cell { display: flex; align-items: center; gap: 15px; font-weight: 500; }
.user-avatar {
  width: 35px;
  height: 35px;
  background: #42b883;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-transform: uppercase;
}

.tag-pill {
  background: #e7f5ff;
  color: #1971c2;
  padding: 4px 10px;
  border-radius: 5px;
  margin-right: 5px;
  font-size: 0.85rem;
  display: inline-flex;
  align-items: center;
}

.tag-remove { background: none; border: none; color: #1971c2; cursor: pointer; margin-left: 5px; }

.delete-user-btn {
  background: #ff4444;
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 0.85rem;
  white-space: nowrap;
}
.delete-user-btn:hover { background: #cc0000; }

/* Кнопки */
button { border: none; border-radius: 8px; cursor: pointer; font-weight: 600; }
.btn-primary { background: #42b883; color: white; width: 100%; padding: 12px; }
.btn-secondary { background: #35495e; color: white; width: 100%; padding: 12px; }
.btn-accent { background: #ff922b; color: white; width: 100%; padding: 12px; }
button:hover { opacity: 0.9; }
</style>