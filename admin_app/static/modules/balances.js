// API Balances Module

import { apiRequest, showLoading, hideLoading, tg } from './api.js';
import { t } from './i18n.js';

export async function loadBalances() {
    try {
        showLoading();

        const data = await apiRequest('/api/balances');

        if (data.success) {
            renderBalances(data.balances);
        }
    } catch (error) {
        if (error.status === 403) {
            document.getElementById('balancesList').innerHTML = `
                <div class="col-span-2 text-center py-8 text-gray-500">${t('error.no_permission')}</div>
            `;
            hideLoading();
            return;
        }
        tg.showAlert(`Error loading balances: ${error.message}`);
    } finally {
        hideLoading();
    }
}

function renderBalances(balances) {
    const container = document.getElementById('balancesList');

    const cards = [];

    // OpenAI
    if (balances.openai) {
        cards.push(renderBalanceCard('openai', 'OpenAI', balances.openai, 'https://platform.openai.com/'));
    }

    // DeepL
    if (balances.deepl) {
        cards.push(renderBalanceCard('deepl', 'DeepL', balances.deepl, 'https://www.deepl.com/pro-api'));
    }

    // ElevenLabs
    if (balances.elevenlabs) {
        cards.push(renderBalanceCard('elevenlabs', 'ElevenLabs', balances.elevenlabs, 'https://elevenlabs.io/'));
    }

    // Yandex
    if (balances.yandex) {
        cards.push(renderBalanceCard('yandex', 'Yandex Translate', balances.yandex, 'https://cloud.yandex.com/'));
    }

    container.innerHTML = cards.join('');
}

function renderBalanceCard(service, name, balance, link) {
    if (balance.error) {
        return `
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-semibold text-gray-800">${name}</h3>
                    <a href="${link}" target="_blank" class="text-blue-500 hover:text-blue-600 text-sm">🔗</a>
                </div>
                <p class="text-sm text-red-500">${balance.error}</p>
            </div>
        `;
    }

    // OpenAI format (status check)
    if (balance.status !== undefined) {
        const statusColor = balance.status === 'Active' ? 'text-green-700' : 'text-gray-600';
        const bgGradient = balance.status === 'Active' ? 'from-green-50 to-green-100' : 'from-gray-50 to-gray-100';
        const borderColor = balance.status === 'Active' ? 'border-green-200' : 'border-gray-200';

        return `
            <div class="bg-gradient-to-br ${bgGradient} rounded-lg p-4 border ${borderColor}">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-semibold text-gray-800">${name}</h3>
                </div>
                <div class="mb-2">
                    <span class="text-lg font-bold ${statusColor}">✓ ${balance.status}</span>
                    ${balance.models_available ? `<span class="text-sm text-gray-600 ml-2">(${balance.models_available} models)</span>` : ''}
                </div>
                <p class="text-xs text-gray-600 mb-3">${balance.info}</p>
                <a href="${balance.link || link}" target="_blank"
                   class="inline-block px-3 py-1.5 bg-blue-500 text-white text-xs font-medium rounded hover:bg-blue-600 transition">
                    💰 ${t('balances.view_balance')}
                </a>
            </div>
        `;
    }

    // DeepL / ElevenLabs format (character-based)
    if (balance.used !== undefined && balance.limit !== undefined) {
        const progressColor = balance.percentage > 80 ? 'bg-red-500' : balance.percentage > 50 ? 'bg-yellow-500' : 'bg-green-500';

        return `
            <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-semibold text-gray-800">${name}</h3>
                </div>
                ${balance.tier ? `<p class="text-xs text-gray-600 mb-2">${t('balances.tier')}: ${balance.tier}</p>` : ''}
                <div class="mb-3">
                    <div class="flex justify-between text-sm mb-1">
                        <span class="text-gray-600">${t('balances.used')}: ${formatNumber(balance.used)} ${balance.unit}</span>
                        <span class="font-semibold text-gray-800">${balance.percentage}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="${progressColor} h-2 rounded-full transition-all" style="width: ${balance.percentage}%"></div>
                    </div>
                </div>
                <div class="flex justify-between items-center text-xs">
                    <div class="text-gray-600">
                        <div>${t('balances.remaining')}: ${formatNumber(balance.remaining)}</div>
                        <div>${t('balances.limit')}: ${formatNumber(balance.limit)}</div>
                    </div>
                    <a href="${link}" target="_blank"
                       class="px-3 py-1.5 bg-blue-500 text-white text-xs font-medium rounded hover:bg-blue-600 transition whitespace-nowrap">
                        🔗 ${t('balances.view_details')}
                    </a>
                </div>
            </div>
        `;
    }

    // Yandex format (info only)
    if (balance.info) {
        return `
            <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                <div class="flex justify-between items-start mb-2">
                    <h3 class="font-semibold text-gray-800">${name}</h3>
                </div>
                <p class="text-sm text-gray-600 mb-3">${balance.info}</p>
                <a href="${balance.link || link}" target="_blank"
                   class="inline-block px-3 py-1.5 bg-blue-500 text-white text-xs font-medium rounded hover:bg-blue-600 transition">
                    🔗 ${t('balances.view_console')}
                </a>
            </div>
        `;
    }

    return '';
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Export for global access
window.loadBalances = loadBalances;
