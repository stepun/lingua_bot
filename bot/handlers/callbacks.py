from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
import logging

from bot.database import db
from bot.keyboards.inline import *
from bot.keyboards.inline import get_voice_options_keyboard, get_quick_styles_keyboard
from bot.keyboards.reply import get_main_reply_keyboard
from bot.services.translator import TranslatorService
from bot.services.voice import VoiceService
from bot.utils.messages import get_text
from bot.handlers.base import escape_html
from config import config

logger = logging.getLogger(__name__)
router = Router()

# Store last translation metadata for callbacks
last_translation_metadata = {}

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(callback: CallbackQuery):
    """Return to main menu"""
    user_info = await db.get_user(callback.from_user.id)
    is_premium = user_info.get('is_premium', False)

    try:
        await callback.message.edit_text(
            get_text('main_menu', user_info.get('interface_language', 'ru')),
            reply_markup=get_main_menu_keyboard(is_premium)
        )
    except TelegramBadRequest:
        await callback.message.delete()
        await callback.message.answer(
            get_text('main_menu', user_info.get('interface_language', 'ru')),
            reply_markup=get_main_menu_keyboard(is_premium)
        )

    await callback.answer()

@router.callback_query(F.data == "select_language")
async def select_language_handler(callback: CallbackQuery):
    """Show language selection"""
    from bot.services.translator import TranslatorService

    user_info = await db.get_user(callback.from_user.id)
    current_lang = user_info.get('target_language', 'en')
    interface_lang = user_info.get('interface_language', 'ru')

    async with TranslatorService() as translator:
        current_lang_name = await translator.get_language_name(current_lang, interface_lang)

    text = get_text('select_language', interface_lang).format(
        current_lang=current_lang_name
    )

    await callback.message.edit_text(text, reply_markup=get_language_selection_keyboard())
    await callback.answer()

@router.callback_query(F.data == "all_languages")
async def all_languages_handler(callback: CallbackQuery):
    """Show all languages"""
    await callback.message.edit_text(
        "Выберите язык перевода:",
        reply_markup=get_all_languages_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("lang_page_"))
async def language_page_handler(callback: CallbackQuery):
    """Handle language pagination"""
    page = int(callback.data.split("_")[-1])

    await callback.message.edit_text(
        "Выберите язык перевода:",
        reply_markup=get_all_languages_keyboard(page)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("lang_"))
async def language_selection_handler(callback: CallbackQuery):
    """Handle language selection"""
    lang_code = callback.data[5:]  # Remove "lang_" prefix

    logger.info(f"Language selection: user={callback.from_user.id}, lang_code={lang_code}, callback_data={callback.data}")

    if lang_code not in config.SUPPORTED_LANGUAGES:
        await callback.answer("❌ Неподдерживаемый язык", show_alert=True)
        return

    # Update user's target language
    await db.update_user_language(callback.from_user.id, lang_code)
    logger.info(f"Updated language for user {callback.from_user.id} to {lang_code}")

    user_info = await db.get_user(callback.from_user.id)
    logger.info(f"Verification after update: user={callback.from_user.id}, target_language={user_info.get('target_language')}")
    lang_name = config.SUPPORTED_LANGUAGES[lang_code]

    success_text = get_text('language_changed', user_info.get('interface_language', 'ru')).format(
        language=lang_name
    )

    await callback.message.edit_text(
        success_text,
        reply_markup=get_main_menu_keyboard(user_info.get('is_premium', False))
    )
    await callback.answer(f"✅ Язык изменен на {lang_name}")

@router.callback_query(F.data == "select_style")
async def select_style_handler(callback: CallbackQuery):
    """Show style selection"""
    user_info = await db.get_user(callback.from_user.id)
    current_style = user_info.get('translation_style', 'informal')

    text = get_text('select_style', user_info.get('interface_language', 'ru')).format(
        current_style=config.TRANSLATION_STYLES.get(current_style, current_style)
    )

    await callback.message.edit_text(text, reply_markup=get_style_selection_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("style_"))
