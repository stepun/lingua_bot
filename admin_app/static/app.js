// Initialize Telegram WebApp
const tg = window.Telegram.WebApp;
tg.expand();

// API base URL (change for production)
const API_BASE = window.location.origin;

// Global state
let currentPage = 1;
let currentUser = null;

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
            <span>${lang.source_language || 'Unknown'}</span>
            <span class="font-bold">${lang.count}</span>
        </div>
    `).join('') || '<div class="text-sm text-gray-500">No data</div>';

    targetLangs.innerHTML = data.target_languages.map(lang => `
        <div class="flex justify-between py-2 border-b border-gray-200 last:border-0 text-sm text-gray-800">
            <span>${lang.target_language || 'Unknown'}</span>
            <span class="font-bold">${lang.count}</span>
        </div>
    `).join('') || '<div class="text-sm text-gray-500">No data</div>';
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
        <div class="bg-white p-3 rounded-lg shadow-sm border border-gray-100">
            <div class="flex justify-between items-center mb-2">
                <span class="font-semibold text-base text-gray-900">${user.name || user.username || 'User'}</span>
                ${user.is_premium ? '<span class="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-2 py-1 rounded-full text-xs font-semibold">PREMIUM</span>' : ''}
            </div>
            <div class="text-xs text-gray-600 mb-2">
                ID: ${user.id} |
                Translations: ${user.total_translations} |
                Joined: ${formatDate(user.created_at)}
            </div>
            <div class="flex gap-2">
                <button class="px-3 py-1.5 bg-blue-500 text-white rounded-lg text-xs font-medium hover:bg-blue-600 transition" onclick="viewUser(${user.id})">View</button>
                ${!user.is_premium ?
                    `<button class="px-3 py-1.5 bg-gray-100 text-gray-800 rounded-lg text-xs font-medium hover:bg-gray-200 transition" onclick="grantPremium(${user.id})">Grant Premium</button>` :
                    ''
                }
            </div>
        </div>
    `).join('');

    // Update pagination
    const totalPages = Math.ceil(data.total / data.per_page);
    document.getElementById('pageInfo').textContent = `Page ${data.page} of ${totalPages}`;
    document.getElementById('prevPage').disabled = data.page === 1;
    document.getElementById('nextPage').disabled = data.page >= totalPages;
}

// View user details
async function viewUser(userId) {
    try {
        showLoading();
        // Get user from current users list (API doesn't have individual user endpoint)
        const usersData = await apiRequest(`/api/users/?page=1&per_page=100`);
        const user = usersData.users.find(u => u.id === userId);
        hideLoading();

        if (!user) {
            tg.showAlert('User not found');
            return;
        }

        const message = `
User: ${user.name || user.username || 'User'}
ID: ${user.id}
Username: @${user.username || 'none'}
Premium: ${user.is_premium ? 'Yes' : 'No'}
Total Translations: ${user.total_translations}
Joined: ${formatDate(user.created_at)}
        `;
        tg.showAlert(message);
    } catch (error) {
        hideLoading();
        tg.showAlert(`Error: ${error.message}`);
    }
}

// Grant premium
async function grantPremium(userId) {
    try {
        showLoading();
        await apiRequest(`/api/users/${userId}/premium`, { method: 'POST' });
        hideLoading();
        tg.showAlert('Premium granted for 30 days!');
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

        // Get filter value
        const filterSelect = document.getElementById('logFilter');
        const filterValue = filterSelect ? filterSelect.value : '';

        // Build URL with filter
        let url = '/api/logs/translations?per_page=20';
        if (filterValue) {
            url += `&filter=${filterValue}`;
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
    `).join('') || '<p class="text-sm text-gray-500">No logs found</p>';
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

    // Log filter
    document.getElementById('logFilter').addEventListener('change', loadLogs);

    // Refresh logs
    document.getElementById('refreshLogs').addEventListener('click', loadLogs);

    // Initialize
    init();
});
