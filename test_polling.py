import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

@dp.message()
async def echo(message: Message):
    print(f"Получено сообщение: {message.text}")
    await message.answer(f"Эхо: {message.text}")

async def main():
    print("Бот запущен, отправьте любое сообщение...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())