-- Migration 006: Add admin_roles table
-- Date: 2025-10-02
-- Task: 3.1 - Role-based access control system

-- Create admin_roles table if not exists
CREATE TABLE IF NOT EXISTS admin_roles (
    user_id BIGINT PRIMARY KEY,
    role TEXT NOT NULL DEFAULT 'analyst',
    permissions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    CHECK (role IN ('admin', 'moderator', 'analyst'))
);

-- Create index on role for faster queries
CREATE INDEX IF NOT EXISTS idx_admin_roles_role ON admin_roles(role);
