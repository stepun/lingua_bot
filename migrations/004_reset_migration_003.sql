-- Migration 004: Reset migration 003 to allow re-application
-- Date: 2025-10-01
-- Task: Remove failed migration 003 record to allow it to run again with fixed transaction logic

-- Remove migration 003 from schema_migrations so it can be re-applied
DELETE FROM schema_migrations WHERE version = '003_remove_premium_fields.sql';
