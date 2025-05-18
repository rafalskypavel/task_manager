import os
import asyncio
import logging
import django
from django.conf import settings
from core import TelegramBot

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_manager.settings')
django.setup()

logger = logging.getLogger(__name__)

def start_bot():
    """Запуск бота с настройками из Django"""
    try:
        bot = TelegramBot(
            token=settings.TELEGRAM_BOT_TOKEN,
            api_url=settings.API_URL
        )
        asyncio.run(bot.run())
    except Exception as e:
        logger.critical(f"Ошибка при запуске бота: {str(e)}")
        raise

if __name__ == '__main__':
    start_bot()