async def style_selection_handler(callback: CallbackQuery):
    """Handle style selection"""
    style = callback.data[6:]  # Remove "style_" prefix

    if style not in config.TRANSLATION_STYLES:
        await callback.answer("❌ Неподдерживаемый стиль", show_alert=True)
        return

    # Update user's translation style
    await db.update_user_style(callback.from_user.id, style)

    user_info = await db.get_user(callback.from_user.id)
    style_name = config.TRANSLATION_STYLES[style]

    success_text = get_text('style_changed', user_info.get('interface_language', 'ru')).format(
        style=style_name
    )

    await callback.message.edit_text(
        success_text,
        reply_markup=get_main_menu_keyboard(user_info.get('is_premium', False))
    )
    await callback.answer(f"✅ Стиль изменен на {style_name}")

@router.callback_query(F.data == "premium")
async def premium_handler(callback: CallbackQuery):
    """Show premium subscription info"""
    user_info = await db.get_user(callback.from_user.id)

    if user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('already_premium', user_info.get('interface_language', 'ru')),
            reply_markup=get_main_menu_keyboard(True)
        )
    else:
        await callback.message.edit_text(
            get_text('premium_info', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard()
        )

    await callback.answer()

@router.callback_query(F.data == "premium_features")
async def premium_features_handler(callback: CallbackQuery):
    """Show premium features"""
    user_info = await db.get_user(callback.from_user.id)

    await callback.message.edit_text(
        get_text('premium_features', user_info.get('interface_language', 'ru')),
        reply_markup=await get_premium_features_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()


@router.callback_query(F.data == "settings")
async def settings_handler(callback: CallbackQuery):
    """Show settings menu"""
    user_info = await db.get_user(callback.from_user.id)

    await callback.message.edit_text(
        get_text('settings_menu', user_info.get('interface_language', 'ru')),
        reply_markup=get_settings_keyboard(user_info)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("toggle_"))
async def toggle_setting_handler(callback: CallbackQuery):
    """Handle setting toggles"""
    setting = callback.data[7:]  # Remove "toggle_" prefix

    user_info = await db.get_user(callback.from_user.id)
    current_value = user_info.get(setting, False)

    # Update setting
    await db.update_user_settings(callback.from_user.id, **{setting: not current_value})

    # Refresh settings menu
    updated_user_info = await db.get_user(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=get_settings_keyboard(updated_user_info))

    setting_names = {
        'auto_voice': 'Автопроигрывание',
        'save_history': 'Сохранение истории',
        'notifications_enabled': 'Уведомления',
        'show_transcription': 'Транскрипция'
    }

    setting_name = setting_names.get(setting, setting)
    new_status = "включено" if not current_value else "выключено"

    await callback.answer(f"✅ {setting_name} {new_status}")

@router.callback_query(F.data == "voice_speed")
async def voice_speed_handler(callback: CallbackQuery):
    """Show voice speed selection"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    current_speed = user_info.get('voice_speed', 1.0)

    await callback.message.edit_text(
        f"Текущая скорость: {current_speed}x\n\nВыберите новую скорость речи:",
        reply_markup=get_voice_speed_keyboard(current_speed)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("speed_"))
async def speed_selection_handler(callback: CallbackQuery):
    """Handle speed selection"""
    speed = float(callback.data[6:])  # Remove "speed_" prefix

    await db.update_user_settings(callback.from_user.id, voice_speed=speed)

    await callback.message.edit_text(
        f"✅ Скорость речи изменена на {speed}x",
        reply_markup=get_settings_keyboard(await db.get_user(callback.from_user.id))
    )
    await callback.answer()

@router.callback_query(F.data == "voice_type")
async def voice_type_handler(callback: CallbackQuery):
    """Show voice type selection"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    current_type = user_info.get('voice_type', 'alloy')

    await callback.message.edit_text(
        "Выберите тип голоса:",
        reply_markup=get_voice_type_keyboard(current_type)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("vtype_"))
async def voice_type_selection_handler(callback: CallbackQuery):
    """Handle voice type selection"""
    voice_type = callback.data[6:]  # Remove "vtype_" prefix

    await db.update_user_settings(callback.from_user.id, voice_type=voice_type)

    await callback.message.edit_text(
        f"✅ Тип голоса изменен",
        reply_markup=get_settings_keyboard(await db.get_user(callback.from_user.id))
    )
    await callback.answer()

@router.callback_query(F.data == "history")
async def history_handler(callback: CallbackQuery):
    """Show translation history"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    history = await db.get_user_history(callback.from_user.id, limit=10)

    if not history:
        await callback.message.edit_text(
            get_text('no_history', user_info.get('interface_language', 'ru')),
            reply_markup=get_main_menu_keyboard(True)
        )
        await callback.answer()
        return

    # Create keyboard with buttons for each history item
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from datetime import datetime

    buttons = []
    for i, item in enumerate(history, 1):
        # Format date
        created_at = item['created_at']
        if isinstance(created_at, datetime):
            date_str = created_at.strftime('%Y-%m-%d %H:%M')
        else:
            date_str = created_at[:16]  # YYYY-MM-DD HH:MM

        # Create button text
        source_preview = item['source_text'][:30] + ('...' if len(item['source_text']) > 30 else '')
        button_text = f"{i}. {source_preview} ({date_str})"

        buttons.append([InlineKeyboardButton(
            text=button_text,
            callback_data=f"history_view_{item['id']}"
        )])

    # Add export and clear buttons
    buttons.extend([
        [InlineKeyboardButton(text="📄 Экспорт в PDF", callback_data="export_pdf")],
        [InlineKeyboardButton(text="🗑️ Очистить историю", callback_data="clear_history_confirm")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    text = get_text('history_header', user_info.get('interface_language', 'ru')) + "\n\n"
    text += "Выберите перевод для просмотра:"

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "clear_history")
async def clear_history_handler(callback: CallbackQuery):
    """Show history clearing confirmation"""
    user_info = await db.get_user(callback.from_user.id)
    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "❓ Вы уверены, что хотите очистить всю историю переводов?",
        reply_markup=get_confirmation_keyboard("clear_history")
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_clear_history")
async def confirm_clear_history_handler(callback: CallbackQuery):
    """Clear translation history"""
    await db.clear_user_history(callback.from_user.id)

    await callback.message.edit_text(
        "✅ История переводов очищена",
        reply_markup=get_main_menu_keyboard(True)
    )
    await callback.answer()

@router.callback_query(F.data == "voice_translation")
async def voice_translation_handler(callback: CallbackQuery):
    """Show voice options selection"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    # Check if alternatives are available
    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})
    has_alternatives = bool(metadata.get('alternatives') and len(metadata.get('alternatives', [])) > 0)

    # If no alternatives in memory, check if we have translation history as fallback
    if not has_alternatives:
        history = await db.get_user_history(user_id, limit=1)
        has_alternatives = bool(history)  # Show alternatives if there's any translation history

    # Get interface language
    interface_lang = user_info.get('interface_language', 'ru')

    # Show voice options selection as a new message to keep the translation visible
    voice_text = {
        'ru': "🎧 Что озвучить?",
        'en': "🎧 What to voice?"
    }

    await callback.message.answer(
        voice_text.get(interface_lang, voice_text['ru']),
        reply_markup=get_voice_options_keyboard(has_alternatives, interface_lang)
    )
    await callback.answer()

