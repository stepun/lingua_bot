-- Migration 007: System Settings
-- Date: 2025-10-02
-- Task: 3.2 - Dynamic system configuration

-- Create system_settings table
CREATE TABLE IF NOT EXISTS system_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    description TEXT,
    value_type TEXT DEFAULT 'string',
    updated_by BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES users (user_id),
    CHECK (category IN ('translation', 'voice', 'pricing', 'limits', 'features', 'general')),
    CHECK (value_type IN ('string', 'integer', 'float', 'boolean', 'json'))
);

-- Create index for faster category filtering
CREATE INDEX IF NOT EXISTS idx_system_settings_category ON system_settings(category);

-- Pre-populate default settings
INSERT INTO system_settings (key, value, category, description, value_type) VALUES
    ('asr_api_provider', 'openai', 'voice', 'ASR API provider: openai, google, azure', 'string'),
    ('asr_enabled', 'true', 'voice', 'Enable/disable voice transcription', 'boolean'),
    ('tts_provider', 'openai', 'voice', 'TTS provider: openai, elevenlabs', 'string'),
    ('free_daily_limit', '10', 'limits', 'Free translations per day', 'integer'),
    ('max_voice_duration', '60', 'limits', 'Max voice message duration (seconds)', 'integer'),
    ('daily_price', '100', 'pricing', 'Daily subscription price (RUB)', 'integer'),
    ('monthly_price', '490', 'pricing', 'Monthly subscription price (RUB)', 'integer'),
    ('yearly_price', '4680', 'pricing', 'Yearly subscription price (RUB)', 'integer'),
    ('deepl_enabled', 'true', 'translation', 'Enable DeepL API', 'boolean'),
    ('yandex_enabled', 'true', 'translation', 'Enable Yandex Translate API', 'boolean'),
    ('gpt_enhancement', 'true', 'translation', 'Enable GPT-4o enhancement', 'boolean'),
    ('max_history_items', '100', 'limits', 'Maximum history items per user', 'integer'),
    ('rate_limit_window', '60', 'limits', 'Rate limit window (seconds)', 'integer'),
    ('rate_limit_requests', '30', 'limits', 'Max requests per window', 'integer')
ON CONFLICT (key) DO NOTHING;
