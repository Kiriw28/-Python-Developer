FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY wait-for-postgres.sh .

# Установка pg_isready
RUN apt-get update && apt-get install -y postgresql-client

CMD ["./wait-for-postgres.sh", "python", "app/main.py"]
