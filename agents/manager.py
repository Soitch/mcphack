# manager.py

import asyncio
import aiohttp
import uuid
from models.schemas import VacancyBase
from agents.hh_parser import HHParser
from config import Config

class AgentWorker:
    def __init__(self):
        self.agent_id = str(uuid.uuid4())
        self.mcp_url = f"http://{Config.API_HOST}:{Config.API_PORT}"
        self.parser = HHParser()
        self.session = aiohttp.ClientSession()

    async def register(self):
        """Регистрация агента на MCP-сервере"""
        async with self.session.post(
            f"{self.mcp_url}/register_agent",
            json={"agent_id": self.agent_id}
        ) as response:
            return response.status == 200

    async def fetch_task(self):
        """Получение задачи от MCP-сервера"""
        async with self.session.get(
            f"{self.mcp_url}/get_task",
            json={"agent_id": self.agent_id}
        ) as response:
            if response.status == 200:
                return await response.json()
            return None

    async def submit_result(self, request_id: str, vacancies: list[VacancyBase]):
        """Отправка результатов на MCP-сервер"""
        vacancies_data = [vacancy.dict() for vacancy in vacancies]
        async with self.session.post(
            f"{self.mcp_url}/submit_result",
            json={
                "request_id": request_id,
                "vacancies": vacancies_data
            }
        ) as response:
            return response.status == 200

    async def run(self):
        """Основной цикл работы агента"""
        if not await self.register():
            print(f"Agent {self.agent_id} registration failed")
            return

        print(f"Agent {self.agent_id} started")

        while True:
            task = await self.fetch_task()
            
            if task and "request_id" in task:
                vacancies = await self.parser.fetch_vacancies(task["query"])
                await self.submit_result(task["request_id"], vacancies)
                print(f"Agent {self.agent_id} processed task {task['request_id']}")
            else:
                await asyncio.sleep(5)

    async def close(self):
        await self.session.close()

async def run_agent():
    worker = AgentWorker()
    try:
        await worker.run()
    finally:
        await worker.close()