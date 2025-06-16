# mcp_server.py
# 112
import sys
import os
import uuid
import asyncio
import time
import logging
from fastmcp import FastMCP

# Добавляем корневую директорию в путь поиска модулей
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Теперь можем импортировать наши модули
from agents.hh_parser import HHParser
from models.schemas import VacancyBase, VacancyRequest, VacancyResponse
from config import Config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Создание MCP-сервера
mcp = FastMCP("HH.ru Vacancy Parser Service")

# Инициализация парсера
parser = HHParser()

# Глобальные переменные для хранения состояния
results = {}
processed_requests = 0
start_time = time.time()

def handle_vacancy_request(params: dict) -> dict:
    """Обработка запроса на поиск вакансий на HH.ru
    
    Args:
        params: Словарь с параметрами запроса
        
    Returns:
        Словарь с результатами обработки
    """
    global processed_requests
    try:
        # Создаем объект запроса из параметров
        request = VacancyRequest(**params)
        request_id = str(uuid.uuid4())
        
        # Логируем запрос
        logger.info(f"Получен запрос {request_id} от пользователя {request.user_id}: {request.query}")
        
        # Получаем вакансии
        vacancies = asyncio.run(parser.fetch_vacancies(request.query))
        
        # Формируем ответ
        response = VacancyResponse(
            vacancies=vacancies,
            user_id=request.user_id,
            request_id=request_id
        )
        
        # Сохраняем результат
        results[request_id] = response
        processed_requests += 1
        
        return {
            "status": "success",
            "request_id": request_id,
            "vacancies_count": len(vacancies)
        }
    except Exception as e:
        logger.error(f"Ошибка обработки запроса: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

def get_system_status() -> dict:
    """Получение статуса системы"""
    return {
        "status": "running",
        "uptime": int(time.time() - start_time),
        "processed_requests": processed_requests,
        "version": "1.0"
    }

def get_results(request_id: str) -> dict:
    """Получение результатов по ID запроса
    
    Args:
        request_id: ID запроса
        
    Returns:
        Результаты обработки или сообщение об ошибке
    """
    if request_id in results:
        return results[request_id].dict()
    return {
        "status": "error",
        "message": "Request ID not found"
    }

# Регистрация инструментов и ресурсов
@mcp.tool
def handle_request(query: str, user_id: int) -> dict:
    """Обработка запроса на поиск вакансий
    
    Args:
        query: Поисковый запрос
        user_id: ID пользователя Telegram
    """
    return handle_vacancy_request({"query": query, "user_id": user_id})

@mcp.resource
def system_status() -> dict:
    """Получение статуса системы"""
    return get_system_status()

@mcp.resource
def get_results_resource(request_id: str) -> dict:
    """Получение результатов по ID запроса
    
    Args:
        request_id: ID запроса
    """
    return get_results(request_id)

# Запуск сервера
if __name__ == "__main__":
    logger.info("Запуск MCP-сервера...")
    logger.info(f"Рабочая директория: {os.getcwd()}")
    logger.info(f"Путь проекта: {project_root}")
    mcp.run()