// Settings Module

import { apiRequest, showLoading, hideLoading, tg } from './api.js';
import { t } from './i18n.js';

let allSettings = [];
let currentCategory = 'all';

export async function loadSettings(category = 'all') {
    try {
        showLoading();

        const url = category !== 'all' ? `/api/settings?category=${category}` : '/api/settings';
        const data = await apiRequest(url);

        if (data.success) {
            allSettings = data.settings;
            currentCategory = category;
            renderSettings(allSettings);
        }
    } catch (error) {
        if (error.status === 403) {
            document.getElementById('settingsList').innerHTML = `
                <div class="text-center py-8 text-gray-500">${t('error.no_permission')}</div>
            `;
            hideLoading();
            return;
        }
        tg.showAlert(`Error loading settings: ${error.message}`);
    } finally {
        hideLoading();
    }
}

function renderSettings(settings) {
    const container = document.getElementById('settingsList');

    // Filter by category
    const filtered = currentCategory === 'all'
        ? settings
        : settings.filter(s => s.category === currentCategory);

    if (filtered.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-500 py-4">No settings found</p>';
        return;
    }

    container.innerHTML = filtered.map(setting => {
        const inputHtml = getSettingInput(setting);
        return `
            <div class="setting-item" data-key="${setting.key}">
                <div class="setting-label">
                    <strong class="text-sm text-gray-800">${setting.key}</strong>
                    <small class="text-xs text-gray-500">${setting.description || 'No description'}</small>
                    <span class="badge cat-${setting.category} inline-block px-2 py-1 rounded text-xs mt-1">${setting.category}</span>
                </div>
                <div class="setting-input flex gap-2 items-center">
                    ${inputHtml}
                    <button onclick="window.resetSetting('${setting.key}')" class="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300" title="Reset to .env default">
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
            return `<input type="checkbox" id="setting-${key}" ${checked ? 'checked' : ''} class="w-5 h-5" />`;

        case 'integer':
            return `<input type="number" id="setting-${key}" value="${value}" step="1" class="flex-1" />`;

        case 'float':
            return `<input type="number" id="setting-${key}" value="${value}" step="0.1" class="flex-1" />`;

        case 'json':
            return `<textarea id="setting-${key}" rows="3" class="flex-1 font-mono text-xs">${value}</textarea>`;

        case 'secret':
            // Password input with show/hide toggle
            const displayValue = value || '';
            const maskedValue = value ? '••••••••••••••••' : '';
            return `
                <div class="flex-1 flex gap-2">
                    <input type="password" id="setting-${key}" value="${displayValue}"
                           class="flex-1 font-mono text-sm"
                           placeholder="${maskedValue || 'Enter API key...'}" />
                    <button type="button" onclick="toggleSecretVisibility('${key}')"
                            class="px-3 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300"
                            title="Show/Hide">
                        👁️
                    </button>
                </div>
            `;

        default: // string
            // Special handling for enums
            if (key === 'asr_api_provider') {
                return `
                    <select id="setting-${key}" class="flex-1">
                        <option value="openai" ${value === 'openai' ? 'selected' : ''}>OpenAI Whisper</option>
                        <option value="google" ${value === 'google' ? 'selected' : ''}>Google Speech-to-Text</option>
                        <option value="azure" ${value === 'azure' ? 'selected' : ''}>Azure Speech</option>
                    </select>
                `;
            } else if (key === 'tts_provider') {
                return `
                    <select id="setting-${key}" class="flex-1">
                        <option value="openai" ${value === 'openai' ? 'selected' : ''}>OpenAI TTS</option>
                        <option value="elevenlabs" ${value === 'elevenlabs' ? 'selected' : ''}>ElevenLabs</option>
                    </select>
                `;
            }
            return `<input type="text" id="setting-${key}" value="${value}" class="flex-1" />`;
    }
}

export async function saveSettings() {
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
            tg.showAlert(t('settings.no_changes'));
            return;
        }

        showLoading();

        // Bulk update
        const data = await apiRequest('/api/settings/bulk', {
            method: 'POST',
            body: JSON.stringify({ settings: updates })
        });

        if (data.success) {
            tg.showAlert(t('settings.saved'));
            await loadSettings(currentCategory);
        }
    } catch (error) {
        tg.showAlert(`${t('settings.error')}: ${error.message}`);
    } finally {
        hideLoading();
    }
}

export async function resetSetting(key) {
    if (!confirm(`Reset setting "${key}" to .env default?`)) return;

    try {
        showLoading();
        const data = await apiRequest(`/api/settings/${key}`, { method: 'DELETE' });

        if (data.success) {
            tg.showAlert(`Setting "${key}" reset to default`);
            await loadSettings(currentCategory);
        }
    } catch (error) {
        tg.showAlert(`Error resetting setting: ${error.message}`);
    } finally {
        hideLoading();
    }
}

// Export current category for external access
export function getCurrentCategory() {
    return currentCategory;
}

// Toggle password visibility for secret fields
window.toggleSecretVisibility = function(key) {
    const input = document.getElementById(`setting-${key}`);
    if (!input) return;

    input.type = input.type === 'password' ? 'text' : 'password';
};
