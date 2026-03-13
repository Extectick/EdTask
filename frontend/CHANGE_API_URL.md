# 🚀 Как изменить API URL

## Для разработки (локально)

Файл: `.env`

```env
VITE_API_URL=http://127.0.0.1:8000
```

## Для продакшена

Файл: `.env.production`

```env
VITE_API_URL=https://api.your-domain.com
```

## Сборка

```bash
# Для разработки (использует .env)
npm run dev

# Для продакшена (использует .env.production)
npm run build
```

## Как это работает

Все запросы к API используют переменную `import.meta.env.VITE_API_URL`:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

await axios.post(`${API_URL}/login`, {...})
```

## Быстрая смена

1. Открой `.env` или `.env.production`
2. Измени `VITE_API_URL`
3. Перезапусти сервер (`npm run dev` или `npm run build`)
