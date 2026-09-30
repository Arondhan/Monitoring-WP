-- Миграция: добавление WordPress-полей в таблицу domains (для мониторинга Uptime Checker)
-- Применить через: docker exec -i uptime_postgres psql -U uptime_user -d uptime_db < add_wordpress_fields_to_domains.sql

ALTER TABLE domains ADD COLUMN IF NOT EXISTS is_wordpress INTEGER DEFAULT 0;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS last_post_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS last_post_title VARCHAR(500);
ALTER TABLE domains ADD COLUMN IF NOT EXISTS last_post_checked_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE domains ADD COLUMN IF NOT EXISTS wordpress_version VARCHAR(50);
