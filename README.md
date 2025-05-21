markdown
# 🚀 Task Manager System

## 🌟 Основные функции
- **REST API** (DRF): CRUD задач + фильтрация по пользователю  
- **Celery+Redis**: Проверка дедлайнов каждую минуту + уведомления за 10 мин  
- **Telegram Bot**:  
  `/start` - Приветствие  
  `/mytasks` - Список задач  
  `/done <ID>` - Отметить выполненной  

## ⚡ Настройка
# 1. Создайте и активируйте venv
python -m venv venv
.\venv\Scripts\activate  # Windows

# 2. Установите зависимости
pip install -r requirements.txt

# 3. Настройте .env
SECRET_KEY=ваш_ключ
TELEGRAM_TOKEN=токен_бота

🚀 Запуск
# В разных терминалах:
python manage.py migrate && python manage.py runserver  # Django
redis-server.exe 
celery -A task_manager beat --loglevel=info
celery -A task_manager worker --loglevel=info --pool=eventlet -B
python bot.py  # Telegram Bot

📡 API Документация
POST /api/tasks/ - Создать задачу
json
{
  "title": "Тест",
  "deadline": "2023-12-31T23:59:00",
  "telegram_user_id": 123456789
}
GET /api/tasks/?telegram_user_id=123456789 - Получить задачи
PATCH /api/tasks/<id>/ - Обновить статус
json
{"status": "done"}
