import logging
from typing import Optional, List, Dict
from datetime import datetime
from aiogram.filters import CommandObject
import pytz
import requests
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import BotCommand
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hbold
from aiogram import F, types
from django.utils.timezone import get_current_timezone as get_local_timezone


logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, api_url: str):
        self.bot = Bot(token=token)
        self.dp = Dispatcher(storage=MemoryStorage())
        self.api_url = api_url.rstrip('/')

        # Регистрация обработчиков
        self.dp.message.register(self._handle_start, Command('start'))
        self.dp.message.register(self._handle_mytasks, Command('mytasks'))
        self.dp.message.register(self._handle_done, Command('done'))

        self.dp.callback_query.register(self._handle_callbacks, F.data.startswith("show_my_tasks"))

    async def _get_user_tasks(self, user_id: int, status: str = None) -> Optional[List[Dict]]:
        """Получение задач пользователя из API"""
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
            logger.error(f"API request error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    async def _update_task_status(self, task_id: int) -> bool:
        """Обновление статуса задачи на 'done'"""
        try:
            response = requests.patch(
                f"{self.api_url}/tasks/{task_id}/",
                json={'status': 'done'},
                timeout=10
            )
            return response.ok
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

    async def _format_task(self, task: Dict) -> str:
        """Форматирование информации о задаче в читаемый вид.

        Args:
            task: Словарь с данными задачи из API

        Returns:
            Отформатированная строка с информацией о задаче или сообщение об ошибке

        Пример возвращаемого значения:
            <b>🔹 Название задачи</b>
            <u>Статус</u>: ✅ Выполнена
            <u>ID</u>: <code>42</code>
            <u>Дедлайн</u>: 20.05.2025 14:30
            <u>Описание</u>: Текст описания...
            ────────────────────
        """
        try:
            # 1. Обработка обязательных полей
            task_id = task.get('id', 'N/A')
            title = task.get('title', 'Без названия')

            # 2. Обработка статуса
            status = "✅ Выполнена" if task.get('status') == 'done' else "🕒 В работе"

            # 3. Обработка описания
            description = task.get('description') or "Нет описания"
            description = (description[:100] + "...") if len(description) > 100 else description

            # 4. Обработка дедлайна с защитой от ошибок
            deadline_text = "Не указан"
            if task.get('deadline'):
                try:
                    deadline_utc = datetime.fromisoformat(task['deadline']) if isinstance(task['deadline'], str) else \
                    task['deadline']
                    if not deadline_utc.tzinfo:
                        deadline_utc = pytz.UTC.localize(deadline_utc)

                    local_tz = get_local_timezone()
                    deadline_local = deadline_utc.astimezone(local_tz)
                    deadline_text = deadline_local.strftime('%d.%m.%Y %H:%M')
                except Exception as e:
                    logger.warning(f"Ошибка форматирования времени для задачи {task_id}: {e}")
                    deadline_text = f"Ошибка формата ({task['deadline']})"

            # 5. Формирование ответа
            return (
                f"<b>🔹 {title}</b>\n"
                f"<u>Статус</u>: {status}\n"
                f"<u>ID</u>: <code>{task_id}</code>\n"
                f"<u>Дедлайн</u>: {deadline_text}\n"
                f"<u>Описание</u>: {description}\n"
                "────────────────────"
            )
        except Exception as e:
            logger.error(f"Critical error formatting task {task.get('id')}: {e}")
            return (
                f"⚠️ Ошибка отображения задачи\n"
                f"ID: {task.get('id', 'unknown')}\n"
                f"Ошибка: {str(e)}"
            )

    async def _handle_start(self, message: types.Message):
        """Обработчик команды /start"""
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
    async def _handle_mytasks(self, message: types.Message):
        """Обработчик команды /mytasks"""
        tasks = await self._get_user_tasks(message.from_user.id)

        if tasks is None:
            await message.answer("⚠️ Произошла ошибка при получении задач. Попробуйте позже.")
            return

        if not tasks:
            await message.answer("📭 У вас пока нет задач!")
            return

        response_text = [f"{hbold('📋 Ваши задачи:')}\n"]
        for task in tasks:
            response_text.append(await self._format_task(task))

        # Разбиваем сообщение на части, если оно слишком длинное
        message_text = "\n\n".join(response_text)
        if len(message_text) > 4000:
            for part in [message_text[i:i + 4000] for i in range(0, len(message_text), 4000)]:
                await message.answer(part, parse_mode='HTML')
        else:
            await message.answer(message_text, parse_mode='HTML')

    async def _handle_callbacks(self, callback: types.CallbackQuery):
        """Обработчик всех callback-запросов"""
        try:
            await callback.answer()  # Убираем часики на кнопке

            if callback.data == "show_my_tasks":
                await self._handle_mytasks(callback.message)
                await callback.message.delete()

            elif callback.data == "delete_message":
                await callback.message.delete()

        except Exception as e:
            logger.error(f"Callback error: {str(e)}")
            await callback.answer("⚠️ Ошибка, попробуйте позже", show_alert=True)

    async def _show_done_usage(self, message: types.Message):
        """Показывает инструкцию по использованию /done"""
        msg = await message.answer(
            "✏️ <b>Как отметить задачу выполненной?</b>\n\n"
            "Используйте: <code>/done ID_задачи</code>\n\n"
            "Пример: <code>/done 42</code>\n\n"
            "Чтобы посмотреть ID задач, используйте /mytasks",
            parse_mode="HTML"
        )

    async def _show_invalid_id(self, message: types.Message):
        """Показывает сообщение о неверном ID"""
        msg = await message.answer(
            "🔢 <b>ID задачи должен быть числом!</b>\n\n"
            "Пример: <code>/done 42</code>",
            parse_mode="HTML"
        )

    async def _handle_done(self, message: types.Message, command: CommandObject):
        """Обработчик команды /done с современным подходом"""
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
            return await message.answer(
                "⚠️ <b>Ошибка сервера</b>\nПопробуйте позже",
                parse_mode="HTML"
            )

        await loading_msg.delete()

        if success:
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
        else:
            await message.answer(
                "❌ <b>Не удалось обновить задачу</b>\n\n"
                "Проверьте ID командой /mytasks",
                parse_mode="HTML"
            )

    async def setup_commands(self):
        """Настройка команд меню бота"""
        commands = [
            BotCommand(command="start", description="Начало работы"),
            BotCommand(command="mytasks", description="Мои задачи"),
            BotCommand(command="done", description="Отметить задачу выполненной"),
        ]
        await self.bot.set_my_commands(commands)

    async def run(self):
        """Запуск бота"""
        await self.setup_commands()
        logger.info("Bot started")
        await self.dp.start_polling(self.bot, skip_updates=True)