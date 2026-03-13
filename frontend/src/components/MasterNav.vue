<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Cookies from 'js-cookie'

const route = useRoute()
const router = useRouter()
const masterToken = Cookies.get('user_token')
const userRole = Cookies.get('user_role')

const isActive = (path) => {
  return route.path === path
}

const navigate = (path) => {
  router.push(path)
}

const logout = () => {
  Cookies.remove('user_token')
  Cookies.remove('user_role')
  router.push('/login')
}

// Показывать навигацию только для мастеров
const isMaster = computed(() => userRole === 'master')
</script>

<template>
  <nav v-if="isMaster" class="master-nav">
    <div class="nav-brand">
      <span class="logo">📚</span>
      <span class="brand-text">Панель Мастера</span>
    </div>

    <div class="nav-links">
      <button 
        @click="navigate('/master/students')" 
        class="nav-link"
        :class="{ active: isActive('/master/students') }"
      >
        👥 Ученики
      </button>
      
      <button 
        @click="navigate('/master/tasks')" 
        class="nav-link"
        :class="{ active: isActive('/master/tasks') }"
      >
        📋 Задачи
      </button>
    </div>

    <div class="nav-user">
      <span class="user-name">{{ masterToken?.split('#')[0] || 'Мастер' }}</span>
      <button @click="logout" class="btn-logout">🚪 Выход</button>
    </div>
  </nav>
</template>

<style scoped>
.master-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #35495e;
  color: white;
  padding: 15px 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 700;
}

.logo {
  font-size: 1.5rem;
}

.nav-links {
  display: flex;
  gap: 10px;
}

.nav-link {
  background: transparent;
  border: 2px solid transparent;
  color: rgba(255,255,255,0.8);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.nav-link:hover {
  background: rgba(255,255,255,0.1);
  color: white;
}

.nav-link.active {
  background: #42b883;
  color: white;
  border-color: #42b883;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-name {
  color: rgba(255,255,255,0.8);
  font-size: 0.9rem;
}

.btn-logout {
  background: rgba(255,255,255,0.1);
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.btn-logout:hover {
  background: rgba(255,255,255,0.2);
}
</style>
