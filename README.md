# 🚀 Task Manager System

**Управление задачами с API, Telegram-ботом и автоматическими уведомлениями**

---

## 🌟 Основные возможности

### 📡 REST API (Django REST Framework)
- Создание и управление задачами
- Получение списка задач по пользователю
- Изменение статуса задач (выполнено/не выполнено)

### ⏰ Фоновые уведомления (Celery + Redis)
- Ежеминутная проверка приближающихся дедлайнов
- Автоматические уведомления в Telegram за 10 минут до дедлайна

### 🤖 Telegram Bot (aiogram)
- `/start` - Приветственное сообщение
- `/mytasks` - Список ваших активных задач
- `/done <ID>` - Отметить задачу как выполненную

---

## 🛠 Технологический стек

| Компонент       | Технологии                     |
|----------------|--------------------------------|
| Backend        | Django 4.2 + Django REST Framework |
| Асинхронные задачи | Celery 5.3 + Redis        |
| Telegram бот   | aiogram 3.x                    |
| База данных    | SQLite (по умолчанию) / PostgreSQL |

---

⚙️ Настройка и запуск
1. Настройка окружения
bash
python -m venv venv
# Linux/MacOS: source venv/bin/activate
# Windows: .\venv\Scripts\activate
Создайте файл .env с содержимым:

SECRET_KEY=ваш_секретный_ключ_django
TELEGRAM_TOKEN=токен_бота_от_BotFather
2. Установка зависимостей
pip install -r requirements.txt
3. Запуск системы
python manage.py migrate
python manage.py runserver
celery -A task_manager worker --loglevel=info --pool=eventlet -B
celery -A task_manager beat --loglevel=info
redis-server.exe
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

Получение задач пользователя

GET /api/tasks/?telegram_user_id=123456789

Изменение статуса

PATCH /api/tasks/<id>/

