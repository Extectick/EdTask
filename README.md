# EdTask - Система управления задачами

Образовательная платформа для учителей и учеников с возможностью:
- ✅ Создания задач с изображениями
- ✅ Управления доступом (по пользователям и ролям)
- ✅ Отправки ответов с фото
- ✅ Мобильной версии (фото с телефона)

---

## 🚀 Быстрый старт

### Разработка

```bash
# Фронтенд (терминал 1)
cd frontend
npm install
npm run dev

# Бэкенд (терминал 2)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Открой: http://127.0.0.1:8000

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

# Локально
uvicorn main:app --reload

# Через ngrok (туннель)
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
- SQLAlchemy (SQLite)
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
