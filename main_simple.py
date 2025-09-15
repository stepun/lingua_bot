#!/usr/bin/env python3
"""
LinguaBot - Простая версия для первого запуска
"""

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

# Add bot directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple handlers
async def start_handler(message: Message):
    """Handle /start command"""
    await message.answer(
        "🎉 <b>Добро пожаловать в LinguaBot!</b>\n\n"
        "🌍 Я умный переводчик с поддержкой ИИ.\n"
        "Просто отправьте мне любой текст, и я переведу его!\n\n"
        "Команды:\n"
        "• /help - справка\n"
        "• /test - проверка работы",
        parse_mode='HTML'
    )

async def help_handler(message: Message):
    """Handle /help command"""
    await message.answer(
        "❓ <b>Справка LinguaBot</b>\n\n"
        "🔸 Отправьте любой текст - получите перевод\n"
        "🔸 /test - проверка подключения к OpenAI\n\n"
        "⚠️ Это упрощенная версия для тестирования."
    )

async def test_handler(message: Message):
    """Test OpenAI connection"""
    try:
        import openai
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'OpenAI connection works!'"}],
            max_tokens=10
        )

        await message.answer(f"✅ Тест успешен: {response.choices[0].message.content}")
    except Exception as e:
        await message.answer(f"❌ Ошибка теста: {str(e)}")

async def text_handler(message: Message):
    """Handle text messages"""
    try:
        # Simple translation using OpenAI
        import openai
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)

        await message.answer("🔄 Перевожу...")

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Переведи следующий текст на английский язык. Отвечай только переводом."},
                {"role": "user", "content": message.text}
            ],
            max_tokens=200
        )

        translation = response.choices[0].message.content
        await message.answer(f"🌍 <b>Перевод:</b>\n{translation}", parse_mode='HTML')

    except Exception as e:
        await message.answer(f"❌ Ошибка перевода: {str(e)}")

async def main():
    """Main function"""
    # Validate configuration
    try:
        config.validate()
        logger.info("✅ Configuration validated")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return

    # Initialize bot and dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Register handlers
    dp.message.register(start_handler, CommandStart())
    dp.message.register(help_handler, Command("help"))
    dp.message.register(test_handler, Command("test"))
    dp.message.register(text_handler)

    # Start bot
    try:
        logger.info("🤖 LinguaBot (Simple) is starting...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Bot startup error: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)