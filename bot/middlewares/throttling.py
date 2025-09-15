"""Throttling middleware"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, Message, CallbackQuery, InlineQuery
import time
import logging

logger = logging.getLogger(__name__)

class ThrottlingMiddleware(BaseMiddleware):
    """Middleware for basic throttling"""

    def __init__(self, rate: int = 10, per: int = 60):
        self.rate = rate  # requests per period
        self.per = per    # period in seconds
        self.storage = {}  # In production, use Redis

    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update | Message | CallbackQuery | InlineQuery,
        data: Dict[str, Any]
    ) -> Any:
        user_id = None

        # Get user ID from different event types
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        elif isinstance(event, InlineQuery):
            user_id = event.from_user.id
        elif hasattr(event, 'message') and event.message:
            user_id = event.message.from_user.id
        elif hasattr(event, 'callback_query') and event.callback_query:
            user_id = event.callback_query.from_user.id
        elif hasattr(event, 'inline_query') and event.inline_query:
            user_id = event.inline_query.from_user.id

        if user_id:
            current_time = time.time()
            key = f"throttle:{user_id}"

            # Clean old entries
            self.cleanup_storage(current_time)

            # Check rate limit
            if key in self.storage:
                user_data = self.storage[key]
                window_start = user_data['window_start']
                request_count = user_data['count']

                # If we're in the same window
                if current_time - window_start < self.per:
                    if request_count >= self.rate:
                        # Rate limit exceeded - ignore the update
                        logger.warning(f"Rate limit exceeded for user {user_id}")
                        return
                    else:
                        # Increment counter
                        self.storage[key]['count'] += 1
                else:
                    # New window
                    self.storage[key] = {
                        'window_start': current_time,
                        'count': 1
                    }
            else:
                # First request
                self.storage[key] = {
                    'window_start': current_time,
                    'count': 1
                }

        return await handler(event, data)

    def cleanup_storage(self, current_time: float):
        """Clean up old entries"""
        keys_to_remove = []
        for key, data in self.storage.items():
            if current_time - data['window_start'] > self.per * 2:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.storage[key]