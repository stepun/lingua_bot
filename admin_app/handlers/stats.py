"""Statistics handlers for admin panel"""

from aiohttp import web
from admin_app.auth import check_admin_with_permission


async def get_stats(request):
    """Get overall statistics"""
    try:
        await check_admin_with_permission(request, 'view_dashboard')  # Check admin access

        from bot.database import db
        from datetime import datetime

        total_users = await db.get_user_count()
        premium_users = await db.get_premium_user_count()
        today_stats = await db.get_statistics(datetime.now().date())

        return web.json_response({
            "total_users": total_users,
            "premium_users": premium_users,
            "active_today": today_stats.get("active_users", 0) if today_stats else 0,
            "translations_today": today_stats.get("total_translations", 0) if today_stats else 0
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def get_daily_stats(request):
    """Get daily statistics for last N days"""
    try:
        await check_admin_with_permission(request, 'view_dashboard')  # Check admin access

        from bot.database import db
        from datetime import datetime, timedelta

        days = int(request.query.get('days', 7))
        stats = []

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).date()
            day_stats = await db.get_statistics(date)
            stats.append({
                "date": date.strftime("%Y-%m-%d"),
                "translations": day_stats.get("total_translations", 0) if day_stats else 0,
                "users": day_stats.get("active_users", 0) if day_stats else 0
            })

        return web.json_response({"stats": list(reversed(stats))})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def get_language_stats(request):
    """Get language usage statistics"""
    try:
        await check_admin_with_permission(request, 'view_dashboard')

        from bot.database import db
        from bot.db_adapter import db_adapter

        async with db_adapter.get_connection() as conn:
            # Source languages
            source_rows = await conn.fetchall(
                """SELECT source_language, COUNT(*) as count
                   FROM translation_history
                   WHERE source_language IS NOT NULL
                   GROUP BY source_language
                   ORDER BY count DESC
                   LIMIT 10"""
            )
            source_langs = [{"lang": row[0] or "auto", "count": row[1]} for row in source_rows]

            # Target languages
            target_rows = await conn.fetchall(
                """SELECT target_language, COUNT(*) as count
                   FROM translation_history
                   WHERE target_language IS NOT NULL
                   GROUP BY target_language
                   ORDER BY count DESC
                   LIMIT 10"""
            )
            target_langs = [{"lang": row[0] or "en", "count": row[1]} for row in target_rows]

        return web.json_response({
            "source_languages": source_langs,
            "target_languages": target_langs
        })
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)


async def get_performance_stats(request):
    """Get performance metrics for translations"""
    try:
        await check_admin_with_permission(request, 'view_dashboard')

        from bot.db_adapter import db_adapter
        from datetime import datetime, timedelta

        async with db_adapter.get_connection() as conn:
            # Average processing time (overall and by type)
            avg_time_row = await conn.fetchone(
                """SELECT
                       AVG(processing_time_ms) as avg_overall,
                       AVG(CASE WHEN is_voice = TRUE THEN processing_time_ms END) as avg_voice,
                       AVG(CASE WHEN is_voice = FALSE THEN processing_time_ms END) as avg_text
                   FROM translation_history
                   WHERE processing_time_ms IS NOT NULL"""
            )

            avg_overall = int(avg_time_row[0]) if avg_time_row and avg_time_row[0] else 0
            avg_voice = int(avg_time_row[1]) if avg_time_row and avg_time_row[1] else 0
            avg_text = int(avg_time_row[2]) if avg_time_row and avg_time_row[2] else 0

            # Success rate
            status_row = await conn.fetchone(
                """SELECT
                       COUNT(*) as total,
                       COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count
                   FROM translation_history"""
            )

            total_count = status_row[0] if status_row else 0
            success_count = status_row[1] if status_row else 0
            success_rate = round((success_count / total_count * 100), 2) if total_count > 0 else 100.0

            # Error breakdown by day (last 7 days)
            seven_days_ago = datetime.now() - timedelta(days=7)
            error_rows = await conn.fetchall(
                """SELECT
                       DATE(created_at) as date,
                       COUNT(*) as error_count
                   FROM translation_history
                   WHERE status != 'success'
                     AND created_at >= ?
                   GROUP BY DATE(created_at)
                   ORDER BY date DESC""",
                seven_days_ago
            )

            errors_by_day = [
                {
                    "date": str(row[0]) if row[0] else None,
                    "count": row[1]
                }
                for row in error_rows
            ]

            # Today's stats
            today = datetime.now().date()
            today_row = await conn.fetchone(
                """SELECT
                       AVG(processing_time_ms) as avg_time,
                       COUNT(*) as total,
                       COUNT(CASE WHEN status = 'success' THEN 1 END) as success_count
                   FROM translation_history
                   WHERE DATE(created_at) = ?
                     AND processing_time_ms IS NOT NULL""",
                today
            )

            today_avg_time = int(today_row[0]) if today_row and today_row[0] else 0
            today_total = today_row[1] if today_row else 0
            today_success = today_row[2] if today_row else 0
            today_success_rate = round((today_success / today_total * 100), 2) if today_total > 0 else 100.0

        return web.json_response({
            "average_processing_time": {
                "overall": avg_overall,
                "voice": avg_voice,
                "text": avg_text
            },
            "success_rate": success_rate,
            "total_translations": total_count,
            "successful_translations": success_count,
            "errors_by_day": errors_by_day,
            "today": {
                "average_time": today_avg_time,
                "total": today_total,
                "success_rate": today_success_rate
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)
