#!/usr/bin/env python3
"""
LinguaBot - AI-powered Telegram Translation Bot
Main application entry point
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Add bot directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import config
from bot.database import db
from bot.handlers import base, callbacks, payments, export, admin
from bot.middlewares.throttling import ThrottlingMiddleware
from bot.middlewares.user_middleware import UserMiddleware
from bot.middlewares.admin import AdminMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / 'bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

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

    # Add middlewares
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(ThrottlingMiddleware())
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.message.middleware(AdminMiddleware())
    dp.callback_query.middleware(AdminMiddleware())

    # Register routers
    dp.include_router(admin.router)  # Admin router first for priority
    dp.include_router(base.router)
    dp.include_router(callbacks.router)
    dp.include_router(payments.router)
    dp.include_router(export.router)

    # Set startup and shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Check if running on Railway or similar cloud platform
    port = int(os.getenv("PORT", "0"))
    if port > 0:
        # Running on cloud platform - use webhook mode
        from aiohttp import web
        from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

        webhook_host = os.getenv("RAILWAY_STATIC_URL") or os.getenv("RAILWAY_PUBLIC_URL") or f"https://localhost:{port}"
        webhook_path = config.WEBHOOK_PATH
        webhook_url = f"{webhook_host}{webhook_path}"

        logger.info(f"🌐 Setting up webhook mode: {webhook_url}")

        # Set webhook
        await bot.set_webhook(
            url=webhook_url,
            allowed_updates=dp.resolve_used_update_types()
        )

        # Create web app
        app = web.Application()
        SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        ).register(app, path=webhook_path)

        setup_application(app, dp, bot=bot)

        # Start web server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()

        logger.info(f"🚀 LinguaBot webhook server started on port {port}")

        # Keep the server running
        try:
            await asyncio.Future()  # Run forever
        finally:
            await runner.cleanup()
            await bot.session.close()
    else:
        # Local development - use polling mode
        try:
            logger.info("🤖 LinguaBot is starting in polling mode...")
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