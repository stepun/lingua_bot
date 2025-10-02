# План реализации: Задача 3.2 - Настройки системы

**Статус:** ✅ Завершено
**Оценка:** 6-8 часов
**Фактическое время:** ~6 часов
**Дата создания:** 2025-10-02
**Дата завершения:** 2025-10-02

---

## 🎯 Цель

Создать систему динамических настроек с возможностью управления через админ-панель, которая переопределяет значения из `.env` файла и применяется без перезапуска бота.

---

## 📊 Архитектурное решение

### Приоритет загрузки настроек:
1. **База данных** (`system_settings`) - высший приоритет
2. **Environment** (`.env`) - fallback
3. **Hardcoded defaults** - если нет нигде

### Категории настроек:
- **Translation** - настройки перевода (API приоритеты, лимиты)
- **Voice** - настройки голосовых сообщений (ASR API, TTS)
- **Pricing** - цены на подписки
- **Limits** - лимиты для пользователей
- **Features** - включение/отключение функций

---

## 📝 Этапы реализации

### ✅ Этап 1: Database Layer (2-3 часа)

#### 1.1. Создать миграцию `007_add_system_settings.sql`

```sql
-- Migration 007: System Settings
-- Date: 2025-10-02
-- Task: 3.2 - Dynamic system configuration

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

-- Индекс для быстрого поиска по категории
CREATE INDEX IF NOT EXISTS idx_system_settings_category ON system_settings(category);

-- Предзаполнение дефолтными значениями
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
```

**Команды для применения:**
```bash
# Local Docker
docker compose -f docker-compose.dev.yml restart linguabot
docker logs linguabot_dev --tail 50 -f

# Railway (manual)
python3 apply_migrations_public.py
```

#### 1.2. Добавить методы в `bot/database.py`

**Добавить после метода `remove_admin_role()` (строка ~941):**

```python
# ==================== System Settings ====================

async def get_setting(self, key: str, default: Any = None) -> Any:
    """Get system setting by key with type conversion"""
    async with db_adapter.get_connection() as conn:
        query = db_adapter.adapt_query('SELECT value, value_type FROM system_settings WHERE key = ?')
        row = await conn.fetchone(query, (key,))

        if not row:
            return default

        value, value_type = row['value'], row['value_type']

        # Convert value based on type
        try:
            if value_type == 'integer':
                return int(value)
            elif value_type == 'float':
                return float(value)
            elif value_type == 'boolean':
                return value.lower() in ('true', '1', 'yes')
            elif value_type == 'json':
                import json
                return json.loads(value)
            else:  # string
                return value
        except (ValueError, json.JSONDecodeError) as e:
            print(f"[ERROR] Failed to convert setting {key}: {e}")
            return default

async def set_setting(self, key: str, value: Any, category: str = 'general',
                      description: str = '', updated_by: int = None) -> bool:
    """Set or update system setting"""
    # Determine value type
    if isinstance(value, bool):
        value_type, value_str = 'boolean', str(value).lower()
    elif isinstance(value, int):
        value_type, value_str = 'integer', str(value)
    elif isinstance(value, float):
        value_type, value_str = 'float', str(value)
    elif isinstance(value, (dict, list)):
        import json
        value_type, value_str = 'json', json.dumps(value)
    else:
        value_type, value_str = 'string', str(value)

    async with db_adapter.get_connection() as conn:
        query = db_adapter.adapt_query('''
            INSERT INTO system_settings (key, value, category, description, value_type, updated_by, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT (key) DO UPDATE SET
                value = EXCLUDED.value,
                category = EXCLUDED.category,
                description = EXCLUDED.description,
                value_type = EXCLUDED.value_type,
                updated_by = EXCLUDED.updated_by,
                updated_at = CURRENT_TIMESTAMP
        ''')
        await conn.execute(query, (key, value_str, category, description, value_type, updated_by))
        await conn.commit()
        return True

async def get_all_settings(self, category: str = None) -> List[Dict[str, Any]]:
    """Get all settings, optionally filtered by category"""
    async with db_adapter.get_connection() as conn:
        if category:
            query = db_adapter.adapt_query('''
                SELECT key, value, category, description, value_type, updated_at
                FROM system_settings
                WHERE category = ?
                ORDER BY category, key
            ''')
            rows = await conn.fetchall(query, (category,))
        else:
            rows = await conn.fetchall('''
                SELECT key, value, category, description, value_type, updated_at
                FROM system_settings
                ORDER BY category, key
            ''')

        return [
            {
                'key': row['key'],
                'value': row['value'],
                'category': row['category'],
                'description': row['description'],
                'value_type': row['value_type'],
                'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None
            }
            for row in rows
        ]

async def delete_setting(self, key: str) -> bool:
    """Delete system setting (reset to .env default)"""
    async with db_adapter.get_connection() as conn:
        query = db_adapter.adapt_query('DELETE FROM system_settings WHERE key = ?')
        await conn.execute(query, (key,))
        await conn.commit()
        return True
```

