"""User middleware for automatic user registration"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, User
import logging

from bot.database import db

logger = logging.getLogger(__name__)

class UserMiddleware(BaseMiddleware):
    """Middleware to automatically register users in database"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        user: User = data.get("event_from_user")

        if user:
            try:
                # Add user to database if not exists
                await db.add_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    language_code=user.language_code or 'ru'
                )
            except Exception as e:
                logger.error(f"User middleware error: {e}")

        return await handler(event, data)