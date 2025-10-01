-- Migration 003: Remove redundant premium fields from users table
-- Date: 2025-10-01
-- Task: Refactoring - Premium status should be determined by subscriptions table only

-- Drop is_premium column (redundant with subscriptions table)
ALTER TABLE users DROP COLUMN IF EXISTS is_premium;

-- Drop premium_until column (redundant with subscriptions table)
ALTER TABLE users DROP COLUMN IF EXISTS premium_until;
