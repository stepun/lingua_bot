// API Module

// API base URL (change for production)
export const API_BASE = window.location.origin;

// Telegram WebApp instance
export const tg = window.Telegram.WebApp;

// Helper: API request with auth
export async function apiRequest(endpoint, options = {}) {
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
        const error = new Error(response.status === 403 ? 'Access Denied: Insufficient permissions' : `API Error: ${response.statusText}`);
        error.status = response.status;
        throw error;
    }

    return response.json();
}

// Helper: Show loading
export function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

// Helper: Hide loading
export function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}