@router.callback_query(F.data == "help")
async def help_handler(callback: CallbackQuery):
    """Show help message"""
    user_info = await db.get_user(callback.from_user.id)

    await callback.message.edit_text(
        get_text('help', user_info.get('interface_language', 'ru')),
        reply_markup=get_main_menu_keyboard(user_info.get('is_premium', False)),
        parse_mode='HTML'
    )
    await callback.answer()

# Handle no-op callbacks (like page numbers)
@router.callback_query(F.data == "noop")
async def noop_handler(callback: CallbackQuery):
    """Handle no-operation callbacks"""
    await callback.answer()

@router.callback_query(F.data == "show_alternatives")
async def show_alternatives_handler(callback: CallbackQuery):
    """Show translation alternatives"""
    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})

    logger.info(f"Alternatives callback for user {user_id}: metadata keys = {list(metadata.keys())}")
    logger.info(f"Alternatives data: {metadata.get('alternatives', 'Not found')}")

    if not metadata.get('alternatives'):
        await callback.answer("❌ Альтернативы недоступны", show_alert=True)
        return

    # Get user settings for transcription display
    user_info = await db.get_user(user_id)
    show_transcription = user_info.get('show_transcription', False) and user_info.get('is_premium', False)

    alternatives_text = "🔄 <b>Альтернативы перевода:</b>\n\n"
    for i, alt in enumerate(metadata['alternatives'][:5], 1):
        # Handle both old format (string) and new format (dict)
        if isinstance(alt, dict):
            # Escape text for HTML
            escaped_text = escape_html(alt['text'])
            alternatives_text += f"{i}. {escaped_text}\n"
            # Show transcription if enabled and available
            if show_transcription and alt.get('transcription'):
                # No need to escape special characters in HTML
                transcription = escape_html(alt['transcription'])
                alternatives_text += f"   🗣️ {transcription}\n"
        else:
            # Old format: plain string - escape for HTML
            escaped_alt = escape_html(alt)
            alternatives_text += f"{i}. {escaped_alt}\n"

    await callback.message.answer(alternatives_text, parse_mode='HTML')
    await callback.answer()

