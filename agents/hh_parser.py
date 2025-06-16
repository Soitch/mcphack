#hh_parser.py

import aiohttp
from config import Config
from models.schemas import VacancyBase
from typing import List

class HHParser:
    def __init__(self):
        self.headers = {
            "User-Agent": Config.HH_USER_AGENT,
            "Accept": "application/json"
        }

    async def fetch_vacancies(self, query: str) -> List[VacancyBase]:
        """Получение и обработка вакансий"""
        params = {
            "text": query,
            "per_page": Config.MAX_VACANCIES,
            "area": 1  # Москва
        }
        
        async with aiohttp.ClientSession() as session:
            raw_vacancies = await self._fetch_hh_api(session, params)
            return self._process_vacancies(raw_vacancies)

    async def _fetch_hh_api(self, session: aiohttp.ClientSession, params: dict) -> list:
        """Вызов API HH.ru"""
        try:
            async with session.get(
                Config.HH_API_URL,
                params=params,
                headers=self.headers,
                timeout=Config.REQUEST_TIMEOUT
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("items", [])
        except Exception as e:
            print(f"Ошибка HH API: {e}")
            return []

    def _process_vacancies(self, raw_vacancies: list) -> List[VacancyBase]:
        """Обработка списка вакансий"""
        processed = []
        for item in raw_vacancies:
            try:
                salary = item.get("salary")
                salary_str = (
                    f"{salary['from']}-{salary['to']} {salary['currency']}" 
                    if salary else "Не указана"
                )
                
                vacancy = VacancyBase(
                    title=item.get("name", "Нет названия"),
                    company=item.get("employer", {}).get("name", "Неизвестно"),
                    salary=salary_str,
                    url=item.get("alternate_url", "#"),
                    description=(item.get("snippet", {}).get("requirement", "Описание отсутствует")[:100] + "...")
                )
                processed.append(vacancy)
            except Exception as e:
                print(f"Ошибка обработки вакансии: {e}")
                # Создаем базовую вакансию при ошибке
                processed.append(VacancyBase(
                    title="Ошибка обработки",
                    company="",
                    salary="",
                    url="#",
                    description="Не удалось обработать данные вакансии"
                ))
        return processed