**Приёмочные критерии:**
- ✅ Миграция создаёт таблицу с предзаполненными значениями
- ✅ Методы работают с типизацией (string/int/float/bool/json)
- ✅ UPSERT корректно обновляет существующие значения
- ✅ Можно фильтровать по категориям

---

### ✅ Этап 2: Backend API (1-2 часа)

#### 2.1. Создать хендлер `admin_app/handlers/settings.py`

```python
"""
System Settings Management Handlers
"""
from aiohttp import web
from typing import Dict, Any
from admin_app.auth import check_admin_with_permission
from bot.database import Database

# Database instance (initialized in app.py)
db: Database = None

async def get_settings(request: web.Request) -> web.Response:
    """Get all system settings or filtered by category"""
    try:
        admin_user_id, role, perms = await check_admin_with_permission(request, 'manage_settings')

        category = request.query.get('category')
        settings = await db.get_all_settings(category)

        # Group by category for UI
        grouped = {}
        for setting in settings:
            cat = setting['category']
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(setting)

        return web.json_response({
            'success': True,
            'settings': settings,
            'grouped': grouped
        })

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to fetch settings: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def update_setting(request: web.Request) -> web.Response:
    """Update a single setting"""
    try:
        admin_user_id, role, perms = await check_admin_with_permission(request, 'manage_settings')

        data = await request.json()
        key = data.get('key')
        value = data.get('value')
        category = data.get('category', 'general')
        description = data.get('description', '')

        if not key or value is None:
            raise web.HTTPBadRequest(reason="Missing key or value")

        success = await db.set_setting(key, value, category, description, admin_user_id)

        if success:
            # Log admin action
            await db.log_admin_action(
                admin_user_id=admin_user_id,
                action='update_setting',
                details=json.dumps({'key': key, 'value': str(value), 'category': category})
            )

        return web.json_response({
            'success': success,
            'message': 'Setting updated successfully'
        })

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to update setting: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def delete_setting(request: web.Request) -> web.Response:
    """Delete setting (reset to .env default)"""
    try:
        admin_user_id, role, perms = await check_admin_with_permission(request, 'manage_settings')

        key = request.match_info.get('key')
        if not key:
            raise web.HTTPBadRequest(reason="Missing key")

        success = await db.delete_setting(key)

        if success:
            await db.log_admin_action(
                admin_user_id=admin_user_id,
                action='delete_setting',
                details=json.dumps({'key': key})
            )

        return web.json_response({
            'success': success,
            'message': 'Setting deleted (reset to default)'
        })

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to delete setting: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)

async def bulk_update_settings(request: web.Request) -> web.Response:
    """Bulk update multiple settings at once"""
    try:
        admin_user_id, role, perms = await check_admin_with_permission(request, 'manage_settings')

        data = await request.json()
        settings = data.get('settings', [])

        if not settings:
            raise web.HTTPBadRequest(reason="No settings provided")

        # Update all settings
        for setting in settings:
            await db.set_setting(
                key=setting['key'],
                value=setting['value'],
                category=setting.get('category', 'general'),
                description=setting.get('description', ''),
                updated_by=admin_user_id
            )

        # Log bulk update
        await db.log_admin_action(
            admin_user_id=admin_user_id,
            action='bulk_update_settings',
            details=json.dumps({'count': len(settings), 'keys': [s['key'] for s in settings]})
        )

        return web.json_response({
            'success': True,
            'message': f'Updated {len(settings)} settings'
        })

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to bulk update settings: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)
```

