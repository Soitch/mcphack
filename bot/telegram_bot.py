#telegram_bot.py

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from fastmcp import Client
from config import Config
from models.schemas import VacancyRequest
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=Config.BOT_TOKEN)
        self.dp = Dispatcher()
        self.mcp_client = Client(f"http://{Config.MCP_HOST}:{Config.MCP_PORT}")
        
        self.dp.message(Command("start"))(self.start_handler)
        self.dp.message(Command("search"))(self.search_handler)
        self.dp.message(Command("status"))(self.status_handler)

    async def connect_to_mcp(self):
        """Подключение к MCP-серверу"""
        max_retries = 5
        for i in range(max_retries):
            try:
                await self.mcp_client.connect()
                logger.info("Успешное подключение к MCP-серверу")
                return True
            except Exception as e:
                logger.error(f"Ошибка подключения к MCP ({i+1}/{max_retries}): {e}")
                await asyncio.sleep(2)
        return False

    async def start_handler(self, message: types.Message):
        await message.answer(
            "👋 Привет! Я бот для поиска вакансий с HH.ru\n\n"
            "🔍 Используй команды:\n"
            "/search <запрос> - поиск вакансий\n"
            "/status - статус системы"
        )

    async def search_handler(self, message: types.Message):
        query = message.text.split(maxsplit=1)
        if len(query) < 2:
            await message.answer("❌ Укажите поисковый запрос после команды\n"
                                "Пример: /search python разработчик")
            return
        
        await message.answer(f"🔍 Ищем вакансии по запросу: {query[1]}...")
        
        try:
            # Отправляем запрос в MCP-сервер
            request = VacancyRequest(
                query=query[1],
                user_id=message.from_user.id
            )
            
            # Вызов метода через MCP Client
            response = await self.mcp_client.call(
                "handle_request",
                **request.model_dump()
            )
            
            for vacancy in response.get("vacancies", []):
                await message.answer(
                    f"🏢 <b>{vacancy.get('title', 'Вакансия')}</b>\n"
                    f"👨‍💼 Компания: {vacancy.get('company', 'Неизвестно')}\n"
                    f"💰 Зарплата: {vacancy.get('salary', 'Не указана')}\n"
                    f"🔗 <a href='{vacancy.get('url', '#')}'>Подробнее</a>",
                    parse_mode="HTML"
                )
                
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}", exc_info=True)
            await message.answer("⚠️ Произошла ошибка при поиске вакансий")

    async def status_handler(self, message: types.Message):
        """Проверка статуса системы"""
        try:
            status = await self.mcp_client.call("get_status")
            await message.answer(
                f"🟢 Система работает\n"
                f"⏱ Uptime: {status.get('uptime', 0)} сек\n"
                f"🤖 Активных агентов: {status.get('active_agents', 0)}\n"
                f"📊 Запросов в очереди: {status.get('queue_size', 0)}"
            )
        except Exception as e:
            logger.error(f"Ошибка проверки статуса: {e}")
            await message.answer("🚫 Не удалось проверить статус системы")

    async def run(self):
        """Запуск бота"""
        if not await self.connect_to_mcp():
            logger.error("Не удалось подключиться к MCP-серверу. Завершение работы.")
            return
        
        await self.dp.start_polling(self.bot)