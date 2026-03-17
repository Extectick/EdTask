# Фронтенд платформы обучения - Готово!

## ✅ Созданные компоненты

### Роутинг (Vue Router)
- `/login` - Страница входа
- `/master/*` - Layout мастера
  - `/master/tasks` - Список задач
  - `/master/tasks/:taskId` - Детали задачи
  - `/master/tasks/new` - Создание задачи
  - `/master/students` - Управление учениками
- `/student/*` - Layout ученика
  - `/student/tasks` - Мои задачи
  - `/student/tasks/:taskId/answer` - Ответ на задачу

### API Сервис (`src/api.js`)
- `authApi.login()` - Вход по токену
- `fileApi.uploadImage()` - Загрузка изображения
- `fileApi.deleteImage()` - Удаление изображения
- `masterUserApi.createUser()` - Создание ученика
- `masterUserApi.deleteUser()` - Удаление ученика
- `masterTaskApi.getTasks()` - Получение задач (с фильтрами)
- `masterTaskApi.createTask()` - Создание задачи
- `masterTaskApi.updateTask()` - Обновление задачи
- `masterTaskApi.deleteTask()` - Удаление задачи
- `answerApi.getAnswers()` - Получение ответов
- `answerApi.createAnswer()` - Создание ответа
- `answerApi.updateAnswer()` - Обновление ответа (комментарий + оценка)

### Stores (Pinia)
- `auth` store - Аутентификация, хранение токена и данных пользователя

### Страницы

#### Auth
- `LoginView.vue` - Вход по токену с редиректом по роли

#### Layouts
- `MasterLayout.vue` - Sidebar с навигацией для мастера
- `StudentLayout.vue` - Sidebar с навигацией для ученика

#### Master
- `TasksView.vue` - Список задач с фильтрами (filter_status, student_id)
- `TaskDetailView.vue` - Просмотр задачи и проверка ответов
- `CreateTaskView.vue` - Создание задачи с загрузкой изображений
- `StudentsView.vue` - Управление учениками (создание/удаление)

#### Student
- `TasksView.vue` - Мои задачи с цветовой кодировкой статуса
- `AnswerView.vue` - Просмотр задачи и отправка ответа

## 🎨 Функции

### Для мастера:
- ✅ Быстрый поиск по статусу (unreviewed, no_answers, in_revision, solved)
- ✅ Фильтр по ученику (student_id)
- ✅ Проверка ответов с comment и comment_grade
- ✅ Создание задач с изображениями
- ✅ Управление учениками

### Для ученика:
- ✅ Просмотр задач с цветовой кодировкой:
  - Серый - нет ответов
  - Жёлтый - на проверке (grade 0)
  - Оранжевый - на доработке (grade 1)
  - Зелёный - решено (grade 2)
- ✅ Отправка ответа с изображением
- ✅ Просмотр комментариев мастера

## 🚀 Запуск

```bash
# Установка зависимостей
npm install

# Запуск dev-сервера
npm run dev

# Сборка production
npm run build
```

## 📁 Структура проекта

```
frontend/
├── src/
│   ├── api.js              # API сервис
│   ├── App.vue             # Корневой компонент
│   ├── main.js             # Точка входа
│   ├── style.css           # Tailwind CSS
│   ├── router/
│   │   └── index.js        # Роутинг
│   ├── stores/
│   │   └── auth.js         # Auth store
│   └── views/
│       ├── layouts/        # Layouts
│       ├── auth/           # Login
│       ├── master/         # Страницы мастера
│       └── student/        # Страницы ученика
├── .env                    # Переменные окружения
├── tailwind.config.js      # Tailwind конфиг
├── postcss.config.js       # PostCSS конфиг
└── package.json
```

## 🔐 Авторизация

1. Введите токен на странице `/login`
2. Данные сохраняются в localStorage
3. Роутер автоматически перенаправляет:
   - Мастеров → `/master/tasks`
   - Учеников → `/student/tasks`

## 📝 Заметки

- Для работы нужен запущенный бэкенд на `http://127.0.0.1:8000`
- Изображения отдаются прямыми URL из MinIO (`image_url`)
- Все запросы используют токен из Pinia store
