"""Admin panel handlers"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.middlewares.admin import is_admin
from bot.database import Database
from config import config
import os
import logging

router = Router()
db = Database()
logger = logging.getLogger(__name__)

# Test handler - should be registered first
@router.message(Command("test_admin"))
async def test_admin_handler(message: Message):
    """Test handler to check if router works"""
    await message.answer(f"✅ Test OK! Your ID: {message.from_user.id}")

class AdminStates(StatesGroup):
    waiting_yookassa_shop_id = State()
    waiting_yookassa_secret_key = State()
    waiting_webhook_secret = State()

@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Admin panel main menu"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return

    admin_text = f"""
🔐 **Админ панель LinguaBot**

👤 **Ваш ID:** `{message.from_user.id}`
✅ **Статус:** Администратор

⚙️ **Доступные команды:**
/admin_panel - Открыть веб-панель администратора
/admin_config - Настройка платежной системы
/admin_stats - Статистика бота
/admin_users - Управление пользователями
/admin_logs - Просмотр логов

💳 **Текущая конфигурация YooKassa:**
• Shop ID: `{config.YOOKASSA_SHOP_ID}`
• Secret Key: `{'✅ Настроен' if config.YOOKASSA_SECRET_KEY != 'your_secret_key' else '❌ Не настроен'}`
• Webhook Secret: `{'✅ Настроен' if config.PAYMENT_WEBHOOK_SECRET != 'your_webhook_secret' else '❌ Не настроен'}`
"""

    await message.answer(admin_text, parse_mode='Markdown')


@router.message(Command("admin_panel"))
async def open_admin_webapp(message: Message):
    """Open admin mini-app"""
    user_id = message.from_user.id
    logger.info(f"Admin panel command from user {user_id}, ADMIN_IDS: {config.ADMIN_IDS}")

    # Check admin rights
    if not is_admin(user_id):
        logger.warning(f"Access denied for user {user_id}")
        await message.answer(
            f"❌ У вас нет прав администратора\n\n"
            f"Ваш ID: `{user_id}`\n"
            f"Текущие админы: `{config.ADMIN_IDS}`\n\n"
            f"Для получения доступа добавьте ваш ID в переменную ADMIN_IDS",
            parse_mode='Markdown'
        )
        return

    logger.info(f"Admin access granted for user {user_id}")

    # Get the admin panel URL from config or use default
    admin_url = os.getenv("ADMIN_PANEL_URL", "http://localhost:8081")

    # Create inline keyboard with WebApp button
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔐 Открыть Admin Panel",
            web_app=WebAppInfo(url=admin_url)
        )]
    ])

    try:
        await message.answer(
            "🎛️ <b>Панель администратора</b>\n\n"
            "Нажмите кнопку ниже, чтобы открыть веб-интерфейс админ-панели.\n\n"
            "В панели доступны:\n"
            "• 📊 Статистика бота\n"
            "• 👥 Управление пользователями\n"
            "• 📝 Просмотр логов\n"
            "• 🌍 Аналитика по языкам\n\n"
            f"URL: {admin_url}",
            reply_markup=keyboard
        )
        logger.info(f"Admin panel opened for user {user_id}")
    except Exception as e:
        logger.error(f"Error opening admin panel: {e}", exc_info=True)
        await message.answer(f"❌ Ошибка открытия админ-панели: {e}")

@router.message(Command("admin_config"))
async def admin_config(message: Message, state: FSMContext):
    """Payment system configuration"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return

    config_text = f"""
💳 **Настройка платежной системы YooKassa**

**Текущие настройки:**
• Shop ID: `{config.YOOKASSA_SHOP_ID}`
• Secret Key: `{'✅ Настроен' if config.YOOKASSA_SECRET_KEY != 'your_secret_key' else '❌ Не настроен'}`
• Webhook Secret: `{'✅ Настроен' if config.PAYMENT_WEBHOOK_SECRET != 'your_webhook_secret' else '❌ Не настроен'}`

**Для настройки отправьте команды:**
/set_shop_id - Установить Shop ID
/set_secret_key - Установить Secret Key
/set_webhook_secret - Установить Webhook Secret

**Получить ключи можно в личном кабинете YooKassa:**
https://yookassa.ru/
"""

    await message.answer(config_text, parse_mode='Markdown')