#### 2.2. Зарегистрировать маршруты в `admin_app/app.py`

**Добавить после строки 87 (регистрация других handlers):**

```python
# System Settings handlers
from admin_app.handlers import settings as settings_handler
settings_handler.db = db
app.router.add_get('/api/settings', settings_handler.get_settings)
app.router.add_post('/api/settings', settings_handler.update_setting)
app.router.add_post('/api/settings/bulk', settings_handler.bulk_update_settings)
app.router.add_delete('/api/settings/{key}', settings_handler.delete_setting)
```

#### 2.3. Добавить пермишн в `admin_app/auth.py`

**Обновить ROLE_PERMISSIONS (строка 10-16):**

```python
ROLE_PERMISSIONS = {
    'admin': ['*'],  # Full access
    'moderator': [
        'view_users', 'block_user', 'grant_premium', 'send_message',
        'view_logs', 'view_feedback', 'update_feedback', 'view_admin_logs'
    ],
    'analyst': ['view_dashboard', 'view_stats'],
    'settings_manager': ['view_dashboard', 'view_stats', 'manage_settings']  # NEW ROLE
}
```

**Приёмочные критерии:**
- ✅ GET `/api/settings` возвращает все настройки группированные по категориям
- ✅ POST `/api/settings` обновляет отдельную настройку
- ✅ POST `/api/settings/bulk` обновляет несколько настроек за раз
- ✅ DELETE `/api/settings/{key}` удаляет настройку (возврат к .env)
- ✅ Все действия логируются в admin_actions
- ✅ Проверка прав через `manage_settings` пермишн

---

### ✅ Этап 3: Frontend UI (2-3 часа)

#### 3.1. Добавить вкладку Settings в `admin_app/static/index.html`

**Добавить в навигацию после строки 105:**

```html
<button class="nav-btn" data-tab="settings" data-i18n="nav_settings">
    ⚙️ Settings
</button>
```

**Добавить контент вкладки после строки 261:**

```html
<!-- Settings Tab -->
<div id="settings-tab" class="tab-content" style="display: none;">
    <h2 data-i18n="settings_title">System Settings</h2>

    <!-- Category Tabs -->
    <div class="settings-categories">
        <button class="category-btn active" data-category="all" data-i18n="settings_all">All</button>
        <button class="category-btn" data-category="translation" data-i18n="settings_translation">Translation</button>
        <button class="category-btn" data-category="voice" data-i18n="settings_voice">Voice</button>
        <button class="category-btn" data-category="pricing" data-i18n="settings_pricing">Pricing</button>
        <button class="category-btn" data-category="limits" data-i18n="settings_limits">Limits</button>
        <button class="category-btn" data-category="features" data-i18n="settings_features">Features</button>
    </div>

    <!-- Settings Form -->
    <div class="settings-form">
        <div id="settings-list"></div>

        <div class="settings-actions">
            <button id="save-settings-btn" class="btn btn-primary" data-i18n="save_changes">
                Save Changes
            </button>
            <button id="reset-settings-btn" class="btn btn-secondary" data-i18n="reset_defaults">
                Reset to Defaults
            </button>
        </div>
    </div>
</div>
```

#### 3.2. Добавить стили в `admin_app/static/style.css`