@router.callback_query(F.data == "show_explanation")
async def show_explanation_handler(callback: CallbackQuery):
    """Show translation explanation"""
    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})

    # Get user's interface language
    from bot.database import db
    user_info = await db.get_user(user_id)
    interface_lang = user_info.get('interface_language', 'ru') if user_info else 'ru'

    explanation = metadata.get('explanation', '') or ''
    explanation = explanation.strip()
    if not explanation:
        error_messages = {
            'ru': "❌ Объяснение недоступно",
            'en': "❌ Explanation not available"
        }
        error_msg = error_messages.get(interface_lang, error_messages['ru'])
        await callback.answer(error_msg, show_alert=True)
        return

    # Multilingual headers
    explanation_headers = {
        'ru': "💡 <b>Объяснение перевода:</b>",
        'en': "💡 <b>Translation explanation:</b>"
    }

    header = explanation_headers.get(interface_lang, explanation_headers['ru'])
    explanation_text = f"{header}\n\n{escape_html(explanation)}"

    await callback.message.answer(explanation_text, parse_mode='HTML')
    await callback.answer()

@router.callback_query(F.data == "show_grammar")
async def show_grammar_handler(callback: CallbackQuery):
    """Show grammar explanation"""
    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})

    # Get user's interface language
    from bot.database import db
    user_info = await db.get_user(user_id)
    interface_lang = user_info.get('interface_language', 'ru') if user_info else 'ru'

    grammar = metadata.get('grammar', '') or ''
    grammar = grammar.strip()
    if not grammar:
        error_messages = {
            'ru': "❌ Грамматическое объяснение недоступно",
            'en': "❌ Grammar explanation not available"
        }
        error_msg = error_messages.get(interface_lang, error_messages['ru'])
        await callback.answer(error_msg, show_alert=True)
        return

    # Multilingual headers
    grammar_headers = {
        'ru': "📚 <b>Грамматическое объяснение:</b>",
        'en': "📚 <b>Grammar explanation:</b>"
    }

    header = grammar_headers.get(interface_lang, grammar_headers['ru'])
    grammar_text = f"{header}\n\n{escape_html(grammar)}"

    await callback.message.answer(grammar_text, parse_mode='HTML')
    await callback.answer()

