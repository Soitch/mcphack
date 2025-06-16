import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MCP Server
    MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
    MCP_PORT = int(os.getenv("MCP_PORT", 8000))
    
    # Telegram
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # GigaChat
    GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
    GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    
    # HH.ru API
    HH_API_URL = "https://api.hh.ru/vacancies"
    HH_USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    
    # Настройки
    MAX_VACANCIES = 5
    AGENT_POOL_SIZE = 3