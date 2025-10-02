-- Migration 009: Add show_transcription field
-- Date: 2025-10-02
-- Task: Добавление настройки отображения фонетической транскрипции (IPA)

ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS show_transcription BOOLEAN DEFAULT FALSE;
