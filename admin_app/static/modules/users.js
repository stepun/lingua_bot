// Users Module

import { apiRequest, showLoading, hideLoading, tg } from './api.js';
import { formatDate, formatDateTime } from './utils.js';
import { t } from './i18n.js';

// Global state
let currentPage = 1;
let currentMessageUserId = null;

// Load Users
export async function loadUsers(page = 1) {
    try {
        showLoading();
        currentPage = page;

        const search = document.getElementById('userSearch').value;
        const premiumOnly = document.getElementById('premiumFilter').checked;

        let url = `/api/users/?page=${page}&per_page=20`;
        if (search) url += `&search=${encodeURIComponent(search)}`;
        if (premiumOnly) url += `&premium_only=true`;

        const data = await apiRequest(url);
        renderUsers(data);

        hideLoading();
    } catch (error) {
        hideLoading();
        if (error.status === 403) {
            document.getElementById('usersList').innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-600 mb-2">🔒 ${error.message}</p>
                    <p class="text-sm text-gray-500">This tab is not available for your role</p>
                </div>
            `;
        } else {
            tg.showAlert(`Error loading users: ${error.message}`);
        }
    }
}

// Render users
function renderUsers(data) {
    const container = document.getElementById('usersList');

    container.innerHTML = data.users.map(user => `
        <div class="bg-white p-3 rounded-lg shadow-sm border border-gray-100 ${user.is_blocked ? 'opacity-60' : ''}">
            <div class="flex justify-between items-center mb-2 flex-wrap gap-2">
                <span class="font-semibold text-base text-gray-900">${user.name || user.username || 'User'}</span>
                <div class="flex gap-2">
                    ${user.is_premium ? `<span class="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-2 py-1 rounded-full text-xs font-semibold">${t('users.premium_badge')}</span>` : ''}
                    ${user.is_blocked ? `<span class="bg-red-500 text-white px-2 py-1 rounded-full text-xs font-semibold">${t('users.blocked_badge')}</span>` : ''}
                </div>
            </div>
            <div class="text-xs text-gray-600 mb-2">
                ID: ${user.id} |
                ${t('users.translations')}: ${user.total_translations} |
                ${t('users.joined')}: ${formatDate(user.created_at)}
            </div>
            <div class="flex gap-2 flex-wrap">
                <button class="px-3 py-1.5 bg-blue-500 text-white rounded-lg text-xs font-medium hover:bg-blue-600 transition" onclick="window.viewUser(${user.id})">${t('users.view')}</button>
                ${!user.is_premium ?
                    `<button class="px-3 py-1.5 bg-gray-100 text-gray-800 rounded-lg text-xs font-medium hover:bg-gray-200 transition" onclick="window.grantPremium(${user.id})">${t('users.grant_premium')}</button>` :
                    ''
                }
                <button class="px-3 py-1.5 bg-purple-500 text-white rounded-lg text-xs font-medium hover:bg-purple-600 transition" onclick="window.openSendMessageModal(${user.id}, '${(user.name || user.username || 'User').replace(/'/g, "\\'")}')">${t('users.send_message')}</button>
                ${!user.is_blocked ?
                    `<button class="px-3 py-1.5 bg-red-500 text-white rounded-lg text-xs font-medium hover:bg-red-600 transition" onclick="window.blockUser(${user.id})">${t('users.block')}</button>` :
                    `<button class="px-3 py-1.5 bg-green-500 text-white rounded-lg text-xs font-medium hover:bg-green-600 transition" onclick="window.unblockUser(${user.id})">${t('users.unblock')}</button>`
                }
            </div>
        </div>
    `).join('');

    // Update pagination
    const totalPages = Math.ceil(data.total / data.per_page);
    document.getElementById('pageInfo').textContent = `${t('pagination.page')} ${data.page} ${t('pagination.of')} ${totalPages}`;
    document.getElementById('prevPage').disabled = data.page === 1;
    document.getElementById('nextPage').disabled = data.page >= totalPages;
}

// View user details with history
export async function viewUser(userId) {
    try {
        showLoading();

        // Get user history
        const historyData = await apiRequest(`/api/users/${userId}/history?limit=10`);

        hideLoading();

        // Show modal with history
        const modal = document.getElementById('userHistoryModal');
        const content = document.getElementById('historyContent');

        if (historyData.history && historyData.history.length > 0) {
            content.innerHTML = historyData.history.map(item => `
                <div class="bg-gray-50 p-3 rounded-lg border border-gray-200">
                    <div class="flex justify-between items-center mb-2 text-xs text-gray-600">
                        <span>${formatDateTime(item.created_at)}</span>
                        <span>${item.source_lang} → ${item.target_lang} ${item.is_voice ? '🎤' : '💬'}</span>
                    </div>
                    <div class="text-sm">
                        <div class="font-semibold text-gray-700 mb-1">Original:</div>
                        <div class="text-gray-600 mb-2">${item.source_text}</div>
                        <div class="font-semibold text-gray-700 mb-1">Translation:</div>
                        <div class="text-gray-900">${item.translation}</div>
                    </div>
                </div>
            `).join('');
        } else {
            content.innerHTML = '<p class="text-center text-gray-500">No translation history found</p>';
        }

        modal.classList.remove('hidden');
    } catch (error) {
        hideLoading();
        tg.showAlert(`Error loading history: ${error.message}`);
    }
}

// Close history modal
export function closeHistoryModal() {
    document.getElementById('userHistoryModal').classList.add('hidden');
}

// Grant premium
export async function grantPremium(userId) {
    try {
        showLoading();
        await apiRequest(`/api/users/${userId}/premium`, { method: 'POST' });
        hideLoading();
        tg.showAlert('Premium granted for 1 day!');
        loadUsers(currentPage);
    } catch (error) {
        hideLoading();
        tg.showAlert(`Error: ${error.message}`);
    }
}

// Block user
export async function blockUser(userId) {
    try {
        showLoading();
        const result = await apiRequest(`/api/users/${userId}/block`, { method: 'POST' });
        hideLoading();
        tg.showAlert(result.message || 'User blocked successfully!');
        loadUsers(currentPage);
    } catch (error) {
        hideLoading();
        tg.showAlert(`Error: ${error.message}`);
    }
}

// Unblock user
export async function unblockUser(userId) {
    try {
        showLoading();
        const result = await apiRequest(`/api/users/${userId}/unblock`, { method: 'POST' });
        hideLoading();
        tg.showAlert(result.message || 'User unblocked successfully!');
        loadUsers(currentPage);
    } catch (error) {
        hideLoading();
        tg.showAlert(`Error: ${error.message}`);
    }
}

// Send Message Modal Functions
export function openSendMessageModal(userId, userName) {
    currentMessageUserId = userId;
    document.getElementById('messageUserId').textContent = userId;
    document.getElementById('messageText').value = '';
    document.getElementById('sendMessageModal').classList.remove('hidden');
}

export function closeSendMessageModal() {
    currentMessageUserId = null;
    document.getElementById('sendMessageModal').classList.add('hidden');
    document.getElementById('messageText').value = '';
}

export async function confirmSendMessage() {
    const messageText = document.getElementById('messageText').value.trim();

    if (!messageText) {
        tg.showAlert(t('message.sent_error') + ': Message cannot be empty');
        return;
    }

    if (!currentMessageUserId) {
        tg.showAlert(t('message.sent_error'));
        return;
    }

    try {
        showLoading();
        const result = await apiRequest(`/api/users/${currentMessageUserId}/send-message`, {
            method: 'POST',
            body: JSON.stringify({ message: messageText })
        });

        hideLoading();
        closeSendMessageModal();
        tg.showAlert(t('message.sent_success'));
    } catch (error) {
        hideLoading();
        tg.showAlert(`${t('message.sent_error')}: ${error.message}`);
    }
}

// Pagination helpers
export function goToPrevPage() {
    if (currentPage > 1) loadUsers(currentPage - 1);
}

export function goToNextPage() {
    loadUsers(currentPage + 1);
}

// Export current page for external access
export function getCurrentPage() {
    return currentPage;
}
