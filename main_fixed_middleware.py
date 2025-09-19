#!/usr/bin/env python3
"""Main bot with fixed middleware registration"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers import base, callbacks, admin, payments, export
from bot.database import db
from bot.middlewares.throttling import ThrottlingMiddleware
from config import config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Main function"""

    logger.info("🚀 Starting PolyglotAI44...")

    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Initialize database
    await db.init()
    logger.info("✅ Database initialized")

    # Register only working middleware
    # ThrottlingMiddleware is safe and doesn't block handlers
    throttle = ThrottlingMiddleware(rate=10, per=60)
    dp.message.middleware(throttle)
    dp.callback_query.middleware(throttle)
    logger.info("✅ Throttling middleware registered")

    # Register routers in correct order
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

    # Get bot info
    me = await bot.get_me()
    logger.info(f"🤖 Bot @{me.username} started successfully!")
    logger.info("✅ All systems operational")

    try:
        # Start polling
        await dp.start_polling(bot, allowed_updates=['message', 'callback_query'])
    except KeyboardInterrupt:
        logger.info("⏹️ Stopping bot...")
    finally:
        await bot.session.close()
        await db.close()
        logger.info("👋 Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())