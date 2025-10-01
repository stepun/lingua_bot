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
    // Add user_id to query params for admin check
    const userId = currentUser ? currentUser.id : null;

    if (!userId) {
        throw new Error('User ID not available');
    }

    // Add user_id to URL
    const separator = endpoint.includes('?') ? '&' : '?';
    const url = `${API_BASE}${endpoint}${separator}user_id=${userId}`;

    const headers = {
        'Content-Type': 'application/json',
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
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(tabName).classList.add('active');

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
        document.getElementById('activeToday').textContent = stats.today.active_users;
        document.getElementById('translationsToday').textContent = stats.today.translations;

        // Load daily stats
        const dailyData = await apiRequest('/api/stats/daily?days=7');
        renderDailyStats(dailyData.data);

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
        <div class="daily-stat-row">
            <span class="daily-stat-date">${formatDate(stat.date)}</span>
            <div class="daily-stat-values">
                <span>👥 ${stat.active_users}</span>
                <span>💬 ${stat.total_translations}</span>
                <span>🎤 ${stat.voice_translations}</span>
            </div>
        </div>
    `).join('');
}

// Render language stats
function renderLanguageStats(data) {
    const sourceLangs = document.getElementById('sourceLangs');
    const targetLangs = document.getElementById('targetLangs');

    sourceLangs.innerHTML = data.source_languages.map(lang => `
        <div class="lang-item">
            <span>${lang.source_language || 'Unknown'}</span>
            <span><strong>${lang.count}</strong></span>
        </div>
    `).join('') || '<div class="lang-item">No data</div>';

    targetLangs.innerHTML = data.target_languages.map(lang => `
        <div class="lang-item">
            <span>${lang.target_language || 'Unknown'}</span>
            <span><strong>${lang.count}</strong></span>
        </div>
    `).join('') || '<div class="lang-item">No data</div>';
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
        <div class="user-card">
            <div class="user-header">
                <span class="user-name">${user.first_name || user.username || 'User'} ${user.last_name || ''}</span>
                ${user.is_premium ? '<span class="user-badge">PREMIUM</span>' : ''}
            </div>
            <div class="user-info">
                ID: ${user.user_id} |
                Translations: ${user.total_translations} |
                Joined: ${formatDate(user.created_at)}
            </div>
            <div class="user-actions">
                <button class="btn-primary" onclick="viewUser(${user.user_id})">View</button>
                ${!user.is_premium ?
                    `<button class="btn-secondary" onclick="grantPremium(${user.user_id})">Grant Premium</button>` :
                    ''
                }
            </div>
        </div>
    `).join('');

    // Update pagination
    document.getElementById('pageInfo').textContent = `Page ${data.page} of ${data.total_pages}`;
    document.getElementById('prevPage').disabled = data.page === 1;
    document.getElementById('nextPage').disabled = data.page === data.total_pages;
}

// View user details
async function viewUser(userId) {
    try {
        showLoading();
        const data = await apiRequest(`/api/users/${userId}`);
        hideLoading();

        const user = data.user;
        const message = `
User: ${user.first_name || ''} ${user.last_name || ''}
ID: ${user.user_id}
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

        // Load translation logs
        const logsData = await apiRequest('/api/logs/translations?per_page=20');
        renderTranslationLogs(logsData.logs);

        // Load system logs
        const systemLogs = await apiRequest('/api/logs/system?lines=50');
        renderSystemLogs(systemLogs.logs);

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
        <div class="log-item">
            <div class="log-header">
                <span>${log.first_name || log.username || 'User'}</span>
                <span>${formatDateTime(log.created_at)}</span>
            </div>
            <div class="log-body">
                ${log.source_language} → ${log.target_language}
                ${log.is_voice ? '🎤' : '💬'}
                <br>
                <small>${(log.source_text || '').substring(0, 50)}...</small>
            </div>
        </div>
    `).join('') || '<p>No logs found</p>';
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

    // Refresh logs
    document.getElementById('refreshLogs').addEventListener('click', loadLogs);

    // Initialize
    init();
});
