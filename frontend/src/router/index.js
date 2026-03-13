import { createRouter, createWebHistory } from 'vue-router'
import Cookies from 'js-cookie'

import LoginView from '../views/Login.vue'
import AdminView from '../views/Admin.vue'
import MasterAdmin from '../views/MasterAdmin.vue'
import MasterTask from '../views/MasterTask.vue'
import MasterNewTask from '../views/MasterNewTask.vue'
import ClientTasks from '../views/ClientTasks.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminView,
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/master/students',
      name: 'master-students',
      component: MasterAdmin,
      meta: { requiresAuth: true, role: 'master' }
    },
    {
      path: '/master/tasks',
      name: 'master-tasks',
      component: MasterTask,
      meta: { requiresAuth: true, role: 'master' }
    },
    {
      path: '/master/tasks/new',
      name: 'master-new-task',
      component: MasterNewTask,
      meta: { requiresAuth: true, role: 'master' }
    },
    {
      path: '/client/tasks',
      name: 'client-tasks',
      component: ClientTasks,
      meta: { requiresAuth: true, role: 'user' }
    }
  ],
})

// Навигационный гард
router.beforeEach((to, from) => {
  const token = Cookies.get('user_token')
  const role = Cookies.get('user_role')

  // 1. Если страница требует авторизации
  if (to.meta.requiresAuth) {
    if (!token) {
      return '/login'
    }

    // 2. Проверка ролей
    if (to.meta.role && to.meta.role !== role) {
      alert('У вас нет прав для доступа к этой странице!')
      // Если мастер пытается зайти к админу — шлем его к студентам, и наоборот
      return role === 'admin' ? '/admin' : '/master/students'
    }
  }
})

export default router