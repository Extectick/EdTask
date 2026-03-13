# 🚀 Развёртывание через Ngrok

## ✅ Готово к тестированию

Фронтенд собран для работы через **ngrok туннель**.

---

## 📋 Требования

1. **Python 3.11+** для бэкенда
2. **Ngrok аккаунт** (бесплатно)
3. **Ngrok установлен**

---

## 🔧 Запуск

### 1. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Запуск бэкенда

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Запуск ngrok (в другом терминале)

```bash
ngrok http 8000
```

### 4. Открой ngrok URL

Ngrok покажет URL вида:
```
https://xxxx-xxx-xxx-xxx.ngrok-free.app
```

---

## 🔄 Сборка фронтенда для ngrok

### 1. Обнови `.env.production`

```env
VITE_API_URL=https://xxxx-xxx-xxx-xxx.ngrok-free.app
```

### 2. Пересобери

```bash
cd frontend
npm run build

# Скопируй в static
xcopy /E /I /Y dist ..\backend\static
```

---

## 📝 Нюансы ngrok

### Бесплатный тариф:
- ⚠️ URL меняется при каждом перезапуске
- ⚠️ Сессия ограничена по времени
- ⚠️ Нужно подтверждение в браузере при первом входе

### Платный тариф:
- ✅ Постоянный домен
- ✅ Без ограничений

---

## 🆘 Если не работает

1. **CORS ошибки:**
   - Проверь что URL в `.env.production` совпадает с ngrok URL
   - Пересобери фронтенд

2. **Ngrok просит подтверждение:**
   - Открой ссылку из терминала ngrok
   - Нажми "Visit Site"

3. **Бэкенд не отвечает:**
   ```bash
   # Проверь что запущен
   netstat -an | findstr :8000
   ```

---

## 📋 Требования

1. **Python 3.11+** для бэкенда
2. **Открытый порт 8000** на сервере

---

## 🔧 Запуск бэкенда

### 1. Установка зависимостей

```bash
cd /path/to/EdTask/backend
pip install -r requirements.txt
```

### 2. Запуск в production режиме

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Проверка

Открой в браузере: `http://tunnel4.com:8000`

---

## 🔧 Nginx (опционально, для проксирования)

Если хочешь использовать nginx как reverse proxy:

### 1. Конфигурация nginx

```nginx
server {
    listen 80;
    server_name tunnel4.com www.tunnel4.com;

    # Фронтенд (статика)
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Изображения
    location /data/img/ {
        proxy_pass http://127.0.0.1:8000/data/img/;
    }
}
```

### 2. Запуск nginx

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

---

## 📝 Проверка

1. Открой `http://tunnel4.com:8000`
2. Проверь консоль браузера (F12) на ошибки
3. Попробуй войти в систему

---

## ⚙️ Production настройки

Уже настроено:
- ✅ CORS для всех origin (можно ограничить)
- ✅ API URL: `http://tunnel4.com:8000`
- ✅ Статика раздаётся через FastAPI
- ✅ 4 worker процесса

---

## 📊 Мониторинг

```bash
# Логи приложения
journalctl -u uvicorn -f

# Проверка процесса
ps aux | grep uvicorn
```

---

## 🆘 Если что-то не работает

1. **Проверь что сервер запущен:**
   ```bash
   ps aux | grep uvicorn
   ```

2. **Проверь порт:**
   ```bash
   netstat -tlnp | grep 8000
   ```

3. **Проверь CORS:**
   - Открой консоль браузера (F12)
   - Попробуй сделать запрос
   - Проверь заголовки `Access-Control-Allow-Origin`

4. **Перезапусти сервер:**
   ```bash
   # Останови (Ctrl+C)
   # Запусти заново
   cd /path/to/EdTask/backend
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

---

## 🔐 Для включения HTTPS

Смотри инструкцию в [DEPLOY_HTTPS.md](DEPLOY_HTTPS.md) (нужно создать отдельно).
