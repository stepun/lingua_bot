// i18n Translations Module

export let currentLanguage = localStorage.getItem('admin_language') || 'ru';

export const translations = {
    ru: {
        // Header & Navigation
        'app.title': 'LinguaBot Admin',
        'nav.dashboard': 'Dashboard',
        'nav.users': 'Пользователи',
        'nav.logs': 'Логи',
        'nav.feedback': 'Feedback',
        'nav.adminLogs': 'Admin Logs',

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
        'users.send_message': 'Отправить сообщение',
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

        // Roles
        'nav.roles': 'Роли',
        'roles.title': 'Управление ролями администраторов',
        'roles.refresh': 'Обновить',
        'roles.add_admin': 'Добавить админа',
        'roles.modal_title': 'Назначить роль администратора',
        'roles.user_id_label': 'ID пользователя:',
        'roles.role_label': 'Роль:',
        'roles.role_admin': 'Администратор (Полный доступ)',
        'roles.role_moderator': 'Модератор (Пользователи и логи)',
        'roles.role_analyst': 'Аналитик (Только просмотр)',
        'roles.assign_btn': 'Назначить роль',
        'roles.change_role': 'Изменить роль',
        'roles.remove_role': 'Удалить роль',
        'roles.current_role': 'Текущая роль',
        'roles.role_badge_admin': 'АДМИН',
        'roles.role_badge_moderator': 'МОДЕРАТОР',
        'roles.role_badge_analyst': 'АНАЛИТИК',
        'roles.assigned_date': 'Назначена',
        'roles.updated_date': 'Обновлена',
        'roles.confirm_remove': 'Вы уверены, что хотите удалить роль администратора у этого пользователя?',
        'roles.success_assigned': 'Роль успешно назначена!',
        'roles.success_removed': 'Роль успешно удалена!',
        'roles.error_assign': 'Ошибка при назначении роли',
        'roles.error_remove': 'Ошибка при удалении роли',

        // Settings
        'nav.settings': 'Настройки',
        'settings.title': 'Системные настройки',
        'settings.category.all': 'Все',
        'settings.category.api_keys': '🔑 API Ключи',
        'settings.category.translation': 'Переводы',
        'settings.category.voice': 'Голос',
        'settings.category.pricing': 'Цены',
        'settings.category.limits': 'Лимиты',
        'settings.category.features': 'Функции',
        'settings.save': 'Сохранить изменения',
        'settings.saved': 'Настройки сохранены успешно',
        'settings.reset': 'Сбросить к дефолту',
        'settings.no_changes': 'Нет изменений для сохранения',
        'settings.error': 'Ошибка при сохранении настроек',

        // Balances
        'balances.title': '💰 Балансы API',
        'balances.refresh': 'Обновить',
        'balances.plan': 'План',
        'balances.tier': 'Тариф',
        'balances.used': 'Использовано',
        'balances.remaining': 'Осталось',
        'balances.limit': 'Лимит',
        'balances.view_balance': 'Посмотреть баланс',
        'balances.view_details': 'Подробнее',
        'balances.view_console': 'Открыть консоль',

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

        // Send Message Modal
        'message.modal_title': 'Отправить сообщение пользователю',
        'message.recipient': 'Получатель:',
        'message.text_label': 'Текст сообщения:',
        'message.placeholder': 'Введите ваше сообщение...',
        'message.send_btn': 'Отправить',
        'message.sent_success': 'Сообщение отправлено!',
        'message.sent_error': 'Ошибка отправки сообщения',

        // Common
        'common.loading': 'Загрузка...',
        'common.error': 'Ошибка',
        'common.cancel': 'Отмена',
        'common.success': 'Успешно',
        'common.no_data': 'Нет данных',
        'common.unknown': 'Неизвестно'
    },
    en: {
        // Header & Navigation
        'app.title': 'LinguaBot Admin',
        'nav.dashboard': 'Dashboard',
        'nav.users': 'Users',
        'nav.logs': 'Logs',
        'nav.feedback': 'Feedback',
        'nav.adminLogs': 'Admin Logs',

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
        'users.send_message': 'Send Message',
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

        // Roles
        'nav.roles': 'Roles',
        'roles.title': 'Admin Role Management',
        'roles.refresh': 'Refresh',
        'roles.add_admin': 'Add Admin',
        'roles.modal_title': 'Assign Admin Role',
        'roles.user_id_label': 'User ID:',
        'roles.role_label': 'Role:',
        'roles.role_admin': 'Admin (Full Access)',
        'roles.role_moderator': 'Moderator (Users & Logs)',
        'roles.role_analyst': 'Analyst (View Only)',
        'roles.assign_btn': 'Assign Role',
        'roles.change_role': 'Change Role',
        'roles.remove_role': 'Remove Role',
        'roles.current_role': 'Current Role',
        'roles.role_badge_admin': 'ADMIN',
        'roles.role_badge_moderator': 'MODERATOR',
        'roles.role_badge_analyst': 'ANALYST',
        'roles.assigned_date': 'Assigned',
        'roles.updated_date': 'Updated',
        'roles.confirm_remove': 'Are you sure you want to remove admin role from this user?',
        'roles.success_assigned': 'Role successfully assigned!',
        'roles.success_removed': 'Role successfully removed!',
        'roles.error_assign': 'Error assigning role',
        'roles.error_remove': 'Error removing role',

        // Settings
        'nav.settings': 'Settings',
        'settings.title': 'System Settings',
        'settings.category.all': 'All',
        'settings.category.api_keys': '🔑 API Keys',
        'settings.category.translation': 'Translation',
        'settings.category.voice': 'Voice',
        'settings.category.pricing': 'Pricing',
        'settings.category.limits': 'Limits',
        'settings.category.features': 'Features',
        'settings.save': 'Save Changes',
        'settings.saved': 'Settings saved successfully',
        'settings.reset': 'Reset to default',
        'settings.no_changes': 'No changes to save',
        'settings.error': 'Error saving settings',

        // Balances
        'balances.title': '💰 API Balances',
        'balances.refresh': 'Refresh',
        'balances.plan': 'Plan',
        'balances.tier': 'Tier',
        'balances.used': 'Used',
        'balances.remaining': 'Remaining',
        'balances.limit': 'Limit',
        'balances.view_balance': 'View Balance',
        'balances.view_details': 'View Details',
        'balances.view_console': 'Open Console',

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

        // Send Message Modal
        'message.modal_title': 'Send Message to User',
        'message.recipient': 'Recipient:',
        'message.text_label': 'Message text:',
        'message.placeholder': 'Enter your message...',
        'message.send_btn': 'Send',
        'message.sent_success': 'Message sent!',
        'message.sent_error': 'Error sending message',

        // Common
        'common.loading': 'Loading...',
        'common.error': 'Error',
        'common.cancel': 'Cancel',
        'common.success': 'Success',
        'common.no_data': 'No data',
        'common.unknown': 'Unknown'
    }
};

// Translation function
export function t(key) {
    return translations[currentLanguage][key] || key;
}

// Apply translations to all elements with data-i18n attribute
export function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const translation = t(key);

        // Handle different element types
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            element.placeholder = translation;
        } else if (element.classList.contains('tab-text')) {
            // For tab text spans, update textContent directly
            element.textContent = translation;
        } else if (element.classList.contains('tab-btn')) {
            // For tab buttons, update only the .tab-text span inside
            const textSpan = element.querySelector('.tab-text');
            if (textSpan) {
                textSpan.textContent = translation;
            }
        } else {
            element.textContent = translation;
        }
    });

    // Update page title
    document.title = t('app.title');
}

// Switch language
export function switchLanguage(lang) {
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
        // Will be imported from dashboard module
        window.loadDashboard?.();
    } else if (activeTab === 'users') {
        window.loadUsers?.(window.currentPage || 1);
    } else if (activeTab === 'feedback') {
        window.loadFeedback?.();
    }
}
