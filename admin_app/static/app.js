// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();

// API base URL (change for production)
const API_BASE = window.location.origin;

// Global state
let currentPage = 1;
let currentUser = null;
let currentLanguage = localStorage.getItem('admin_language') || 'ru';

// i18n Translations
const translations = {
    ru: {
        // Header & Navigation
        'app.title': 'LinguaBot Admin',
        'nav.dashboard': '📊 Dashboard',
        'nav.users': '👥 Пользователи',
        'nav.logs': '📝 Логи',
        'nav.feedback': '💬 Feedback',
        'nav.adminLogs': '🔒 Admin Logs',

        // Dashboard
        'dashboard.title': 'Статистика бота',
        'dashboard.total_users': 'Всего пользователей',
        'dashboard.premium_users': 'Premium подписчики',
        'dashboard.today_active': 'Активных сегодня',
        'dashboard.translations_today': 'Переводов за сегодня',
        'dashboard.daily_stats': 'Статистика по дням',
        'dashboard.language_stats': 'Статистика по языкам',
        'dashboard.source_languages': 'Исходные языки',
        'dashboard.target_languages': 'Целевые языки',
        'dashboard.performance': 'Производительность',
        'dashboard.avg_processing': 'Среднее время обработки',
        'dashboard.success_rate': 'Успешных запросов',
        'dashboard.errors_7days': 'Ошибки за 7 дней',

        // Users
        'users.title': 'Управление пользователями',
        'users.search': 'Поиск по username...',
        'users.filter_premium': 'Только Premium',
        'users.refresh': 'Обновить',
        'users.translations': 'Переводов',
        'users.joined': 'Присоединился',
        'users.view': 'Просмотр',
        'users.grant_premium': 'Выдать Premium',
        'users.block': 'Заблокировать',
        'users.unblock': 'Разблокировать',
        'users.premium_badge': 'PREMIUM',
        'users.blocked_badge': 'ЗАБЛОКИРОВАН',

        // User History Modal
        'history.title': 'История переводов пользователя',
        'history.close': 'Закрыть',
        'history.voice': 'Голосовой',
        'history.text': 'Текст',
        'history.from': 'из',
        'history.to': 'в',
        'history.no_translations': 'Нет переводов',

        // Logs
        'logs.title': 'Логи переводов',
        'logs.filter_all': 'Все логи',
        'logs.filter_voice': 'Только голосовые',
        'logs.filter_text': 'Только текст',
        'logs.search': 'Поиск по username или тексту...',
        'logs.refresh': 'Обновить',
        'logs.user': 'Пользователь',
        'logs.type': 'Тип',
        'logs.translation': 'Перевод',
        'logs.date': 'Дата',
        'logs.voice': '🎤 Голос',
        'logs.text': '💬 Текст',

        // Feedback
        'feedback.title': 'Отзывы пользователей',
        'feedback.filter_all': 'Все отзывы',
        'feedback.filter_new': 'Только новые',
        'feedback.filter_reviewed': 'Просмотренные',
        'feedback.filter_resolved': 'Решённые',
        'feedback.refresh': 'Обновить',
        'feedback.mark_reviewed': 'Отметить как просмотрено',
        'feedback.mark_resolved': 'Отметить как решено',
        'feedback.status_new': 'НОВЫЙ',
        'feedback.status_reviewed': 'ПРОСМОТРЕН',
        'feedback.status_resolved': 'РЕШЁН',
        'feedback.from': 'От',

        // Admin Logs
        'adminLogs.title': 'Логи действий администраторов',
        'adminLogs.filter_all_admins': 'Все администраторы',
        'adminLogs.filter_all_actions': 'Все действия',
        'adminLogs.refresh': 'Обновить',

        // Pagination
        'pagination.prev': 'Назад',
        'pagination.next': 'Вперёд',
        'pagination.page': 'Страница',
        'pagination.of': 'из',

        // Performance
        'perf.voice': 'Голос',
        'perf.text': 'Текст',
        'perf.translations': 'переводов',
        'perf.errors': 'ошибок',
        'perf.no_errors': 'Нет ошибок за последние 7 дней 🎉',

        // Common
        'common.loading': 'Загрузка...',
        'common.error': 'Ошибка',
        'common.success': 'Успешно',
        'common.no_data': 'Нет данных',
        'common.unknown': 'Неизвестно'
    },
    en: {
        // Header & Navigation
        'app.title': 'LinguaBot Admin',
        'nav.dashboard': '📊 Dashboard',
        'nav.users': '👥 Users',
        'nav.logs': '📝 Logs',
        'nav.feedback': '💬 Feedback',
        'nav.adminLogs': '🔒 Admin Logs',

        // Dashboard
        'dashboard.title': 'Bot Statistics',
        'dashboard.total_users': 'Total Users',
        'dashboard.premium_users': 'Premium Subscribers',
        'dashboard.today_active': 'Active Today',
        'dashboard.translations_today': 'Translations Today',
        'dashboard.daily_stats': 'Daily Statistics',
        'dashboard.language_stats': 'Language Statistics',
        'dashboard.source_languages': 'Source Languages',
        'dashboard.target_languages': 'Target Languages',
        'dashboard.performance': 'Performance',
        'dashboard.avg_processing': 'Average Processing Time',
        'dashboard.success_rate': 'Success Rate',
        'dashboard.errors_7days': 'Errors (7 days)',

        // Users
        'users.title': 'User Management',
        'users.search': 'Search by username...',
        'users.filter_premium': 'Premium Only',
        'users.refresh': 'Refresh',
        'users.translations': 'Translations',
        'users.joined': 'Joined',
        'users.view': 'View',
        'users.grant_premium': 'Grant Premium',
        'users.block': 'Block',
        'users.unblock': 'Unblock',
        'users.premium_badge': 'PREMIUM',
        'users.blocked_badge': 'BLOCKED',

        // User History Modal
        'history.title': 'User Translation History',
        'history.close': 'Close',
        'history.voice': 'Voice',
        'history.text': 'Text',
        'history.from': 'from',
        'history.to': 'to',
        'history.no_translations': 'No translations',

        // Logs
        'logs.title': 'Translation Logs',
        'logs.filter_all': 'All logs',
        'logs.filter_voice': 'Voice only',
        'logs.filter_text': 'Text only',
        'logs.search': 'Search by username or text...',
        'logs.refresh': 'Refresh',
        'logs.user': 'User',
        'logs.type': 'Type',
        'logs.translation': 'Translation',
        'logs.date': 'Date',
        'logs.voice': '🎤 Voice',
        'logs.text': '💬 Text',

        // Feedback
        'feedback.title': 'User Feedback',
        'feedback.filter_all': 'All feedback',
        'feedback.filter_new': 'New only',
        'feedback.filter_reviewed': 'Reviewed',
        'feedback.filter_resolved': 'Resolved',
        'feedback.refresh': 'Refresh',
        'feedback.mark_reviewed': 'Mark as Reviewed',
        'feedback.mark_resolved': 'Mark as Resolved',
        'feedback.status_new': 'NEW',
        'feedback.status_reviewed': 'REVIEWED',
        'feedback.status_resolved': 'RESOLVED',
        'feedback.from': 'From',

        // Admin Logs
        'adminLogs.title': 'Admin Action Logs',
        'adminLogs.filter_all_admins': 'All admins',
        'adminLogs.filter_all_actions': 'All actions',
        'adminLogs.refresh': 'Refresh',

        // Pagination
        'pagination.prev': 'Previous',
        'pagination.next': 'Next',
        'pagination.page': 'Page',
        'pagination.of': 'of',

        // Performance
        'perf.voice': 'Voice',
        'perf.text': 'Text',
        'perf.translations': 'translations',
        'perf.errors': 'errors',
        'perf.no_errors': 'No errors in the last 7 days 🎉',

        // Common
        'common.loading': 'Loading...',
        'common.error': 'Error',
        'common.success': 'Success',
        'common.no_data': 'No data',
        'common.unknown': 'Unknown'
    }
};