# Voice generation handlers
async def generate_voice_for_text(callback: CallbackQuery, text: str, voice_type_name: str):
    """Helper function to generate voice for given text"""
    user_info = await db.get_user(callback.from_user.id)

    if not text.strip():
        await callback.answer("❌ Текст для озвучки не найден", show_alert=True)
        return

    await callback.answer(f"🔊 Генерирую {voice_type_name}...")

    # Show voice recording status
    await callback.bot.send_chat_action(chat_id=callback.message.chat.id, action='record_voice')

    try:
        async with VoiceService() as voice_service:
            target_lang = user_info.get('target_language', 'en')
            audio_data = await voice_service.generate_speech(
                text=text.strip(),
                language=target_lang,
                premium=True,
                speed=user_info.get('voice_speed', 1.0),
                voice_type=user_info.get('voice_type', 'alloy')
            )

            if audio_data:
                from aiogram.types import BufferedInputFile
                audio_file = BufferedInputFile(audio_data, filename=f"{voice_type_name}.mp3")
                await callback.message.answer_voice(audio_file)
            else:
                await callback.answer("❌ Не удалось создать голосовое сообщение", show_alert=True)

    except Exception as e:
        logger.error(f"Voice generation error: {e}")
        await callback.answer("❌ Ошибка при создании голосового сообщения", show_alert=True)

@router.callback_query(F.data == "voice_exact")
async def voice_exact_handler(callback: CallbackQuery):
    """Generate voice for exact translation"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    # Get exact translation from metadata
    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})
    exact_text = metadata.get('basic_translation', '')

    # If no basic translation in memory, get from history
    if not exact_text:
        history = await db.get_user_history(user_id, limit=1)
        if history and history[0].get('basic_translation'):
            exact_text = history[0]['basic_translation']

    await generate_voice_for_text(callback, exact_text, "точный перевод")

@router.callback_query(F.data == "voice_styled")
async def voice_styled_handler(callback: CallbackQuery):
    """Generate voice for styled translation"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    # Get styled translation from metadata - need to extract from message or use stored data
    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})

    # Try to get enhanced translation, fallback to basic if not available
    styled_text = metadata.get('enhanced_translation', metadata.get('basic_translation', ''))

    # If no styled text in memory, get from history
    if not styled_text:
        history = await db.get_user_history(user_id, limit=1)
        if history:
            # Prefer enhanced translation, fallback to regular translated_text
            styled_text = (history[0].get('enhanced_translation') or
                          history[0].get('translated_text', ''))

    await generate_voice_for_text(callback, styled_text, "стилизованный перевод")

@router.callback_query(F.data == "voice_alternatives")
async def voice_alternatives_handler(callback: CallbackQuery):
    """Show alternatives selection for voice generation"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    # Get alternatives from metadata first
    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})
    alternatives = metadata.get('alternatives', [])

    # If no alternatives in memory, try to get from database
    if not alternatives:
        history = await db.get_user_history(user_id, limit=1)
        if history and history[0].get('alternatives'):
            import json
            try:
                alternatives = json.loads(history[0]['alternatives'])
            except (json.JSONDecodeError, TypeError):
                alternatives = []

    if not alternatives:
        await callback.answer("❌ Альтернативы недоступны", show_alert=True)
        return

    # Create keyboard with alternatives
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    buttons = []
    for i, alt in enumerate(alternatives[:5], 1):
        # Handle both old format (string) and new format (dict)
        if isinstance(alt, dict):
            text = alt['text'][:50] + ('...' if len(alt['text']) > 50 else '')
        else:
            text = alt[:50] + ('...' if len(alt) > 50 else '')

        buttons.append([InlineKeyboardButton(
            text=f"{i}. {text}",
            callback_data=f"voice_alt_{i-1}"
        )])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_voice_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        "Выберите альтернативу для озвучивания:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data.startswith("voice_alt_"))
async def voice_specific_alternative_handler(callback: CallbackQuery):
    """Voice a specific alternative"""
    # Get alternative index
    alt_index = int(callback.data.split("_")[-1])

    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})
    alternatives = metadata.get('alternatives', [])

    # If no alternatives in memory, try to get from database
    if not alternatives:
        history = await db.get_user_history(user_id, limit=1)
        if history and history[0].get('alternatives'):
            import json
            try:
                alternatives = json.loads(history[0]['alternatives'])
            except (json.JSONDecodeError, TypeError):
                alternatives = []

    if not alternatives or alt_index >= len(alternatives):
        await callback.answer("❌ Альтернатива недоступна", show_alert=True)
        return

    selected_alternative = alternatives[alt_index]

    # Handle both old format (string) and new format (dict)
    if isinstance(selected_alternative, dict):
        alternative_text = selected_alternative['text']
    else:
        alternative_text = selected_alternative

    await generate_voice_for_text(callback, alternative_text, f"альтернатива #{alt_index + 1}")

@router.callback_query(F.data == "back_to_translation")
async def back_to_translation_handler(callback: CallbackQuery):
    """Return to translation actions"""
    user_info = await db.get_user(callback.from_user.id)
    interface_lang = user_info.get('interface_language', 'ru')
    is_premium = user_info.get('is_premium', False)

    # Get original translation message (need to reconstruct or store)
    # For now, just go back to menu
    await callback.message.edit_text(
        get_text('main_menu', interface_lang),
        reply_markup=get_main_menu_keyboard(is_premium)
    )
    await callback.answer()

@router.callback_query(F.data == "voice_any_style")
async def voice_any_style_handler(callback: CallbackQuery):
    """Show style selection for voice generation"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    interface_lang = user_info.get('interface_language', 'ru')

    style_text = {
        'ru': "🎨 Выберите стиль для озвучки:",
        'en': "🎨 Select style for voice:"
    }

    await callback.message.edit_text(
        style_text.get(interface_lang, style_text['ru']),
        reply_markup=get_quick_styles_keyboard(interface_lang, 'voice')
    )
    await callback.answer()

