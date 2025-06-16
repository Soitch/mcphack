import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import Config
from common.models import VacancyRequest
from fastmcp import MCPClient
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=Config.BOT_TOKEN)
        self.dp = Dispatcher()
        self.mcp_client = MCPClient(f"http://{Config.MCP_HOST}:{Config.MCP_PORT}")
        self.user_states = {}
        
        # Регистрация обработчиков
        self.dp.message(Command("start"))(self.start_handler)
        self.dp.message(Command("search"))(self.search_handler)
        self.dp.message(Command("status"))(self.status_handler)
        self.dp.message(F.text)(self.text_handler)

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
        """Обработка команды /start"""
        await message.answer(
            "👋 Привет! Я бот для поиска вакансий с HH.ru\n\n"
            "🔍 Используй команды:\n"
            "/search <запрос> - поиск вакансий\n"
            "/status - статус системы\n\n"
            "Или просто введи поисковый запрос"
        )

    async def status_handler(self, message: types.Message):
        """Проверка статуса системы"""
        try:
            status = await self.mcp_client.models.vacancy_manager.get_status()
            await message.answer(f"🟢 Система работает\n"
                                f"🔁 Активных агентов: {status['active_agents']}\n"
                                f"✅ Обработано запросов: {status['processed_requests']}")
        except Exception as e:
            logger.error(f"Ошибка получения статуса: {e}")
            await message.answer("🔴 Ошибка получения статуса системы")

    async def search_handler(self, message: types.Message):
        """Обработка команды /search"""
        query = message.text.split(maxsplit=1)
        if len(query) < 2:
            await message.answer("❌ Укажите поисковый запрос после команды\n"
                                "Пример: /search python разработчик")
            return
        
        await self.process_search(message.from_user.id, query[1], message)

    async def text_handler(self, message: types.Message):
        """Обработка текстовых сообщений"""
        if message.text.startswith('/'):
            return
            
        await self.process_search(message.from_user.id, message.text, message)

    async def process_search(self, user_id: int, query: str, message: types.Message):
        """Обработка поискового запроса"""
        # Показываем индикатор загрузки
        loading_msg = await message.answer(f"🔍 Ищем вакансии по запросу: {query}...")
        
        try:
            # Создаем запрос к MCP
            request = VacancyRequest(
                query=query,
                user_id=user_id
            )
            
            # Отправляем запрос в MCP-сервер
            response = await self.mcp_client.models.vacancy_manager.handle_request(request)
            
            if not response.vacancies:
                await loading_msg.edit_text("😕 По вашему запросу ничего не найдено")
                return
            
            # Отправляем результаты
            await loading_msg.delete()
            for vacancy in response.vacancies:
                await self.send_vacancy_message(message, vacancy)
                
        except Exception as e:
            logger.exception(f"Ошибка поиска: {e}")
            await loading_msg.edit_text("⚠️ Произошла ошибка при поиске вакансий")

    async def send_vacancy_message(self, message: types.Message, vacancy: dict):
        """Отправка сообщения с вакансией"""
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="📄 Открыть вакансию",
            url=vacancy.get('url', 'https://hh.ru')
        ))
        
        salary = vacancy.get('salary')
        if not salary or salary.lower() == 'не указана':
            salary_text = "ℹ️ Зарплата не указана"
        else:
            salary_text = f"💰 {salary}"
        
        text = (
            f"🏢 <b>{vacancy.get('title', 'Вакансия')}</b>\n"
            f"👨‍💼 Компания: {vacancy.get('company', 'Неизвестно')}\n"
            f"{salary_text}\n"
            f"📌 {vacancy.get('description', '')}\n"
            f"📍 {vacancy.get('address', 'Локация не указана')}"
        )
        
        await message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

    async def run(self):
        """Запуск бота"""
        if not await self.connect_to_mcp():
            logger.error("Не удалось подключиться к MCP-серверу. Завершение работы.")
            return
        
        await self.dp.start_polling(self.bot)