// Translation function
function t(key) {
    return translations[currentLanguage][key] || key;
}

// Apply translations to all elements with data-i18n attribute
function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);

        // Handle different element types
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.placeholder = translation;
        } else {
            element.textContent = translation;
        }
    });

    // Update page title
    document.title = t('app.title');
}

// Switch language
function switchLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('admin_language', lang);
    applyTranslations();

    // Update active state on language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // Refresh current tab content to update dynamic translations
    const activeTab = document.querySelector('.tab-btn.active')?.dataset.tab;
    if (activeTab === 'dashboard') {
        loadDashboard();
    } else if (activeTab === 'users') {
        loadUsers(currentPage);
    } else if (activeTab === 'feedback') {
        loadFeedback();
    }
}

// Helper: API request with auth
async function apiRequest(endpoint, options = {}) {
    // Get Telegram WebApp initData for authentication
    const initData = tg.initData;

    if (!initData) {
        throw new Error('Telegram WebApp data not available');
    }

    const url = `${API_BASE}${endpoint}`;

    const headers = {
        'Content-Type': 'application/json',
        'X-Telegram-Init-Data': initData,
        ...options.headers
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (!response.ok) {
        const text = await response.text();
        console.error('API Error:', response.status, text);
        throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
}

// Helper: Show loading
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

// Helper: Hide loading
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// Helper: Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Helper: Format datetime
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Helper: Format time duration (milliseconds to human-readable)
function formatDuration(ms) {
    if (ms === 0 || !ms) return 'N/A';

    if (ms < 1000) {
        return `${ms}ms`;
    } else if (ms < 60000) {
        return `${(ms / 1000).toFixed(1)}s`;
    } else {
        const minutes = Math.floor(ms / 60000);
        const seconds = ((ms % 60000) / 1000).toFixed(0);
        return `${minutes}m ${seconds}s`;
    }
}

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
            }
        });
    });
}

