# Фронтенд платформы обучения

## Технологии

- Vue 3 (Composition API)
- Pinia (state management)
- Vue Router (навигация)
- Tailwind CSS (стили)
- Axios (HTTP запросы)

## Установка

```bash
npm install
```

## Запуск

```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:5173

## Структура проекта

```
src/
├── api.js              # API сервис
├── App.vue             # Корневой компонент
├── main.js             # Точка входа
├── style.css           # Глобальные стили
├── router/
│   └── index.js        # Настройка роутинга
├── stores/
│   └── auth.js         # Auth store (Pinia)
├── views/
│   ├── layouts/
│   │   ├── MasterLayout.vue    # Layout мастера
│   │   └── StudentLayout.vue   # Layout ученика
│   ├── auth/
│   │   └── LoginView.vue       # Страница входа
│   ├── master/
│   │   ├── TasksView.vue       # Список задач
│   │   ├── TaskDetailView.vue  # Детали задачи
│   │   ├── CreateTaskView.vue  # Создание задачи
│   │   └── StudentsView.vue    # Управление учениками
│   └── student/
│       ├── TasksView.vue       # Задачи ученика
│       └── AnswerView.vue      # Ответ на задачу
└── components/         # Переиспользуемые компоненты
```

## Роли

### Мастер (учитель)
- Создание и управление задачами
- Проверка ответов учеников
- Управление учениками

### Ученик
- Просмотр задач
- Отправка ответов
- Просмотр комментариев мастера

## Переменные окружения

Создайте файл `.env` в корне проекта:

```
VITE_API_URL=http://127.0.0.1:8000
```

## Сборка

```bash
npm run build
```
