# mcp_server.py

from fastmcp import FastMCP, Request
from agents.hh_parser import HHParser
from models.schemas import VacancyRequest, VacancyResponse
import uuid
import asyncio
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

app = FastMCP()

class VacancyAgentManager:
    def __init__(self):
        self.active_agents = []
        self.task_queue = asyncio.Queue()
        self.results = {}
        self.processed_requests = 0
        self.start_time = time.time()
        self.dispatcher_task = None

    async def start(self):
        """Запуск диспетчера задач"""
        self.dispatcher_task = asyncio.create_task(self.task_distributor())
        logger.info("Диспетчер задач запущен")

    async def register_agent(self, agent_id: str):
        if agent_id not in self.active_agents:
            self.active_agents.append(agent_id)
            logger.info(f"Агент {agent_id} зарегистрирован")
        return {"status": "success"}

    async def handle_request(self, request: VacancyRequest):
        request_id = str(uuid.uuid4())
        await self.task_queue.put((request_id, request))
        logger.info(f"Получен запрос {request_id} от пользователя {request.user_id}")
        return await self.wait_for_result(request_id)

    async def task_distributor(self):
        """Распределение задач по агентам"""
        logger.info("Диспетчер задач начал работу")
        while True:
            request_id, request = await self.task_queue.get()
            logger.info(f"Обработка запроса {request_id}: {request.query}")
            asyncio.create_task(self.process_request(request_id, request))

    async def process_request(self, request_id: str, request: VacancyRequest):
        """Обработка запроса"""
        try:
            parser = HHParser()
            vacancies = await parser.fetch_vacancies(request.query)
            self.results[request_id] = VacancyResponse(
                vacancies=vacancies,
                user_id=request.user_id,
                request_id=request_id
            )
            self.processed_requests += 1
            logger.info(f"Запрос {request_id} успешно обработан")
        except Exception as e:
            logger.error(f"Ошибка обработки запроса {request_id}: {e}")
            self.results[request_id] = VacancyResponse(
                vacancies=[],
                user_id=request.user_id,
                request_id=request_id
            )

    async def wait_for_result(self, request_id: str, timeout: int = 30):
        """Ожидание результата"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if request_id in self.results:
                return self.results.pop(request_id)
            await asyncio.sleep(0.5)
        return VacancyResponse(vacancies=[], user_id=0, request_id=request_id)

    async def get_status(self):
        """Получение статуса системы"""
        return {
            "status": "running",
            "uptime": int(time.time() - self.start_time),
            "active_agents": len(self.active_agents),
            "queue_size": self.task_queue.qsize(),
            "processed_requests": self.processed_requests
        }

# Инициализация менеджера
manager = VacancyAgentManager()

# Регистрация методов FastMCP
@app.method("register_agent")
async def register_agent(request: Request):
    agent_id = request.params.get("agent_id")
    return await manager.register_agent(agent_id)

@app.method("handle_request")
async def handle_request(request: Request):
    req_data = request.params
    vacancy_request = VacancyRequest(**req_data)
    return await manager.handle_request(vacancy_request)

@app.method("get_status")
async def get_status(request: Request):
    return await manager.get_status()

# Запуск диспетчера при старте
@app.on_event("startup")
async def startup():
    await manager.start()
    logger.info("MCP Server запущен")