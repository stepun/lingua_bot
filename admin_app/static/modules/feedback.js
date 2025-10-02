// Feedback Module

import { apiRequest, showLoading, hideLoading, tg } from './api.js';
import { formatDateTime } from './utils.js';
import { t } from './i18n.js';

// Load Feedback
export async function loadFeedback() {
    try {
        showLoading();

        // Get filter value
        const filterSelect = document.getElementById('feedbackStatusFilter');
        const filterValue = filterSelect ? filterSelect.value : '';

        // Build URL with filter
        let url = '/api/feedback?limit=100';
        if (filterValue) {
            url += `&status=${filterValue}`;
        }

        const data = await apiRequest(url);
        renderFeedback(data.feedback);

        hideLoading();
    } catch (error) {
        hideLoading();
        if (error.status === 403) {
            document.getElementById('feedbackList').innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-600 mb-2">🔒 ${error.message}</p>
                    <p class="text-sm text-gray-500">This tab is not available for your role</p>
                </div>
            `;
        } else {
            tg.showAlert(`Error loading feedback: ${error.message}`);
        }
    }
}

// Render feedback list
function renderFeedback(feedbackList) {
    const container = document.getElementById('feedbackList');

    if (feedbackList.length === 0) {
        container.innerHTML = `<div class="text-center text-gray-500 py-8">${t('common.no_data')}</div>`;
        return;
    }

    container.innerHTML = feedbackList.map(fb => {
        const statusColors = {
            'new': 'bg-blue-100 text-blue-800',
            'reviewed': 'bg-yellow-100 text-yellow-800',
            'resolved': 'bg-green-100 text-green-800'
        };

        const statusColor = statusColors[fb.status] || 'bg-gray-100 text-gray-800';
        const statusText = t(`feedback.status_${fb.status}`);

        return `
            <div class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <span class="font-semibold text-gray-900">@${fb.username}</span>
                        <span class="text-xs text-gray-500 ml-2">${fb.user_name}</span>
                    </div>
                    <span class="px-2 py-1 rounded-full text-xs font-medium ${statusColor} uppercase">${statusText}</span>
                </div>
                <div class="text-sm text-gray-800 mb-3 whitespace-pre-wrap">${fb.message}</div>
                <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-500">📅 ${formatDateTime(fb.created_at)}</span>
                    <div class="flex gap-2">
                        ${fb.status === 'new' ? `
                            <button onclick="window.updateFeedbackStatus(${fb.id}, 'reviewed')"
                                    class="px-3 py-1 bg-yellow-500 text-white rounded text-xs font-medium hover:bg-yellow-600 transition">
                                ${t('feedback.mark_reviewed')}
                            </button>
                        ` : ''}
                        ${fb.status === 'reviewed' ? `
                            <button onclick="window.updateFeedbackStatus(${fb.id}, 'resolved')"
                                    class="px-3 py-1 bg-green-500 text-white rounded text-xs font-medium hover:bg-green-600 transition">
                                ${t('feedback.mark_resolved')}
                            </button>
                        ` : ''}
                        ${fb.status === 'resolved' ? `
                            <span class="text-xs text-green-600 font-medium">✓ ${t('feedback.filter_resolved')}</span>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Update feedback status
export async function updateFeedbackStatus(feedbackId, newStatus) {
    try {
        showLoading();
        const result = await apiRequest(`/api/feedback/${feedbackId}/status`, {
            method: 'POST',
            body: JSON.stringify({ status: newStatus })
        });
        hideLoading();
        tg.showAlert(result.message || 'Status updated successfully!');
        loadFeedback();
    } catch (error) {
        hideLoading();
        tg.showAlert(`Error: ${error.message}`);
    }
}
