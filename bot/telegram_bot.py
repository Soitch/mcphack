#telegram_bot.py

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import Config
import asyncio
import aiohttp
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=Config.BOT_TOKEN)
        self.dp = Dispatcher()
        
        self.dp.message(Command("start"))(self.start_handler)
        self.dp.message(Command("search"))(self.search_handler)
        self.dp.message(Command("status"))(self.status_handler)
        self.dp.message(Command("help"))(self.help_handler)

    async def start_handler(self, message: types.Message):
        await message.answer(
            "👋 Привет! Я бот для поиска вакансий с HH.ru\n\n"
            "🔍 Используй команды:\n"
            "/search <запрос> - поиск вакансий\n"
            "/status - статус системы\n"
            "/help - помощь"
        )

    async def help_handler(self, message: types.Message):
        await message.answer(
            "📖 Доступные команды:\n\n"
            "/search <запрос> - поиск вакансий\n"
            "Пример: /search python разработчик\n\n"
            "/status - проверка статуса системы\n"
            "/help - показать это сообщение"
        )

    async def search_handler(self, message: types.Message):
        query = message.text.split(maxsplit=1)
        if len(query) < 2:
            await message.answer("❌ Укажите поисковый запрос после команды\n"
                                "Пример: /search python разработчик")
            return
        
        await message.answer(f"🔍 Ищем вакансии по запросу: {query[1]}...")
        
        try:
            # Имитация поиска без MCP
            vacancies = [
                {
                    "title": "Python Developer",
                    "company": "ТехноЛогика",
                    "salary": "150 000 - 200 000 руб.",
                    "url": "https://hh.ru/vacancy/12345",
                    "description": "Разработка backend на Python"
                },
                {
                    "title": "Data Scientist",
                    "company": "АналитикаПро",
                    "salary": "180 000 - 250 000 руб.",
                    "url": "https://hh.ru/vacancy/67890",
                    "description": "Анализ данных и машинное обучение"
                }
            ]
            
            for vacancy in vacancies:
                await message.answer(
                    f"🏢 <b>{vacancy['title']}</b>\n"
                    f"👨‍💼 Компания: {vacancy['company']}\n"
                    f"💰 Зарплата: {vacancy['salary']}\n"
                    f"📝 {vacancy['description']}\n"
                    f"🔗 <a href='{vacancy['url']}'>Подробнее</a>",
                    parse_mode="HTML"
                )
                
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}", exc_info=True)
            await message.answer("⚠️ Произошла ошибка при поиске вакансий")

    async def status_handler(self, message: types.Message):
        """Статус системы"""
        await message.answer(
            "🟠 Система работает в автономном режиме\n\n"
            "MCP сервер: не подключен\n"
            "Агенты: не активны\n"
            "Режим: тестовый\n\n"
            "Используйте /search для тестового поиска"
        )

    async def run(self):
        """Запуск бота"""
        logger.info("Запуск Telegram бота в автономном режиме")
        await self.dp.start_polling(self.bot)