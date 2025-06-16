#hh_parser.py

import aiohttp
from models.schemas import VacancyBase
from config import Config
from gigachat import GigaChat
from typing import List

class HHParser:
    def __init__(self):
        self.headers = {"User-Agent": Config.HH_USER_AGENT}
        self.giga = GigaChat(
            credentials=Config.GIGACHAT_CREDENTIALS,
            scope=Config.GIGACHAT_SCOPE,
            verify_ssl_certs=False
        )

    async def fetch_vacancies(self, query: str) -> List[VacancyBase]:
        params = {
            "text": query,
            "per_page": Config.MAX_VACANCIES,
            "area": 1  # Москва
        }
        async with aiohttp.ClientSession() as session:
            vacancies = await self._fetch_api(session, params)
            return [self._parse_vacancy(v) for v in vacancies]

    async def _fetch_api(self, session, params):
        try:
            async with session.get(
                Config.HH_API_URL,
                params=params,
                headers=self.headers,
                timeout=Config.REQUEST_TIMEOUT
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("items", [])[:Config.MAX_VACANCIES]
        except Exception as e:
            print(f"HH API error: {e}")
            return []

    def _parse_vacancy(self, item) -> VacancyBase:
        salary = item.get("salary")
        salary_str = (
            f"{salary['from']}-{salary['to']} {salary['currency']}" 
            if salary else None
        )
        
        return VacancyBase(
            title=item.get("name", ""),
            company=item.get("employer", {}).get("name", ""),
            salary=salary_str,
            url=item.get("alternate_url", "#"),
            description=item.get("snippet", {}).get("requirement", "")[:100]
        )
    
    