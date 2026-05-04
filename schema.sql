-- ============================================================
-- NOTIFICATION SERVICE API - DATABASE SCHEMA
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users
CREATE TABLE users (
    user_id     UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username    VARCHAR(100) NOT NULL UNIQUE,
    email       VARCHAR(150) NOT NULL UNIQUE,
    password    VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Jakarta'),
    is_deleted  BOOLEAN NOT NULL DEFAULT false
);

-- Notifications
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(user_id),
    channel         VARCHAR(10) NOT NULL CHECK (channel IN ('in_app', 'email', 'push')),
    title           VARCHAR(255) NOT NULL,
    body            TEXT NOT NULL,
    data            JSONB,
    is_read         BOOLEAN NOT NULL DEFAULT false,
    read_at         TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Jakarta'),
    is_deleted      BOOLEAN NOT NULL DEFAULT false
);

-- Device Tokens (untuk push notification)
CREATE TABLE device_tokens (
    token_id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID NOT NULL REFERENCES users(user_id),
    device_token    VARCHAR(500) NOT NULL,
    platform        VARCHAR(10) NOT NULL CHECK (platform IN ('android', 'ios')),
    updated_at      TIMESTAMP NOT NULL DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Jakarta'),
    UNIQUE (user_id, platform)
);

-- Index untuk performa query
CREATE INDEX idx_notifications_user_read    ON notifications(user_id, is_read) WHERE is_deleted = false;
CREATE INDEX idx_notifications_user_channel ON notifications(user_id, channel) WHERE is_deleted = false;
CREATE INDEX idx_notifications_created_at   ON notifications(created_at DESC);
CREATE INDEX idx_device_tokens_user         ON device_tokens(user_id);
