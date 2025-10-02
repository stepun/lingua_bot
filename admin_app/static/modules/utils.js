// Utility Functions Module

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

// Helper: Format date
export function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Helper: Format datetime
export function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Helper: Format time duration (milliseconds to human-readable)
export function formatDuration(ms) {
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

// Get language name from code
export function getLanguageName(code) {
    return LANGUAGE_NAMES[code] || code.toUpperCase();
}
