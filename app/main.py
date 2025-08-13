from api import app
from database import db
import asyncio
from grpc_service import serve

async def startup():
    # Инициализация базы данных
    await db.connect()

async def shutdown():
    # Закрытие соединений
    await db.disconnect()

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

if __name__ == "__main__":
    import uvicorn
    # Запуск FastAPI и gRPC серверов
    loop = asyncio.get_event_loop()
    loop.create_task(serve())
    uvicorn.run(app, host="0.0.0.0", port=8000)