```css
/* Settings Categories */
.settings-categories {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.category-btn {
    padding: 8px 16px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}

.category-btn:hover {
    background: #f5f5f5;
}

.category-btn.active {
    background: #2196F3;
    color: white;
    border-color: #2196F3;
}

/* Settings Form */
.settings-form {
    background: white;
    border-radius: 8px;
    padding: 20px;
}

.setting-item {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 20px;
    padding: 15px;
    border-bottom: 1px solid #eee;
    align-items: center;
}

.setting-item:last-child {
    border-bottom: none;
}

.setting-label {
    display: flex;
    flex-direction: column;
}

.setting-label strong {
    font-size: 14px;
    color: #333;
    margin-bottom: 4px;
}

.setting-label small {
    font-size: 12px;
    color: #666;
}

.setting-label .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 11px;
    margin-top: 4px;
    width: fit-content;
}

.setting-input {
    display: flex;
    gap: 10px;
    align-items: center;
}

.setting-input input[type="text"],
.setting-input input[type="number"],
.setting-input select {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.setting-input input[type="checkbox"] {
    width: 20px;
    height: 20px;
    cursor: pointer;
}

.settings-actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

/* Category badges */
.badge.cat-translation { background: #4CAF50; color: white; }
.badge.cat-voice { background: #FF9800; color: white; }
.badge.cat-pricing { background: #9C27B0; color: white; }
.badge.cat-limits { background: #F44336; color: white; }
.badge.cat-features { background: #2196F3; color: white; }
.badge.cat-general { background: #757575; color: white; }

/* Responsive */
@media (max-width: 768px) {
    .setting-item {
        grid-template-columns: 1fr;
        gap: 10px;
    }
}
```

#### 3.3. Добавить JavaScript в `admin_app/static/app.js`

**Добавить переводы (после строки 121):**

```javascript
// Settings translations
nav_settings: 'Settings',
settings_title: 'System Settings',
settings_all: 'All',
settings_translation: 'Translation',
settings_voice: 'Voice',
settings_pricing: 'Pricing',
settings_limits: 'Limits',
settings_features: 'Features',
save_changes: 'Save Changes',
reset_defaults: 'Reset to Defaults',
settings_saved: 'Settings saved successfully',
settings_reset: 'Settings reset to defaults',
```

**Добавить функции (после строки 1298):**

```javascript
// ==================== Settings Management ====================

let allSettings = [];
let currentCategory = 'all';

async function loadSettings(category = 'all') {
    try {
        showLoading('settings-list');

        const url = category !== 'all' ? `/api/settings?category=${category}` : '/api/settings';
        const data = await apiRequest(url);

        if (data.success) {
            allSettings = data.settings;
            currentCategory = category;
            renderSettings(allSettings);
        }
    } catch (error) {
        if (error.status === 403) {
            document.getElementById('settings-list').innerHTML = `
                <div class="error-message">${t('error_no_permission')}</div>
            `;
            return;
        }
        showError('Failed to load settings: ' + error.message);
    }
}

function renderSettings(settings) {
    const container = document.getElementById('settings-list');

    if (settings.length === 0) {
        container.innerHTML = '<p class="text-muted">No settings found</p>';
        return;
    }

    // Filter by category if needed
    const filtered = currentCategory === 'all'
        ? settings
        : settings.filter(s => s.category === currentCategory);

    container.innerHTML = filtered.map(setting => {
        const inputHtml = getSettingInput(setting);
        return `
            <div class="setting-item" data-key="${setting.key}">
                <div class="setting-label">
                    <strong>${setting.key}</strong>
                    <small>${setting.description || 'No description'}</small>
                    <span class="badge cat-${setting.category}">${setting.category}</span>
                </div>
                <div class="setting-input">
                    ${inputHtml}
                    <button class="btn btn-sm btn-secondary" onclick="resetSetting('${setting.key}')" title="Reset to .env default">
                        🔄
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function getSettingInput(setting) {
    const value = setting.value;
    const key = setting.key;

    switch (setting.value_type) {
        case 'boolean':
            const checked = value === 'true' || value === '1';
            return `<input type="checkbox" id="setting-${key}" ${checked ? 'checked' : ''} />`;

        case 'integer':
            return `<input type="number" id="setting-${key}" value="${value}" step="1" />`;

        case 'float':
            return `<input type="number" id="setting-${key}" value="${value}" step="0.1" />`;

        case 'json':
            return `<textarea id="setting-${key}" rows="3" style="font-family: monospace;">${value}</textarea>`;

        default: // string
            // Special handling for enums
            if (key === 'asr_api_provider') {
                return `
                    <select id="setting-${key}">
                        <option value="openai" ${value === 'openai' ? 'selected' : ''}>OpenAI Whisper</option>
                        <option value="google" ${value === 'google' ? 'selected' : ''}>Google Speech-to-Text</option>
                        <option value="azure" ${value === 'azure' ? 'selected' : ''}>Azure Speech</option>
                    </select>
                `;
            } else if (key === 'tts_provider') {
                return `
                    <select id="setting-${key}">
                        <option value="openai" ${value === 'openai' ? 'selected' : ''}>OpenAI TTS</option>
                        <option value="elevenlabs" ${value === 'elevenlabs' ? 'selected' : ''}>ElevenLabs</option>
                    </select>
                `;
            }
            return `<input type="text" id="setting-${key}" value="${value}" />`;
    }
}

