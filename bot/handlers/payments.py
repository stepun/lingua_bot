"""Payment handlers"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from bot.database import db
from bot.services.payment import PaymentService
from bot.keyboards.inline import get_payment_keyboard, get_main_menu_keyboard
from bot.utils.messages import get_text

logger = logging.getLogger(__name__)
router = Router()

class PaymentStates(StatesGroup):
    waiting_for_payment = State()

payment_service = PaymentService()

@router.callback_query(F.data.startswith("buy_"))
async def handle_subscription_purchase(callback: CallbackQuery, state: FSMContext):
    """Handle subscription purchase"""
    subscription_type = callback.data[4:]  # Remove "buy_" prefix

    if subscription_type not in ["monthly", "yearly"]:
        await callback.answer("❌ Неверный тип подписки", show_alert=True)
        return

    user_info = await db.get_user(callback.from_user.id)

    if user_info.get('is_premium'):
        await callback.answer("✅ У вас уже есть премиум подписка!", show_alert=True)
        return

    # Get subscription details
    amount = payment_service.get_subscription_price(subscription_type)
    description = payment_service.get_subscription_description(subscription_type)

    # Create payment
    payment_data = await payment_service.create_payment(
        user_id=callback.from_user.id,
        subscription_type=subscription_type,
        amount=amount,
        description=description
    )

    if not payment_data:
        # Check if it's a configuration issue
        from config import config
        if (not config.YOOKASSA_SHOP_ID or not config.YOOKASSA_SECRET_KEY or
            config.YOOKASSA_SHOP_ID == "your_shop_id" or
            config.YOOKASSA_SECRET_KEY == "your_secret_key"):
            error_text = "❌ Платежная система временно недоступна.\n\n🔧 Администратор не настроил платежные реквизиты YooKassa."
        else:
            error_text = "❌ Ошибка при создании платежа. Попробуйте позже."

        await callback.message.edit_text(
            error_text,
            reply_markup=get_main_menu_keyboard(False)
        )
        await callback.answer()
        return

    # Save payment info in state
    await state.update_data(
        payment_id=payment_data["payment_id"],
        subscription_type=subscription_type,
        amount=amount
    )
    await state.set_state(PaymentStates.waiting_for_payment)

    # Send payment message
    payment_text = f"""💳 *Оплата подписки*

📦 Тип: {description}
💰 Сумма: {amount}₽
🔑 ID платежа: `{payment_data["payment_id"]}`

Нажмите кнопку ниже для оплаты. После успешной оплаты премиум функции будут активированы автоматически."""

    await callback.message.edit_text(
        payment_text,
        parse_mode='Markdown',
        reply_markup=get_payment_keyboard(payment_data["confirmation_url"])
    )

    await callback.answer("💳 Переход к оплате...")

@router.callback_query(F.data == "check_payment", PaymentStates.waiting_for_payment)
async def check_payment_status(callback: CallbackQuery, state: FSMContext):
    """Check payment status manually"""
    state_data = await state.get_data()
    payment_id = state_data.get("payment_id")

    if not payment_id:
        await callback.answer("❌ Платеж не найден", show_alert=True)
        return

    # Check payment status
    payment_status = await payment_service.check_payment_status(payment_id)

    if not payment_status:
        await callback.answer("❌ Ошибка проверки платежа", show_alert=True)
        return

    if payment_status["paid"]:
        # Payment successful - activate subscription
        subscription_type = state_data.get("subscription_type")
        amount = state_data.get("amount")

        success = await db.activate_subscription(
            user_id=callback.from_user.id,
            subscription_type=subscription_type,
            payment_id=payment_id,
            amount=amount
        )

        if success:
            await state.clear()

            success_text = f"""✅ *Платеж успешно обработан!*

🎉 Премиум подписка активирована!
💎 Теперь вам доступны все функции бота:
• Безлимитные переводы
• Голосовые сообщения
• История переводов
• Экспорт в PDF
• ИИ-улучшения

Спасибо за покупку! 🙏"""

            await callback.message.edit_text(
                success_text,
                parse_mode='Markdown',
                reply_markup=get_main_menu_keyboard(True)
            )

            await callback.answer("🎉 Подписка активирована!")
        else:
            await callback.answer("❌ Ошибка активации подписки", show_alert=True)
    else:
        status_text = f"⏳ Статус платежа: {payment_status['status']}\n\nПлатеж еще не завершен."
        await callback.answer(status_text, show_alert=True)

@router.message(F.text == "Проверить платеж", PaymentStates.waiting_for_payment)
async def check_payment_message(message: Message, state: FSMContext):
    """Check payment via message"""
    state_data = await state.get_data()
    payment_id = state_data.get("payment_id")

    if not payment_id:
        await message.answer("❌ Активный платеж не найден")
        return

    # Check payment status
    payment_status = await payment_service.check_payment_status(payment_id)

    if not payment_status:
        await message.answer("❌ Ошибка при проверке статуса платежа")
        return

    if payment_status["paid"]:
        # Payment successful
        subscription_type = state_data.get("subscription_type")
        amount = state_data.get("amount")

        success = await db.activate_subscription(
            user_id=message.from_user.id,
            subscription_type=subscription_type,
            payment_id=payment_id,
            amount=amount
        )

        if success:
            await state.clear()
            await message.answer(
                "✅ Премиум подписка успешно активирована! 🎉",
                reply_markup=get_main_menu_keyboard(True)
            )
        else:
            await message.answer("❌ Ошибка при активации подписки")
    else:
        await message.answer(
            f"⏳ Платеж еще не завершен.\nСтатус: {payment_status['status']}\n\n"
            "Попробуйте проверить позже или обратитесь в поддержку."
        )

# Webhook handler (for production)
async def process_payment_webhook(webhook_data: dict):
    """Process payment webhook from YooKassa"""
    try:
        result = await payment_service.process_webhook(webhook_data)

        if result and result["event"] == "payment_succeeded":
            user_id = result["user_id"]
            subscription_type = result["subscription_type"]
            payment_id = result["payment_id"]
            amount = result["amount"]

            # Activate subscription
            success = await db.activate_subscription(
                user_id=user_id,
                subscription_type=subscription_type,
                payment_id=payment_id,
                amount=amount
            )

            if success:
                logger.info(f"Premium subscription activated for user {user_id}")
                # You could send a notification message here
                return True
            else:
                logger.error(f"Failed to activate subscription for user {user_id}")

        return False

    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return False