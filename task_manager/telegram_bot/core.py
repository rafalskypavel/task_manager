import logging
from datetime import datetime
from typing import Dict, List, Optional

import pytz
import requests
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold

from utils.timezone import get_local_timezone

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot for managing tasks with an external API."""

    def __init__(self, token: str, api_url: str) -> None:
        """Initialize the bot with token and API URL."""
        self.bot = Bot(token=token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.api_url = api_url.rstrip('/')

        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register all message and callback handlers."""
        self.dp.message.register(self._handle_start, Command('start'))
        self.dp.message.register(self._handle_mytasks, Command('mytasks'))
        self.dp.message.register(self._handle_done, Command('done'))
        self.dp.callback_query.register(
            self._handle_callbacks,
            F.data.startswith("show_my_tasks")
        )

    async def _get_user_tasks(self, user_id: int, status: Optional[str] = None) -> Optional[List[Dict]]:
        """Fetch user tasks from API.

        Args:
            user_id: Telegram user ID
            status: Optional task status filter

        Returns:
            List of tasks or None if error occurs
        """
        try:
            params = {'telegram_user_id': user_id}
            if status:
                params['status'] = status

            response = requests.get(
                f"{self.api_url}/tasks/",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error for user {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while fetching tasks: {e}")
            return None

    async def _update_task_status(self, task_id: int) -> bool:
        """Update task status to 'done'.

        Args:
            task_id: ID of the task to update

        Returns:
            True if update was successful, False otherwise
        """
        try:
            response = requests.patch(
                f"{self.api_url}/tasks/{task_id}/",
                json={'status': 'done'},
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error for task {task_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while updating task {task_id}: {e}")
            return False

    async def _format_task(self, task: Dict) -> str:
        """Format task data into a readable string.

        Args:
            task: Task dictionary with task data

        Returns:
            Formatted string with task information
        """
        try:
            task_id = task['id']
            title = task['title']
            status = "✅ Выполнена" if task.get('status') == 'done' else "🕒 В работе"
            description = (task.get('description') or "Нет описания")[:100] + "..." if len(
                task.get('description', '')
            ) > 100 else (task.get('description') or "Нет описания")

            deadline_text = "Не указан"
            if task.get('deadline'):
                try:
                    deadline_utc = (
                        datetime.fromisoformat(task['deadline'])
                        if isinstance(task['deadline'], str)
                        else task['deadline']
                    )
                    if not deadline_utc.tzinfo:
                        deadline_utc = pytz.UTC.localize(deadline_utc)

                    local_tz = get_local_timezone()
                    deadline_local = deadline_utc.astimezone(local_tz)
                    deadline_text = deadline_local.strftime('%d.%m.%Y %H:%M')
                except Exception as e:
                    logger.warning(f"Time formatting error for task {task_id}: {e}")
                    deadline_text = f"Ошибка формата ({task['deadline']})"

            return (
                f"<b>🔹 {title}</b>\n"
                f"<u>Статус</u>: {status}\n"
                f"<u>ID</u>: <code>{task_id}</code>\n"
                f"<u>Дедлайн</u>: {deadline_text}\n"
                f"<u>Описание</u>: {description}\n"
                "────────────────────"
            )
        except KeyError as e:
            logger.error(f"Missing required field in task {task.get('id')}: {e}")
            return (
                f"⚠️ Ошибка отображения задачи\n"
                f"ID: {task.get('id', 'unknown')}\n"
                f"Отсутствует обязательное поле: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Critical error formatting task {task.get('id')}: {e}")
            return (
                f"⚠️ Ошибка отображения задачи\n"
                f"ID: {task.get('id', 'unknown')}\n"
                f"Ошибка: {str(e)}"
            )

    async def _handle_start(self, message: types.Message) -> None:
        """Handle /start command."""
        welcome_text = (
            "<b>🚀 Task Manager Bot</b>\n\n"
            "Этот бот поможет вам управлять вашими задачами:\n"
            "• Создавать и просматривать задачи\n"
            "• Отслеживать сроки выполнения\n"
            "• Отмечать выполненные задачи\n\n"
            "<u>Доступные команды</u>:\n"
            "/mytasks - Показать все ваши задачи\n"
            "/done &lt;ID&gt; - Отметить задачу выполненной\n\n"
            "Задачи создаются через веб-интерфейс или API."
        )
        await message.answer(welcome_text, parse_mode='HTML')

    async def _handle_mytasks(self, message: types.Message) -> None:
        """Handle /mytasks command."""
        user_id = message.from_user.id
        tasks = await self._get_user_tasks(user_id)

        if tasks is None:
            await message.answer("⚠️ Произошла ошибка при получении задач. Попробуйте позже.")
            return

        if not tasks:
            await message.answer("📭 У вас пока нет задач!")
            return

        response_parts = [f"{hbold('📋 Ваши задачи:')}\n"]
        response_parts.extend([await self._format_task(task) for task in tasks])
        full_response = "\n\n".join(response_parts)

        # Split long messages
        max_length = 4000
        if len(full_response) > max_length:
            for i in range(0, len(full_response), max_length):
                await message.answer(
                    full_response[i:i + max_length],
                    parse_mode='HTML'
                )
        else:
            await message.answer(full_response, parse_mode='HTML')

    async def _handle_callbacks(self, callback: types.CallbackQuery) -> None:
        """Handle all callback queries."""
        try:
            await callback.answer()  # Acknowledge the callback

            if callback.data == "show_my_tasks":
                await self._handle_mytasks(callback.message)
                await callback.message.delete()
            elif callback.data == "delete_message":
                await callback.message.delete()

        except Exception as e:
            logger.error(f"Callback error: {str(e)}")
            await callback.answer("⚠️ Ошибка, попробуйте позже", show_alert=True)

    async def _show_done_usage(self, message: types.Message) -> None:
        """Show instructions for /done command."""
        await message.answer(
            "✏️ <b>Как отметить задачу выполненной?</b>\n\n"
            "Используйте: <code>/done ID_задачи</code>\n\n"
            "Пример: <code>/done 42</code>\n\n"
            "Чтобы посмотреть ID задач, используйте /mytasks",
            parse_mode="HTML"
        )

    async def _show_invalid_id(self, message: types.Message) -> None:
        """Show invalid ID message."""
        await message.answer(
            "🔢 <b>ID задачи должен быть числом!</b>\n\n"
            "Пример: <code>/done 42</code>",
            parse_mode="HTML"
        )

    async def _handle_done(self, message: types.Message, command: CommandObject) -> None:
        """Handle /done command."""
        if not command.args:
            return await self._show_done_usage(message)

        try:
            task_id = int(command.args.strip())
        except ValueError:
            return await self._show_invalid_id(message)

        loading_msg = await message.answer("⏳ Обновляем статус задачи...")

        try:
            success = await self._update_task_status(task_id)
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}")
            await loading_msg.delete()
            await message.answer(
                "⚠️ <b>Ошибка сервера</b>\nПопробуйте позже",
                parse_mode="HTML"
            )
            return

        await loading_msg.delete()

        if not success:
            await message.answer(
                "❌ <b>Не удалось обновить задачу</b>\n\n"
                "Проверьте ID командой /mytasks",
                parse_mode="HTML"
            )
            return

        builder = InlineKeyboardBuilder()
        builder.row(
            types.InlineKeyboardButton(
                text="🔍 Посмотреть задачи",
                callback_data="show_my_tasks"
            ),
            types.InlineKeyboardButton(
                text="✅ Готово",
                callback_data="delete_message"
            )
        )

        await message.answer(
            f"✅ <b>Задача ID {task_id} выполнена!</b>",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

    async def setup_commands(self) -> None:
        """Set up bot commands menu."""
        commands = [
            BotCommand(command="start", description="Начало работы"),
            BotCommand(command="mytasks", description="Мои задачи"),
            BotCommand(command="done", description="Отметить задачу выполненной"),
        ]
        await self.bot.set_my_commands(commands)

    async def run(self) -> None:
        """Run the bot."""
        await self.setup_commands()
        logger.info("Starting bot...")
        await self.dp.start_polling(self.bot, skip_updates=True)