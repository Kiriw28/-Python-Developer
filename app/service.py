from datetime import datetime, timedelta
import asyncpg
from fastapi import HTTPException

async def update_balance(conn: asyncpg.Connection, user_id: int, current_change: float, max_change: float):
    # Атомарное обновление баланса с проверкой валидности
    async with conn.transaction():
        # Блокировка строки пользователя
        user = await conn.fetchrow(
            "SELECT current_balance, max_balance FROM users WHERE user_id = $1 FOR UPDATE", user_id
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        new_current = user["current_balance"] + current_change
        new_max = user["max_balance"] + max_change

        # Проверка валидности нового состояния
        if new_current < 0 or new_max < new_current or new_max < 0:
            raise HTTPException(status_code=400, detail="Invalid balance update")

        await conn.execute(
            "UPDATE users SET current_balance = $1, max_balance = $2 WHERE user_id = $3",
            new_current, new_max, user_id
        )
        return {"current_balance": new_current, "max_balance": new_max}

async def open_transaction(conn: asyncpg.Connection, user_id: int, amount: float):
    # Открытие транзакции с блокировкой средств
    async with conn.transaction():
        user = await conn.fetchrow(
            "SELECT current_balance, max_balance FROM users WHERE user_id = $1 FOR UPDATE", user_id
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Проверка, что достаточно средств для блокировки
        locked_sum = await conn.fetchval(
            "SELECT COALESCE(SUM(locked_amount), 0) FROM transactions WHERE user_id = $1 AND status = 'OPEN'",
            user_id
        )
        if user["current_balance"] + locked_sum + amount > user["max_balance"] or amount < 0:
            raise HTTPException(status_code=400, detail="Insufficient funds or invalid amount")

        # Создание транзакции
        transaction_id = await conn.fetchval(
            "INSERT INTO transactions (user_id, locked_amount, status, created_at) VALUES ($1, $2, 'OPEN', NOW()) RETURNING transaction_id",
            user_id, amount
        )
        return {"transaction_id": transaction_id, "locked_amount": amount}

async def commit_transaction(conn: asyncpg.Connection, transaction_id: int):
    # Подтверждение транзакции
    async with conn.transaction():
        tx = await conn.fetchrow(
            "SELECT user_id, locked_amount, status, created_at FROM transactions WHERE transaction_id = $1 FOR UPDATE",
            transaction_id
        )
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if tx["status"] != "OPEN":
            raise HTTPException(status_code=400, detail="Transaction already processed")

        # Проверка таймаута (1 час)
        if datetime.now() - tx["created_at"] > timedelta(hours=1):
            await conn.execute(
                "UPDATE transactions SET status = 'CANCELLED' WHERE transaction_id = $1", transaction_id
            )
            raise HTTPException(status_code=400, detail="Transaction timed out")

        # Списание заблокированных средств
        await conn.execute(
            "UPDATE users SET current_balance = current_balance - $1 WHERE user_id = $2",
            tx["locked_amount"], tx["user_id"]
        )
        await conn.execute(
            "UPDATE transactions SET status = 'COMMITTED' WHERE transaction_id = $1", transaction_id
        )
        return {"status": "committed"}

async def cancel_transaction(conn: asyncpg.Connection, transaction_id: int):
    # Отмена транзакции
    async with conn.transaction():
        tx = await conn.fetchrow(
            "SELECT status FROM transactions WHERE transaction_id = $1 FOR UPDATE", transaction_id
        )
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if tx["status"] != "OPEN":
            raise HTTPException(status_code=400, detail="Transaction already processed")

        await conn.execute(
            "UPDATE transactions SET status = 'CANCELLED' WHERE transaction_id = $1", transaction_id
        )
        return {"status": "cancelled"}