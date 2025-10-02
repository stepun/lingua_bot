-- Migration 008: Add API Keys to System Settings
-- Date: 2025-10-02
-- Task: Add API keys for all services to admin panel

-- Add 'api_keys' to category CHECK constraint
ALTER TABLE system_settings DROP CONSTRAINT IF EXISTS system_settings_category_check;
ALTER TABLE system_settings ADD CONSTRAINT system_settings_category_check
    CHECK (category IN ('translation', 'voice', 'pricing', 'limits', 'features', 'general', 'api_keys'));

-- Add 'secret' value type for sensitive data (masked in UI)
ALTER TABLE system_settings DROP CONSTRAINT IF EXISTS system_settings_value_type_check;
ALTER TABLE system_settings ADD CONSTRAINT system_settings_value_type_check
    CHECK (value_type IN ('string', 'integer', 'float', 'boolean', 'json', 'secret'));

-- Add API keys with empty defaults (admin must fill them)
INSERT INTO system_settings (key, value, category, description, value_type) VALUES
    ('deepl_api_key', '', 'api_keys', 'DeepL API Key (https://www.deepl.com/pro-api)', 'secret'),
    ('yandex_api_key', '', 'api_keys', 'Yandex Translate API Key (https://cloud.yandex.com/)', 'secret'),
    ('openai_api_key', '', 'api_keys', 'OpenAI API Key (https://platform.openai.com/)', 'secret'),
    ('elevenlabs_api_key', '', 'api_keys', 'ElevenLabs API Key (https://elevenlabs.io/)', 'secret'),
    ('yookassa_shop_id', '', 'api_keys', 'YooKassa Shop ID', 'string'),
    ('yookassa_secret_key', '', 'api_keys', 'YooKassa Secret Key', 'secret'),
    ('telegram_bot_token', '', 'api_keys', 'Telegram Bot Token (from @BotFather)', 'secret')
ON CONFLICT (key) DO NOTHING;
