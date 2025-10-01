"""User management API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from bot.database import Database
from bot.db_adapter import db_adapter
import aiosqlite

router = APIRouter(prefix="/api/users", tags=["users"])
db = Database()


@router.get("/")
async def get_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    premium_only: bool = False
):
    """Get paginated list of users"""
    try:
        offset = (page - 1) * per_page

        async with db_adapter.get_connection() as conn:
            # Build query
            query = "SELECT * FROM users WHERE 1=1"
            params = []

            if search:
                query += " AND (username LIKE ? OR first_name LIKE ? OR CAST(user_id AS TEXT) LIKE ?)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param])

            if premium_only:
                if db_adapter.is_postgres:
                    query += " AND is_premium = TRUE"
                else:
                    query += " AND is_premium = 1"

            # Count total
            count_query = query.replace("SELECT *", "SELECT COUNT(*)")
            rows = await conn.fetchall(count_query, *params)
            total = rows[0][0] if rows else 0

            # Get paginated results
            query += f" ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([per_page, offset])

            rows = await conn.fetchall(query, *params)
            users = [dict(zip(['user_id', 'username', 'first_name', 'last_name', 'language_code',
                              'interface_language', 'target_language', 'translation_style',
                              'is_premium', 'premium_until', 'free_translations_today',
                              'last_translation_date', 'total_translations', 'created_at', 'updated_at'],
                             row)) for row in rows]

            return {
                "users": users,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_user_details(user_id: int):
    """Get detailed user information"""
    try:
        user = await db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user's translation history
        history = await db.get_user_history(user_id, limit=10)

        # Get subscription info
        async with aiosqlite.connect(db.db_path) as conn:
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute('''
                SELECT * FROM subscriptions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 1
            ''', (user_id,))
            subscription = await cursor.fetchone()

        return {
            "user": user,
            "recent_translations": history,
            "subscription": dict(subscription) if subscription else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/block")
async def block_user(user_id: int):
    """Block/unblock a user"""
    try:
        async with aiosqlite.connect(db.db_path) as conn:
            # Add a 'blocked' field check
            cursor = await conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            user = await cursor.fetchone()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # For now, we'll set premium to 0 as a form of blocking
            # In future, add a dedicated 'blocked' column
            await conn.execute('''
                UPDATE users
                SET is_premium = 0, premium_until = NULL, updated_at = ?
                WHERE user_id = ?
            ''', (datetime.now(), user_id))
            await conn.commit()

            return {"success": True, "message": "User blocked"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/premium")
async def grant_premium(user_id: int, days: int = 30):
    """Grant premium access to user"""
    try:
        from datetime import timedelta

        user = await db.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        expires_at = datetime.now() + timedelta(days=days)

        async with aiosqlite.connect(db.db_path) as conn:
            await conn.execute('''
                UPDATE users
                SET is_premium = 1, premium_until = ?, updated_at = ?
                WHERE user_id = ?
            ''', (expires_at, datetime.now(), user_id))
            await conn.commit()

        return {
            "success": True,
            "message": f"Premium granted for {days} days",
            "expires_at": expires_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
