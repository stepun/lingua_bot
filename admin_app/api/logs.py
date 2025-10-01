"""Logs and translation history API endpoints"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from bot.database import Database
import aiosqlite

router = APIRouter(prefix="/api/logs", tags=["logs"])
db = Database()


@router.get("/translations")
async def get_translation_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    user_id: Optional[int] = None,
    source_lang: Optional[str] = None,
    target_lang: Optional[str] = None,
    is_voice: Optional[bool] = None
):
    """Get paginated translation history logs"""
    try:
        offset = (page - 1) * per_page

        async with aiosqlite.connect(db.db_path) as conn:
            conn.row_factory = aiosqlite.Row

            # Build query
            query = '''
                SELECT
                    t.id,
                    t.user_id,
                    u.username,
                    u.first_name,
                    t.source_text,
                    t.source_language,
                    t.translated_text,
                    t.target_language,
                    t.translation_style,
                    t.is_voice,
                    t.created_at
                FROM translation_history t
                LEFT JOIN users u ON t.user_id = u.user_id
                WHERE 1=1
            '''
            params = []

            if user_id:
                query += " AND t.user_id = ?"
                params.append(user_id)

            if source_lang:
                query += " AND t.source_language = ?"
                params.append(source_lang)

            if target_lang:
                query += " AND t.target_language = ?"
                params.append(target_lang)

            if is_voice is not None:
                query += " AND t.is_voice = ?"
                params.append(1 if is_voice else 0)

            # Count total
            count_query = query.replace(
                "SELECT t.id, t.user_id, u.username, u.first_name, t.source_text, t.source_language, t.translated_text, t.target_language, t.translation_style, t.is_voice, t.created_at",
                "SELECT COUNT(*)"
            )
            cursor = await conn.execute(count_query, params)
            total = (await cursor.fetchone())[0]

            # Get paginated results
            query += " ORDER BY t.created_at DESC LIMIT ? OFFSET ?"
            params.extend([per_page, offset])

            cursor = await conn.execute(query, params)
            logs = [dict(row) for row in await cursor.fetchall()]

            return {
                "logs": logs,
                "total": total,
                "page": page,
                "per_page": per_page,
                "total_pages": (total + per_page - 1) // per_page
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system")
async def get_system_logs(lines: int = Query(100, ge=1, le=1000)):
    """Get system logs from log files"""
    try:
        import os
        from pathlib import Path

        log_file = Path("logs/bot.log")

        if not log_file.exists():
            return {"logs": [], "message": "Log file not found"}

        # Read last N lines
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            last_lines = all_lines[-lines:]

        return {
            "logs": [line.strip() for line in last_lines],
            "total_lines": len(last_lines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/errors")
async def get_error_logs(lines: int = Query(50, ge=1, le=500)):
    """Get error logs from log files"""
    try:
        import os
        from pathlib import Path

        log_file = Path("logs/bot.log")

        if not log_file.exists():
            return {"errors": [], "message": "Log file not found"}

        # Read and filter error lines
        error_lines = []
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'ERROR' in line or 'Exception' in line or 'Traceback' in line:
                    error_lines.append(line.strip())

        return {
            "errors": error_lines[-lines:],
            "total_errors": len(error_lines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
