from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Voice, Audio, Document
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
import logging
import time

from bot.database import db
from bot.keyboards.inline import get_main_menu_keyboard, get_translation_actions_keyboard
from bot.keyboards.reply import get_main_reply_keyboard
from bot.services.translator import TranslatorService
from bot.services.voice import VoiceService
from bot.utils.messages import get_text, get_welcome_text
from bot.utils.rate_limit import rate_limit
from config import config

logger = logging.getLogger(__name__)
router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()

    # Add user to database
    user = message.from_user
    await db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code or 'ru'
    )

    # Get user info
    user_info = await db.get_user(user.id)

    # Check active subscription from subscriptions table
    from datetime import datetime
    async with db_adapter.get_connection() as conn:
        subscription = await conn.fetchone("""
            SELECT expires_at FROM subscriptions
            WHERE user_id = $1
              AND status = 'active'
              AND expires_at > $2
            ORDER BY expires_at DESC LIMIT 1
        """, user.id, datetime.now())

    is_premium = subscription is not None
    premium_until = subscription['expires_at'] if subscription else None

    welcome_text = get_welcome_text(
        language=user_info.get('interface_language', 'ru'),
        is_premium=is_premium,
        premium_until=premium_until
    )

    await message.answer(
        welcome_text,
        reply_markup=get_main_reply_keyboard(is_premium)
    )

    await message.answer(
        get_text('main_menu', user_info.get('interface_language', 'ru')),
        reply_markup=get_main_menu_keyboard(is_premium)
    )

@router.message(Command("help", "помощь"))
async def help_handler(message: Message):
    """Handle help command"""
    user_info = await db.get_user(message.from_user.id)
    help_text = get_text('help', user_info.get('interface_language', 'ru'))

    await message.answer(help_text)

@router.message(Command("premium", "премиум"))
async def premium_handler(message: Message):
    """Handle premium command"""
    user_info = await db.get_user(message.from_user.id)

    if user_info.get('is_premium'):
        premium_text = get_text('already_premium', user_info.get('interface_language', 'ru'))
    else:
        premium_text = get_text('premium_info', user_info.get('interface_language', 'ru'))

    await message.answer(premium_text)

@router.message(Command("language", "язык"))
async def language_handler(message: Message):
    """Handle language selection command"""
    from bot.keyboards.inline import get_language_selection_keyboard

    from bot.services.translator import TranslatorService

    user_info = await db.get_user(message.from_user.id)
    current_lang = user_info.get('target_language', 'en')
    interface_lang = user_info.get('interface_language', 'ru')

    async with TranslatorService() as translator:
        current_lang_name = await translator.get_language_name(current_lang, interface_lang)

    text = get_text('select_language', interface_lang).format(
        current_lang=current_lang_name
    )

    await message.answer(text, reply_markup=get_language_selection_keyboard())

@router.message(Command("style", "стиль"))
async def style_handler(message: Message):
    """Handle style selection command"""
    from bot.keyboards.inline import get_style_selection_keyboard

    user_info = await db.get_user(message.from_user.id)
    current_style = user_info.get('translation_style', 'informal')

    text = get_text('select_style', user_info.get('interface_language', 'ru')).format(
        current_style=config.TRANSLATION_STYLES.get(current_style, current_style)
    )

    await message.answer(text, reply_markup=get_style_selection_keyboard())

@router.message(Command("settings", "настройки"))
async def settings_handler(message: Message):
    """Handle settings command"""
    from bot.keyboards.inline import get_settings_keyboard

    user_info = await db.get_user(message.from_user.id)
    text = get_text('settings_menu', user_info.get('interface_language', 'ru'))

    await message.answer(text, reply_markup=get_settings_keyboard(user_info))

