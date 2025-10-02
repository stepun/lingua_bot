// Dashboard Module

import { apiRequest, showLoading, hideLoading, tg } from './api.js';
import { formatDate, formatDuration, getLanguageName } from './utils.js';
import { t } from './i18n.js';

// Load Dashboard
export async function loadDashboard() {
    try {
        showLoading();

        // Load overall stats
        const stats = await apiRequest('/api/stats/');
        document.getElementById('totalUsers').textContent = stats.total_users;
        document.getElementById('premiumUsers').textContent = stats.premium_users;
        document.getElementById('activeToday').textContent = stats.active_today;
        document.getElementById('translationsToday').textContent = stats.translations_today;

        // Load daily stats
        const dailyData = await apiRequest('/api/stats/daily?days=7');
        renderDailyStats(dailyData.stats);

        // Load language stats
        const langData = await apiRequest('/api/stats/languages');
        renderLanguageStats(langData);

        // Load performance stats
        const perfData = await apiRequest('/api/stats/performance');
        renderPerformanceStats(perfData);

        hideLoading();
    } catch (error) {
        hideLoading();
        tg.showAlert(`Error loading dashboard: ${error.message}`);
    }
}

// Render daily stats
function renderDailyStats(data) {
    const container = document.getElementById('dailyStats');
    container.innerHTML = data.map(stat => `
        <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg text-sm">
            <span class="font-semibold text-gray-800">${formatDate(stat.date)}</span>
            <div class="flex gap-3 text-xs text-gray-600">
                <span>👥 ${stat.users}</span>
                <span>💬 ${stat.translations}</span>
            </div>
        </div>
    `).join('');
}

// Render language stats
function renderLanguageStats(data) {
    const sourceLangs = document.getElementById('sourceLangs');
    const targetLangs = document.getElementById('targetLangs');

    sourceLangs.innerHTML = data.source_languages.map(lang => `
        <div class="flex justify-between py-2 border-b border-gray-200 last:border-0 text-sm text-gray-800">
            <span>${getLanguageName(lang.lang)}</span>
            <span class="font-bold">${lang.count}</span>
        </div>
    `).join('') || `<div class="text-sm text-gray-500">${t('common.no_data')}</div>`;

    targetLangs.innerHTML = data.target_languages.map(lang => `
        <div class="flex justify-between py-2 border-b border-gray-200 last:border-0 text-sm text-gray-800">
            <span>${getLanguageName(lang.lang)}</span>
            <span class="font-bold">${lang.count}</span>
        </div>
    `).join('') || `<div class="text-sm text-gray-500">${t('common.no_data')}</div>`;
}

// Render performance stats
function renderPerformanceStats(data) {
    // Average processing time
    const avgTime = data.average_processing_time.overall;
    document.getElementById('avgProcessingTime').textContent = formatDuration(avgTime);
    document.getElementById('avgProcessingDetails').textContent =
        `${t('perf.voice')}: ${formatDuration(data.average_processing_time.voice)} | ${t('perf.text')}: ${formatDuration(data.average_processing_time.text)}`;

    // Success rate
    document.getElementById('successRate').textContent = `${data.success_rate}%`;
    document.getElementById('successDetails').textContent =
        `${data.successful_translations} / ${data.total_translations} ${t('perf.translations')}`;

    // Errors by day
    const errorsContainer = document.getElementById('errorsByDay');
    if (data.errors_by_day && data.errors_by_day.length > 0) {
        errorsContainer.innerHTML = data.errors_by_day.map(error => `
            <div class="flex justify-between items-center p-2 bg-white rounded text-sm">
                <span class="text-gray-700">${formatDate(error.date)}</span>
                <span class="font-bold text-red-600">${error.count} ${t('perf.errors')}</span>
            </div>
        `).join('');
    } else {
        errorsContainer.innerHTML = `<div class="text-sm text-gray-500 text-center py-2">${t('perf.no_errors')}</div>`;
    }
}