@router.callback_query(F.data == "translate_any_style")
async def translate_any_style_handler(callback: CallbackQuery):
    """Show style selection for re-translation"""
    user_info = await db.get_user(callback.from_user.id)

    if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=await get_premium_keyboard(),
            parse_mode='HTML'
        )
        await callback.answer()
        return

    interface_lang = user_info.get('interface_language', 'ru')

    style_text = {
        'ru': "🔄 Выберите новый стиль перевода:",
        'en': "🔄 Select new translation style:"
    }

    await callback.message.edit_text(
        style_text.get(interface_lang, style_text['ru']),
        reply_markup=get_quick_styles_keyboard(interface_lang, 'translate')
    )
    await callback.answer()

# Helper function for style-based translation
async def translate_with_style(callback: CallbackQuery, style: str, for_voice: bool = False):
    """Helper function to translate text with specific style"""
    user_info = await db.get_user(callback.from_user.id)
    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})

    # Get original text and target language from metadata
    original_text = metadata.get('original_text', '')
    if not original_text:
        await callback.answer("❌ Исходный текст не найден", show_alert=True)
        return

    target_lang = user_info.get('target_language', 'en')
    basic_translation = metadata.get('basic_translation', '')

    await callback.answer(f"🔄 Переводим в стиль: {style}...")

    # Show typing
    await callback.bot.send_chat_action(chat_id=callback.message.chat.id, action='typing')

    try:
        async with TranslatorService() as translator:
            # Re-translate with new style
            translated, new_metadata = await translator.translate(
                text=original_text,
                target_lang=target_lang,
                style=style,
                enhance=True,
                user_id=user_id,
                explain_grammar=True
            )

            if not translated:
                await callback.answer("❌ Ошибка перевода", show_alert=True)
                return

            # Update stored metadata
            last_translation_metadata[user_id] = new_metadata

            # If for voice, generate audio immediately
            if for_voice:
                await generate_voice_for_text(callback, translated, f"перевод в стиле {style}")
            else:
                # Show new translation
                from config import config
                style_names = config.TRANSLATION_STYLES_MULTILINGUAL.get(
                    user_info.get('interface_language', 'ru'),
                    config.TRANSLATION_STYLES_MULTILINGUAL['ru']
                )
                style_display = style_names.get(style, style)

                # Format response similar to main translation handler
                source_lang_name = await translator.get_language_name(
                    new_metadata.get('source_lang', 'auto'),
                    user_info.get('interface_language', 'ru')
                )
                target_lang_name = await translator.get_language_name(
                    target_lang,
                    user_info.get('interface_language', 'ru')
                )

                response_text = f"🌍 <b>{source_lang_name} → {target_lang_name}</b>\n\n"
                response_text += f"📝 <b>Точный перевод:</b>\n{escape_html(new_metadata.get('basic_translation', ''))}\n\n"
                response_text += f"✨ <b>Стилизованный перевод ({style_display}):</b>\n{escape_html(translated)}"

                # Add alternatives and grammar if available
                if new_metadata.get('alternatives'):
                    response_text += f"\n\n🔄 <b>Альтернативы:</b>\n"
                    for alt in new_metadata['alternatives'][:3]:
                        alt_text = alt['text'] if isinstance(alt, dict) else alt
                        response_text += f"• {escape_html(alt_text)}\n"

                if new_metadata.get('grammar') and new_metadata['grammar'].strip():
                    grammar = new_metadata['grammar'].strip()
                    if not grammar.endswith('.') and not grammar.endswith('!') and not grammar.endswith('?'):
                        grammar += '.'
                    response_text += f"\n\n📚 <b>Грамматика:</b> {escape_html(grammar[:250])}"
                    if len(grammar) > 250:
                        response_text += "..."

                keyboard = get_translation_actions_keyboard(is_premium=True, interface_lang=user_info.get('interface_language', 'ru'))

                await callback.message.answer(
                    response_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )

    except Exception as e:
        logger.error(f"Style translation error: {e}")
        await callback.answer("❌ Ошибка при переводе", show_alert=True)

