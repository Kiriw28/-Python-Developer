#!/bin/bash
# Ожидание, пока PostgreSQL не станет доступен
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done
echo "PostgreSQL is ready!"
exec "$@"