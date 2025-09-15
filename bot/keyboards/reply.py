from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_reply_keyboard(is_premium: bool = False) -> ReplyKeyboardMarkup:
    """Main reply keyboard"""
    buttons = [
        [KeyboardButton(text="🌍 Язык"), KeyboardButton(text="🎨 Стиль")],
        [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="❓ Помощь")]
    ]

    if is_premium:
        buttons.insert(1, [KeyboardButton(text="📚 История"), KeyboardButton(text="📄 Экспорт")])
    else:
        buttons.append([KeyboardButton(text="⭐ Премиум")])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=False,
        placeholder="Выберите действие или отправьте текст для перевода"
    )

def get_language_quick_select_keyboard() -> ReplyKeyboardMarkup:
    """Quick language selection keyboard"""
    buttons = [
        [KeyboardButton(text="🇺🇸 EN"), KeyboardButton(text="🇷🇺 RU"), KeyboardButton(text="🇪🇸 ES")],
        [KeyboardButton(text="🇫🇷 FR"), KeyboardButton(text="🇩🇪 DE"), KeyboardButton(text="🇮🇹 IT")],
        [KeyboardButton(text="📋 Все языки"), KeyboardButton(text="◀️ Назад")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_style_quick_select_keyboard() -> ReplyKeyboardMarkup:
    """Quick style selection keyboard"""
    buttons = [
        [KeyboardButton(text="😊 Неформально"), KeyboardButton(text="🎩 Формально")],
        [KeyboardButton(text="💼 Деловой"), KeyboardButton(text="✈️ Путешествия")],
        [KeyboardButton(text="🎓 Академический"), KeyboardButton(text="◀️ Назад")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_confirmation_keyboard() -> ReplyKeyboardMarkup:
    """Confirmation keyboard"""
    buttons = [
        [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Cancel keyboard"""
    buttons = [
        [KeyboardButton(text="❌ Отмена")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )