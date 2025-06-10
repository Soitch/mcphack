import os
from dotenv import find_dotenv, load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_gigachat import GigaChat
from langgraph.prebuilt import create_react_agent

load_dotenv(find_dotenv())
load_dotenv()
api_key = os.getenv("GIGA_API_KEY")

llm = GigaChat(model="GigaChat-2", top_p=0, credentials=api_key, verify_ssl_certs=False)
search_tool = DuckDuckGoSearchRun()

agent = create_react_agent(llm, tools=[search_tool], prompt="Ты полезный компаньон")

inputs = {"messages": [("user", "Выдай шутку про летнюю погоду?")]}
messages = agent.invoke(inputs)["messages"]

print(messages[-1].content)