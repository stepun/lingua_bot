"""Payment processing service"""

import uuid
import json
from typing import Optional, Dict, Any
from config import config
import logging

logger = logging.getLogger(__name__)

class TelegramPaymentService:
    """Telegram native payment service"""

    def __init__(self):
        pass

    def get_subscription_price(self, subscription_type: str) -> float:
        """Get subscription price"""
        if subscription_type == "monthly":
            return config.MONTHLY_PRICE
        elif subscription_type == "yearly":
            return config.YEARLY_PRICE
        return 0.0

    def get_subscription_description(self, subscription_type: str) -> str:
        """Get subscription description"""
        if subscription_type == "monthly":
            return "Премиум подписка на 1 месяц"
        elif subscription_type == "yearly":
            return "Премиум подписка на 1 год"
        return "Премиум подписка"

    async def create_invoice(self, user_id: int, subscription_type: str, amount: float, description: str = None):
        """Create Telegram invoice"""
        if not config.PROVIDER_TOKEN:
            logger.error("PROVIDER_TOKEN not configured")
            return None

        try:
            from aiogram.types import LabeledPrice

            price_kopecks = int(amount * 100)

            payment_data = {
                "title": f"Premium подписка - {subscription_type}",
                "description": description or f"LinguaBot Premium {subscription_type} подписка",
                "provider_token": config.PROVIDER_TOKEN,
                "currency": "RUB",
                "prices": [LabeledPrice(label=f"Подписка {subscription_type}", amount=price_kopecks)],
                "payload": f"{user_id}:{subscription_type}:{amount}"
            }

            # Store LabeledPrice class for use in handlers
            self.LabeledPrice = LabeledPrice

            return payment_data

        except Exception as e:
            logger.error(f"Error creating Telegram invoice: {e}")
            return None

