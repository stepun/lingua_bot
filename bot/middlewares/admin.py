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
    """Check if user is admin (legacy - synchronous, only checks ADMIN_IDS)"""
    return user_id in config.ADMIN_IDS


async def check_admin_role(user_id: int) -> bool:
    """Check if user has admin role (async, checks database first)

    Checks admin_roles table first, then falls back to ADMIN_IDS for backward compatibility.
    Returns True if user has any admin role (admin, moderator, analyst).
    """
    from bot.database import db

    # Check database first
    role_data = await db.get_user_role(user_id)
    if role_data:
        return True  # Any role grants access

    # Fallback to legacy ADMIN_IDS
    return user_id in config.ADMIN_IDS