# schemas.py

from pydantic import BaseModel
from typing import List, Optional

class VacancyBase(BaseModel):
    title: str
    company: str
    salary: Optional[str] = None
    url: str
    description: Optional[str] = None

class VacancyRequest(BaseModel):
    query: str
    user_id: int

class VacancyResponse(BaseModel):
    vacancies: List[VacancyBase]
    user_id: int
    request_id: str