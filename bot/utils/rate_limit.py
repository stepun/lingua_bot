"""Rate limiting decorator"""

import asyncio
from functools import wraps
from typing import Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Store rate limit data in memory (in production, use Redis)
rate_limit_storage: Dict[str, Dict[str, Any]] = {}

def rate_limit(key: str, rate: int, per: int):
    """
    Rate limiting decorator

    Args:
        key: Rate limit key (e.g., 'translation', 'voice')
        rate: Number of allowed requests
        per: Time period in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user_id from message or callback
            user_id = None
            for arg in args:
                if hasattr(arg, 'from_user'):
                    user_id = arg.from_user.id
                    break

            if not user_id:
                # If we can't get user_id, allow the request
                return await func(*args, **kwargs)

            # Create rate limit key
            rl_key = f"{key}:{user_id}"
            current_time = datetime.now()

            # Clean up old entries
            cleanup_old_entries()

            # Check rate limit
            if rl_key in rate_limit_storage:
                data = rate_limit_storage[rl_key]
                window_start = data['window_start']
                request_count = data['count']

                # If we're in the same window
                if current_time - window_start < timedelta(seconds=per):
                    if request_count >= rate:
                        # Rate limit exceeded
                        logger.warning(f"Rate limit exceeded for user {user_id}, key {key}")

                        # Try to send rate limit message
                        try:
                            for arg in args:
                                if hasattr(arg, 'answer'):
                                    await arg.answer(
                                        "⚠️ Слишком много запросов. Попробуйте через минуту.",
                                        show_alert=True
                                    )
                                    break
                                elif hasattr(arg, 'reply'):
                                    await arg.reply("⚠️ Слишком много запросов. Попробуйте через минуту.")
                                    break
                        except Exception as e:
                            logger.error(f"Error sending rate limit message: {e}")

                        return
                    else:
                        # Increment counter
                        rate_limit_storage[rl_key]['count'] += 1
                else:
                    # New window
                    rate_limit_storage[rl_key] = {
                        'window_start': current_time,
                        'count': 1
                    }
            else:
                # First request
                rate_limit_storage[rl_key] = {
                    'window_start': current_time,
                    'count': 1
                }

            # Execute the function
            return await func(*args, **kwargs)

        return wrapper
    return decorator

def cleanup_old_entries():
    """Clean up old rate limit entries"""
    current_time = datetime.now()
    keys_to_remove = []

    for key, data in rate_limit_storage.items():
        if current_time - data['window_start'] > timedelta(hours=1):
            keys_to_remove.append(key)

    for key in keys_to_remove:
        del rate_limit_storage[key]

def get_rate_limit_status(user_id: int, key: str, rate: int, per: int) -> Dict[str, Any]:
    """Get current rate limit status for a user"""
    rl_key = f"{key}:{user_id}"
    current_time = datetime.now()

    if rl_key not in rate_limit_storage:
        return {
            'remaining': rate,
            'reset_at': current_time + timedelta(seconds=per),
            'blocked': False
        }

    data = rate_limit_storage[rl_key]
    window_start = data['window_start']
    request_count = data['count']

    if current_time - window_start >= timedelta(seconds=per):
        # Window expired
        return {
            'remaining': rate,
            'reset_at': current_time + timedelta(seconds=per),
            'blocked': False
        }

    remaining = max(0, rate - request_count)
    reset_at = window_start + timedelta(seconds=per)
    blocked = remaining == 0

    return {
        'remaining': remaining,
        'reset_at': reset_at,
        'blocked': blocked
    }