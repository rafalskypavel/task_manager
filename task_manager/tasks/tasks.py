from celery import shared_task
from django.utils import timezone
from datetime import timedelta, datetime

from task_manager.settings import TIME_ZONE
from .models import Task
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def check_deadlines(self):
    now = timezone.now()  # Уже в UTC благодаря USE_TZ=True
    soon_deadline = now + timedelta(minutes=10)

    tasks = Task.objects.filter(
        status=Task.Status.UNDONE,
        deadline__range=(now, soon_deadline),  # Сравнение в UTC
        notification_sent=False
    )

    logger.info(f"Сформированный SQL-запрос: {str(tasks.query)}")

    found_tasks = list(tasks)  # Выполняем запрос
    logger.info(f"Найдено задач: {len(found_tasks)}")

    for task in found_tasks:
        logger.info(f"Обработка задачи ID {task.id}: {task.title} (дедлайн: {task.deadline})")
        send_telegram_notification.delay(
            task_id=task.id,
            chat_id=task.telegram_user_id,
            task_title=task.title,
            deadline=task.deadline.isoformat()
        )
        task.notification_sent = True
        task.save()

    return f"Checked {len(found_tasks)} tasks"


@shared_task(bind=True, max_retries=3)
def send_telegram_notification(self, task_id, chat_id, task_title, deadline):
    try:
        # deadline указан в UTC!, пример deadline: 2025-05-21T17:12:00+00:00

        # deadline_dt форматирует из "2025-05-21T17:12:00+00:00" в "2025-05-21 17:12:00+00:00"
        deadline_dt = datetime.fromisoformat(deadline) if isinstance(deadline, str) else deadline

        # здесь уже переводим в локальное время (настрйка локальной зоны в .env)
        local_deadline = deadline_dt.astimezone(TIME_ZONE)

        # formatted_deadline форматирует из "2025-05-21 20:12:00+03:00" в "21.05.2025 20:12"
        formatted_deadline = local_deadline.strftime('%d.%m.%Y %H:%M')

        message = (
            f"⏰ *Напоминание о задаче*\n"
            f"*{task_title}*\n"
            f"Дедлайн: {formatted_deadline}\n"
            f"Осталось менее 10 минут!\n"
            f"ID: {task_id}"
        )

        resp = requests.post(
            f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            },
            timeout=10
        )
        resp.raise_for_status()
        return f"Notification sent to {chat_id}"
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        raise self.retry(exc=e, countdown=60)