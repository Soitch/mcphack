import uuid
import asyncio
from fastmcp import FastMCP, MCPModel
from common.models import VacancyRequest, VacancyResponse
from config import Config
from agents.hh_parser_agent import HHParserAgent
import time

app = FastMCP()

class VacancyAgentManager(MCPModel):
    def __init__(self):
        self.active_agents = []
        self.task_queue = asyncio.Queue()
        self.results = {}
        self.processed_requests = 0
        self.start_time = time.time()
        
        # Запуск обработчиков задач
        asyncio.create_task(self.task_distributor())

    async def register_agent(self, agent_id: str):
        """Регистрация нового агента"""
        if agent_id not in self.active_agents:
            self.active_agents.append(agent_id)
            print(f"Агент {agent_id} зарегистрирован")
        return {"status": "success"}

    async def handle_request(self, request: VacancyRequest):
        """Обработка запроса на поиск вакансий"""
        request_id = str(uuid.uuid4())
        await self.task_queue.put((request_id, request))
        return await self.wait_for_result(request_id)

    async def task_distributor(self):
        """Распределение задач между агентами"""
        while True:
            request_id, request = await self.task_queue.get()
            asyncio.create_task(self.process_request(request_id, request))

    async def process_request(self, request_id: str, request: VacancyRequest):
        """Обработка запроса с помощью агента"""
        try:
            agent = HHParserAgent()
            vacancies = await agent.fetch_vacancies(request.query)
            self.results[request_id] = VacancyResponse(
                vacancies=vacancies,
                user_id=request.user_id,
                request_id=request_id
            )
            self.processed_requests += 1
        except Exception as e:
            print(f"Ошибка обработки запроса: {e}")
            self.results[request_id] = VacancyResponse(
                vacancies=[],
                user_id=request.user_id,
                request_id=request_id
            )

    async def wait_for_result(self, request_id: str, timeout: int = 30):
        """Ожидание результата обработки"""
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

# Регистрация модели
app.add_model("vacancy_manager", VacancyAgentManager())