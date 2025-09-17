"""Admin middleware"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery
from config import config
import logging

logger = logging.getLogger(__name__)

class AdminMiddleware(BaseMiddleware):
    """Middleware for admin access control"""

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update | Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None

        # Get user ID from different event types
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        elif hasattr(event, 'message') and event.message:
            user_id = event.message.from_user.id
        elif hasattr(event, 'callback_query') and event.callback_query:
            user_id = event.callback_query.from_user.id

        # Add admin status to data
        data['is_admin'] = user_id in config.ADMIN_IDS

        if data['is_admin']:
            logger.info(f"Admin access granted for user {user_id}")

        return await handler(event, data)

def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in config.ADMIN_IDS