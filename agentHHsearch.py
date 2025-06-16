#agentHHsearch

from langchain.tools import BaseTool
import pandas as pd
from typing import Optional, Type
from pydantic import BaseModel, Field
# Импортируем функции из файла парсера
from agentparser import get_vacancies_data, save_vacancies_to_csv, read_vacancies_from_csv

# Определяем входную схему для инструмента с использованием Pydantic
class HeadHunterJobSearchInput(BaseModel):
    """Input schema for the HeadHunter job search tool."""
    query: str = Field(description="Поисковый запрос для вакансий (например, 'бухгалтер', 'Python разработчик').")
    area_id: Optional[int] = Field(None, description="ID региона для поиска (например, 1 для Москвы, 113 для всей России). По умолчанию ищет по всей России, если не указано.")
    pages: Optional[int] = Field(1, description="Количество страниц для парсинга результатов. По умолчанию 1.")
    save_to_file: Optional[str] = Field(None, description="Путь к файлу для сохранения результатов в CSV. Если указано, данные будут сохранены.")
    read_from_file: Optional[str] = Field(None, description="Путь к файлу CSV для чтения вакансий вместо поиска.")

class HeadHunterJobSearchTool(BaseTool):
    """Tool for searching, saving, and reading HeadHunter job data."""
    name: str = "headhunter_job_search"
    description: str = "Полезен для поиска, сохранения и чтения данных о вакансиях на HeadHunter. Принимает поисковый запрос и опциональные параметры."
    # Указываем Pydantic модель в качестве схемы аргументов
    args_schema: Type[BaseModel] = HeadHunterJobSearchInput

    def _run(self, query: str, area_id: Optional[int] = None, pages: Optional[int] = 1, save_to_file: Optional[str] = None, read_from_file: Optional[str] = None) -> str:
        """
        Синхронное выполнение поиска, сохранения или чтения данных о вакансиях.
        Используется для выполнения основных операций инструмента.
        """
        if read_from_file:
            # Читаем из файла, если указано
            df_result = read_vacancies_from_csv(read_from_file)
            if isinstance(df_result, str):
                return df_result # Возвращаем сообщение об ошибке, если чтение не удалось

            # Обработка прочитанного DataFrame (например, расчет средней зарплаты)
            # В данном случае, добавим расчет средней максимальной зарплаты
            if 'salary_to' in df_result.columns:
                valid_salaries = df_result['salary_to'].dropna()
                if not valid_salaries.empty:
                    numeric_salaries = pd.to_numeric(valid_salaries, errors='coerce').dropna()
                    if not numeric_salaries.empty:
                        average_salary = numeric_salaries.mean()
                        return f"Прочитано {len(df_result)} вакансий из файла '{read_from_file}'. Средняя максимальная зарплата: {average_salary:.2f}"
                    else:
                         return f"В файле '{read_from_file}' нет числовых значений зарплаты для расчета среднего."
                else:
                    return f"В файле '{read_from_file}' нет информации о максимальной зарплате для расчета среднего."
            else:
                 return f"В файле '{read_from_file}' отсутствует столбец 'salary_to' для расчета средней зарплаты."

        else:
            # Выполняем поиск вакансий, если не указано чтение из файла
            area = area_id if area_id is not None else 113 # По умолчанию вся Россия (ID 113)
            job_titles = [query] # Передаем поисковый запрос как список
            pages_to_parse = pages if pages is not None else 1 # По умолчанию 1 страница

            df_vacancies = get_vacancies_data(job_titles, pages_to_parse, area)

            if df_vacancies is None or df_vacancies.empty:
                return f"Не найдено вакансий по запросу '{query}' в регионе с ID {area}."

            result_message = f"Найдено {len(df_vacancies)} вакансий по запросу '{query}' в регионе с ID {area}."

            if save_to_file:
                # Сохраняем в файл, если указано
                save_message = save_vacancies_to_csv(df_vacancies, save_to_file)
                result_message += f" {save_message}"

            # Возвращаем краткую информацию о найденных вакансиях
            top_n = 5
            if len(df_vacancies) > top_n:
                vacancies_summary = df_vacancies.head(top_n)[['name', 'employer', 'city', 'salary_to', 'link']].to_string(index=False)
                result_message += f"\n\nПервые {top_n} вакансий:\n{vacancies_summary}"
            else:
                 vacancies_summary = df_vacancies[['name', 'employer', 'city', 'salary_to', 'link']].to_string(index=False)
                 result_message += f"\n\nНайденные вакансии:\n{vacancies_summary}"

            return result_message


    async def _arun(self, query: str, area_id: Optional[int] = None, pages: Optional[int] = 1, save_to_file: Optional[str] = None, read_from_file: Optional[str] = None) -> str:
        """
        Асинхронное выполнение поиска, сохранения или чтения данных о вакансиях.
        В данной реализации просто вызывает синхронную версию для простоты.
        Для истинной асинхронности, используйте асинхронные версии методов requests
        или библиотеки для асинхронного парсинга.
        """
        # Для простоты, вызываем синхронную версию
        return self._run(query, area_id, pages, save_to_file, read_from_file)