// Load Dashboard
async function loadDashboard() {
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
// Language code to name mapping
const LANGUAGE_NAMES = {
    'en': 'English',
    'ru': 'Русский',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'zh': '中文',
    'ja': '日本語',
    'ko': '한국어',
    'ar': 'العربية',
    'hi': 'हिन्दी',
    'tr': 'Türkçe',
    'pl': 'Polski',
    'uk': 'Українська',
    'nl': 'Nederlands',
    'sv': 'Svenska',
    'cs': 'Čeština',
    'da': 'Dansk',
    'fi': 'Suomi',
    'el': 'Ελληνικά',
    'he': 'עברית',
    'id': 'Bahasa Indonesia',
    'ms': 'Bahasa Melayu',
    'no': 'Norsk',
    'ro': 'Română',
    'sk': 'Slovenčina',
    'th': 'ไทย',
    'vi': 'Tiếng Việt',
    'bg': 'Български',
    'hr': 'Hrvatski',
    'hu': 'Magyar',
    'lt': 'Lietuvių',
    'lv': 'Latviešu',
    'sl': 'Slovenščina',
    'et': 'Eesti',
    'mk': 'Македонски',
    'sr': 'Српски',
    'ca': 'Català',
    'gl': 'Galego',
    'eu': 'Euskara',
    'cy': 'Cymraeg',
    'is': 'Íslenska',
    'ga': 'Gaeilge',
    'mt': 'Malti',
    'sq': 'Shqip',
    'az': 'Azərbaycan',
    'ka': 'ქართული',
    'hy': 'Հայերեն',
    'auto': 'Auto-detect'
};

function getLanguageName(code) {
    return LANGUAGE_NAMES[code] || code.toUpperCase();
}

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

// Load Users
async function loadUsers(page = 1) {
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
        tg.showAlert(`Error loading users: ${error.message}`);
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
                <button class="px-3 py-1.5 bg-blue-500 text-white rounded-lg text-xs font-medium hover:bg-blue-600 transition" onclick="viewUser(${user.id})">${t('users.view')}</button>
                ${!user.is_premium ?
                    `<button class="px-3 py-1.5 bg-gray-100 text-gray-800 rounded-lg text-xs font-medium hover:bg-gray-200 transition" onclick="grantPremium(${user.id})">${t('users.grant_premium')}</button>` :
                    ''
                }
                ${!user.is_blocked ?
                    `<button class="px-3 py-1.5 bg-red-500 text-white rounded-lg text-xs font-medium hover:bg-red-600 transition" onclick="blockUser(${user.id})">${t('users.block')}</button>` :
                    `<button class="px-3 py-1.5 bg-green-500 text-white rounded-lg text-xs font-medium hover:bg-green-600 transition" onclick="unblockUser(${user.id})">${t('users.unblock')}</button>`
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
async function viewUser(userId) {
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
function closeHistoryModal() {
    document.getElementById('userHistoryModal').classList.add('hidden');
}

// Grant premium
async function grantPremium(userId) {
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
async function blockUser(userId) {
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
async function unblockUser(userId) {
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

// Load Logs
async function loadLogs() {
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

        // System logs temporarily disabled (not implemented)
        // const systemLogs = await apiRequest('/api/logs/system?lines=50');
        // renderSystemLogs(systemLogs.logs);

        hideLoading();
    } catch (error) {
        hideLoading();
        tg.showAlert(`Error loading logs: ${error.message}`);
    }
}

// Load Feedback
async function loadFeedback() {
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
        tg.showAlert(`Error loading feedback: ${error.message}`);
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
                            <button onclick="updateFeedbackStatus(${fb.id}, 'reviewed')"
                                    class="px-3 py-1 bg-yellow-500 text-white rounded text-xs font-medium hover:bg-yellow-600 transition">
                                ${t('feedback.mark_reviewed')}
                            </button>
                        ` : ''}
                        ${fb.status === 'reviewed' ? `
                            <button onclick="updateFeedbackStatus(${fb.id}, 'resolved')"
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
async function updateFeedbackStatus(feedbackId, newStatus) {
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

// Load Admin Logs
async function loadAdminLogs() {
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
        tg.showAlert(`Error loading admin logs: ${error.message}`);
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

// Render translation logs
function renderTranslationLogs(logs) {
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

// Render system logs
function renderSystemLogs(logs) {
    const container = document.getElementById('systemLogs');
    container.textContent = logs.join('\n');
}

// Setup event listeners
document.addEventListener('DOMContentLoaded', () => {
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
    document.getElementById('prevPage').addEventListener('click', () => {
        if (currentPage > 1) loadUsers(currentPage - 1);
    });
    document.getElementById('nextPage').addEventListener('click', () => {
        loadUsers(currentPage + 1);
    });

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

    // Initialize
    init();
});
