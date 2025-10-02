// Roles Module

import { apiRequest, showLoading, hideLoading, tg } from './api.js';
import { formatDateTime } from './utils.js';
import { t } from './i18n.js';

// Load admin roles
export async function loadRoles() {
    try {
        showLoading();

        const data = await apiRequest('/api/admin-roles');
        renderRoles(data.admins, data.current_user);

        hideLoading();
    } catch (error) {
        hideLoading();
        if (error.status === 403) {
            document.getElementById('rolesList').innerHTML = `
                <div class="text-center py-8">
                    <p class="text-gray-600 mb-2">🔒 ${error.message}</p>
                    <p class="text-sm text-gray-500">This tab is not available for your role</p>
                </div>
            `;
        } else {
            tg.showAlert(`Error loading roles: ${error.message}`);
        }
    }
}

// Render roles list
function renderRoles(admins, currentUser) {
    const container = document.getElementById('rolesList');

    if (admins.length === 0) {
        container.innerHTML = `<div class="text-center text-gray-500 py-8">${t('common.no_data')}</div>`;
        return;
    }

    const roleColors = {
        'admin': 'bg-red-100 text-red-800',
        'moderator': 'bg-blue-100 text-blue-800',
        'analyst': 'bg-green-100 text-green-800'
    };

    const roleBadges = {
        'admin': t('roles.role_badge_admin'),
        'moderator': t('roles.role_badge_moderator'),
        'analyst': t('roles.role_badge_analyst')
    };

    container.innerHTML = admins.map(admin => {
        const roleColor = roleColors[admin.role] || 'bg-gray-100 text-gray-800';
        const roleBadge = roleBadges[admin.role] || admin.role.toUpperCase();
        const isCurrentUser = currentUser && admin.user_id === currentUser.user_id;

        return `
            <div class="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <span class="font-semibold text-gray-900">@${admin.username}</span>
                        <span class="text-xs text-gray-500 ml-2">${admin.first_name} ${admin.last_name}</span>
                        ${isCurrentUser ? '<span class="ml-2 text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">YOU</span>' : ''}
                    </div>
                    <span class="px-2 py-1 rounded-full text-xs font-medium ${roleColor}">${roleBadge}</span>
                </div>
                <div class="text-sm text-gray-600 mb-2">
                    <div><strong>User ID:</strong> ${admin.user_id}</div>
                    <div><strong>${t('roles.assigned_date')}:</strong> ${formatDateTime(admin.created_at)}</div>
                    <div><strong>${t('roles.updated_date')}:</strong> ${formatDateTime(admin.updated_at)}</div>
                </div>
                <div class="flex gap-2 mt-3">
                    <button onclick="window.openEditRoleModal(${admin.user_id}, '${admin.role}')" class="flex-1 px-3 py-2 bg-blue-500 text-white rounded-lg text-xs font-medium hover:bg-blue-600 transition" data-i18n="roles.change_role">${t('roles.change_role')}</button>
                    ${!isCurrentUser ? `
                        <button onclick="window.confirmRemoveRole(${admin.user_id})" class="flex-1 px-3 py-2 bg-red-500 text-white rounded-lg text-xs font-medium hover:bg-red-600 transition" data-i18n="roles.remove_role">${t('roles.remove_role')}</button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Open assign role modal (for new admin)
export function openAssignRoleModal() {
    document.getElementById('roleUserId').value = '';
    document.getElementById('roleSelect').value = 'analyst';
    document.getElementById('assignRoleModal').classList.remove('hidden');
}

// Open edit role modal (for existing admin)
export function openEditRoleModal(userId, currentRole) {
    document.getElementById('roleUserId').value = userId;
    document.getElementById('roleUserId').disabled = true;
    document.getElementById('roleSelect').value = currentRole;
    document.getElementById('assignRoleModal').classList.remove('hidden');
}

// Close assign role modal
export function closeAssignRoleModal() {
    document.getElementById('roleUserId').disabled = false;
    document.getElementById('assignRoleModal').classList.add('hidden');
}

// Confirm assign role
export async function confirmAssignRole() {
    const userId = parseInt(document.getElementById('roleUserId').value);
    const role = document.getElementById('roleSelect').value;

    if (!userId) {
        tg.showAlert('Please enter a valid User ID');
        return;
    }

    try {
        showLoading();
        await apiRequest('/api/admin-roles', {
            method: 'POST',
            body: JSON.stringify({ user_id: userId, role: role })
        });

        tg.showAlert(t('roles.success_assigned'));
        closeAssignRoleModal();
        loadRoles();
    } catch (error) {
        hideLoading();
        tg.showAlert(`${t('roles.error_assign')}: ${error.message}`);
    }
}

// Confirm remove role
export async function confirmRemoveRole(userId) {
    if (!confirm(t('roles.confirm_remove'))) {
        return;
    }

    try {
        showLoading();
        await apiRequest(`/api/admin-roles/${userId}`, {
            method: 'DELETE'
        });

        tg.showAlert(t('roles.success_removed'));
        loadRoles();
    } catch (error) {
        hideLoading();
        tg.showAlert(`${t('roles.error_remove')}: ${error.message}`);
    }
}
