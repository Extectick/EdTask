# API Documentation

Полная документация по всем API endpoint'ам проекта.

## Содержание

- [Auth](#auth)
- [File/Image](#fileimage)
- [File/File](#filefile)
- [Master/User](#masteruser)
- [Master/Task](#mastertask)
- [User/Answer](#useranswer)

---

## Auth

### POST /auth/login

Вход в аккаунт по токену.

**Content-Type:** `application/json`

**Request:**
```json
{
  "token": "user_token_abc123"
}
```

**Поля запроса:**
| Поле | Тип | Описание |
|------|-----|----------|
| token | string | Уникальный токен пользователя |

**Response (200 OK):**
```json
{
  "status": "success",
  "user": {
    "id": 5,
    "token": "user_token_abc123",
    "full_name": "Иван Петров",
    "is_master": false,
    "master_id": 1,
    "type": "student"
  }
}
```

**Поля ответа:**
| Поле | Тип | Описание |
|------|-----|----------|
| status | string | Статус операции |
| user | object | Данные пользователя |
| user.id | integer | ID пользователя |
| user.token | string | Токен пользователя |
| user.full_name | string | Полное имя |
| user.is_master | boolean | true = мастер, false = ученик |
| user.master_id | integer | ID мастера (для учеников) |
| user.type | string | "master" или "student" |

**Ошибки:**
- `404 Not Found` — Пользователь с таким токеном не найден

---

## File/Image

### POST /file/image

Загрузка изображения на сервер.

**Content-Type:** `multipart/form-data`

**Request:**
```
image: <файл>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "image_id": 5,
  "image_name": "550e8400-e29b-41d4-a716-446655440000.jpg",
  "image_url": "http://localhost:9000/edtask-images/images/550e8400-e29b-41d4-a716-446655440000.jpg",
  "file_path": "http://localhost:9000/edtask-images/images/550e8400-e29b-41d4-a716-446655440000.jpg",
  "size": 1024567,
  "content_type": "image/jpeg"
}
```

**Поля ответа:**
| Поле | Тип | Описание |
|------|-----|----------|
| status | string | Статус операции |
| image_id | integer | ID изображения в БД |
| image_name | string | Уникальное имя файла |
| image_url | string | Публичный URL изображения в MinIO |
| file_path | string | То же значение, что и `image_url` |
| size | integer | Размер в байтах |
| content_type | string | MIME-тип файла |

---

### DELETE /file/image

Удаление изображения с сервера.

**Content-Type:** `application/json`

**Request:**
```json
{
  "image_url": "http://localhost:9000/edtask-images/images/550e8400-e29b-41d4-a716-446655440000.jpg"
}
```

**Поля запроса:**
| Поле | Тип | Описание |
|------|-----|----------|
| image_url | string | URL изображения для удаления |

**Response (200 OK):**
```json
{
  "status": "success",
  "image_name": "550e8400-e29b-41d4-a716-446655440000.jpg",
  "image_url": "http://localhost:9000/edtask-images/images/550e8400-e29b-41d4-a716-446655440000.jpg"
}
```

---

## File/File

### POST /file/file

Загрузка файла на сервер.

**Content-Type:** `multipart/form-data`

**Request:**
```
file: <файл>
```

**Response (200 OK):**
```json
{
  "status": "success",
  "file_name": "550e8400-e29b-41d4-a716-446655440000.pdf",
  "file_path": "data/files/550e8400-e29b-41d4-a716-446655440000.pdf",
  "size": 2048576,
  "content_type": "application/pdf"
}
```

**Поля ответа:**
| Поле | Тип | Описание |
|------|-----|----------|
| status | string | Статус операции |
| file_name | string | Уникальное имя файла |
| file_path | string | Путь к файлу |
| size | integer | Размер в байтах |
| content_type | string | MIME-тип файла |

---

### DELETE /file/file

Удаление файла с сервера.

**Content-Type:** `application/json`

**Request:**
```json
{
  "file_name": "550e8400-e29b-41d4-a716-446655440000.pdf"
}
```

**Поля запроса:**
| Поле | Тип | Описание |
|------|-----|----------|
| file_name | string | Имя файла для удаления |

**Response (200 OK):**
```json
{
  "status": "success",
  "file_name": "550e8400-e29b-41d4-a716-446655440000.pdf"
}
```

---

## Master/User

### POST /master/user/create

Создание нового пользователя (ученика).

**Content-Type:** `application/json`

**Request:**
```json
{
  "user_id": "user123",
  "full_name": "Иван Петров",
  "master_token": "master_token_abc"
}
```

**Поля запроса:**
| Поле | Тип | Описание |
|------|-----|----------|
| user_id | string | Уникальный токен пользователя |
| full_name | string | Полное имя пользователя |
| master_token | string | Токен мастера (пользователь с is_master=True) |

**Response (200 OK):**
```json
{
  "status": "success",
  "type": "user",
  "id": 5,
  "user_id": "user123",
  "full_name": "Иван Петров",
  "master_id": 1
}
```

**Поля ответа:**
| Поле | Тип | Описание |
|------|-----|----------|
| status | string | Статус операции |
| type | string | Тип сущности |
| id | integer | ID нового пользователя |
| user_id | string | Токен пользователя |
| full_name | string | Полное имя |
| master_id | integer | ID мастера |

**Ошибки:**
- `400 Bad Request` — Пользователь уже существует
- `404 Not Found` — Мастер не найден

---

### POST /master/user/delete

Удаление пользователя (ученика).

**Content-Type:** `application/json`

**Request:**
```json
{
  "user_id": "user123",
  "master_token": "master_token_abc"
}
```

**Поля запроса:**
| Поле | Тип | Описание |
|------|-----|----------|
| user_id | string | Токен пользователя для удаления |
| master_token | string | Токен мастера |

**Response (200 OK):**
```json
{
  "status": "success",
  "user_id": "user123"
}
```

**Ошибки:**
- `404 Not Found` — Мастер или пользователь не найден
- `403 Forbidden` — Пользователь не принадлежит этому мастеру

---

## Master/Task

### POST /master/task/create

Создание новой задачи.

**Content-Type:** `application/json`

**Request:**
```json
{
  "title": "Домашняя работа №1",
  "description": "Решить задачи 1-10",
  "master_token": "master_token_abc",
  "image_ids": [1, 2, 3]
}
```

**Поля запроса:**
| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| title | string | Да | Заголовок задачи |
| description | string | Да | Описание задачи |
| master_token | string | Да | Токен мастера |
| image_ids | array[int] | Нет | Список ID изображений для привязки |

**Response (200 OK):**
```json
{
  "status": "success",
  "task_id": 10,
  "title": "Домашняя работа №1",
  "description": "Решить задачи 1-10"
}
```

**Поля ответа:**
| Поле | Тип | Описание |
|------|-----|----------|
| status | string | Статус операции |
| task_id | integer | ID новой задачи |
| title | string | Заголовок |
| description | string | Описание |

**Ошибки:**
- `404 Not Found` — Мастер не найден

---

### GET /master/task

Получение списка задач или одной задачи по ID с поддержкой фильтрации.

**Content-Type:** `application/json`

**Параметры запроса (Query Parameters):**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| master_token | string | Да | Токен мастера |
| task_id | integer | Нет | ID конкретной задачи |
| user_id | string | Нет | Токен ученика для получения его задач |
| filter_status | string | Нет | unreviewed \| no_answers \| in_revision \| solved |
| student_id | string | Нет | Токен ученика для фильтрации ответов |
| is_material | boolean | Нет | true = только материалы, false = только задачи |

**Примеры:**
```
# Все задачи мастера
GET /master/task?master_token=master_token_abc

# Одна задача по ID
GET /master/task?master_token=master_token_abc&task_id=10

# Задачи для конкретного ученика
GET /master/task?master_token=master_token_abc&user_id=user123

# Задачи без ответов
GET /master/task?master_token=master_token_abc&filter_status=no_answers

# Задачи, ожидающие проверки (comment_grade == 0)
GET /master/task?master_token=master_token_abc&filter_status=unreviewed

# Задачи на доработке (comment_grade == 1)
GET /master/task?master_token=master_token_abc&filter_status=in_revision

# Решённые задачи (comment_grade == 2)
GET /master/task?master_token=master_token_abc&filter_status=solved

# Задачи конкретного ученика на проверке
GET /master/task?master_token=master_token_abc&student_id=user456&filter_status=unreviewed
```

**Значения filter_status:**
| Значение | Описание |
|----------|----------|
| `unreviewed` | Задачи, где есть хотя бы один ответ с `comment_grade == 0` (новый ответ) |
| `no_answers` | Задачи, у которых вообще нет ответов |
| `in_revision` | Задачи, где есть ответы со статусом `comment_grade == 1` (на доработке) |
| `solved` | Задачи, где есть ответы со статусом `comment_grade == 2` (решено) |

**Response (список задач, 200 OK):**
```json
{
  "status": "success",
  "master_id": 1,
  "count": 2,
  "tasks": [
    {
      "id": 10,
      "title": "Домашняя работа №1",
      "description": "Решить задачи 1-10",
      "is_active": true,
      "created_at": "2024-01-15 10:30:00",
      "images": [
        {"id": 1, "path": "img/task1.jpg"},
        {"id": 2, "path": "img/task2.jpg"}
      ],
      "answers_count": 5,
      "answers": [
        {
          "id": 1,
          "content": "Ответ ученика",
          "created_at": "2024-01-15 12:00:00",
          "image": {"id": 5, "path": "img/answer1.jpg"},
          "comment": "Хорошо",
          "comment_grade": 5
        }
      ]
    }
  ]
}
```

**Response (одна задача по ID, 200 OK):**
```json
{
  "status": "success",
  "task": {
    "id": 10,
    "title": "Домашняя работа №1",
    "description": "Решить задачи 1-10",
    "is_active": true,
    "created_at": "2024-01-15 10:30:00",
    "images": [
      {"id": 1, "path": "img/task1.jpg"}
    ],
    "answers": [
      {
        "id": 1,
        "task_id": 10,
        "content": "Мой ответ",
        "created_at": "2024-01-15 12:00:00",
        "image": {"id": 5, "path": "img/answer1.jpg"},
        "comment": "Хорошо",
        "comment_grade": 5
      }
    ]
  }
}
```

**Response (задачи ученика, 200 OK):**
```json
{
  "status": "success",
  "user_id": "user123",
  "tasks": [
    {
      "id": 10,
      "title": "Домашняя работа №1",
      "description": "Решить задачи 1-10",
      "is_active": true,
      "created_at": "2024-01-15 10:30:00",
      "images": [
        {"id": 1, "path": "img/task1.jpg"}
      ],
      "my_answers": [
        {
          "id": 15,
          "content": "Мой ответ",
          "created_at": "2024-01-15 12:00:00",
          "image": {"id": 5, "path": "img/answer1.jpg"},
          "comment": "Хорошо",
          "comment_grade": 5
        }
      ]
    }
  ]
}
```

**Поля ответа:**
| Поле | Тип | Описание |
|------|-----|----------|
| status | string | Статус операции |
| master_id | integer | ID мастера (для списка задач) |
| count | integer | Количество задач в ответе |
| tasks | array | Список задач |
| tasks[].id | integer | ID задачи |
| tasks[].title | string | Заголовок |
| tasks[].description | string | Описание |
| tasks[].is_active | boolean | Активна ли задача |
| tasks[].created_at | string | Дата создания |
| tasks[].images | array | Изображения задачи |
| tasks[].answers_count | integer | Количество ответов |
| tasks[].answers | array | Ответы на задачу |
| tasks[].answers[].id | integer | ID ответа |
| tasks[].answers[].content | string | Текст ответа |
| tasks[].answers[].created_at | string | Дата создания |
| tasks[].answers[].image | object | Изображение ответа |
| tasks[].answers[].comment | string | Комментарий мастера |
| tasks[].answers[].comment_grade | integer | Оценка мастера (0-новый, 1-доработка, 2-решено) |
| tasks[].my_answers | array | Ответы ученика (при запросе с user_id) |
| task | object | Данные одной задачи (если запрошена по ID) |
| task.answers | array | Ответы на задачу |

**Ошибки:**
- `404 Not Found` — Мастер или задача не найдены
- `403 Forbidden` — Задача не принадлежит этому мастеру или ученик не принадлежит мастеру

---

### PATCH /master/task

Обновление задачи.

**Content-Type:** `application/json`

**Request:**
```json
{
  "task_id": 10,
  "title": "Обновлённый заголовок",
  "description": "Новое описание",
  "master_token": "master_token_abc",
  "image_ids": [4, 5]
}
```

**Поля запроса:**
| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| task_id | integer | Да | ID задачи для обновления |
| title | string | Нет | Новый заголовок |
| description | string | Нет | Новое описание |
| master_token | string | Да | Токен мастера |
| image_ids | array[int] | Нет | Дополнительные изображения |

**Response (200 OK):**
```json
{
  "status": "success",
  "task_id": 10,
  "title": "Обновлённый заголовок",
  "description": "Новое описание"
}
```

**Ошибки:**
- `404 Not Found` — Мастер или задача не найдены
- `403 Forbidden` — Задача не принадлежит этому мастеру

---

### POST /master/task/delete

Удаление задачи.

**Content-Type:** `application/json`

**Request:**
```json
{
  "task_id": 10,
  "master_token": "master_token_abc"
}
```

**Поля запроса:**
| Поле | Тип | Описание |
|------|-----|----------|
| task_id | integer | ID задачи для удаления |
| master_token | string | Токен мастера |

**Response (200 OK):**
```json
{
  "status": "success",
  "task_id": 10
}
```

**Ошибки:**
- `404 Not Found` — Мастер или задача не найдены
- `403 Forbidden` — Задача не принадлежит этому мастеру

---

## User/Answer

### POST /user/answer

Создание ответа на задачу.

**Content-Type:** `application/json`

**Request:**
```json
{
  "task_id": 10,
  "user_id": "user123",
  "content": "Мой ответ на задачу",
  "master_token": "master_token_abc",
  "image_id": 5
}
```

**Поля запроса:**
| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| task_id | integer | Да | ID задачи |
| user_id | string | Да | Токен пользователя |
| content | string | Да | Текст ответа |
| master_token | string | Да | Токен мастера (для проверки доступа) |
| image_id | integer | Нет | ID изображения ответа |

**Response (200 OK):**
```json
{
  "status": "success",
  "answer_id": 15,
  "task_id": 10,
  "content": "Мой ответ на задачу"
}
```

**Поля ответа:**
| Поле | Тип | Описание |
|------|-----|----------|
| status | string | Статус операции |
| answer_id | integer | ID нового ответа |
| task_id | integer | ID задачи |
| content | string | Текст ответа |

**Ошибки:**
- `404 Not Found` — Мастер, задача или пользователь не найдены
- `403 Forbidden` — Задача не принадлежит этому мастеру

---

### GET /user/answer

Получение ответов.

**Content-Type:** `application/json`

**Параметры запроса (Query Parameters):**
| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| master_token | string | Да | Токен мастера |
| task_id | integer | Нет | ID задачи для фильтрации |
| answer_id | integer | Нет | ID конкретного ответа |

**Примеры:**
```
GET /user/answer?master_token=master_token_abc
GET /user/answer?master_token=master_token_abc&task_id=10
GET /user/answer?master_token=master_token_abc&answer_id=15
```

**Response (список ответов, 200 OK):**
```json
{
  "status": "success",
  "answers": [
    {
      "id": 15,
      "task_id": 10,
      "content": "Мой ответ",
      "created_at": "2024-01-15 12:00:00",
      "image": {"id": 5, "path": "img/answer1.jpg"},
      "comment": "Хорошо",
      "comment_grade": 5
    }
  ]
}
```

**Response (один ответ, 200 OK):**
```json
{
  "status": "success",
  "answer": {
    "id": 15,
    "task_id": 10,
    "content": "Мой ответ",
    "created_at": "2024-01-15 12:00:00",
    "image": {"id": 5, "path": "img/answer1.jpg"},
    "comment": "Хорошо",
    "comment_grade": 5
  }
}
```

**Поля ответа:**
| Поле | Тип | Описание |
|------|-----|----------|
| status | string | Статус операции |
| answers | array | Список ответов |
| answers[].id | integer | ID ответа |
| answers[].task_id | integer | ID задачи |
| answers[].content | string | Текст ответа |
| answers[].created_at | string | Дата создания |
| answers[].image | object | Изображение ответа |
| answers[].comment | string | Комментарий мастера |
| answers[].comment_grade | integer | Оценка мастера |
| answer | object | Данные одного ответа (если запрошен по ID) |

**Ошибки:**
- `404 Not Found` — Мастер, задача или ответ не найдены
- `403 Forbidden` — Задача не принадлежит этому мастеру

---

### PATCH /user/answer

Обновление ответа (мастер может добавить комментарий и оценку).

**Content-Type:** `application/json`

**Request:**
```json
{
  "answer_id": 15,
  "content": "Обновлённый ответ",
  "image_id": 6,
  "comment": "Отличная работа!",
  "comment_grade": 5,
  "master_token": "master_token_abc"
}
```

**Поля запроса:**
| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| answer_id | integer | Да | ID ответа для обновления |
| content | string | Нет | Новый текст ответа |
| image_id | integer | Нет | Новое изображение |
| comment | string | Нет | Комментарий мастера |
| comment_grade | integer | Нет | Оценка мастера (1-5) |
| master_token | string | Да | Токен мастера |

**Response (200 OK):**
```json
{
  "status": "success",
  "answer_id": 15,
  "content": "Обновлённый ответ",
  "comment": "Отличная работа!",
  "comment_grade": 5
}
```

**Ошибки:**
- `404 Not Found` — Мастер или ответ не найдены
- `403 Forbidden` — Задача не принадлежит этому мастеру

---

### DELETE /user/answer

Удаление ответа.

**Content-Type:** `application/json`

**Request:**
```json
{
  "answer_id": 15,
  "master_token": "master_token_abc"
}
```

**Поля запроса:**
| Поле | Тип | Описание |
|------|-----|----------|
| answer_id | integer | ID ответа для удаления |
| master_token | string | Токен мастера |

**Response (200 OK):**
```json
{
  "status": "success",
  "answer_id": 15
}
```

**Ошибки:**
- `404 Not Found` — Мастер или ответ не найдены
- `403 Forbidden` — Задача не принадлежит этому мастеру

---

## Статические файлы

### Получение изображения

Новые изображения открываются напрямую по `image_url`, который возвращает backend после загрузки.
Старые записи с локальным `data/img/...` продолжают работать через backend для обратной совместимости.

---

### GET /data/files/{file_name}

Получение файла по имени.

**Пример:**
```
GET /data/files/550e8400-e29b-41d4-a716-446655440000.pdf
```

**Response:** Файл или 404 Not Found

---

## Структура базы данных

### User
| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | ID пользователя |
| token | string | Уникальный токен |
| full_name | string | Полное имя |
| is_master | boolean | true = мастер, false = ученик |
| master_id | integer | ID мастера (для учеников) |

### Task
| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | ID задачи |
| title | string | Заголовок |
| content | string | Описание |
| is_active | boolean | Активна ли |
| created_at | datetime | Дата создания |
| master_id | integer | ID мастера-владельца |
| user_id | integer | ID пользователя |

### Answer
| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | ID ответа |
| content | string | Текст ответа |
| image_id | integer | ID изображения |
| created_at | datetime | Дата создания |
| task_id | integer | ID задачи |
| comment | string | Комментарий мастера |
| comment_grade | integer | Оценка мастера |

### Image
| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | ID изображения |
| path | string | Путь к файлу |

### File
| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | ID файла |
| path | string | Путь к файлу |

### TaskImage
| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | ID записи |
| task_id | integer | ID задачи |
| image_id | integer | ID изображения |

### TaskFile
| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | ID записи |
| task_id | integer | ID задачи |
| file_id | integer | ID файла |

### AnswerImage
| Поле | Тип | Описание |
|------|-----|----------|
| id | integer | ID записи |
| answer_id | integer | ID ответа |
| image_id | integer | ID изображения |
