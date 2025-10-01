"""Message templates for different languages"""

MESSAGES = {
    'ru': {
        'welcome': """🎉 *Добро пожаловать в PolyglotAI44!*

{premium_status}

🌍 Я умный переводчик с поддержкой ИИ, который поможет вам:
• Переводить тексты на 25+ языков
• Улучшать переводы с помощью GPT
• Работать с голосовыми сообщениями
• Изучать языки с объяснениями

Просто отправьте мне текст, и я переведу его на выбранный язык!

🆓 *Бесплатно:* до 10 переводов в день
⭐ *Премиум:* безлимитные переводы, голос, история и многое другое!""",

        'main_menu': """📋 *Главное меню*

Выберите действие из меню ниже или просто отправьте текст для перевода.""",

        'help': """❓ *Справка по боту*

*Основные команды:*
• Отправьте любой текст — получите перевод
• /язык — выбрать язык перевода
• /стиль — выбрать стиль перевода
• /настройки — настройки бота
• /премиум — информация о подписке
• /отзыв — оставить отзыв о боте

*Стили перевода:*
• 😊 Неформальный — для общения с друзьями
• 🎩 Формальный — для официальных документов
• 💼 Деловой — для бизнес-переписки
• ✈️ Путешествия — простые фразы для туристов
• 🎓 Академический — для научных текстов

*Премиум функции:*
• 🔊 Голосовые сообщения и озвучка
• 📚 История переводов (100 последних)
• 📄 Экспорт истории в PDF
• 🔄 Альтернативные варианты перевода
• 📝 Объяснение грамматики
• ⚡ Приоритетная обработка

*Поддерживаемые языки:*
Английский, Русский, Испанский, Французский, Немецкий, Итальянский, Португальский, Японский, Китайский, Корейский, Арабский, Хинди, Турецкий и многие другие!""",

        'premium_info': """⭐ *Премиум подписка*

*Что входит в премиум:*
• 🚫 Безлимитные переводы
• 🎤 Голосовой ввод (Whisper AI)
• 🔊 Озвучка переводов (качественный TTS)
• 📚 История переводов (100 последних)
• 📄 Экспорт истории в PDF
• 🔄 Альтернативные варианты
• 📝 Объяснение грамматики
• ⚡ Приоритетная обработка
• 🎨 Дополнительные стили

💰 *Выберите план подписки:*
Нажмите на кнопку ниже для мгновенной оплаты!

🔥 *Специальное предложение!*
При покупке годовой подписки вы экономите 1200₽!

*Способы оплаты:*
Банковские карты, СБП, электронные кошельки""",

        'premium_features': """⭐ *Премиум функции подробно*

*🎤 Голосовой ввод*
Отправляйте голосовые сообщения — я распознаю речь и переведу

*🔊 Озвучка переводов*
Получайте переводы в виде голосовых сообщений с естественным произношением

*📚 История переводов*
Сохраняйте до 100 последних переводов для повторного использования

*📄 Экспорт в PDF*
Создавайте персональные разговорники из вашей истории

*🔄 Альтернативы*
Получайте несколько вариантов перевода для выбора лучшего

*📝 Объяснения*
ИИ объясняет грамматику и особенности перевода

*⚡ Приоритет*
Ваши запросы обрабатываются в первую очередь""",

        'already_premium': """✅ *У вас уже есть премиум подписка!*

Наслаждайтесь всеми возможностями бота:
• Безлимитные переводы
• Голосовые сообщения
• История и экспорт
• ИИ-улучшения""",

        'daily_limit_reached': """⚠️ *Лимит исчерпан*

Вы использовали все 10 бесплатных переводов на сегодня.

💡 *Обновление в 00:00 МСК*

⭐ *Премиум подписка* дает безлимитные переводы!
Нажмите кнопку ниже, чтобы узнать больше.""",

        'translation_failed': """❌ *Ошибка перевода*

Не удалось перевести текст. Попробуйте:
• Переформулировать фразу
• Проверить язык текста
• Повторить запрос через минуту""",

        'voice_premium_required': """🎤 *Голосовые функции*

Распознавание и озвучка доступны только в премиум версии.

⭐ Оформите подписку, чтобы пользоваться голосовыми функциями!""",

        'processing_voice': """🎤 Обрабатываю голосовое сообщение...""",

        'voice_processing_failed': """❌ Не удалось обработать голосовое сообщение

Попробуйте:
• Говорить четче
• Уменьшить фоновый шум
• Отправить более короткое сообщение""",

        'select_language': """🌍 *Выбор языка перевода*

Текущий язык: *{current_lang}*

Выберите новый язык из списка ниже:""",

        'language_changed': """✅ *Язык изменен*

Теперь все тексты будут переводиться на: *{language}*""",

        'select_style': """🎨 *Выбор стиля перевода*

Текущий стиль: *{current_style}*

Выберите новый стиль:""",

        'style_changed': """✅ *Стиль изменен*

Теперь переводы будут в стиле: *{style}*""",

        'settings_menu': """⚙️ *Настройки*

Персонализируйте работу бота под ваши потребности:""",

        'history_header': """📚 *История переводов*

Ваши последние переводы:""",

        'no_history': """📚 *История пуста*

У вас пока нет сохраненных переводов.
История доступна только в премиум версии.""",

        'premium_required': """⭐ *Премиум функция*

Эта функция доступна только подписчикам премиум версии.

💳 Оформите подписку прямо сейчас и получите мгновенный доступ!"""
    },

    'en': {
        'welcome': """🎉 *Welcome to PolyglotAI44!*

🌍 I'm an AI-powered smart translator that will help you:
• Translate texts into 25+ languages
• Improve translations with GPT
• Work with voice messages
• Learn languages with explanations

Just send me any text and I'll translate it to your chosen language!

🆓 *Free:* up to 10 translations per day
⭐ *Premium:* unlimited translations, voice, history and more!""",

        'main_menu': """📋 *Main Menu*

Choose an action from the menu below or just send text for translation.""",

        'help': """❓ *Bot Help*

*Main commands:*
• Send any text — get translation
• /language — choose translation language
• /style — choose translation style
• /settings — bot settings
• /premium — subscription info
• /feedback — leave feedback about the bot

*Translation styles:*
• 😊 Informal — for chatting with friends
• 🎩 Formal — for official documents
• 💼 Business — for business correspondence
• ✈️ Travel — simple phrases for tourists
• 🎓 Academic — for scientific texts

*Premium features:*
• 🔊 Voice messages and speech
• 📚 Translation history (last 100)
• 📄 Export history to PDF
• 🔄 Alternative translations
• 📝 Grammar explanations
• ⚡ Priority processing

*Supported languages:*
English, Russian, Spanish, French, German, Italian, Portuguese, Japanese, Chinese, Korean, Arabic, Hindi, Turkish and many more!""",

        'premium_info': """⭐ *Premium Subscription*

*What's included in premium:*
• 🚫 Unlimited translations
• 🎤 Voice input (Whisper AI)
• 🔊 Text-to-speech (quality TTS)
• 📚 Translation history (last 100)
• 📄 Export history to PDF
• 🔄 Alternative variants
• 📝 Grammar explanations
• ⚡ Priority processing
• 🎨 Additional styles

*Prices:*
• 📅 Monthly: 490₽
• 📅 Yearly: 4680₽ (20% off!)

*Payment methods:*
Bank cards, SBP, e-wallets"""
    }
}

def get_text(key: str, language: str = 'ru') -> str:
    """Get localized text"""
    return MESSAGES.get(language, MESSAGES['ru']).get(key, f"Missing text: {key}")

def get_welcome_text(language: str = 'ru', is_premium: bool = False, premium_until: str = None) -> str:
    """Get welcome text with premium status"""
    welcome_template = get_text('welcome', language)

    if is_premium and premium_until:
        from datetime import datetime
        try:
            # Parse premium_until date
            if isinstance(premium_until, str):
                premium_until_dt = datetime.fromisoformat(premium_until.replace('Z', '+00:00'))
            else:
                premium_until_dt = premium_until

            premium_status = f"✅ *Премиум статус: АКТИВЕН*\n📅 Действует до: {premium_until_dt.strftime('%d.%m.%Y')}"
        except:
            premium_status = "✅ *Премиум статус: АКТИВЕН*"
    else:
        premium_status = "🆓 *Статус: Базовый пользователь*"

    return welcome_template.format(premium_status=premium_status)