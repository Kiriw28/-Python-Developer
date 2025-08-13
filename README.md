Структура

├── app
│   ├── api.py                 # Реализация REST API (FastAPI)
│   ├── balance.proto          # Proto-файл для gRPC API
│   ├── balance_pb2.py         # Сгенерированный файл для gRPC сообщений
│   ├── balance_pb2_grpc.py    # Сгенерированный файл для gRPC сервиса
│   ├── database.py            # Управление подключением к PostgreSQL
│   ├── grpc_service.py        # Реализация gRPC сервера
│   ├── __init__.py            # Пустой файл для обозначения Python-пакета
│   ├── main.py                # Точка входа, запуск FastAPI и gRPC серверов
│   ├── __pycache__         # Скомпилированные Python-файлы
│   └── service.py             # Бизнес-логика управления балансом и транзакциями
├── docker-compose.yaml        # Конфигурация Docker Compose для запуска приложения и PostgreSQL
├── Dockerfile                 # Инструкции для сборки Docker-образа приложения
├── init.sql                   # SQL-скрипт для инициализации таблиц в PostgreSQL
├── requirements.txt           # Список Python-зависимостей
└── wait-for-postgres.sh       # Скрипт ожидания готовности PostgreSQL


Описание файлов
    • app/api.py: Реализует REST API с использованием FastAPI. Определяет эндпоинты /balance/update, /transaction/open, /transaction/commit, /transaction/cancel, а также /health для проверки подключения к базе. Включает проверку JWT-токенов. 
    • app/balance.proto: Определяет gRPC интерфейс для операций с балансом и транзакциями. 
    • app/balance_pb2.py, app/balance_pb2_grpc.py: Сгенерированные файлы для gRPC, содержащие определения сообщений и сервиса. 
    • app/database.py: Управляет пулом соединений с PostgreSQL через asyncpg. Реализует Dependency Injection через функцию get_db. 
    • app/grpc_service.py: Реализует gRPC сервер с методами, аналогичными REST API. 
    • app/main.py: Точка входа приложения, запускает FastAPI и gRPC серверы, управляет жизненным циклом базы данных. 
    • app/service.py: Содержит бизнес-логику для операций с балансом и транзакциями, включая проверки валидности и атомарные операции. 
    • docker-compose.yaml: Настраивает два сервиса: app (Python-приложение) и postgres (база данных). Порт PostgreSQL на хосте изменён на 5433 для избежания конфликтов. 
    • Dockerfile: Описывает сборку Docker-образа приложения, включая установку зависимостей и генерацию gRPC файлов. 
    • init.sql: Создаёт таблицы users и transactions с индексами и ограничениями. 
    • requirements.txt: Список зависимостей (fastapi, uvicorn, asyncpg, pyjwt, grpcio, grpcio-tools). 
    • wait-for-postgres.sh: Скрипт, обеспечивающий ожидание готовности PostgreSQL перед запуском приложения.

	Запуск  решения
Сделайте скрипт wait-for-postgres.sh исполняемым:
chmod +x wait-for-postgres.sh 
Запустить контейнер:
docker-compose up --build
