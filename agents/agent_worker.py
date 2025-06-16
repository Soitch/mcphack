#agent_worker.py

import asyncio
import uuid
import logging
from fastmcp import Client
from config import Config

# Настройка логирования
logger = logging.getLogger("agent_worker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class AgentWorker:
    def __init__(self):
        self.agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        self.client = Client(f"http://{Config.MCP_HOST}:{Config.MCP_PORT}")
        logger.info(f"Агент инициализирован: {self.agent_id}")

    async def register(self):
        """Регистрация агента на MCP-сервере"""
        try:
            await self.client.connect()
            response = await self.client.call(
                "register_agent",
                agent_id=self.agent_id
            )
            
            if response.get("status") == "success":
                logger.info(f"Агент зарегистрирован: {self.agent_id}")
                return True
            else:
                logger.error(f"Ошибка регистрации: {response}")
                return False
        except Exception as e:
            logger.error(f"Ошибка регистрации: {str(e)}")
            return False

    async def run(self):
        """Основной цикл работы агента"""
        if not await self.register():
            logger.error("Не удалось зарегистрировать агента. Завершение работы.")
            return
        
        logger.info(f"Агент запущен: {self.agent_id}")
        
        try:
            # В реальной системе здесь будет обработка задач
            while True:
                await asyncio.sleep(10)
                logger.debug(f"Агент {self.agent_id} активен")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Ошибка в рабочем цикле: {str(e)}")
        finally:
            logger.info(f"Агент остановлен: {self.agent_id}")

async def run_agent():
    worker = AgentWorker()
    await worker.run()