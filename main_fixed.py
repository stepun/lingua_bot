#!/usr/bin/env python3
"""
LinguaBot - AI-powered Telegram Translation Bot
Fixed main application entry point
"""

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Add bot directory to Python path
sys.path.append(str(Path(__file__).parent))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Import config
try:
    from config import config
    logger.info("✅ Config loaded")
except Exception as e:
    logger.error(f"❌ Config error: {e}")
    sys.exit(1)

# Import database
try:
    from bot.database import db
    logger.info("✅ Database module loaded")
except Exception as e:
    logger.error(f"❌ Database error: {e}")
    sys.exit(1)

# Import handlers
try:
    from bot.handlers import base
    logger.info("✅ Base handlers loaded")
except Exception as e:
    logger.error(f"❌ Base handlers error: {e}")
    # Continue without some handlers
    base = None

try:
    from bot.handlers import callbacks
    logger.info("✅ Callback handlers loaded")
except Exception as e:
    logger.error(f"❌ Callback handlers error: {e}")
    callbacks = None

try:
    from bot.handlers import payments
    logger.info("✅ Payment handlers loaded")
except Exception as e:
    logger.error(f"❌ Payment handlers error: {e}")
    payments = None

try:
    from bot.handlers import export
    logger.info("✅ Export handlers loaded")
except Exception as e:
    logger.error(f"❌ Export handlers error: {e}")
    export = None

# Import middlewares
try:
    from bot.middlewares.throttling import ThrottlingMiddleware
    from bot.middlewares.user_middleware import UserMiddleware
    logger.info("✅ Middlewares loaded")
except Exception as e:
    logger.error(f"❌ Middlewares error: {e}")
    ThrottlingMiddleware = None
    UserMiddleware = None

async def on_startup():
    """Bot startup handler"""
    logger.info("🚀 Starting LinguaBot...")

    # Validate configuration
    try:
        config.validate()
        logger.info("✅ Configuration validated")
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        return False

    # Initialize database
    try:
        await db.init()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        return False

    logger.info("🎉 LinguaBot started successfully!")
    return True

async def on_shutdown():
    """Bot shutdown handler"""
    logger.info("🛑 Shutting down LinguaBot...")
    logger.info("👋 LinguaBot stopped")

async def main():
    """Main function"""
    # Validate configuration before starting
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set.")
        return

    # Initialize bot and dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Add middlewares if available
    if ThrottlingMiddleware:
        dp.message.middleware(ThrottlingMiddleware())
        dp.callback_query.middleware(ThrottlingMiddleware())
        logger.info("✅ Throttling middleware added")

    if UserMiddleware:
        dp.message.middleware(UserMiddleware())
        dp.callback_query.middleware(UserMiddleware())
        logger.info("✅ User middleware added")

    # Register routers if available
    if base:
        dp.include_router(base.router)
        logger.info("✅ Base router registered")

    if callbacks:
        dp.include_router(callbacks.router)
        logger.info("✅ Callbacks router registered")

    if payments:
        dp.include_router(payments.router)
        logger.info("✅ Payments router registered")

    if export:
        dp.include_router(export.router)
        logger.info("✅ Export router registered")

    # Set startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Start bot
    try:
        logger.info("🤖 LinguaBot is starting...")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
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