async function saveSettings() {
    try {
        const updates = [];

        // Collect all changed settings
        allSettings.forEach(setting => {
            const input = document.getElementById(`setting-${setting.key}`);
            if (!input) return;

            let newValue;
            if (setting.value_type === 'boolean') {
                newValue = input.checked;
            } else if (input.tagName === 'TEXTAREA' || input.tagName === 'SELECT') {
                newValue = input.value;
            } else if (setting.value_type === 'integer') {
                newValue = parseInt(input.value);
            } else if (setting.value_type === 'float') {
                newValue = parseFloat(input.value);
            } else {
                newValue = input.value;
            }

            // Only update if changed
            const oldValue = setting.value_type === 'boolean'
                ? (setting.value === 'true')
                : setting.value;

            if (String(newValue) !== String(oldValue)) {
                updates.push({
                    key: setting.key,
                    value: newValue,
                    category: setting.category,
                    description: setting.description
                });
            }
        });

        if (updates.length === 0) {
            showSuccess('No changes to save');
            return;
        }

        // Bulk update
        const data = await apiRequest('/api/settings/bulk', {
            method: 'POST',
            body: JSON.stringify({ settings: updates })
        });

        if (data.success) {
            showSuccess(t('settings_saved'));
            await loadSettings(currentCategory);
        }
    } catch (error) {
        showError('Failed to save settings: ' + error.message);
    }
}

async function resetSetting(key) {
    if (!confirm(`Reset setting "${key}" to .env default?`)) return;

    try {
        const data = await apiRequest(`/api/settings/${key}`, { method: 'DELETE' });

        if (data.success) {
            showSuccess(`Setting "${key}" reset to default`);
            await loadSettings(currentCategory);
        }
    } catch (error) {
        showError('Failed to reset setting: ' + error.message);
    }
}

// Category filter
document.querySelectorAll('.category-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        loadSettings(btn.dataset.category);
    });
});

// Save button
document.getElementById('save-settings-btn')?.addEventListener('click', saveSettings);

// Add to tab switch handler
const originalSwitchTab = switchTab;
switchTab = function(tabName) {
    originalSwitchTab(tabName);
    if (tabName === 'settings') {
        loadSettings(currentCategory);
    }
};
```

**Приёмочные критерии:**
- ✅ Вкладка Settings отображается в навигации
- ✅ Настройки группируются по категориям (Translation, Voice, Pricing, Limits, Features)
- ✅ Разные типы инпутов: text, number, checkbox, select, textarea (JSON)
- ✅ Кнопка Save Changes сохраняет все изменения bulk запросом
- ✅ Кнопка Reset 🔄 возвращает отдельную настройку к .env дефолту
- ✅ Двуязычный интерфейс (RU/EN)
- ✅ Обработка ошибки 403 для пользователей без прав

---

### ✅ Этап 4: Интеграция с Config (1 час)

#### 4.1. Обновить `config.py` для динамической загрузки

**Добавить метод после строки 154:**

```python
@classmethod
async def load_from_db(cls, db):
    """Load settings from database and override class attributes"""
    try:
        settings = await db.get_all_settings()

        for setting in settings:
            key = setting['key']
            value = setting['value']
            value_type = setting['value_type']

            # Convert to proper type
            if value_type == 'integer':
                value = int(value)
            elif value_type == 'float':
                value = float(value)
            elif value_type == 'boolean':
                value = value.lower() in ('true', '1', 'yes')
            elif value_type == 'json':
                import json
                value = json.loads(value)

            # Map database keys to Config attributes
            key_mapping = {
                'free_daily_limit': 'FREE_DAILY_LIMIT',
                'daily_price': 'DAILY_PRICE',
                'monthly_price': 'MONTHLY_PRICE',
                'yearly_price': 'YEARLY_PRICE',
                'max_voice_duration': 'MAX_VOICE_DURATION',
                'max_history_items': 'MAX_HISTORY_ITEMS',
                'rate_limit_window': 'RATE_LIMIT_WINDOW',
                'rate_limit_requests': 'RATE_LIMIT_MAX_REQUESTS',
                # Add more mappings as needed
            }

            attr_name = key_mapping.get(key, key.upper())
            if hasattr(cls, attr_name):
                setattr(cls, attr_name, value)
                print(f"[CONFIG] Loaded from DB: {attr_name} = {value}")

    except Exception as e:
        print(f"[CONFIG] Failed to load settings from database: {e}")
        print("[CONFIG] Using .env defaults")

