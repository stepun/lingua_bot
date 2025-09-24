from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import config

def get_main_menu_keyboard(is_premium: bool = False) -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    buttons = [
        [InlineKeyboardButton(text="🌍 Выбрать язык", callback_data="select_language")],
        [InlineKeyboardButton(text="🎨 Стиль перевода", callback_data="select_style")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
    ]

    if is_premium:
        buttons.extend([
            [InlineKeyboardButton(text="📚 История переводов", callback_data="history")],
            [InlineKeyboardButton(text="📄 Экспорт в PDF", callback_data="export_pdf")]
        ])
    else:
        buttons.append([InlineKeyboardButton(text="⭐ Премиум подписка", callback_data="premium")])

    buttons.append([InlineKeyboardButton(text="❓ Помощь", callback_data="help")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    buttons = []
    row = []

    popular_languages = [
        ('en', '🇺🇸 English'),
        ('ru', '🇷🇺 Русский'),
        ('es', '🇪🇸 Español'),
        ('fr', '🇫🇷 Français'),
        ('de', '🇩🇪 Deutsch'),
        ('it', '🇮🇹 Italiano'),
        ('pt', '🇧🇷 Português'),
        ('ja', '🇯🇵 日本語'),
        ('zh', '🇨🇳 中文'),
        ('ko', '🇰🇷 한국어'),
        ('ar', '🇸🇦 العربية'),
        ('hi', '🇮🇳 हिन्दी')
    ]

    for i, (code, name) in enumerate(popular_languages):
        row.append(InlineKeyboardButton(text=name, callback_data=f"lang_{code}"))
        if len(row) == 2 or i == len(popular_languages) - 1:
            buttons.append(row)
            row = []

    buttons.append([InlineKeyboardButton(text="📋 Все языки", callback_data="all_languages")])
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_all_languages_keyboard(page: int = 0, page_size: int = 10) -> InlineKeyboardMarkup:
    """All languages keyboard with pagination"""
    languages = list(config.SUPPORTED_LANGUAGES.items())
    total_pages = (len(languages) + page_size - 1) // page_size

    start_idx = page * page_size
    end_idx = start_idx + page_size
    page_languages = languages[start_idx:end_idx]

    buttons = []
    for code, name in page_languages:
        buttons.append([InlineKeyboardButton(text=f"{name}", callback_data=f"lang_{code}")])

    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️", callback_data=f"lang_page_{page-1}"))

    nav_buttons.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="▶️", callback_data=f"lang_page_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="select_language")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_style_selection_keyboard() -> InlineKeyboardMarkup:
    """Translation style selection keyboard"""
    styles = [
        ('informal', '😊 Неформальный'),
        ('formal', '🎩 Формальный'),
        ('business', '💼 Деловой'),
        ('travel', '✈️ Для путешествий'),
        ('academic', '🎓 Академический')
    ]

    buttons = []
    for code, name in styles:
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"style_{code}")])

    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_premium_keyboard() -> InlineKeyboardMarkup:
    """Premium subscription keyboard"""
    buttons = [
        [InlineKeyboardButton(text="⚡ Премиум на 1 день — 100₽", callback_data="buy_telegram_daily")],
        [InlineKeyboardButton(text="💳 Месячная подписка — 490₽", callback_data="buy_telegram_monthly")],
        [InlineKeyboardButton(text="💎 Годовая подписка — 4680₽ (-20%)", callback_data="buy_telegram_yearly")],
        [InlineKeyboardButton(text="🎁 Экономьте 1200₽ с годовой подпиской!", callback_data="noop")],
        [InlineKeyboardButton(text="❓ Что входит в премиум?", callback_data="premium_features")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_premium_features_keyboard() -> InlineKeyboardMarkup:
    """Premium features info keyboard"""
    buttons = [
        [InlineKeyboardButton(text="⚡ 1 день — 100₽", callback_data="buy_telegram_daily")],
        [InlineKeyboardButton(text="💳 Месячная — 490₽", callback_data="buy_telegram_monthly"),
         InlineKeyboardButton(text="💎 Годовая — 4680₽", callback_data="buy_telegram_yearly")],
        [InlineKeyboardButton(text="◀️ Назад к подпискам", callback_data="premium")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_settings_keyboard(user_settings: dict) -> InlineKeyboardMarkup:
    """User settings keyboard"""
    auto_voice = "🔊 Вкл" if user_settings.get('auto_voice', False) else "🔇 Выкл"
    save_history = "✅ Вкл" if user_settings.get('save_history', True) else "❌ Выкл"
    notifications = "🔔 Вкл" if user_settings.get('notifications_enabled', True) else "🔕 Выкл"
    is_premium = user_settings.get('is_premium', False)

    buttons = []

    # Premium features
    if is_premium:
        buttons.extend([
            [InlineKeyboardButton(text=f"🔊 Автопроигрывание: {auto_voice}", callback_data="toggle_auto_voice")],
            [InlineKeyboardButton(text="🎚️ Скорость речи", callback_data="voice_speed")],
            [InlineKeyboardButton(text="🗣️ Тип голоса", callback_data="voice_type")]
        ])

    # General settings for all users
    buttons.extend([
        [InlineKeyboardButton(text=f"💾 Сохранение истории: {save_history}", callback_data="toggle_save_history")],
        [InlineKeyboardButton(text=f"📢 Уведомления: {notifications}", callback_data="toggle_notifications_enabled")]
    ])

    # Premium-only features
    if is_premium:
        buttons.append([InlineKeyboardButton(text="🗑️ Очистить историю", callback_data="clear_history")])

    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_voice_speed_keyboard(current_speed: float = 1.0) -> InlineKeyboardMarkup:
    """Voice speed selection keyboard"""
    speeds = [0.5, 0.75, 1.0, 1.25, 1.5]
    buttons = []

    for speed in speeds:
        if speed == current_speed:
            text = f"🎯 {speed}x"
        else:
            text = f"{speed}x"
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"speed_{speed}")])

    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="settings")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_voice_type_keyboard(current_type: str = 'alloy') -> InlineKeyboardMarkup:
    """Voice type selection keyboard"""
    voices = [
        ('alloy', '👨 Мужской 1'),
        ('echo', '👨 Мужской 2'),
        ('fable', '👨 Мужской 3'),
        ('onyx', '👨 Мужской 4'),
        ('nova', '👩 Женский 1'),
        ('shimmer', '👩 Женский 2')
    ]

    buttons = []
    for voice_id, name in voices:
        if voice_id == current_type:
            text = f"🎯 {name}"
        else:
            text = name
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"vtype_{voice_id}")])

    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="settings")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_history_keyboard(page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Translation history keyboard"""
    buttons = []

    # Navigation
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Пред.", callback_data=f"hist_page_{page-1}"))

    nav_buttons.append(InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="noop"))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="След. ▶️", callback_data=f"hist_page_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.extend([
        [InlineKeyboardButton(text="📄 Экспорт в PDF", callback_data="export_pdf")],
        [InlineKeyboardButton(text="🗑️ Очистить историю", callback_data="clear_history_confirm")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_export_format_keyboard() -> InlineKeyboardMarkup:
    """Export format selection keyboard"""
    buttons = [
        [InlineKeyboardButton(text="📄 PDF", callback_data="export_pdf")],
        [InlineKeyboardButton(text="📝 TXT", callback_data="export_txt")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="history")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirmation_keyboard(confirm_action: str) -> InlineKeyboardMarkup:
    """Confirmation dialog keyboard"""
    buttons = [
        [InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{confirm_action}")],
        [InlineKeyboardButton(text="❌ Нет", callback_data="back_to_menu")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_translation_actions_keyboard(is_premium: bool = False, interface_lang: str = 'ru') -> InlineKeyboardMarkup:
    """Actions for translation result"""
    buttons = []

    # Multilingual button texts
    button_texts = {
        'ru': {
            'voice': "🔊 Озвучить",
            'alternatives': "🔄 Альтернативы",
            'explanation': "📝 Объяснение",
            'grammar': "📚 Грамматика",
            'menu': "🏠 Меню"
        },
        'en': {
            'voice': "🔊 Voice",
            'alternatives': "🔄 Alternatives",
            'explanation': "📝 Explanation",
            'grammar': "📚 Grammar",
            'menu': "🏠 Menu"
        }
    }

    texts = button_texts.get(interface_lang, button_texts['ru'])

    # Always show voice button for premium users
    if is_premium:
        buttons.append([InlineKeyboardButton(text=texts['voice'], callback_data="voice_translation")])

    if is_premium:
        buttons.extend([
            [InlineKeyboardButton(text=texts['alternatives'], callback_data="show_alternatives")],
            [InlineKeyboardButton(text=texts['explanation'], callback_data="show_explanation")],
            [InlineKeyboardButton(text=texts['grammar'], callback_data="show_grammar")]
        ])

    # Always add menu button
    buttons.append([InlineKeyboardButton(text=texts['menu'], callback_data="back_to_menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_voice_options_keyboard(has_alternatives: bool = False, interface_lang: str = 'ru') -> InlineKeyboardMarkup:
    """Voice options selection keyboard"""
    button_texts = {
        'ru': {
            'exact': "🎯 Точный перевод",
            'styled': "✨ Стилизованный перевод",
            'alternatives': "🔄 Альтернативы",
            'any_style': "🎨 Любой стиль",
            'translate_style': "🔄 Перевести в другой стиль",
            'back': "◀️ Назад"
        },
        'en': {
            'exact': "🎯 Exact translation",
            'styled': "✨ Styled translation",
            'alternatives': "🔄 Alternatives",
            'any_style': "🎨 Any style",
            'translate_style': "🔄 Translate to other style",
            'back': "◀️ Back"
        }
    }

    texts = button_texts.get(interface_lang, button_texts['ru'])

    buttons = [
        [InlineKeyboardButton(text=texts['exact'], callback_data="voice_exact")],
        [InlineKeyboardButton(text=texts['styled'], callback_data="voice_styled")]
    ]

    # Add alternatives option only if they exist
    if has_alternatives:
        buttons.append([InlineKeyboardButton(text=texts['alternatives'], callback_data="voice_alternatives")])

    # Add quick style options
    buttons.extend([
        [InlineKeyboardButton(text=texts['any_style'], callback_data="voice_any_style")],
        [InlineKeyboardButton(text=texts['translate_style'], callback_data="translate_any_style")]
    ])

    buttons.append([InlineKeyboardButton(text=texts['back'], callback_data="back_to_translation")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_quick_styles_keyboard(interface_lang: str = 'ru', action_type: str = 'voice') -> InlineKeyboardMarkup:
    """Quick style selection for translation/voice without re-entering text"""
    # Get multilingual style names
    from config import config
    style_names = config.TRANSLATION_STYLES_MULTILINGUAL.get(interface_lang, config.TRANSLATION_STYLES_MULTILINGUAL['ru'])

    # Action prefixes: voice_ for voice generation, translate_ for translation
    action_prefix = f"{action_type}_style_"

    buttons = []
    styles = [
        ('informal', '😊'),
        ('formal', '🎩'),
        ('business', '💼'),
        ('travel', '✈️'),
        ('academic', '📚')
    ]

    # Create buttons for each style
    for style_key, emoji in styles:
        style_display = style_names.get(style_key, style_key)
        text = f"{emoji} {style_display}"
        callback_data = f"{action_prefix}{style_key}"
        buttons.append([InlineKeyboardButton(text=text, callback_data=callback_data)])

    # Back button
    back_texts = {
        'ru': "◀️ Назад",
        'en': "◀️ Back"
    }
    buttons.append([InlineKeyboardButton(text=back_texts.get(interface_lang, back_texts['ru']), callback_data="back_to_voice_menu")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    """Payment keyboard"""
    buttons = [
        [InlineKeyboardButton(text="💳 Оплатить", url=payment_url)],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_menu")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_export_keyboard() -> InlineKeyboardMarkup:
    """Export format selection keyboard"""
    buttons = [
        [InlineKeyboardButton(text="📄 PDF", callback_data="export_pdf")],
        [InlineKeyboardButton(text="📝 TXT", callback_data="export_txt")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_menu")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin panel keyboard"""
    buttons = [
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton(text="💰 Платежи", callback_data="admin_payments")],
        [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="🔧 Настройки", callback_data="admin_settings")]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)