# Voice style handlers
@router.callback_query(F.data.startswith("voice_style_"))
async def voice_style_handler(callback: CallbackQuery):
    """Generate voice with specific style"""
    style = callback.data[12:]  # Remove "voice_style_" prefix
    await translate_with_style(callback, style, for_voice=True)

# Translation style handlers
@router.callback_query(F.data.startswith("translate_style_"))
async def translate_style_handler(callback: CallbackQuery):
    """Translate with specific style"""
    style = callback.data[16:]  # Remove "translate_style_" prefix
    await translate_with_style(callback, style, for_voice=False)

@router.callback_query(F.data == "back_to_voice_menu")
async def back_to_voice_menu_handler(callback: CallbackQuery):
    """Return to voice options menu"""
    user_info = await db.get_user(callback.from_user.id)
    user_id = callback.from_user.id
    metadata = last_translation_metadata.get(user_id, {})
    has_alternatives = bool(metadata.get('alternatives') and len(metadata.get('alternatives', [])) > 0)

    # If no alternatives in memory, check if we have translation history as fallback
    if not has_alternatives:
        history = await db.get_user_history(user_id, limit=1)
        has_alternatives = bool(history)  # Show alternatives if there's any translation history

    interface_lang = user_info.get('interface_language', 'ru')

    voice_text = {
        'ru': "🎧 Что озвучить?",
        'en': "🎧 What to voice?"
    }

    await callback.message.edit_text(
        voice_text.get(interface_lang, voice_text['ru']),
        reply_markup=get_voice_options_keyboard(has_alternatives, interface_lang)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("history_view_"))
