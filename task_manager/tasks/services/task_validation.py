# app/services/task_validation.py

import logging
import pytz
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from task_manager import settings
from ..models import Task

logger = logging.getLogger(__name__)


def validate_status_or_raise(value: str, current_status: str = None) -> str:
    allowed_choices = Task.Status.choices
    allowed_values = [choice[0] for choice in allowed_choices]

    if value not in allowed_values:
        choices_display = ", ".join([f"{choice[0]} ({choice[1]})" for choice in allowed_choices])
        error_msg = f"Недопустимый статус: {value}. Допустимые значения: {choices_display}"
        logger.warning(f"Валидация статуса не пройдена: {error_msg}")
        raise ValidationError({"status": [error_msg]})

    if current_status is not None and value == current_status:
        info_msg = f"Статус уже установлен в '{value}'. Обновление не требуется."
        logger.info(info_msg)
        raise ValidationError({"status": [info_msg]})

    return value


def normalize_deadline_input(value: any) -> any:
    if timezone.is_naive(value):
        value = pytz.timezone(settings.TIME_ZONE).localize(value)
    value = value.astimezone(pytz.UTC)

    now = timezone.now()
    if value < now:
        error_msg = "Срок выполнения не может быть в прошлом"
        logger.warning(f"Валидация дедлайна не пройдена: {error_msg} (введено: {value}, сейчас: {now})")
        raise ValidationError({"deadline": [error_msg]})

    return value


def validate_telegram_user_id(value: int) -> int:
    if not (0 < value <= 2 ** 63 - 1):
        error_msg = "ID пользователя Telegram должен быть положительным числом"
        logger.warning(f"Валидация telegram_user_id не пройдена: {error_msg} (введено: {value})")
        raise ValidationError({"telegram_user_id": [error_msg]})
    return value