@router.message(Command("feedback"))
async def feedback_handler(message: Message):
    """Handle feedback command"""
    user_info = await db.get_user(message.from_user.id)
    interface_lang = user_info.get('interface_language', 'ru')

    # Extract feedback message from command
    feedback_text = message.text.split(maxsplit=1)

    if len(feedback_text) < 2:
        # No feedback text provided
        if interface_lang == 'ru':
            await message.answer(
                "📝 Отправьте отзыв или сообщение о проблеме:\n\n"
                "Используйте: /feedback [ваше сообщение]\n\n"
                "Например:\n"
                "/feedback Отличный бот, но хотелось бы добавить поддержку японского языка"
            )
        else:
            await message.answer(
                "📝 Send feedback or report a problem:\n\n"
                "Usage: /feedback [your message]\n\n"
                "Example:\n"
                "/feedback Great bot, but would love to see Japanese language support"
            )
        return

    feedback_message = feedback_text[1].strip()

    # Save feedback to database
    success = await db.add_feedback(message.from_user.id, feedback_message)

    if success:
        if interface_lang == 'ru':
            await message.answer(
                "✅ Спасибо за ваш отзыв!\n\n"
                "Ваше сообщение получено и будет рассмотрено администрацией."
            )
        else:
            await message.answer(
                "✅ Thank you for your feedback!\n\n"
                "Your message has been received and will be reviewed by the administration."
            )
    else:
        if interface_lang == 'ru':
            await message.answer(
                "❌ Ошибка при сохранении отзыва. Попробуйте позже."
            )
        else:
            await message.answer(
                "❌ Error saving feedback. Please try again later."
            )

@router.message(Command("history", "история"))
async def history_handler(message: Message):
    """Handle history command"""
    user_info = await db.get_user(message.from_user.id)

    if not user_info.get('is_premium'):
        await message.answer(get_text('premium_required', user_info.get('interface_language', 'ru')))
        return

    # Get recent history
    history = await db.get_user_history(message.from_user.id, limit=10)

    if not history:
        await message.answer(get_text('no_history', user_info.get('interface_language', 'ru')))
        return

    text = get_text('history_header', user_info.get('interface_language', 'ru')) + "\n\n"

    for item in history:
        text += f"🔸 {item['source_text'][:50]}{'...' if len(item['source_text']) > 50 else ''}\n"
        text += f"   → {item['translated_text'][:50]}{'...' if len(item['translated_text']) > 50 else ''}\n"
        text += f"   📅 {item['created_at'][:19]}\n\n"

    from bot.keyboards.inline import get_history_keyboard
    await message.answer(text, reply_markup=get_history_keyboard())

