import asyncpg
from typing import AsyncGenerator

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        # Создание пула соединений для асинхронной работы с PostgreSQL
        self.pool = await asyncpg.create_pool(
            user="postgres", password="password", database="balance_db", host="postgres", port=5432
        )

    async def disconnect(self):
        # Закрытие пула соединений
        if self.pool:
            await self.pool.close()

    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        # Получение соединения из пула
        async with self.pool.acquire() as conn:
            yield conn

db = Database()

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    # Dependency Injection для получения соединения с базой
    async for conn in db.get_connection():
        yield conn
