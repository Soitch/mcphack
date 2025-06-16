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
    request_id: str
    user_id: int

class AgentRegister(BaseModel):
    agent_id: str

# Добавим модель для статуса агента
class AgentStatus(BaseModel):
    agent_id: str
    last_seen: int  # секунды назад

class SystemStatus(BaseModel):
    status: str
    uptime: int
    active_agents: List[AgentStatus]
    queue_size: int
    processed_requests: int