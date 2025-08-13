from fastapi import FastAPI, Depends, HTTPException, Header
from pydantic import BaseModel
import asyncpg
from database import get_db
from service import update_balance, open_transaction, commit_transaction, cancel_transaction
import jwt

app = FastAPI()

# Модель для запросов на обновление баланса
class BalanceUpdate(BaseModel):
    user_id: int
    current_change: float
    max_change: float

# Модель для открытия транзакции
class TransactionOpen(BaseModel):
    user_id: int
    amount: float

# Модель для закрытия транзакции
class TransactionClose(BaseModel):
    transaction_id: int

# Проверка JWT-токена
async def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/balance/update")
async def update_balance_endpoint(
    update: BalanceUpdate,
    db: asyncpg.Connection = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    # Обновление баланса пользователя
    return await update_balance(db, update.user_id, update.current_change, update.max_change)

@app.post("/transaction/open")
async def open_transaction_endpoint(
    transaction: TransactionOpen,
    db: asyncpg.Connection = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    # Открытие транзакции
    return await open_transaction(db, transaction.user_id, transaction.amount)

@app.post("/transaction/commit")
async def commit_transaction_endpoint(
    transaction: TransactionClose,
    db: asyncpg.Connection = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    # Подтверждение транзакции
    return await commit_transaction(db, transaction.transaction_id)

@app.post("/transaction/cancel")
async def cancel_transaction_endpoint(
    transaction: TransactionClose,
    db: asyncpg.Connection = Depends(get_db),
    payload: dict = Depends(verify_token)
):
    # Отмена транзакции
    return await cancel_transaction(db, transaction.transaction_id)