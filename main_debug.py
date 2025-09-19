#!/usr/bin/env python3
"""Debug version of main bot with logging"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv

from bot.handlers import base, callbacks, admin, payments, export
from bot.database import db
from bot.middlewares.throttle import ThrottleMiddleware
from bot.middlewares.user import UserMiddleware
from config import config

# Load environment variables
load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function"""

    logger.info("🚀 Starting bot in DEBUG mode...")

    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Initialize database
    await db.init()
    logger.info("✅ Database initialized")

    # Register middlewares
    dp.message.middleware(ThrottleMiddleware())
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    logger.info("✅ Middlewares registered")

    # IMPORTANT: Register routers in correct order
    # Admin handlers have highest priority
    dp.include_router(admin.router)
    logger.info("✅ Admin router registered")

    # Then base handlers (includes /start)
    dp.include_router(base.router)
    logger.info("✅ Base router registered")

    # Then callback handlers
    dp.include_router(callbacks.router)
    logger.info("✅ Callbacks router registered")

    # Then payment handlers
    dp.include_router(payments.router)
    logger.info("✅ Payments router registered")

    # Finally export handlers
    dp.include_router(export.router)
    logger.info("✅ Export router registered")

    # Add debug handler to see all incoming messages
    @dp.message()
    async def debug_handler(message: Message):
        logger.info(f"📨 [DEBUG] Unhandled message from {message.from_user.username}: {message.text}")

    # Get bot info
    me = await bot.get_me()
    logger.info(f"🤖 Bot @{me.username} started successfully!")
    logger.info("Waiting for messages...")

    try:
        # Start polling
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("⏹️ Stopping bot...")
    finally:
        await bot.session.close()
        await db.close()
        logger.info("👋 Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())