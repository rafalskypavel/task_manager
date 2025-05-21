# 🚀 Task Manager System

Универсальное приложение для управления задачами с REST API, Telegram-ботом и фоновыми задачами через Celery.

---

## 🌟 Основные функции

- **REST API (Django REST Framework)**  
  - CRU-операции с задачами  
  - Фильтрация задач по `telegram_user_id`

- **Фоновая обработка (Celery + Redis)**  
  - Проверка дедлайнов каждую минуту  
  - Уведомление за 10 минут до дедлайна

- **Telegram-бот**  
  Команды:
  - `/start` — Приветствие  
  - `/mytasks` — Список задач  
  - `/done <ID>` — Отметить задачу как выполненную

---

## ⚙️ Настройка

1. **Создайте и активируйте виртуальное окружение**:

   ```bash
   python -m venv venv
   .\venv\Scripts\activate   # Windows
   source venv/bin/activate     # macOS/Linux
   ```

2. **Установите зависимости**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Настройте файл `.env`**:

   ```env
   SECRET_KEY=ваш_ключ
   TELEGRAM_TOKEN=токен_бота
   ```

---

## 🚀 Запуск проекта

Откройте **несколько терминалов** и выполните команды по очереди:

**1. Запустите Django-сервер**:

```bash
python manage.py migrate
python manage.py runserver
```

**2. Запустите Redis-сервер**:

```bash
redis-server.exe
```

**3. Запустите Celery (beat + worker)**:

```bash
celery -A task_manager beat --loglevel=info
celery -A task_manager worker --loglevel=info --pool=eventlet -B
```

**4. Запустите Telegram-бота**:

```bash
python bot.py
```

---

## 📡 API Документация

- **Создать задачу**

  `POST /api/tasks/`

  ```json
  {
    "title": "Тест",
    "deadline": "2023-12-31T23:59:00",
    "telegram_user_id": 123456789
  }
  ```

- **Получить задачи по пользователю**

  `GET /api/tasks/?telegram_user_id=123456789`

- **Обновить статус задачи**

  `PATCH /api/tasks/<id>/`

  ```json
  {
    "status": "done"
  }
  ```

---
