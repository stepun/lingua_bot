"""Payment processing service"""

import uuid
import json
from typing import Optional, Dict, Any
from yookassa import Configuration, Payment
from config import config
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        if config.YOOKASSA_SHOP_ID and config.YOOKASSA_SECRET_KEY:
            Configuration.account_id = config.YOOKASSA_SHOP_ID
            Configuration.secret_key = config.YOOKASSA_SECRET_KEY

    async def create_payment(self, user_id: int, subscription_type: str, amount: float,
                           description: str = None) -> Optional[Dict[str, Any]]:
        """Create a payment"""
        if not config.YOOKASSA_SHOP_ID or not config.YOOKASSA_SECRET_KEY:
            logger.error("YooKassa credentials not configured")
            return None

        # Check if credentials are just placeholders
        if (config.YOOKASSA_SHOP_ID == "your_shop_id" or
            config.YOOKASSA_SECRET_KEY == "your_secret_key"):
            logger.error("YooKassa credentials are not properly configured - using placeholder values")
            return None

        try:
            payment_id = str(uuid.uuid4())

            payment_data = {
                "amount": {
                    "value": str(amount),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": "https://t.me/your_bot_username"
                },
                "capture": True,
                "description": description or f"Подписка {subscription_type}",
                "metadata": {
                    "user_id": str(user_id),
                    "subscription_type": subscription_type,
                    "bot_payment": "true"
                }
            }

            payment = Payment.create(payment_data, payment_id)

            return {
                "payment_id": payment.id,
                "status": payment.status,
                "confirmation_url": payment.confirmation.confirmation_url,
                "amount": float(payment.amount.value),
                "currency": payment.amount.currency,
                "description": payment.description
            }

        except Exception as e:
            logger.error(f"Payment creation error: {e}")
            return None

    async def check_payment_status(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Check payment status"""
        if not config.YOOKASSA_SHOP_ID or not config.YOOKASSA_SECRET_KEY:
            return None

        try:
            payment = Payment.find_one(payment_id)

            return {
                "payment_id": payment.id,
                "status": payment.status,
                "paid": payment.paid,
                "amount": float(payment.amount.value) if payment.amount else 0,
                "currency": payment.amount.currency if payment.amount else "RUB",
                "metadata": payment.metadata or {}
            }

        except Exception as e:
            logger.error(f"Payment status check error: {e}")
            return None

    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process YooKassa webhook"""
        try:
            event_type = webhook_data.get("event")
            payment_data = webhook_data.get("object", {})

            if event_type == "payment.succeeded":
                payment_id = payment_data.get("id")
                metadata = payment_data.get("metadata", {})
                user_id = metadata.get("user_id")
                subscription_type = metadata.get("subscription_type")

                if user_id and subscription_type:
                    return {
                        "event": "payment_succeeded",
                        "payment_id": payment_id,
                        "user_id": int(user_id),
                        "subscription_type": subscription_type,
                        "amount": float(payment_data.get("amount", {}).get("value", 0))
                    }

            elif event_type == "payment.canceled":
                payment_id = payment_data.get("id")
                metadata = payment_data.get("metadata", {})
                user_id = metadata.get("user_id")

                if user_id:
                    return {
                        "event": "payment_canceled",
                        "payment_id": payment_id,
                        "user_id": int(user_id)
                    }

            return None

        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return None

    def get_subscription_price(self, subscription_type: str) -> float:
        """Get subscription price"""
        if subscription_type == "monthly":
            return config.MONTHLY_PRICE
        elif subscription_type == "yearly":
            return config.YEARLY_PRICE
        return 0.0

    def get_subscription_description(self, subscription_type: str) -> str:
        """Get subscription description"""
        descriptions = {
            "monthly": "LinguaBot Premium - Месячная подписка",
            "yearly": "LinguaBot Premium - Годовая подписка"
        }
        return descriptions.get(subscription_type, "LinguaBot Premium")

# Alternative payment methods (for future implementation)

class TelegramPaymentService:
    """Telegram native payments (Stars)"""

    async def create_invoice(self, user_id: int, subscription_type: str,
                           amount: int, description: str = None):
        """Create Telegram invoice"""
        # Implementation for Telegram Stars payments
        pass

class TinkoffPaymentService:
    """Tinkoff payment service"""

    def __init__(self):
        self.terminal_key = None  # Configure from environment
        self.secret_key = None

    async def create_payment(self, user_id: int, subscription_type: str,
                           amount: float, description: str = None):
        """Create Tinkoff payment"""
        # Implementation for Tinkoff payments
        pass

class SberPaymentService:
    """Sberbank payment service"""

    def __init__(self):
        self.username = None  # Configure from environment
        self.password = None

    async def create_payment(self, user_id: int, subscription_type: str,
                           amount: float, description: str = None):
        """Create Sberbank payment"""
        # Implementation for Sberbank payments
        pass