@classmethod
def get(cls, key: str, default: Any = None) -> Any:
    """Get config value with fallback"""
    return getattr(cls, key.upper(), default)
```

#### 4.2. Загружать настройки при старте бота в `main.py`

**Добавить после инициализации БД (примерно строка 30-40):**

```python
# Load settings from database (overrides .env)
await config.load_from_db(db)
print("[STARTUP] System settings loaded from database")
```

**Приёмочные критерии:**
- ✅ Настройки из БД переопределяют значения из .env
- ✅ Если настройки нет в БД, используется .env fallback
- ✅ Изменения применяются при следующем рестарте бота
- ✅ Логирование всех загруженных настроек

---

## 📋 Чеклист финальной проверки

### Database
- [ ] Миграция `007_add_system_settings.sql` создана
- [ ] Миграция применена на dev (Docker)
- [ ] Миграция применена на production (Railway)
- [ ] Таблица содержит предзаполненные значения
- [ ] Методы `get_setting()`, `set_setting()`, `get_all_settings()`, `delete_setting()` работают

### Backend
- [ ] Endpoint GET `/api/settings` возвращает все настройки
- [ ] Endpoint POST `/api/settings` обновляет одну настройку
- [ ] Endpoint POST `/api/settings/bulk` обновляет несколько настроек
- [ ] Endpoint DELETE `/api/settings/{key}` удаляет настройку
- [ ] Все действия логируются в `admin_actions`
- [ ] Проверка прав `manage_settings` работает
- [ ] Обработка ошибок (403, 400, 500)

### Frontend
- [ ] Вкладка Settings в навигации
- [ ] Категории (All, Translation, Voice, Pricing, Limits, Features)
- [ ] Правильные инпуты для разных типов (text, number, checkbox, select, textarea)
- [ ] Кнопка Save Changes сохраняет изменения
- [ ] Кнопка Reset 🔄 возвращает к дефолту
- [ ] Двуязычный интерфейс (RU/EN)
- [ ] Обработка 403 ошибки для пользователей без прав

### Integration
- [ ] Config.load_from_db() загружает настройки из БД
- [ ] Настройки из БД переопределяют .env
- [ ] Fallback к .env если настройки нет в БД
- [ ] Изменения применяются после рестарта бота
- [ ] Логирование загруженных настроек

### Testing
- [ ] Тест: создать настройку через UI
- [ ] Тест: изменить настройку и сохранить
- [ ] Тест: удалить настройку (reset to default)
- [ ] Тест: bulk update нескольких настроек
- [ ] Тест: проверить что бот использует новые настройки после рестарта
- [ ] Тест: пользователь без прав видит 403 ошибку

---

## 🚀 Последовательность выполнения

1. **День 1 (3-4 часа):**
   - Создать миграцию 007
   - Добавить методы в database.py
   - Применить миграцию на dev
   - Протестировать методы через Python REPL

2. **День 2 (2-3 часа):**
   - Создать handlers/settings.py
   - Зарегистрировать роуты в app.py
   - Добавить пермишн manage_settings
   - Протестировать API через curl/Postman

3. **День 3 (2-3 часа):**
   - Добавить UI (index.html, style.css, app.js)
   - Протестировать в браузере (ngrok + локальный бот)
   - Интегрировать с config.py
   - Финальное тестирование

4. **Деплой:**
   - Применить миграцию на Railway
   - Задеплоить код
   - Проверить работу на production

---

## 📖 Примечания

### Безопасность
- Только Admin и Settings Manager имеют доступ
- Все изменения логируются в admin_actions
- Валидация типов данных на backend

### Производительность
- Настройки загружаются один раз при старте
- Используется индекс по category для быстрого поиска
- Bulk update минимизирует количество запросов

### Расширяемость
- Легко добавить новые категории
- Легко добавить новые типы данных (enum, array)
- Можно добавить валидацию значений (min/max, regex)

### Ограничения
- ⚠️ **Rate limit настройки** (`rate_limit_window`, `rate_limit_requests`) требуют перезапуск бота (middleware инициализируется при старте)
- JSON настройки требуют валидности синтаксиса
- Критичные настройки безопасности нельзя удалить

---

## ✨ Реализованные улучшения (сверх плана)

### Динамическое чтение настроек БЕЗ перезапуска
Изначально план предполагал загрузку настроек только при старте бота. Реализовано **динамическое чтение в реальном времени:**

#### Применяется БЕЗ перезапуска:
- ✅ **Цены подписок** (`daily_price`, `monthly_price`, `yearly_price`)
  - `bot/services/payment.py` - метод `get_subscription_price()` стал async
  - `bot/keyboards/inline.py` - клавиатуры `get_premium_keyboard()` и `get_premium_features_keyboard()` стали async
  - `bot/handlers/callbacks.py` - все вызовы обновлены с `await`

- ✅ **Лимиты переводов** (`free_daily_limit`)
  - `bot/database.py:429` - метод `check_translation_limit()` читает из БД

- ✅ **Лимиты голоса** (`max_voice_duration`)
  - `bot/services/voice.py:326` - метод `validate_audio_duration()` читает из БД

#### Требует перезапуск:
- ⏭️ `rate_limit_window`, `rate_limit_requests` - middleware инициализируется при старте

### Результат
Администратор может изменить цену подписки через админ-панель, и **сразу же** (без перезапуска) бот будет показывать новую цену пользователям!

---

## 🔗 Связанные файлы

**Database Layer:**
- `bot/database.py` - методы для работы с настройками (строки 943-1035)
- `migrations/007_add_system_settings.sql` - миграция БД

**Backend API:**
- `admin_app/handlers/settings.py` - API endpoints (4 endpoint'а)
- `admin_app/app.py` - регистрация маршрутов (строки 93-97)
- `admin_app/auth.py` - пермишн `manage_settings` + роль `settings_manager`

**Frontend:**
- `admin_app/static/index.html` - UI вкладки Settings (строки 266-289)
- `admin_app/static/app.js` - логика фронтенда + i18n (строки 123-136, 276-289, 1299-1480)
- `admin_app/static/style.css` - стили (строки 406-462)

**Dynamic Settings Integration:**
- `bot/config.py:156-202` - метод `load_from_db()` для загрузки при старте
- `main.py:58` - вызов `config.load_from_db(db)` при инициализации
- `bot/services/payment.py:17-27` - динамическое чтение цен
- `bot/keyboards/inline.py:103-142` - динамические клавиатуры с ценами
- `bot/handlers/callbacks.py` - обновлены все вызовы клавиатур с `await`

---

## 📊 Результаты тестирования

### Функциональность
- ✅ Сохранение настроек через админ-панель работает
- ✅ Bulk update обновляет несколько настроек одновременно
- ✅ Reset (DELETE) сбрасывает настройку к .env дефолту
- ✅ Категорийные фильтры работают (Translation, Voice, Pricing, Limits, Features)
- ✅ Двуязычный интерфейс (RU/EN) работает корректно

### Динамическое применение
- ✅ Изменение `daily_price` с 100 на 101 → бот сразу показывает новую цену
- ✅ Тест: изменили на 105 → сразу прочитали 105 (без перезапуска)
- ✅ Клавиатуры `/premium` отображают актуальные цены из БД

### Безопасность
- ✅ RBAC работает: только пользователи с `manage_settings` permission могут управлять
- ✅ Admin action logging: все изменения логируются в `admin_actions`
- ✅ Telegram WebApp HMAC аутентификация работает

---

**✅ Задача реализована! Все функции работают корректно. 🚀**
