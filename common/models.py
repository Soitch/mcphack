from pydantic import BaseModel

class VacancyRequest(BaseModel):
    query: str
    user_id: int

class VacancyResponse(BaseModel):
    vacancies: list[dict]
    user_id: int
    request_id: str