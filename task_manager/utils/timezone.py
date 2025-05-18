import logging
import pytz
from pytz.exceptions import UnknownTimeZoneError
from task_manager.task_manager.settings import TIME_ZONE

# Значение по умолчанию, если TIME_ZONE не задан или некорректен
DEFAULT_TIME_ZONE = 'UTC'

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)

def get_local_timezone() -> pytz.BaseTzInfo:
    """
    Возвращает локальную временную зону, указанную в настройках.
    Если временная зона не указана или указана некорректно, используется UTC.
    """
    timezone_name = TIME_ZONE or DEFAULT_TIME_ZONE
    try:
        return pytz.timezone(timezone_name)
    except (UnknownTimeZoneError, AttributeError, TypeError) as e:
        logger.warning(
            f"Некорректная настройка TIME_ZONE: '{timezone_name}'. Используется зона по умолчанию: '{DEFAULT_TIME_ZONE}'. Ошибка: {e}"
        )
        return pytz.timezone(DEFAULT_TIME_ZONE)
