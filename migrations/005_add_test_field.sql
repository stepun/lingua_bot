-- Migration 005: Add test field to users table
-- Date: 2025-10-01
-- Task: Test migration system with simple field addition

-- Add TEST text field to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS test TEXT;
