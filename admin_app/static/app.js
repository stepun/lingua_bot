// Main Application Entry Point

import { tg } from './modules/api.js';
import { showLoading, hideLoading } from './modules/api.js';
import { t, applyTranslations, switchLanguage, currentLanguage } from './modules/i18n.js';
import { loadDashboard } from './modules/dashboard.js';
import {
    loadUsers,
    viewUser,
    closeHistoryModal,
    grantPremium,
    blockUser,
    unblockUser,
    openSendMessageModal,
    closeSendMessageModal,
    confirmSendMessage,
    goToPrevPage,
    goToNextPage,
    getCurrentPage
} from './modules/users.js';
import { loadLogs } from './modules/logs.js';
import { loadFeedback, updateFeedbackStatus } from './modules/feedback.js';
import { loadAdminLogs } from './modules/adminLogs.js';
import {
    loadRoles,
    openAssignRoleModal,
    openEditRoleModal,
    closeAssignRoleModal,
    confirmAssignRole,
    confirmRemoveRole
} from './modules/roles.js';
import { loadSettings, saveSettings, resetSetting, getCurrentCategory } from './modules/settings.js';
import { loadBalances } from './modules/balances.js';

// Global state
let currentUser = null;

// Expose functions to window for onclick handlers
window.loadDashboard = loadDashboard;
window.loadUsers = loadUsers;
window.viewUser = viewUser;
window.closeHistoryModal = closeHistoryModal;
window.grantPremium = grantPremium;
window.blockUser = blockUser;
window.unblockUser = unblockUser;
window.openSendMessageModal = openSendMessageModal;
window.closeSendMessageModal = closeSendMessageModal;
window.confirmSendMessage = confirmSendMessage;
window.updateFeedbackStatus = updateFeedbackStatus;
window.openAssignRoleModal = openAssignRoleModal;
window.openEditRoleModal = openEditRoleModal;
window.closeAssignRoleModal = closeAssignRoleModal;
window.confirmAssignRole = confirmAssignRole;
window.confirmRemoveRole = confirmRemoveRole;
window.resetSetting = resetSetting;
window.saveSettings = saveSettings;
window.currentPage = 1;

// Initialize Telegram WebApp
tg.expand();

// Initialize app
async function init() {
    try {
        showLoading();

        // Security check: Must be opened through Telegram WebApp
        if (!tg.initData) {
            hideLoading();
            document.getElementById('app').innerHTML = `
                <div class="flex items-center justify-center min-h-screen bg-gray-100">
                    <div class="text-center p-8 bg-white rounded-xl shadow-lg max-w-md">
                        <div class="text-6xl mb-4">🔒</div>
                        <h1 class="text-2xl font-bold text-gray-800 mb-2">Access Denied</h1>
                        <p class="text-gray-600 mb-4">This admin panel can only be accessed through Telegram Bot.</p>
                        <p class="text-sm text-gray-500">Please use the /admin_panel command in the bot.</p>
                    </div>
                </div>
            `;
            return;
        }

        // Get current user info from Telegram
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            currentUser = tg.initDataUnsafe.user;
            document.getElementById('userInfo').textContent =
                `${currentUser.first_name || currentUser.username || 'Admin'}`;
        } else {
            document.getElementById('userInfo').textContent = 'Admin';
        }

        // Set up theme
        document.documentElement.style.setProperty('--tg-theme-bg-color', tg.themeParams.bg_color || '#ffffff');
        document.documentElement.style.setProperty('--tg-theme-text-color', tg.themeParams.text_color || '#000000');
        document.documentElement.style.setProperty('--tg-theme-hint-color', tg.themeParams.hint_color || '#999999');
        document.documentElement.style.setProperty('--tg-theme-link-color', tg.themeParams.link_color || '#2481cc');
        document.documentElement.style.setProperty('--tg-theme-button-color', tg.themeParams.button_color || '#2481cc');

        // Apply language translations
        applyTranslations();

        // Set active language button
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === currentLanguage);
        });

        // Set up tab navigation
        setupTabs();

        // Load initial data
        await loadDashboard();

        hideLoading();
    } catch (error) {
        hideLoading();
        tg.showAlert(`Error initializing app: ${error.message}`);
    }
}

// Setup tabs
function setupTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;

            // Update active states
            tabBtns.forEach(b => {
                b.classList.remove('active', 'text-blue-600', 'border-b-blue-600');
                b.classList.add('text-gray-600', 'border-b-transparent');
            });
            tabContents.forEach(c => {
                c.classList.add('hidden');
                c.classList.remove('active');
            });

            btn.classList.add('active', 'text-blue-600', 'border-b-blue-600');
            btn.classList.remove('text-gray-600', 'border-b-transparent');
            const content = document.getElementById(tabName);
            content.classList.remove('hidden');
            content.classList.add('active');

            // Load tab data
            switch(tabName) {
                case 'dashboard':
                    loadDashboard();
                    break;
                case 'users':
                    loadUsers();
                    break;
                case 'logs':
                    loadLogs();
                    break;
                case 'feedback':
                    loadFeedback();
                    break;
                case 'adminLogs':
                    loadAdminLogs();
                    break;
                case 'roles':
                    loadRoles();
                    break;
                case 'settings':
                    loadSettings(getCurrentCategory());
                    loadBalances();
                    break;
            }
        });
    });
}

// Setup event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Language switcher
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            switchLanguage(btn.dataset.lang);
        });
    });

    // User search
    const searchInput = document.getElementById('userSearch');
    let searchTimeout;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => loadUsers(1), 500);
    });

    // Premium filter
    document.getElementById('premiumFilter').addEventListener('change', () => loadUsers(1));

    // Pagination
    document.getElementById('prevPage').addEventListener('click', goToPrevPage);
    document.getElementById('nextPage').addEventListener('click', goToNextPage);

    // Log search with debounce
    const logSearchInput = document.getElementById('logSearch');
    let logSearchTimeout;
    logSearchInput.addEventListener('input', () => {
        clearTimeout(logSearchTimeout);
        logSearchTimeout = setTimeout(() => loadLogs(), 500);
    });

    // Log filter
    document.getElementById('logFilter').addEventListener('change', loadLogs);

    // Refresh logs
    document.getElementById('refreshLogs').addEventListener('click', loadLogs);

    // Feedback filter
    document.getElementById('feedbackStatusFilter').addEventListener('change', loadFeedback);

    // Refresh feedback
    document.getElementById('refreshFeedback').addEventListener('click', loadFeedback);

    // Admin logs filters
    document.getElementById('adminLogsAdminFilter').addEventListener('change', loadAdminLogs);
    document.getElementById('adminLogsActionFilter').addEventListener('change', loadAdminLogs);

    // Refresh admin logs
    document.getElementById('refreshAdminLogs').addEventListener('click', loadAdminLogs);

    // Roles management
    document.getElementById('refreshRoles').addEventListener('click', loadRoles);
    document.getElementById('addAdminBtn').addEventListener('click', openAssignRoleModal);

    // Settings event listeners
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadSettings(btn.dataset.category);
        });
    });

    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', saveSettings);
    }

    // Balances event listeners
    const refreshBalancesBtn = document.getElementById('refreshBalancesBtn');
    if (refreshBalancesBtn) {
        refreshBalancesBtn.addEventListener('click', loadBalances);
    }

    // Initialize
    init();
});
