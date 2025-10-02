-- Migration 010: Add transcription field to translation_history
-- Date: 2025-10-02
-- Task: Сохранение фонетической транскрипции (IPA) в истории переводов

ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS transcription TEXT;
