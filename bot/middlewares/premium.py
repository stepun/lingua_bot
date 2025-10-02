"""Premium status middleware"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from datetime import datetime
from bot.db_adapter import db_adapter


class PremiumMiddleware(BaseMiddleware):
    """Middleware to add premium status to user data"""

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Get user ID from event
        user_id = event.from_user.id if event.from_user else None

        if user_id:
            # Check active subscription
            async with db_adapter.get_connection() as conn:
                subscription = await conn.fetchone("""
                    SELECT expires_at FROM subscriptions
                    WHERE user_id = ?
                      AND status = 'active'
                      AND expires_at > ?
                    ORDER BY expires_at DESC LIMIT 1
                """, user_id, datetime.now())

            # Add premium status to data
            data['is_premium'] = subscription is not None
            data['premium_until'] = subscription['expires_at'] if subscription else None

        return await handler(event, data)