async def history_view_handler(callback: CallbackQuery):
    """View translation from history with full details"""
    # Extract history item ID
    history_id = int(callback.data.split("_")[-1])
    user_id = callback.from_user.id

    # Show typing
    await callback.bot.send_chat_action(chat_id=callback.message.chat.id, action='typing')

    # Get history item from database
    item = await db.get_history_item(history_id, user_id)

    if not item:
        await callback.answer("❌ Перевод не найден", show_alert=True)
        return

    user_info = await db.get_user(user_id)
    interface_lang = user_info.get('interface_language', 'ru')

    # Parse alternatives from JSON
    import json
    alternatives = []
    if item.get('alternatives'):
        try:
            alternatives = json.loads(item['alternatives'])
        except (json.JSONDecodeError, TypeError):
            alternatives = []

    # Build metadata dict
    metadata = {
        'source_lang': item.get('source_language', 'auto'),
        'basic_translation': item.get('basic_translation'),
        'enhanced_translation': item.get('enhanced_translation'),
        'alternatives': alternatives,
        'transcription': item.get('transcription'),
        'enhanced_transcription': item.get('enhanced_transcription'),
        'grammar': item.get('grammar'),
        'explanation': item.get('explanation')
    }

    # Store metadata for buttons to work
    last_translation_metadata[user_id] = metadata

    # Format response text
    from bot.services.translator import TranslatorService
    async with TranslatorService() as translator:
        source_lang_name = await translator.get_language_name(
            item.get('source_language', 'auto'),
            interface_lang
        )
        target_lang_name = await translator.get_language_name(
            item.get('target_language', 'en'),
            interface_lang
        )

    response_text = f"🌍 <b>{source_lang_name} → {target_lang_name}</b>\n\n"

    # Show basic and enhanced translations
    if item.get('basic_translation'):
        response_text += f"📝 <b>Точный перевод:</b>\n{escape_html(item['basic_translation'])}\n"

        # Show transcription if enabled
        if (user_info.get('show_transcription', False) and
            item.get('transcription')):
            response_text += f"🗣️ {escape_html(item['transcription'])}\n"

        # Get style display name
        from config import config
        style = item.get('style', 'informal')
        style_names = config.TRANSLATION_STYLES_MULTILINGUAL.get(
            interface_lang,
            config.TRANSLATION_STYLES_MULTILINGUAL['ru']
        )
        style_display = style_names.get(style, style)

        if item.get('enhanced_translation'):
            response_text += f"\n✨ <b>Стилизованный перевод ({style_display}):</b>\n{escape_html(item['enhanced_translation'])}"

            # Show enhanced transcription if enabled
            if (user_info.get('show_transcription', False) and
                item.get('enhanced_transcription')):
                response_text += f"\n🗣️ {escape_html(item['enhanced_transcription'])}"
    else:
        # Single translation display
        response_text += f"📝 <b>Перевод:</b>\n{escape_html(item.get('translated_text', ''))}"

    # Show alternatives if available
    if alternatives and user_info.get('is_premium', False):
        response_text += f"\n\n🔄 <b>Альтернативы:</b>\n"
        for alt in alternatives[:3]:
            if isinstance(alt, dict):
                response_text += f"• {escape_html(alt['text'])}\n"
                if (user_info.get('show_transcription', False) and
                    alt.get('transcription')):
                    response_text += f"  🗣️ {escape_html(alt['transcription'])}\n"
            else:
                response_text += f"• {escape_html(alt)}\n"

    # Show explanation if available
    if item.get('explanation') and item['explanation'].strip():
        explanation = item['explanation'].strip()[:200]
        explanation_labels = {
            'ru': "💡 <b>Объяснение:</b>",
            'en': "💡 <b>Explanation:</b>"
        }
        label = explanation_labels.get(interface_lang, explanation_labels['ru'])
        response_text += f"\n{label} {escape_html(explanation)}"
        if len(item['explanation']) > 200:
            response_text += "..."

    # Show grammar if available
    if item.get('grammar') and item['grammar'].strip():
        grammar = item['grammar'].strip()
        if not grammar.endswith('.') and not grammar.endswith('!') and not grammar.endswith('?'):
            grammar += '.'
        grammar_labels = {
            'ru': "📚 <b>Грамматика:</b>",
            'en': "📚 <b>Grammar:</b>"
        }
        label = grammar_labels.get(interface_lang, grammar_labels['ru'])
        response_text += f"\n\n{label} {escape_html(grammar[:250])}"
        if len(grammar) > 250:
            response_text += "..."

    # Send message with action buttons
    from bot.keyboards.inline import get_translation_actions_keyboard
    keyboard = get_translation_actions_keyboard(
        is_premium=user_info.get('is_premium', False),
        interface_lang=interface_lang
    )

    await callback.message.answer(
        response_text,
        parse_mode='HTML',
        reply_markup=keyboard
    )
    await callback.answer()