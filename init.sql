-- Создание таблицы пользователей
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    current_balance DECIMAL(15, 2) NOT NULL DEFAULT 0.0,
    max_balance DECIMAL(15, 2) NOT NULL DEFAULT 1000.0,
    CONSTRAINT valid_balance CHECK (current_balance >= 0 AND max_balance >= current_balance AND max_balance >= 0)
);

-- Создание таблицы транзакций
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    locked_amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN', -- OPEN, COMMITTED, CANCELLED
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT valid_amount CHECK (locked_amount >= 0)
);

-- Индексы для оптимизации запросов
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_status ON transactions(status);