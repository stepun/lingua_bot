-- Migration 001: Add is_blocked field to users table
-- Date: 2025-10-01
-- Task: 2.1 - User blocking functionality

ALTER TABLE users ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT FALSE;