@router.message(F.voice)
@rate_limit(key='voice', rate=5, per=60)
async def voice_handler(message: Message):
    """Handle voice messages"""
    start_time = time.time()
    user_info = await db.get_user(message.from_user.id)

    # Check if user can use voice features
    if not user_info.get('is_premium'):
        await message.answer(get_text('voice_premium_required', user_info.get('interface_language', 'ru')))
        return

    # Check daily limit for free users (voice counts as translation) - skip for admins
    from config import config
    is_admin = message.from_user.id in config.ADMIN_IDS

    if not is_admin:
        can_translate, remaining = await db.check_daily_limit(message.from_user.id)
        if not can_translate:
            await message.answer(get_text('daily_limit_reached', user_info.get('interface_language', 'ru')))
            return

    # Show processing message
    processing_msg = await message.answer(get_text('processing_voice', user_info.get('interface_language', 'ru')))

    try:
        async with VoiceService() as voice_service:
            # Process voice message
            text = await voice_service.process_voice_message(message.voice.file_id, message.bot)

            if not text:
                await processing_msg.edit_text(get_text('voice_processing_failed', user_info.get('interface_language', 'ru')))
                return

            # Translate the transcribed text
            async with TranslatorService() as translator:
                target_lang = user_info.get('target_language', 'en')
                style = user_info.get('translation_style', 'informal')

                # Check if user is admin or has premium (already imported config above)
                has_premium = user_info.get('is_premium', False) or is_admin

                translated, metadata = await translator.translate(
                    text=text,
                    target_lang=target_lang,
                    style=style,
                    enhance=has_premium,
                    user_id=message.from_user.id,
                    explain_grammar=has_premium
                )

                if not translated:
                    await processing_msg.edit_text(get_text('translation_failed', user_info.get('interface_language', 'ru')))
                    return

                # Update counters
                processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
                await db.increment_translation_count(message.from_user.id)
                await db.add_translation_history(
                    user_id=message.from_user.id,
                    source_text=text,
                    source_language=metadata.get('source_lang'),
                    translated_text=translated,
                    target_language=target_lang,
                    style=style,
                    is_voice=True,
                    basic_translation=metadata.get('basic_translation'),
                    enhanced_translation=metadata.get('enhanced_translation', translated),
                    alternatives=metadata.get('alternatives'),
                    processing_time_ms=processing_time
                )

                # Get style display name
                from config import config
                style_names = config.TRANSLATION_STYLES_MULTILINGUAL.get(
                    user_info.get('interface_language', 'ru'),
                    config.TRANSLATION_STYLES_MULTILINGUAL['ru']
                )
                style_display = style_names.get(style, style)

                # Format response
                response_text = f"🎤 *Распознано:* {text}\n\n"

                # Show both translation stages for premium users
                if 'basic_translation' in metadata and user_info.get('is_premium', False):
                    response_text += f"📝 *Точный перевод:*\n{metadata['basic_translation']}\n\n"
                    response_text += f"✨ *Улучшенный перевод ({style_display}):*\n{translated}"

                    # Add synonyms/alternatives if available
                    if metadata.get('alternatives'):
                        response_text += f"\n\n🔄 *Альтернативы:*\n"
                        for alt in metadata['alternatives'][:2]:  # Show max 2 alternatives
                            response_text += f"• {alt}\n"

                    # Add explanation if available
                    if metadata.get('explanation') and metadata['explanation'].strip():
                        explanation = metadata['explanation'].strip()[:150]  # Shorter for voice
                        explanation_labels = {
                            'ru': "💡 *Объяснение:*",
                            'en': "💡 *Explanation:*"
                        }
                        label = explanation_labels.get(user_info.get('interface_language', 'ru'), explanation_labels['ru'])
                        response_text += f"\n{label} {explanation}"
                        if len(metadata['explanation']) > 150:
                            response_text += "..."
                else:
                    response_text += f"🌍 *Перевод ({style_display}, {config.SUPPORTED_LANGUAGES.get(target_lang, target_lang)}):*\n{translated}"

                # Store metadata for callback buttons
                if user_info.get('is_premium', False):
                    from bot.handlers.callbacks import last_translation_metadata
                    last_translation_metadata[message.from_user.id] = metadata

                await processing_msg.edit_text(
                    response_text,
                    parse_mode='Markdown',
                    reply_markup=get_translation_actions_keyboard(is_premium=user_info.get('is_premium', False), interface_lang=user_info.get('interface_language', 'ru'))
                )

    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        await processing_msg.edit_text(get_text('voice_processing_failed', user_info.get('interface_language', 'ru')))

