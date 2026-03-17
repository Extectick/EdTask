# Документация API для фронтенда

## Auth

### POST /auth/login
Вход в систему по токену.

**Request:**
```json
{
  "token": "user_token"
}
```

**Response:**
```json
{
  "status": "success",
  "user": {
    "id": 1,
    "token": "user_token",
    "full_name": "Иван Петров",
    "is_master": true,
    "master_id": null,
    "type": "master"
  }
}
```

---

## Master/Task

### GET /master/task
Получение списка задач мастера.

**Query параметры:**
- `master_token` (required) - токен мастера
- `filter_status` (optional) - unreviewed | no_answers | in_revision | solved
- `student_id` (optional) - токен ученика для фильтрации

**Response:**
```json
{
  "status": "success",
  "master_id": 1,
  "count": 2,
  "tasks": [
    {
      "id": 1,
      "title": "Задача 1",
      "description": "Описание",
      "is_active": true,
      "created_at": "2024-01-01 10:00:00",
      "images": [],
      "answers_count": 3,
      "answers": [...]
    }
  ]
}
```

### POST /master/task/create
Создание задачи.

**Request:**
```json
{
  "title": "Задача 1",
  "description": "Описание задачи",
  "master_token": "master_token",
  "image_ids": [1, 2, 3]
}
```

### PATCH /master/task
Обновление задачи.

**Request:**
```json
{
  "task_id": 1,
  "title": "Новое название",
  "description": "Новое описание",
  "master_token": "master_token",
  "image_ids": [4, 5]
}
```

### POST /master/task/delete
Удаление задачи.

**Request:**
```json
{
  "task_id": 1,
  "master_token": "master_token"
}
```

---

## Master/User

### POST /master/user/create
Создание ученика.

**Request:**
```json
{
  "user_id": "student_token",
  "full_name": "Петр Иванов",
  "master_token": "master_token"
}
```

### POST /master/user/delete
Удаление ученика.

**Request:**
```json
{
  "user_id": "student_token",
  "master_token": "master_token"
}
```

---

## User/Answer

### GET /user/answer
Получение ответов.

**Query параметры:**
- `master_token` (required)
- `task_id` (optional)
- `answer_id` (optional)

### POST /user/answer
Создание ответа.

**Request:**
```json
{
  "task_id": 1,
  "user_id": "student_token",
  "content": "Мой ответ",
  "master_token": "master_token",
  "image_id": 5
}
```

### PATCH /user/answer
Обновление ответа (мастер добавляет комментарий).

**Request:**
```json
{
  "answer_id": 1,
  "comment": "Хорошая работа!",
  "comment_grade": 2,
  "master_token": "master_token"
}
```

comment_grade:
- 0 = новый (на проверке)
- 1 = на доработку
- 2 = решено

---

## File/Image

### POST /file/image
Загрузка изображения.

**Content-Type:** multipart/form-data

**Request:**
```
image: <файл>
```

**Response:**
```json
{
  "status": "success",
  "image_id": 5,
  "image_name": "uuid.jpg",
  "image_url": "http://localhost:9000/edtask-images/images/uuid.jpg",
  "file_path": "http://localhost:9000/edtask-images/images/uuid.jpg",
  "size": 1024,
  "content_type": "image/jpeg"
}
```

### DELETE /file/image
Удаление изображения.

**Request:**
```json
{
  "image_url": "http://localhost:9000/edtask-images/images/uuid.jpg"
}
```

---

## Статические файлы

Изображения доступны напрямую по `image_url`, который возвращает backend после загрузки.
