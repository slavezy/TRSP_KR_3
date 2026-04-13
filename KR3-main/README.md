# Контрольная работа №3 — FastAPI

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Задания и запуск

Каждое задание находится в отдельной папке. Запускать из корня репозитория:

| Задание | Папка | Команда |
|---------|-------|---------|
| 6.1 | 6.1 | `uvicorn 6.1.main:app --reload` |
| 6.2 | 6.2 | `uvicorn 6.2.main:app --reload` |
| 6.3 | 6.3 | `uvicorn 6.3.main:app --reload` |
| 6.4 | 6.4 | `uvicorn 6.4.main:app --reload` |
| 6.5 | 6.5 | `uvicorn 6.5.main:app --reload` |
| 7.1 | 7.1 | `uvicorn 7.1.main:app --reload` |
| 8.1 | 8.1 | `uvicorn 8.1.main:app --reload` |
| 8.2 | 8.2 | `uvicorn 8.2.main:app --reload` |

---

## Переменные окружения (Задание 6.3)

Скопируйте `.env.example` в `.env` и задайте значения:

```bash
cp .env.example .env
```

```
MODE=DEV          # DEV или PROD
DOCS_USER=admin
DOCS_PASSWORD=secret
```

---

## Тестирование эндпоинтов (curl)

### Задание 6.1 — Basic Auth GET /login
```bash
# Успешный логин
curl -u admin:secret http://localhost:8000/login

# Неверный пароль
curl -u admin:wrong http://localhost:8000/login
```

### Задание 6.2 — Регистрация + хеширование паролей
```bash
# Регистрация
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"correctpass"}' \
  http://localhost:8000/register

# Успешный логин
curl -u user1:correctpass http://localhost:8000/login

# Неверный пароль
curl -u user1:wrongpass http://localhost:8000/login
```

### Задание 6.3 — Docs с авторизацией (DEV/PROD)
```bash
# DEV: открыть документацию (нужен логин/пароль)
curl -u admin:secret http://localhost:8000/docs

# PROD: всё возвращает 404
curl http://localhost:8000/docs
```

### Задание 6.4 — JWT авторизация
```bash
# Логин (иногда 401 — stub рандомный)
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"securepassword123"}' \
  http://localhost:8000/login

# Доступ к защищённому ресурсу
curl -H "Authorization: Bearer <token>" http://localhost:8000/protected_resource
```

### Задание 6.5 — JWT + регистрация + rate limit
```bash
# Регистрация
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8000/register

# Логин
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"qwerty123"}' \
  http://localhost:8000/login

# Защищённый ресурс
curl -H "Authorization: Bearer <token>" http://localhost:8000/protected_resource
```

### Задание 7.1 — RBAC (роли)
```bash
# Логин под admin
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"admin_user","password":"adminpass"}' \
  http://localhost:8000/login

# Создать ресурс (только admin)
curl -X POST -H "Authorization: Bearer <token>" http://localhost:8000/resources

# Прочитать (доступно всем ролям)
curl -H "Authorization: Bearer <token>" http://localhost:8000/resources

# Удалить (только admin)
curl -X DELETE -H "Authorization: Bearer <token>" http://localhost:8000/resources/1
```

### Задание 8.1 — SQLite /register
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"test_user","password":"12345"}' \
  http://localhost:8000/register
```

### Задание 8.2 — Todo CRUD
```bash
# Создать todo
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread"}' \
  http://localhost:8000/todos

# Получить todo по id
curl http://localhost:8000/todos/1

# Обновить todo
curl -X PUT -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread","completed":true}' \
  http://localhost:8000/todos/1

# Удалить todo
curl -X DELETE http://localhost:8000/todos/1
```