@router.message(F.text & ~F.text.startswith('/'))
@rate_limit(key='translation', rate=10, per=60)
async def text_translation_handler(message: Message):
    """Handle text translation"""
    start_time = time.time()
    user_info = await db.get_user(message.from_user.id)

    # Handle keyboard button presses
    if message.text == '🌍 Язык':
        await language_handler(message)
        return
    elif message.text == '🎨 Стиль':
        await style_handler(message)
        return
    elif message.text == '⚙️ Настройки':
        await settings_handler(message)
        return
    elif message.text == '❓ Помощь':
        await help_handler(message)
        return
    elif message.text == '📚 История':
        await history_handler(message)
        return
    elif message.text == '📄 Экспорт':
        # Handle export request
        user_info = await db.get_user(message.from_user.id)
        if not user_info.get('is_premium'):
            await message.answer(get_text('premium_required', user_info.get('interface_language', 'ru')))
            return
        from bot.keyboards.inline import get_export_keyboard
        await message.answer(
            get_text('select_export_format', user_info.get('interface_language', 'ru')),
            reply_markup=get_export_keyboard()
        )
        return
    elif message.text == '⭐ Премиум':
        await premium_handler(message)
        return

    # Check daily limit (skip for admins)
    from config import config
    is_admin = message.from_user.id in config.ADMIN_IDS

    if not is_admin:
        can_translate, remaining = await db.check_daily_limit(message.from_user.id)
        if not can_translate:
            limit_text = get_text('daily_limit_reached', user_info.get('interface_language', 'ru'))
            await message.answer(limit_text)
            return

    # Show typing
    await message.bot.send_chat_action(chat_id=message.chat.id, action='typing')

    try:
        async with TranslatorService() as translator:
            target_lang = user_info.get('target_language', 'en')
            style = user_info.get('translation_style', 'informal')

            logger.info(f"Translation request: user={message.from_user.id}, target_lang={target_lang}, user_info_target={user_info.get('target_language')}")

            # Check if user is admin and should get premium features (already imported above)
            has_premium = user_info.get('is_premium', False) or is_admin

            logger.info(f"Translation for user {message.from_user.id}: admin={is_admin}, premium={has_premium}")

            translated, metadata = await translator.translate(
                text=message.text,
                target_lang=target_lang,
                style=style,
                enhance=has_premium,
                user_id=message.from_user.id,
                explain_grammar=has_premium
            )

            if not translated:
                await message.answer(get_text('translation_failed', user_info.get('interface_language', 'ru')))
                return

            # Update counters
            logger.info("Starting database updates...")
            processing_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            await db.increment_translation_count(message.from_user.id)
            await db.add_translation_history(
                user_id=message.from_user.id,
                source_text=message.text,
                source_language=metadata.get('source_lang'),
                translated_text=translated,
                target_language=target_lang,
                style=style,
                is_voice=False,
                basic_translation=metadata.get('basic_translation'),
                enhanced_translation=metadata.get('enhanced_translation', translated),
                alternatives=metadata.get('alternatives'),
                processing_time_ms=processing_time
            )
            logger.info("Database updates completed")

            # Format response
            logger.info(f"Getting language names: source={metadata.get('source_lang', 'auto')}, target={target_lang}")
            source_lang_name = await translator.get_language_name(
                metadata.get('source_lang', 'auto'),
                user_info.get('interface_language', 'ru')
            )
            logger.info(f"Source language name: {source_lang_name}")
            target_lang_name = await translator.get_language_name(
                target_lang,
                user_info.get('interface_language', 'ru')
            )
            logger.info(f"Target language name: {target_lang_name}")

            response_text = f"🌍 *{source_lang_name} → {target_lang_name}*\n\n"

            # Debug logging for translation display
            basic_trans = metadata.get('basic_translation', 'N/A')
            logger.info(f"Translation display logic: basic='{basic_trans[:50]}...', enhanced='{translated[:50]}...', same={basic_trans == translated}")
            logger.info(f"Metadata keys: {list(metadata.keys())}")
            logger.info(f"Has basic_translation key: {'basic_translation' in metadata}")
            logger.info(f"Basic != Enhanced: {metadata.get('basic_translation') != translated}")

            # Get style display name
            from config import config
            style_names = config.TRANSLATION_STYLES_MULTILINGUAL.get(
                user_info.get('interface_language', 'ru'),
                config.TRANSLATION_STYLES_MULTILINGUAL['ru']
            )
            style_display = style_names.get(style, style)

            # Show translations based on user type
            if 'basic_translation' in metadata:
                # For all users - show both basic and styled translations
                logger.info("Showing two-stage translation (basic + styled)")
                response_text += f"📝 *Точный перевод:*\n{metadata['basic_translation']}\n\n"
                response_text += f"✨ *Стилизованный перевод ({style_display}):*\n{translated}"

                # Premium features - alternatives and explanations
                if has_premium:
                    # Add synonyms/alternatives if available
                    if metadata.get('alternatives'):
                        response_text += f"\n\n🔄 *Альтернативы:*\n"
                        for alt in metadata['alternatives'][:3]:  # Show max 3 alternatives
                            response_text += f"• {alt}\n"

                    # Add explanation if available
                    if metadata.get('explanation') and metadata['explanation'].strip():
                        explanation = metadata['explanation'].strip()[:200]  # Limit length
                        explanation_labels = {
                            'ru': "💡 *Объяснение:*",
                            'en': "💡 *Explanation:*"
                        }
                        label = explanation_labels.get(user_info.get('interface_language', 'ru'), explanation_labels['ru'])
                        response_text += f"\n{label} {explanation}"
                        if len(metadata['explanation']) > 200:
                            response_text += "..."

                    # Add grammar if available
                    if metadata.get('grammar') and metadata['grammar'].strip():
                        grammar = metadata['grammar'].strip()
                        # Ensure grammar explanation ends with proper punctuation
                        if not grammar.endswith('.') and not grammar.endswith('!') and not grammar.endswith('?'):
                            grammar += '.'

                        grammar_labels = {
                            'ru': "📚 *Грамматика:*",
                            'en': "📚 *Grammar:*"
                        }
                        label = grammar_labels.get(user_info.get('interface_language', 'ru'), grammar_labels['ru'])
                        response_text += f"\n\n{label} {grammar[:250]}"
                        if len(grammar) > 250:
                            response_text += "..."
            else:
                logger.info("Showing single translation (no two stages)")
                response_text += f"📝 *Перевод ({style_display}):*\n{translated}"

            # Add remaining translations info for free users
            if not user_info.get('is_premium'):
                response_text += f"\n\n📊 Осталось переводов сегодня: {remaining - 1}"

            # Add enhanced info for premium users
            if user_info.get('is_premium') and metadata.get('alternatives'):
                response_text += f"\n\n🔄 *Альтернативы:*\n"
                for alt in metadata['alternatives'][:2]:
                    response_text += f"• {alt}\n"

            keyboard = get_translation_actions_keyboard(is_premium=user_info.get('is_premium', False), interface_lang=user_info.get('interface_language', 'ru'))

            # Store metadata for callback buttons
            if user_info.get('is_premium', False):
                from bot.handlers.callbacks import last_translation_metadata
                logger.info(f"Storing metadata for user {message.from_user.id}: keys = {list(metadata.keys())}")
                logger.info(f"Alternatives: {metadata.get('alternatives', 'Not found')}")
                logger.info(f"Explanation: {metadata.get('explanation', 'Not found')}")
                logger.info(f"Grammar: {metadata.get('grammar', 'Not found')}")
                last_translation_metadata[message.from_user.id] = metadata

            logger.info(f"Sending response to user {message.from_user.id}")
            await message.answer(
                response_text,
                parse_mode='Markdown',
                reply_markup=keyboard
            )
            logger.info("Response sent successfully")

            # Auto voice if enabled
            if user_info.get('auto_voice') and user_info.get('is_premium'):
                try:
                    async with VoiceService() as voice_service:
                        # Use basic translation for voice (more accurate pronunciation)
                        voice_text = metadata.get('basic_translation', translated)
                        logger.info(f"Generating voice for: {voice_text[:50]}...")
                        audio_data = await voice_service.generate_speech(
                            text=voice_text,
                            language=target_lang,
                            premium=True,
                            speed=user_info.get('voice_speed', 1.0),
                            voice_type=user_info.get('voice_type', 'alloy')
                        )

                        if audio_data:
                            from aiogram.types import BufferedInputFile
                            audio_file = BufferedInputFile(audio_data, filename="translation.mp3")
                            await message.answer_voice(audio_file)
                except Exception as e:
                    logger.error(f"Auto voice error: {e}")

    except Exception as e:
        logger.error(f"Translation error: {e}")
        await message.answer(get_text('translation_failed', user_info.get('interface_language', 'ru')))