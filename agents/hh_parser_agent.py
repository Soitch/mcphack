import aiohttp
import json
from config import Config
from gigachat import GigaChat
from typing import List, Dict

class HHParserAgent:
    def __init__(self):
        self.headers = {
            "User-Agent": Config.HH_USER_AGENT,
            "Accept": "application/json"
        }
        self.giga = GigaChat(
            credentials=Config.GIGACHAT_CREDENTIALS,
            scope=Config.GIGACHAT_SCOPE,
            verify_ssl_certs=False
        )

    async def fetch_vacancies(self, query: str) -> List[Dict]:
        """Получение и обработка вакансий"""
        params = {
            "text": query,
            "per_page": Config.MAX_VACANCIES,
            "area": 1,  # Москва
            "only_with_salary": True
        }
        
        async with aiohttp.ClientSession() as session:
            raw_vacancies = await self._fetch_hh_api(session, params)
            return await self._process_vacancies(raw_vacancies)

    async def _fetch_hh_api(self, session: aiohttp.ClientSession, params: Dict) -> List[Dict]:
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

    async def _process_vacancies(self, raw_vacancies: List[Dict]) -> List[Dict]:
        """Обработка списка вакансий"""
        processed = []
        for vacancy in raw_vacancies:
            try:
                processed.append(await self._process_vacancy(vacancy))
            except Exception as e:
                print(f"Ошибка обработки вакансии: {e}")
                processed.append(self._fallback_vacancy(vacancy))
        return processed

    async def _process_vacancy(self, vacancy: Dict) -> Dict:
        """Обработка одной вакансии с помощью GigaChat"""
        prompt = (
            "Извлеки ключевую информацию о вакансии в JSON формате со следующими полями: "
            "title (строка), company (строка), salary (строка), "
            "description (не более 100 символов), address (строка), url (строка). "
            f"Данные: {json.dumps(vacancy, ensure_ascii=False)}"
        )
        
        response = await self.giga.achat(prompt)
        result = json.loads(response.choices[0].message.content)
        result['url'] = vacancy.get('alternate_url', '#')
        return result

    def _fallback_vacancy(self, vacancy: Dict) -> Dict:
        """Резервная обработка вакансии"""
        salary = vacancy.get('salary')
        salary_str = f"{salary['from']}-{salary['to']} {salary['currency']}" if salary else "Не указана"
        
        return {
            "title": vacancy.get('name', ''),
            "company": vacancy.get('employer', {}).get('name', ''),
            "salary": salary_str,
            "description": vacancy.get('snippet', {}).get('requirement', '')[:100],
            "address": vacancy.get('area', {}).get('name', ''),
            "url": vacancy.get('alternate_url', '#')
        }