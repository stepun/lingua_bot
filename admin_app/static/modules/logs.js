// Logs Module

import { apiRequest, showLoading, hideLoading, tg } from './api.js';
import { formatDateTime } from './utils.js';
import { t } from './i18n.js';

// Load Logs
export async function loadLogs() {
    try {
        showLoading();

        // Get filter and search values
        const filterSelect = document.getElementById('logFilter');
        const filterValue = filterSelect ? filterSelect.value : '';
        const searchInput = document.getElementById('logSearch');
        const searchValue = searchInput ? searchInput.value.trim() : '';

        // Build URL with filter and search
        let url = '/api/logs/translations?per_page=20';
        if (filterValue) {
            url += `&filter=${filterValue}`;
        }
        if (searchValue) {
            url += `&search=${encodeURIComponent(searchValue)}`;
        }

        // Load translation logs
        const logsData = await apiRequest(url);
        renderTranslationLogs(logsData.logs);

        hideLoading();
    } catch (error) {
        hideLoading();
        if (error.status === 403) {
            document.getElementById('logsList').innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-600 mb-2">🔒 ${error.message}</p>
                    <p class="text-sm text-gray-500">This tab is not available for your role</p>
                </div>
            `;
        } else {
            tg.showAlert(`Error loading logs: ${error.message}`);
        }
    }
}

// Render translation logs
export function renderTranslationLogs(logs) {
    const container = document.getElementById('translationLogs');

    container.innerHTML = logs.map(log => `
        <div class="bg-white p-3 rounded-lg border-l-4 border-blue-500 text-xs">
            <div class="flex justify-between mb-1.5 font-semibold text-gray-900">
                <span>${log.username || 'User'}</span>
                <span class="text-gray-500">${formatDateTime(log.created_at)}</span>
            </div>
            <div class="text-gray-600">
                ${log.source_lang || 'auto'} → ${log.target_lang || 'en'}
                ${log.is_voice ? '🎤' : '💬'}
                <br>
                <span class="text-xs">${(log.source_text || '').substring(0, 50)}...</span>
            </div>
        </div>
    `).join('') || `<p class="text-sm text-gray-500">${t('common.no_data')}</p>`;
}
