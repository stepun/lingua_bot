"""Statistics API endpoints"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bot.database import Database

router = APIRouter(prefix="/api/stats", tags=["statistics"])
db = Database()


@router.get("/")
async def get_overall_stats():
    """Get overall bot statistics"""
    try:
        total_users = await db.get_user_count()
        premium_users = await db.get_premium_user_count()
        today_stats = await db.get_statistics(datetime.now())

        return {
            "total_users": total_users,
            "premium_users": premium_users,
            "free_users": total_users - premium_users,
            "today": {
                "active_users": today_stats["active_users"],
                "translations": today_stats["total_translations"],
                "voice_translations": today_stats["voice_translations"],
                "revenue": today_stats["revenue"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/daily")
async def get_daily_stats(days: int = 7):
    """Get daily statistics for the last N days"""
    try:
        stats_list = []
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            stats = await db.get_statistics(date)
            stats_list.append(stats)

        return {"data": stats_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_language_stats():
    """Get translation statistics by language"""
    try:
        import aiosqlite
        async with aiosqlite.connect(db.db_path) as conn:
            conn.row_factory = aiosqlite.Row

            # Source languages
            cursor = await conn.execute('''
                SELECT source_language, COUNT(*) as count
                FROM translation_history
                WHERE created_at >= date('now', '-7 days')
                GROUP BY source_language
                ORDER BY count DESC
                LIMIT 10
            ''')
            source_langs = [dict(row) for row in await cursor.fetchall()]

            # Target languages
            cursor = await conn.execute('''
                SELECT target_language, COUNT(*) as count
                FROM translation_history
                WHERE created_at >= date('now', '-7 days')
                GROUP BY target_language
                ORDER BY count DESC
                LIMIT 10
            ''')
            target_langs = [dict(row) for row in await cursor.fetchall()]

            return {
                "source_languages": source_langs,
                "target_languages": target_langs
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
