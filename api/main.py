from fastapi import FastAPI
from agents.manager import AgentManager
from models.schemas import VacancyRequest, VacancyResponse, AgentRegister
import uvicorn

app = FastAPI()
manager = AgentManager()

@app.post("/register_agent", response_model=dict)
async def register_agent(agent: AgentRegister):
    return await manager.register_agent(agent.agent_id)

@app.post("/search", response_model=VacancyResponse)
async def search_vacancies(request: VacancyRequest):
    return await manager.handle_request(request)

@app.get("/status")
async def get_status():
    return await manager.get_status()

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000)