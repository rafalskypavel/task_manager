# app/services/task_status.py

import logging
from django.db import transaction, DatabaseError
from rest_framework.exceptions import APIException
from ..models import Task
from .task_validation import validate_status_or_raise

logger = logging.getLogger(__name__)


def update_task_status(task: Task, new_status: str) -> Task:
    """
    Обновляет статус задачи, если он изменился и новый статус валиден.
    """
    validate_status_or_raise(new_status, current_status=task.status)

    old_status = task.status

    try:
        with transaction.atomic():
            task.status = new_status
            task.save(update_fields=['status'])
    except DatabaseError as e:
        logger.exception(f"Ошибка при обновлении статуса задачи ID {task.id}: {e}")
        raise APIException("Не удалось обновить статус задачи. Повторите попытку позже.")

    logger.info("Статус задачи ID %s обновлён: '%s' → '%s'", task.id, old_status, new_status)
    return task
