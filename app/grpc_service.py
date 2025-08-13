import grpc
from concurrent import futures
import balance_pb2
import balance_pb2_grpc
from service import update_balance, open_transaction, commit_transaction, cancel_transaction
from database import db
import asyncio


class BalanceService(balance_pb2_grpc.BalanceServiceServicer):
    async def UpdateBalance(self, request, context):
        async with db.pool.acquire() as conn:
            result = await update_balance(conn, request.user_id, request.current_change, request.max_change)
            return balance_pb2.BalanceResponse(
                current_balance=result["current_balance"],
                max_balance=result["max_balance"]
            )

    async def OpenTransaction(self, request, context):
        async with db.pool.acquire() as conn:
            result = await open_transaction(conn, request.user_id, request.amount)
            return balance_pb2.TransactionResponse(
                transaction_id=result["transaction_id"],
                locked_amount=result["locked_amount"]
            )

    async def CommitTransaction(self, request, context):
        async with db.pool.acquire() as conn:
            result = await commit_transaction(conn, request.transaction_id)
            return balance_pb2.TransactionStatus(status=result["status"])

    async def CancelTransaction(self, request, context):
        async with db.pool.acquire() as conn:
            result = await cancel_transaction(conn, request.transaction_id)
            return balance_pb2.TransactionStatus(status=result["status"])

async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    balance_pb2_grpc.add_BalanceServiceServicer_to_server(BalanceService(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()