#!/usr/bin/env python3
"""Main bot without middlewares for testing"""

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
from config import config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function"""

    logger.info("🚀 Starting bot WITHOUT middlewares...")

    # Initialize bot and dispatcher
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Initialize database
    await db.init()
    logger.info("✅ Database initialized")

    # NO MIDDLEWARES - testing raw handlers

    # Register routers in correct order
    dp.include_router(admin.router)
    logger.info("✅ Admin router registered")

    dp.include_router(base.router)
    logger.info("✅ Base router registered")

    dp.include_router(callbacks.router)
    logger.info("✅ Callbacks router registered")

    dp.include_router(payments.router)
    logger.info("✅ Payments router registered")

    dp.include_router(export.router)
    logger.info("✅ Export router registered")

    # Get bot info
    me = await bot.get_me()
    logger.info(f"🤖 Bot @{me.username} started successfully!")
    logger.info("⚠️ Running WITHOUT middlewares for testing")

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