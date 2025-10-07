"""Payment handlers"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import logging

from bot.database import db
from bot.services.payment import TelegramPaymentService
from bot.keyboards.inline import get_payment_keyboard, get_main_menu_keyboard
from bot.utils.messages import get_text
from config import config

async def safe_callback_answer(callback, text: str = None, show_alert: bool = False):
    """Safe callback answer that doesn't crash on timeout errors"""
    try:
        await callback.answer(text, show_alert=show_alert)
    except Exception as e:
        if "query is too old" in str(e) or "timeout expired" in str(e):
            logger.warning(f"Callback timeout ignored: {e}")
        else:
            logger.error(f"Callback error: {e}")

logger = logging.getLogger(__name__)
router = Router()

class PaymentStates(StatesGroup):
    waiting_for_payment = State()

telegram_payment_service = TelegramPaymentService()

# All old YooKassa handlers removed - now only Telegram Payments below

# Telegram Payments handlers

@router.callback_query(F.data.startswith("buy_telegram_"))
async def handle_telegram_payment(callback: CallbackQuery):
    """Handle Telegram payment"""
    logger.info(f"Telegram payment handler called: callback_data={callback.data}, user_id={callback.from_user.id}")

    subscription_type = callback.data[13:]  # Remove "buy_telegram_" prefix
    logger.info(f"Parsed subscription_type: {subscription_type}")

    if subscription_type not in ["daily", "monthly", "yearly"]:
        await safe_callback_answer(callback,"❌ Неверный тип подписки", show_alert=True)
        return

    user_info = await db.get_user(callback.from_user.id)
    if user_info.get('is_premium'):
        await safe_callback_answer(callback,"✅ У вас уже есть премиум подписка!", show_alert=True)
        return

    # Get subscription details
    amount = await telegram_payment_service.get_subscription_price(subscription_type)
    description = telegram_payment_service.get_subscription_description(subscription_type)

    # Create Telegram invoice
    logger.info(f"Creating Telegram invoice: user_id={callback.from_user.id}, type={subscription_type}, amount={amount}")

    invoice_data = await telegram_payment_service.create_invoice(
        user_id=callback.from_user.id,
        subscription_type=subscription_type,
        amount=amount,
        description=description
    )

    logger.info(f"Invoice creation result: invoice_data={invoice_data}")

    if not invoice_data:
        if not config.PROVIDER_TOKEN:
            error_text = "❌ Платежная система Telegram временно недоступна.\n\n🔧 Администратор не настроил PROVIDER_TOKEN."
        else:
            error_text = "❌ Ошибка при создании счета. Попробуйте позже."

        await callback.message.edit_text(
            error_text,
            reply_markup=get_main_menu_keyboard(False)
        )
        await safe_callback_answer(callback,)
        return

    # Send invoice
    try:
        await callback.bot.send_invoice(
            chat_id=callback.from_user.id,
            **invoice_data
        )
        await safe_callback_answer(callback,"💳 Счет отправлен!")

    except Exception as e:
        logger.error(f"Failed to send invoice: {e}")
        await safe_callback_answer(callback,"❌ Ошибка при отправке счета", show_alert=True)

@router.message(F.successful_payment)
async def handle_successful_payment(message: Message):
    """Handle successful Telegram payment"""
    try:
        payment_mode = "TEST" if config.PAYMENT_TEST else "PRODUCTION"
        logger.info(f"Successful payment received from user {message.from_user.id} in {payment_mode} mode")

        payment_info = message.successful_payment
        logger.info(f"Payment info: charge_id={payment_info.telegram_payment_charge_id}")
        logger.info(f"Invoice payload: {payment_info.invoice_payload}")

        # Parse payload: user_id:subscription_type:amount
        payload_parts = payment_info.invoice_payload.split(':')
        if len(payload_parts) >= 3:
            user_id = int(payload_parts[0])
            subscription_type = payload_parts[1]
            amount = float(payload_parts[2])

            # Activate subscription (same logic for test and production)
            success = await db.activate_subscription(
                user_id=user_id,
                subscription_type=subscription_type,
                payment_id=payment_info.telegram_payment_charge_id,
                amount=amount
            )

            if success:
                # Log different messages for test vs production, but same business logic
                if config.PAYMENT_TEST:
                    logger.info(f"TEST payment processed successfully for user {user_id}")
                else:
                    logger.info(f"PRODUCTION payment processed successfully for user {user_id}")

                success_text = f"""✅ <b>Платеж успешно обработан!</b>

🎉 Премиум подписка активирована!
💎 Теперь вам доступны все функции бота:
• Безлимитные переводы
• Голосовые сообщения
• История переводов
• Экспорт в PDF
• ИИ-улучшения

Спасибо за покупку! 🙏"""

                await message.answer(
                    success_text,
                    parse_mode='HTML',
                    reply_markup=get_main_menu_keyboard(True)
                )
            else:
                await message.answer("❌ Ошибка при активации подписки. Обратитесь в поддержку.")
        else:
            logger.error(f"Invalid payload format: {payment_info.invoice_payload}")
            await message.answer("❌ Ошибка в данных платежа. Обратитесь в поддержку.")

    except Exception as e:
        logger.error(f"Error processing successful payment: {e}")
        await message.answer("❌ Ошибка при обработке платежа. Обратитесь в поддержку.")

@router.pre_checkout_query()
async def handle_pre_checkout(pre_checkout_query):
    """Handle pre-checkout query"""
    logger.info(f"Pre-checkout query received: id={pre_checkout_query.id}, user_id={pre_checkout_query.from_user.id}")
    logger.info(f"Invoice payload: {pre_checkout_query.invoice_payload}")

    # Validate payment here if needed
    # Both test and production payments go through same validation

    try:
        await pre_checkout_query.answer(ok=True)
        logger.info("Pre-checkout query approved")
    except Exception as e:
        if "query is too old" in str(e) or "timeout expired" in str(e):
            logger.warning(f"Pre-checkout timeout ignored: {e}")
        else:
            logger.error(f"Pre-checkout error: {e}")