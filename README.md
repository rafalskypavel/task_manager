markdown
# 🚀 Task Manager System

**Управление задачами с API, Telegram-ботом и автоматическими уведомлениями**

---

## 🌟 Основные возможности

### 📡 REST API (Django REST Framework)
- ✅ Создание и управление задачами
- 📋 Получение списка задач по пользователю
- 🔄 Изменение статуса задач (выполнено/не выполнено)

### ⏰ Фоновые уведомления (Celery + Redis)
- 🔍 Ежеминутная проверка дедлайнов
- 🔔 Автоматические уведомления в Telegram за 10 минут до дедлайна

### 🤖 Telegram Bot (aiogram)
- `/start` - Приветственное сообщение
- `/mytasks` - Список активных задач
- `/done <ID>` - Отметить задачу выполненной

---

## 🛠 Технологический стек

| Компонент       | Технологии                     |
|----------------|-------------------------------|
| Backend        | Django 4.2 + DRF              |
| Очереди задач  | Celery 5.3 + Redis            |
| Telegram бот   | aiogram 3.x                   |
| БД             | SQLite / PostgreSQL           |

---

## ⚙️ Настройка и запуск

### 1. Настройка окружения
```bash
# Создание и активация окружения
python -m venv venv
source venv/bin/activate  # Linux/MacOS
.\venv\Scripts\activate   # Windows
Добавьте свои данные в .env файл:

ini
SECRET_KEY=your_django_secret_key
TELEGRAM_TOKEN=your_bot_token_from_BotFather
2. Установка зависимостей
bash
pip install -r requirements.txt
3. Запуск системы
bash
# Миграции и сервер
python manage.py migrate
python manage.py runserver

# Celery и Redis
celery -A task_manager worker -l info -P eventlet -B
celery -A task_manager beat -l info
redis-server

# Telegram бот
python bot.py
📚 Документация API
Создание задачи
POST /api/tasks/

json
{
  "title": "Завершить проект",
  "description": "Доделать все задачи",
  "deadline": "2023-12-31T23:59:00",
  "telegram_user_id": 123456789
}
Получение задач
GET /api/tasks/?telegram_user_id=123456789

Изменение статуса
PATCH /api/tasks/<id>/

json
{
  "status": "done"
}
