import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layouts
import MasterLayout from '@/views/layouts/MasterLayout.vue'
import StudentLayout from '@/views/layouts/StudentLayout.vue'

// Auth
import LoginView from '@/views/auth/LoginView.vue'

// Master views
import MasterTasksView from '@/views/master/TasksView.vue'
import MasterTaskDetailView from '@/views/master/TaskDetailView.vue'
import MasterCreateTaskView from '@/views/master/CreateTaskView.vue'
import MasterStudentsView from '@/views/master/StudentsView.vue'

// Student views
import StudentTasksView from '@/views/student/TasksView.vue'
import StudentAnswerView from '@/views/student/AnswerView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login',
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { guest: true },
    },
    {
      path: '/master',
      component: MasterLayout,
      meta: { requiresAuth: true, role: 'master' },
      children: [
        {
          path: 'tasks',
          name: 'master-tasks',
          component: MasterTasksView,
        },
        {
          path: 'tasks/:taskId',
          name: 'master-task-detail',
          component: MasterTaskDetailView,
          props: true,
        },
        {
          path: 'tasks/new',
          name: 'master-create-task',
          component: MasterCreateTaskView,
        },
        {
          path: 'students',
          name: 'master-students',
          component: MasterStudentsView,
        },
      ],
    },
    {
      path: '/student',
      component: StudentLayout,
      meta: { requiresAuth: true, role: 'student' },
      children: [
        {
          path: 'tasks',
          name: 'student-tasks',
          component: StudentTasksView,
        },
        {
          path: 'tasks/:taskId/answer',
          name: 'student-answer',
          component: StudentAnswerView,
          props: true,
        },
      ],
    },
  ],
})

// Навигационный гард
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const isAuthenticated = authStore.isAuthenticated
  const user = authStore.user

  // Инициализация аутентификации
  authStore.initAuth()

  // Страницы только для гостей
  if (to.meta.guest) {
    if (isAuthenticated) {
      return next(user?.type === 'master' ? '/master/tasks' : '/student/tasks')
    }
    return next()
  }

  // Страницы требующие авторизации
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      return next('/login')
    }

    // Проверка роли
    if (to.meta.role && to.meta.role !== user?.type) {
      // Перенаправляем на правильную страницу в зависимости от роли
      return next(user?.type === 'master' ? '/master/tasks' : '/student/tasks')
    }
  }

  next()
})

export default router
