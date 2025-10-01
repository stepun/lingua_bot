-- Migration 002: Add performance tracking to translation_history
-- Date: 2025-10-01
-- Task: 2.4 - Performance metrics

ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER;
ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'success';
ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS error_message TEXT;
