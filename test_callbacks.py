#!/usr/bin/env python3
"""Test script specifically for callback queries"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from dotenv import load_dotenv
import os

load_dotenv()

# Enable detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message(Command("test"))
async def test_command(message: Message):
    """Send test inline keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔘 Test Button 1", callback_data="test1")],
        [InlineKeyboardButton(text="🔘 Test Button 2", callback_data="test2")],
        [InlineKeyboardButton(text="🏠 Menu", callback_data="back_to_menu")]
    ])

    await message.answer("Test keyboard:", reply_markup=keyboard)
    logger.info(f"Sent test keyboard to {message.from_user.username}")

@dp.callback_query(F.data == "test1")
async def test1_handler(callback: CallbackQuery):
    logger.info(f"Received callback: test1 from {callback.from_user.username}")
    await callback.answer("Test 1 clicked!")
    await callback.message.edit_text("You clicked Test 1")

@dp.callback_query(F.data == "test2")
async def test2_handler(callback: CallbackQuery):
    logger.info(f"Received callback: test2 from {callback.from_user.username}")
    await callback.answer("Test 2 clicked!")
    await callback.message.edit_text("You clicked Test 2")

@dp.callback_query(F.data == "back_to_menu")
async def menu_handler(callback: CallbackQuery):
    logger.info(f"Received callback: back_to_menu from {callback.from_user.username}")
    await callback.answer("Menu clicked!")
    await callback.message.edit_text("You clicked Menu")

@dp.callback_query()
async def any_callback(callback: CallbackQuery):
    logger.warning(f"Unhandled callback: {callback.data} from {callback.from_user.username}")
    await callback.answer(f"Unknown callback: {callback.data}")

@dp.message()
async def echo(message: Message):
    logger.info(f"Received message: {message.text}")
    await message.answer(f"Echo: {message.text}")

async def main():
    logger.info("Starting callback test bot...")
    logger.info("Send /test to get test keyboard")

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Stopping bot...")

if __name__ == "__main__":
    asyncio.run(main())