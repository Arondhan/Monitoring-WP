-- Миграция для добавления таблиц настроек и прокси
-- Применить через: docker exec -i uptime_postgres psql -U uptime_user -d uptime_db < migrate_settings.sql

-- Таблица proxy_servers
CREATE TABLE IF NOT EXISTS proxy_servers (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    username VARCHAR(255),
    password VARCHAR(255),
    protocol VARCHAR(20) DEFAULT 'http',
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_working BOOLEAN,
    last_checked_at TIMESTAMP WITH TIME ZONE,
    usage_type VARCHAR(50) DEFAULT 'security',
    country VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS ix_proxy_servers_name ON proxy_servers(name);
CREATE INDEX IF NOT EXISTS ix_proxy_servers_active ON proxy_servers(is_active);
CREATE INDEX IF NOT EXISTS ix_proxy_servers_usage ON proxy_servers(usage_type);

-- Таблица app_settings
CREATE TABLE IF NOT EXISTS app_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) NOT NULL UNIQUE,
    value TEXT,
    value_type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_app_settings_key ON app_settings(key);
