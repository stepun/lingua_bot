// Admin Logs Module

import { apiRequest, showLoading, hideLoading, tg } from './api.js';
import { formatDateTime } from './utils.js';
import { t } from './i18n.js';

// Load Admin Logs
export async function loadAdminLogs() {
    try {
        showLoading();

        // Get filter values
        const adminFilter = document.getElementById('adminLogsAdminFilter');
        const actionFilter = document.getElementById('adminLogsActionFilter');
        const adminValue = adminFilter ? adminFilter.value : '';
        const actionValue = actionFilter ? actionFilter.value : '';

        // Build URL with filters
        let url = '/api/admin-logs?limit=100';
        if (adminValue) {
            url += `&admin_user_id=${adminValue}`;
        }
        if (actionValue) {
            url += `&action=${actionValue}`;
        }

        const data = await apiRequest(url);
        renderAdminLogs(data.logs);
        populateAdminFilter(data.logs);

        hideLoading();
    } catch (error) {
        hideLoading();
        if (error.status === 403) {
            document.getElementById('adminLogsList').innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-600 mb-2">🔒 ${error.message}</p>
                    <p class="text-sm text-gray-500">This tab is not available for your role</p>
                </div>
            `;
        } else {
            tg.showAlert(`Error loading admin logs: ${error.message}`);
        }
    }
}

// Render admin logs list
function renderAdminLogs(logs) {
    const container = document.getElementById('adminLogsList');

    if (logs.length === 0) {
        container.innerHTML = `<div class="text-center text-gray-500 py-8">${t('common.no_data')}</div>`;
        return;
    }

    container.innerHTML = logs.map(log => {
        const actionColors = {
            'grant_premium': 'bg-green-100 text-green-800',
            'revoke_premium': 'bg-red-100 text-red-800',
            'ban_user': 'bg-red-100 text-red-800',
            'unban_user': 'bg-green-100 text-green-800',
            'send_message': 'bg-purple-100 text-purple-800',
            'update_feedback': 'bg-blue-100 text-blue-800',
            'view_history': 'bg-gray-100 text-gray-800'
        };

        const actionColor = actionColors[log.action] || 'bg-gray-100 text-gray-800';
        const actionText = log.action.replace(/_/g, ' ').toUpperCase();

        let detailsHtml = '';
        if (log.details && Object.keys(log.details).length > 0) {
            detailsHtml = `<div class="mt-2 text-xs text-gray-600 bg-gray-50 p-2 rounded">
                ${Object.entries(log.details).map(([key, value]) =>
                    `<div><strong>${key}:</strong> ${value}</div>`
                ).join('')}
            </div>`;
        }

        return `
            <div class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <span class="font-semibold text-gray-900">@${log.admin_username}</span>
                        <span class="text-xs text-gray-500 ml-2">${log.admin_name}</span>
                    </div>
                    <span class="px-2 py-1 rounded-full text-xs font-medium ${actionColor}">${actionText}</span>
                </div>
                ${log.target_user_id ? `
                    <div class="text-sm text-gray-700 mb-2">
                        <span class="text-gray-500">Target:</span>
                        <span class="font-medium">@${log.target_username}</span>
                        <span class="text-xs text-gray-500 ml-1">${log.target_name}</span>
                    </div>
                ` : ''}
                ${detailsHtml}
                <div class="flex justify-between items-center mt-2">
                    <span class="text-xs text-gray-500">📅 ${formatDateTime(log.created_at)}</span>
                </div>
            </div>
        `;
    }).join('');
}

// Populate admin filter dropdown
function populateAdminFilter(logs) {
    const filterSelect = document.getElementById('adminLogsAdminFilter');
    if (!filterSelect) return;

    // Get unique admins
    const admins = new Map();
    logs.forEach(log => {
        if (!admins.has(log.admin_user_id)) {
            admins.set(log.admin_user_id, {
                username: log.admin_username,
                name: log.admin_name
            });
        }
    });

    // Keep existing "All admins" option
    const currentValue = filterSelect.value;
    const allOption = filterSelect.querySelector('option[value=""]');
    filterSelect.innerHTML = '';
    filterSelect.appendChild(allOption);

    // Add admin options
    admins.forEach((admin, userId) => {
        const option = document.createElement('option');
        option.value = userId;
        option.textContent = `@${admin.username} (${admin.name})`;
        filterSelect.appendChild(option);
    });

    filterSelect.value = currentValue;
}
