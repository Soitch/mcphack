from fastmcp import Client
from fastmcp.client.transports import PythonStdioTransport
import os

def main():
    # Получаем абсолютный путь к серверу
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    
    # Проверяем существование файла
    if not os.path.exists(server_path):
        raise FileNotFoundError(f"Файл сервера не найден: {server_path}")

    transport = PythonStdioTransport(script_path=server_path)
    client = Client(transport)
    
    try:
        response = client.call("add", {"a": 5, "b": 3})
        print("Результат сложения:", response["result"])  # Должно быть 8
    except Exception as e:
        print("Ошибка:", e)

if __name__ == "__main__":
    main()