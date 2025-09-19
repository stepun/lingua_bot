#!/usr/bin/env python3
"""
Удаление webhook для запуска бота в polling режиме
"""

import asyncio
import os
from aiogram import Bot
from dotenv import load_dotenv

async def delete_webhook():
    load_dotenv()

    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN не найден в .env")
        return

    bot = Bot(token=token)

    try:
        # Удаляем webhook
        await bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook удален")

        # Проверяем информацию о боте
        me = await bot.get_me()
        print(f"✅ Бот @{me.username} готов к работе в polling режиме")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(delete_webhook())