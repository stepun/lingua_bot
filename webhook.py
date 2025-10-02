#!/usr/bin/env python3
"""
Payment webhook handler for YooKassa payments
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

from aiohttp import web, ClientSession
from aiohttp.web import Request, Response

from config import config
from bot.database import db
from bot.services.payment import PaymentService

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self):
        self.payment_service = PaymentService()

    async def handle_yookassa_webhook(self, request: Request) -> Response:
        """Handle YooKassa webhook notifications"""
        try:
            # Verify webhook secret if configured
            if config.PAYMENT_WEBHOOK_SECRET:
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer ') or auth_header[7:] != config.PAYMENT_WEBHOOK_SECRET:
                    logger.warning("Invalid webhook authorization")
                    return web.Response(status=401, text="Unauthorized")

            # Parse webhook data
            webhook_data = await request.json()
            logger.info(f"Received webhook: {webhook_data}")

            # Process webhook
            result = await self.payment_service.process_webhook(webhook_data)

            if result:
                if result['event'] == 'payment_succeeded':
                    await self._handle_successful_payment(result)
                elif result['event'] == 'payment_canceled':
                    await self._handle_canceled_payment(result)

            return web.Response(status=200, text="OK")

        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook request")
            return web.Response(status=400, text="Invalid JSON")
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return web.Response(status=500, text="Internal Server Error")

    async def _handle_successful_payment(self, payment_data: Dict[str, Any]):
        """Handle successful payment"""
        user_id = payment_data['user_id']
        subscription_type = payment_data['subscription_type']
        amount = payment_data['amount']

        logger.info(f"Processing successful payment for user {user_id}: {subscription_type} subscription, {amount}₽")

        # Calculate subscription end date
        if subscription_type == "monthly":
            days = 30
        elif subscription_type == "yearly":
            days = 365
        else:
            days = 30

        subscription_end = datetime.now().timestamp() + (days * 24 * 60 * 60)

        # Update user subscription in database
        await db.update_user_subscription(
            user_id=user_id,
            is_premium=True,
            subscription_type=subscription_type,
            subscription_end=subscription_end
        )

        # Send notification to user via bot
        await self._send_payment_notification(user_id, subscription_type, True)

        logger.info(f"Successfully activated {subscription_type} subscription for user {user_id}")

    async def _handle_canceled_payment(self, payment_data: Dict[str, Any]):
        """Handle canceled payment"""
        user_id = payment_data['user_id']
        logger.info(f"Payment canceled for user {user_id}")

        # Send notification to user
        await self._send_payment_notification(user_id, None, False)

    async def _send_payment_notification(self, user_id: int, subscription_type: str, success: bool):
        """Send payment notification to user via bot"""
        try:
            from aiogram import Bot
            from aiogram.exceptions import TelegramForbiddenError, TelegramNotFound

            bot = Bot(token=config.BOT_TOKEN)

            if success:
                if subscription_type == "monthly":
                    message = (
                        "🎉 Поздравляем! Месячная премиум подписка активирована!\n\n"
                        "✨ Теперь вам доступны все функции:\n"
                        "• Безлимитные переводы\n"
                        "• Озвучивание переводов\n"
                        "• История переводов\n"
                        "• Экспорт в PDF/TXT\n"
                        "• Альтернативные переводы\n"
                        "• Грамматические объяснения\n\n"
                        "Спасибо за выбор PolyglotAI44! 🚀"
                    )
                else:
                    message = (
                        "🎉 Поздравляем! Годовая премиум подписка активирована!\n\n"
                        "✨ Теперь вам доступны все функции:\n"
                        "• Безлимитные переводы\n"
                        "• Озвучивание переводов\n"
                        "• История переводов\n"
                        "• Экспорт в PDF/TXT\n"
                        "• Альтернативные переводы\n"
                        "• Грамматические объяснения\n\n"
                        "Спасибо за выбор PolyglotAI44! 🚀\n"
                        "💰 Вы сэкономили 20% с годовой подпиской!"
                    )
            else:
                message = (
                    "❌ Платёж был отменён.\n\n"
                    "Если у вас возникли проблемы с оплатой, "
                    "попробуйте снова или обратитесь в поддержку."
                )

            await bot.send_message(user_id, message)
            await bot.session.close()

        except (TelegramForbiddenError, TelegramNotFound):
            logger.warning(f"Cannot send notification to user {user_id} - bot blocked or user not found")
        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {e}")

def create_webhook_app() -> web.Application:
    """Create webhook application"""
    app = web.Application()
    handler = WebhookHandler()

    # Add webhook route
    app.router.add_post('/webhook/yookassa', handler.handle_yookassa_webhook)

    # Health check endpoint
    async def health_check(request: Request) -> Response:
        return web.Response(text="OK")

    app.router.add_get('/health', health_check)

    return app

async def run_webhook_server():
    """Run webhook server"""
    app = create_webhook_app()

    runner = web.AppRunner(app)
    await runner.setup()

    host = config.WEBAPP_HOST
    port = config.WEBAPP_PORT

    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"Webhook server started on {host}:{port}")
    logger.info(f"Webhook URL: http://{host}:{port}/webhook/yookassa")

    # Keep server running
    try:
        await asyncio.Future()
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    try:
        asyncio.run(run_webhook_server())
    except KeyboardInterrupt:
        logger.info("Webhook server stopped by user")
    except Exception as e:
        logger.error(f"Webhook server error: {e}")
