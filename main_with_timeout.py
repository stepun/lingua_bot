#!/usr/bin/env python3
"""Main bot with proper timeouts and error handling"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
import aiohttp

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

    logger.info("🚀 Starting PolyglotAI44 with timeouts...")

    # Create session with timeout
    timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_read=10)
    connector = aiohttp.TCPConnector(limit=100, ttl_dns_cache=300)

    session = AiohttpSession(
        timeout=timeout,
        connector=connector
    )

    # Initialize bot with custom session
    bot = Bot(
        token=config.BOT_TOKEN,
        session=session
    )

    dp = Dispatcher()

    # Initialize database
    await db.init()
    logger.info("✅ Database initialized")

    # Register only working middleware
    throttle = ThrottlingMiddleware(rate=10, per=60)
    dp.message.middleware(throttle)
    dp.callback_query.middleware(throttle)
    logger.info("✅ Throttling middleware registered")

    # Register routers
    dp.include_router(admin.router)
    dp.include_router(base.router)
    dp.include_router(callbacks.router)
    dp.include_router(payments.router)
    dp.include_router(export.router)
    logger.info("✅ All routers registered")

    # Get bot info
    me = await bot.get_me()
    logger.info(f"🤖 Bot @{me.username} started with timeout protection")

    try:
        # Start polling with allowed updates
        await dp.start_polling(
            bot,
            allowed_updates=['message', 'callback_query', 'inline_query'],
            handle_signals=False
        )
    except KeyboardInterrupt:
        logger.info("⏹️ Stopping bot...")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        await bot.session.close()
        await db.close()
        logger.info("👋 Bot stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")