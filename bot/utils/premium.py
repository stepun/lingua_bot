"""Premium status helper functions"""
from datetime import datetime
from bot.db_adapter import db_adapter


async def check_premium_status(user_id: int) -> tuple[bool, datetime | None]:
    """
    Check if user has active premium subscription

    Returns:
        tuple: (is_premium: bool, expires_at: datetime | None)
    """
    async with db_adapter.get_connection() as conn:
        subscription = await conn.fetchone("""
            SELECT expires_at FROM subscriptions
            WHERE user_id = $1
              AND status = 'active'
              AND expires_at > $2
            ORDER BY expires_at DESC LIMIT 1
        """, user_id, datetime.now())

    if subscription:
        return True, subscription['expires_at']
    return False, None


async def is_premium(user_id: int) -> bool:
    """Check if user has active premium subscription"""
    is_premium_status, _ = await check_premium_status(user_id)
    return is_premium_status
