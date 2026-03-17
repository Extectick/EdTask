# EdTask - Система управления задачами

Образовательная платформа для учителей и учеников с возможностью:
- ✅ Создания задач с изображениями
- ✅ Управления доступом (по пользователям и ролям)
- ✅ Отправки ответов с фото
- ✅ Мобильной версии (фото с телефона)

---

## 🚀 Быстрый старт

### Разработка через Docker Compose

```bash
docker compose up --build
```

Открой:
- Frontend: http://127.0.0.1:5173
- Backend API: http://127.0.0.1:8000

---

### Что поднимается

- `postgres` - основная БД
- `backend` - FastAPI, подключается к Postgres через `DATABASE_URL`
- `frontend` - Vite dev server
- `minio` - S3-совместимое хранилище изображений на `9000`, консоль на `9001`

Картинки больше не хранятся в локальном `data/img` как основной storage: новые изображения загружаются в MinIO, а в БД сохраняется их публичный URL.

### Bootstrap мастера

Первый мастер создаётся автоматически при старте backend из переменных окружения в `docker-compose.yml`:

```yaml
BOOTSTRAP_MASTER_TOKEN: admin
BOOTSTRAP_MASTER_FULL_NAME: 123
```

После первого старта используй токен `admin` для входа. Эти значения нужно сменить для своего окружения.

### Ручное создание мастера

```bash
docker compose exec backend python create_master.py teacher1 "Иван Петров"
```

---

## 📦 Продакшн сборка

### 1. Смена API URL

```bash
cd frontend
# Измени .env.production:
# VITE_API_URL=http://tunnel4.com:8000

npm run build
```

### 2. Копирование сборки

```bash
# Скопировать dist в backend/static
xcopy /E /I /Y frontend\dist backend\static
```

### 3. Запуск сервера

```bash
cd backend
pip install -r requirements.txt

# DATABASE_URL должен указывать на доступный PostgreSQL
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Открой:**
- Frontend: `http://localhost:5173`
- Backend API: `http://127.0.0.1:8000`

Смотри [DEPLOY.md](DEPLOY.md) для подробностей.

---

## 📁 Структура

```
EdTask/
├── backend/
│   ├── main.py              # FastAPI приложение
│   ├── routers/             # API эндпоинты
│   │   ├── auth.py          # Логин
│   │   ├── admin.py         # Админка
│   │   ├── master.py        # Панель мастера
│   │   └── master_task.py   # Задачи + клиент API
│   ├── data/
│   │   ├── data.py          # SQLAlchemy модели
│   │   └── img/             # Изображения
│   └── static/              # Фронтенд сборка
├── frontend/
│   ├── src/
│   │   ├── views/           # Vue компоненты
│   │   ├── components/      # Переиспользуемые компоненты
│   │   └── router/          # Vue Router
│   ├── .env                 # URL для разработки
│   └── .env.production      # URL для продакшена
├── DEPLOY_HTTPS.md          # Инструкция по HTTPS
└── README.md                # Этот файл
```

---

## 🔐 Роли

| Роль | Описание | Страница |
|------|----------|----------|
| **admin** | Создание мастеров | `/admin` |
| **master** | Управление задачами и учениками | `/master/students` |
| **user** | Просмотр и отправка ответов | `/client/tasks` |

---

## 📱 Мобильная версия

- ✅ Фото с телефона (камера)
- ✅ Адаптивный интерфейс
- ✅ PWA готовность

---

## 🛠 Технологии

**Фронтенд:**
- Vue 3 (Composition API)
- Vue Router
- Axios
- Vite

**Бэкенд:**
- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn

---

## 📝 Переменные окружения

### `.env` (разработка)
```env
VITE_API_URL=http://127.0.0.1:8000
```

### `.env.production` (продакшн)
```env
VITE_API_URL=https://tunnel4.com
```

---

## 🔧 Команды

### Фронтенд
```bash
npm run dev      # Запуск dev сервера
npm run build    # Сборка продакшена
npm run preview  # Предпросмотр сборки
npm run lint     # Проверка кода
```

### Бэкенд
```bash
uvicorn main:app --reload   # Dev режим
uvicorn main:app --workers 4  # Production
python create_master.py admin Admin  # Ручное создание мастера при наличии DATABASE_URL
python -m py_compile *.py   # Проверка синтаксиса
```

---

## 📞 Поддержка

При проблемах смотри:
- [DEPLOY_HTTPS.md](DEPLOY_HTTPS.md) - HTTPS развёртывание
- [CHANGE_API_URL.md](frontend/CHANGE_API_URL.md) - Смена API URL

---

## 📄 Лицензия

MIT
