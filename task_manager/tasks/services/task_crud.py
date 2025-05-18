# app/services/task_crud.py

import logging
from django.db import DatabaseError
from rest_framework.exceptions import APIException, ValidationError
from typing import Dict, Any
from ..models import Task
from .task_validation import normalize_deadline_input

logger = logging.getLogger(__name__)


def create_task(validated_data: Dict[str, Any]) -> Task:
    deadline = validated_data.pop('deadline_input', None)
    if deadline:
        validated_data['deadline'] = normalize_deadline_input(deadline)

    validated_data['status'] = Task.Status.UNDONE

    try:
        task = Task.objects.create(**validated_data)
    except DatabaseError as e:
        logger.exception(f"Ошибка при создании задачи: {e}")
        raise APIException("Не удалось создать задачу. Повторите попытку позже.")

    logger.info(f"Создана задача [ID:{task.id}] для TG user {task.telegram_user_id} со сроком {task.deadline}")
    return task


def update_task(instance: Task, validated_data: Dict[str, Any]) -> Task:
    deadline = validated_data.pop('deadline_input', None)
    if deadline:
        validated_data['deadline'] = normalize_deadline_input(deadline)

    changed = False
    for attr, value in validated_data.items():
        if getattr(instance, attr) != value:
            setattr(instance, attr, value)
            changed = True

    if not changed:
        logger.info(f"Обновление задачи ID {instance.id} не требуется — данные не изменились.")
        raise ValidationError({"detail": "Нет изменений для сохранения."})

    try:
        instance.save()
    except DatabaseError as e:
        logger.exception(f"Ошибка при обновлении задачи ID {instance.id}: {e}")
        raise APIException("Не удалось обновить задачу. Повторите попытку позже.")

    logger.info(f"Обновлена задача ID {instance.id}")
    return instance
