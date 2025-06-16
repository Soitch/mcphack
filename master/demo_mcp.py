# demo.py
# A simple server demonstrating resources, tools, and prompts:
# Запуск сервера:  fastmcp dev demo_mcp.py
# 
# Ресурсы — это то, как вы предоставляете данные LLM. 
# Они похожи на конечные точки GET в REST API — они предоставляют данные, но не должны выполнять существенные вычисления или иметь побочные эффекты.
# 
# Инструменты - позволяют LLM выполнять действия через сервер. 
# В отличие от ресурсов, инструменты должны выполнять вычисления и иметь побочные эффекты. Они похожи на конечные точки POST в REST API
# 
# Промпты — это повторно используемые шаблоны, которые помогают LLM эффективно взаимодействовать с сервером. 
# Они как «лучшие практики», закодированные в вашем сервере. Подсказка может быть такой же простой, как строка
# Пимер сервера, исползующего все три типа
#

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Echo")

@mcp.resource("echo://{message}")
def echo_resource(message: str) -> str:
    """Echo a message as a resource"""
    return f"Resource echo: {message}"

@mcp.tool()
def echo_tool(message: str) -> str:
    """Echo a message as a tool"""
    return f"Tool echo: {message}"

@mcp.prompt()
def echo_prompt(message: str) -> str:
    """Create an echo prompt"""
    return f"Please process this message: {message}"