-- Fix Railway migrations
-- Clear and reapply migrations

-- 1. Delete migration records
DELETE FROM schema_migrations WHERE version IN ('001_add_is_blocked.sql', '002_add_performance_metrics.sql');

-- 2. Apply migration 001
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT FALSE;

-- Mark as applied
INSERT INTO schema_migrations (version) VALUES ('001_add_is_blocked.sql');

-- 3. Apply migration 002
ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER;
ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'success';
ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Mark as applied
INSERT INTO schema_migrations (version) VALUES ('002_add_performance_metrics.sql');

-- 4. Verify
SELECT version, applied_at FROM schema_migrations ORDER BY version;
