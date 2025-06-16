import asyncio
import multiprocessing
import uvicorn
from master.mcp_server import app
from agents.agent_worker import run_agent
from bot.telegram_bot import TelegramBot
from config import Config

def run_mcp_server():
    """Запуск MCP-сервера"""
    uvicorn.run(
        app, 
        host=Config.MCP_HOST, 
        port=Config.MCP_PORT,
        log_level="info"
    )

async def run_agents(num_agents: int = 3):
    """Запуск пула агентов"""
    tasks = []
    for _ in range(num_agents):
        task = asyncio.create_task(run_agent())
        tasks.append(task)
    await asyncio.gather(*tasks)

async def run_telegram_bot():
    """Запуск Telegram-бота"""
    bot = TelegramBot()
    await bot.run()

async def main():
    """Основная функция запуска системы"""
    # Запуск MCP-сервера в отдельном процессе
    server_process = multiprocessing.Process(target=run_mcp_server)
    server_process.start()
    
    # Запуск агентов и бота в асинхронном режиме
    try:
        agents_task = asyncio.create_task(run_agents(Config.AGENT_POOL_SIZE))
        bot_task = asyncio.create_task(run_telegram_bot())
        
        await asyncio.gather(agents_task, bot_task)
    except KeyboardInterrupt:
        print("Завершение работы...")
    finally:
        server_process.terminate()

if __name__ == "__main__":
    asyncio.run(main())