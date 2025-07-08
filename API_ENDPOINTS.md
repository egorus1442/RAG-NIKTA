# RAG API - Документация эндпоинтов

## Аутентификация

Все эндпоинты требуют заголовок аутентификации:
```
Authorization: Bearer <API_TOKEN>
```

---

## POST /upload

**Загружает файл, извлекает текст и сохраняет эмбединги в векторную базу данных.**

### Параметры запроса
- **Content-Type:** `multipart/form-data`
- **file:** Файл для загрузки (PDF, DOCX, TXT)

### Поддерживаемые форматы
- PDF (.pdf)
- DOCX (.docx)
- TXT (.txt)

### Пример запроса
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer rag_api_secret_token_2024" \
  -F "file=@document.pdf"
```

### Ответ
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "document.pdf",
  "chunks_count": 5,
  "message": "Файл успешно загружен и обработан"
}
```

### Коды ответов
- **200 OK** - Файл успешно загружен
- **400 Bad Request** - Неподдерживаемый формат файла
- **401 Unauthorized** - Неверный API токен
- **500 Internal Server Error** - Ошибка обработки файла

---

## POST /query

**Выполняет семантический поиск по документам и генерирует ответ на основе найденного контекста.**

### Параметры запроса
- **Content-Type:** `application/json`

### Тело запроса
```json
{
  "question": "Ваш вопрос здесь"
}
```

### Пример запроса
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer rag_api_secret_token_2024" \
  -H "Content-Type: application/json" \
  -d '{"question": "Что такое машинное обучение?"}'
```

### Ответ
```json
{
  "answer": "Машинное обучение - это подраздел искусственного интеллекта...",
  "context_documents": [
    {
      "document": "Фрагмент текста из документа...",
      "metadata": {
        "file_id": "550e8400-e29b-41d4-a716-446655440000",
        "chunk_index": 0,
        "chunk_size": 1000,
        "filename": "document.pdf"
      },
      "distance": 0.123
    }
  ],
  "question": "Что такое машинное обучение?"
}
```

### Коды ответов
- **200 OK** - Ответ успешно сгенерирован
- **401 Unauthorized** - Неверный API токен
- **500 Internal Server Error** - Ошибка генерации ответа

---

## DELETE /file/{file_id}

**Удаляет файл с диска и его эмбединги из векторной базы данных.**

### Параметры пути
- **file_id:** Уникальный идентификатор файла (UUID)

### Пример запроса
```bash
curl -X DELETE "http://localhost:8000/file/550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Bearer rag_api_secret_token_2024"
```

### Ответ
```json
{
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Файл успешно удален"
}
```

### Коды ответов
- **200 OK** - Файл успешно удален
- **401 Unauthorized** - Неверный API токен
- **404 Not Found** - Файл не найден
- **500 Internal Server Error** - Ошибка удаления

---

## GET /health

**Проверяет состояние API и доступность сервисов.**

### Параметры запроса
Нет

### Пример запроса
```bash
curl -X GET "http://localhost:8000/health"
```

### Ответ
```json
{
  "status": "healthy",
  "message": "RAG API работает"
}
```

### Коды ответов
- **200 OK** - API работает нормально
- **500 Internal Server Error** - Проблемы с API

---

## Обработка ошибок

Все эндпоинты возвращают ошибки в едином формате:

```json
{
  "error": "Описание ошибки",
  "detail": "Дополнительная информация об ошибке"
}
```

### Общие коды ошибок
- **400 Bad Request** - Неверные параметры запроса
- **401 Unauthorized** - Неверная аутентификация
- **404 Not Found** - Ресурс не найден
- **500 Internal Server Error** - Внутренняя ошибка сервера 