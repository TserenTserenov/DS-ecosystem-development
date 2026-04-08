-- WP-183 Migration 001: Create finance.payments table
-- Applied: 2026-04-08 to Neon (database: directus, NOT aist_bot)
-- Schema: finance (Payment Registry, SYS.011)
-- Decision: Дима согласовал 8 апр. 1 строка на платёж (UPSERT).

CREATE SCHEMA IF NOT EXISTS finance;

CREATE TABLE finance.payments (
    id              BIGSERIAL PRIMARY KEY,
    ext_id          TEXT,                    -- внешний ID от платёжной системы
    source_id       BIGINT,                  -- оригинальный id из Aisystant (для сверки)
    source_table    TEXT NOT NULL DEFAULT 'payment', -- 'payment' или 'charge_off' (откуда пришла запись)

    -- Кто
    suser_id        BIGINT,                  -- Aisystant user ID (переходный период)
    telegram_id     BIGINT,                  -- Telegram user ID
    email           TEXT,
    ory_id          UUID,                    -- Фаза B

    -- Что
    purpose         TEXT NOT NULL CHECK (purpose IN ('BALANCE','SUBSCRIPTION','DONATION','INTERNSHIP','WORKSHOP')),
    code            TEXT,                    -- код тарифа/курса/потока/семинара
    amount          NUMERIC(12,2) NOT NULL,
    currency        TEXT NOT NULL DEFAULT 'RUB',

    -- Откуда
    payment_system  TEXT,                    -- 'yoo', 'paybox', 'stripe', 'tg_stars'
    channel         SMALLINT NOT NULL,       -- 1-8
    source_system   TEXT NOT NULL DEFAULT 'aisystant',

    -- Статус
    status          TEXT,                    -- 'succeeded', 'canceled', 'pending', 'ok', 'paid', etc.
    success         BOOLEAN NOT NULL DEFAULT false,
    processed       BOOLEAN NOT NULL DEFAULT false,
    charged_off_at  TIMESTAMPTZ,             -- NULL = платёж, NOT NULL = успешное списание

    -- Подписка
    payment_index   INTEGER,
    autopay         BOOLEAN NOT NULL DEFAULT false,
    autopay_data    TEXT,
    auto_extend     BOOLEAN,
    locale          TEXT,
    error_data      TEXT,

    -- Контекст списания (из charge_off)
    details         TEXT,                    -- детали списания
    potok_id        BIGINT,                  -- ID потока (когорты)

    -- Бот
    notified_bot    BOOLEAN NOT NULL DEFAULT false,

    -- Метаданные
    timestamp       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    archived_at     TIMESTAMPTZ
);

CREATE INDEX idx_payments_suser ON finance.payments (suser_id) WHERE suser_id IS NOT NULL;
CREATE INDEX idx_payments_telegram ON finance.payments (telegram_id) WHERE telegram_id IS NOT NULL;
CREATE INDEX idx_payments_ext_id ON finance.payments (ext_id) WHERE ext_id IS NOT NULL;
CREATE INDEX idx_payments_ory ON finance.payments (ory_id) WHERE ory_id IS NOT NULL;
CREATE INDEX idx_payments_charged_off ON finance.payments (charged_off_at) WHERE charged_off_at IS NOT NULL;
CREATE INDEX idx_payments_not_notified ON finance.payments (created_at) WHERE notified_bot = false AND success = true;
CREATE INDEX idx_payments_channel_ts ON finance.payments (channel, timestamp);
CREATE INDEX idx_payments_source ON finance.payments (source_table, source_id);
CREATE UNIQUE INDEX idx_payments_upsert ON finance.payments (source_id, source_table, source_system) WHERE source_id IS NOT NULL;  -- source_table нужен: payment.id=1 и chargeoff.id=1 — разные записи