@router.message(Command("set_shop_id"))
async def set_shop_id(message: Message, state: FSMContext):
    """Set YooKassa Shop ID"""
    if not is_admin(message.from_user.id):
        return

    await message.answer("💳 Введите Shop ID от YooKassa:")
    await state.set_state(AdminStates.waiting_yookassa_shop_id)

@router.message(AdminStates.waiting_yookassa_shop_id)
async def process_shop_id(message: Message, state: FSMContext):
    """Process Shop ID input"""
    shop_id = message.text.strip()

    if len(shop_id) < 5:
        await message.answer("❌ Shop ID слишком короткий. Попробуйте снова:")
        return

    # Update .env file
    update_env_var("YOOKASSA_SHOP_ID", shop_id)

    await message.answer(f"✅ Shop ID установлен: `{shop_id}`\n\n⚠️ Для применения изменений необходимо перезапустить бота.", parse_mode='Markdown')
    await state.clear()

@router.message(Command("set_secret_key"))
async def set_secret_key(message: Message, state: FSMContext):
    """Set YooKassa Secret Key"""
    if not is_admin(message.from_user.id):
        return

    await message.answer("🔑 Введите Secret Key от YooKassa:")
    await state.set_state(AdminStates.waiting_yookassa_secret_key)

@router.message(AdminStates.waiting_yookassa_secret_key)
async def process_secret_key(message: Message, state: FSMContext):
    """Process Secret Key input"""
    secret_key = message.text.strip()

    if len(secret_key) < 10:
        await message.answer("❌ Secret Key слишком короткий. Попробуйте снова:")
        return

    # Update .env file
    update_env_var("YOOKASSA_SECRET_KEY", secret_key)

    # Delete the message with secret key for security
    try:
        await message.delete()
    except:
        pass

    await message.answer("✅ Secret Key установлен и удален из чата для безопасности.\n\n⚠️ Для применения изменений необходимо перезапустить бота.")
    await state.clear()

@router.message(Command("set_webhook_secret"))
async def set_webhook_secret(message: Message, state: FSMContext):
    """Set Webhook Secret"""
    if not is_admin(message.from_user.id):
        return

    await message.answer("🔐 Введите Webhook Secret:")
    await state.set_state(AdminStates.waiting_webhook_secret)

@router.message(AdminStates.waiting_webhook_secret)
async def process_webhook_secret(message: Message, state: FSMContext):
    """Process Webhook Secret input"""
    webhook_secret = message.text.strip()

    if len(webhook_secret) < 8:
        await message.answer("❌ Webhook Secret слишком короткий. Попробуйте снова:")
        return

    # Update .env file
    update_env_var("PAYMENT_WEBHOOK_SECRET", webhook_secret)

    # Delete the message with secret for security
    try:
        await message.delete()
    except:
        pass

    await message.answer("✅ Webhook Secret установлен и удален из чата для безопасности.\n\n⚠️ Для применения изменений необходимо перезапустить бота.")
    await state.clear()

@router.message(Command("admin_stats"))
async def admin_stats(message: Message):
    """Show bot statistics"""
    if not is_admin(message.from_user.id):
        return

    try:
        # Get stats from database
        total_users = await db.get_user_count()
        premium_users = await db.get_premium_user_count()

        stats_text = f"""
📊 **Статистика бота**

👥 **Пользователи:**
• Всего: {total_users}
• Премиум: {premium_users}
• Обычные: {total_users - premium_users}

💳 **Платежная система:**
• Статус: {'✅ Настроена' if config.YOOKASSA_SHOP_ID != 'your_shop_id' else '❌ Не настроена'}

🔧 **Система:**
• Версия Python: 3.11
• База данных: SQLite
• Админ ID: {config.ADMIN_ID}
"""

        await message.answer(stats_text, parse_mode='Markdown')
    except Exception as e:
        await message.answer(f"❌ Ошибка получения статистики: {e}")

def update_env_var(key: str, value: str):
    """Update environment variable in .env file"""
    env_path = ".env"

    # Read current .env content
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Update or add the variable
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break

    if not found:
        lines.append(f"{key}={value}\n")

    # Write back to .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    logger.info(f"Updated .env variable: {key}")