import asyncio
import uuid
from fastmcp import MCPClient
from config import Config

class AgentWorker:
    def __init__(self):
        self.agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        self.client = MCPClient(f"http://{Config.MCP_HOST}:{Config.MCP_PORT}")

    async def start(self):
        """Основной цикл работы агента"""
        try:
            await self.client.connect()
            await self.client.models.vacancy_manager.register_agent(self.agent_id)
            print(f"Агент {self.agent_id} запущен")
            
            while True:
                await asyncio.sleep(10)  # Проверка задач каждые 10 секунд
                # В реальной системе здесь будет получение задач из очереди
                
        except Exception as e:
            print(f"Агент {self.agent_id} завершил работу с ошибкой: {e}")

async def run_agent():
    worker = AgentWorker()
    await worker.start()

if __name__ == "__main__":
    asyncio.run(run_agent())