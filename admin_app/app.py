"""aiohttp Admin Panel Application"""

from pathlib import Path
import json


def setup_admin_routes(aiohttp_app):
    """Setup admin panel routes in aiohttp app"""
    from aiohttp import web

    # Get static directory
    static_dir = Path(__file__).parent / "static"

    # Serve index.html at root
    async def serve_admin_index(request):
        # For HTML page, we can't check auth yet (initData is only available in JS)
        # So we just serve the page and let JS handle authentication
        index_file = static_dir / "index.html"
        if index_file.exists():
            return web.FileResponse(index_file)
        return web.Response(text="Admin panel not found", status=404)

    # Serve static files
    async def serve_static(request):
        filename = request.match_info.get('filename', '')
        file_path = static_dir / filename
        if file_path.exists() and file_path.is_file():
            return web.FileResponse(file_path)
        return web.Response(text=f"File not found: {filename}", status=404)

    # Helper: Check admin access
    def check_admin(request):
        """Check if request is from admin using Telegram WebApp authentication"""
        from config import config
        from admin_app.auth import validate_telegram_webapp_data, is_admin
        import json

        # Get Telegram init data from header
        init_data = request.headers.get('X-Telegram-Init-Data')

        if not init_data:
            raise web.HTTPForbidden(text="Access denied: Telegram authentication required")

        # Validate Telegram data
        validated_data = validate_telegram_webapp_data(init_data)

        if not validated_data:
            raise web.HTTPForbidden(text="Access denied: Invalid Telegram data")

        # Extract user data
        try:
            user_json = validated_data.get('user', '{}')
            user_data = json.loads(user_json)
            user_id = user_data.get('id')
        except (json.JSONDecodeError, AttributeError):
            raise web.HTTPForbidden(text="Access denied: Invalid user data")

        if not user_id:
            raise web.HTTPForbidden(text="Access denied: user_id not found")

        if not is_admin(user_id):
            raise web.HTTPForbidden(text=f"Access denied: user {user_id} is not admin")

        return user_id

    # API endpoints for admin panel
    async def get_stats(request):
        """Get overall statistics"""
        try:
            check_admin(request)  # Check admin access

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
            check_admin(request)  # Check admin access

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

    async def get_users(request):
        """Get users list with pagination"""
        try:
            check_admin(request)  # Check admin access

            from bot.database import db
            from bot.db_adapter import db_adapter

            page = int(request.query.get('page', 1))
            per_page = int(request.query.get('per_page', 10))
            search = request.query.get('search', '').strip()
            premium_only = request.query.get('premium_only', '').lower() == 'true'

            # Build WHERE clause
            where_conditions = []
            params = []

            if search:
                where_conditions.append(
                    "(u.username LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ? OR CAST(u.user_id AS TEXT) LIKE ?)"
                )
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param, search_param])

            if premium_only:
                where_conditions.append(
                    """EXISTS (
                        SELECT 1 FROM subscriptions s
                        WHERE s.user_id = u.user_id
                          AND s.status = 'active'
                          AND s.expires_at > CURRENT_TIMESTAMP
                    )"""
                )

            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

            # Get users directly from database with SQL
            async with db_adapter.get_connection() as conn:
                query = f"""SELECT u.user_id, u.username, u.first_name, u.last_name,
                              u.total_translations, u.created_at,
                              CASE
                                WHEN EXISTS (
                                  SELECT 1 FROM subscriptions s
                                  WHERE s.user_id = u.user_id
                                    AND s.status = 'active'
                                    AND s.expires_at > CURRENT_TIMESTAMP
                                ) THEN 1 ELSE 0
                              END as is_premium,
                              u.is_blocked
                       FROM users u
                       {where_clause}
                       ORDER BY u.created_at DESC
                       LIMIT ? OFFSET ?"""

                params.extend([per_page, (page-1)*per_page])
                rows = await conn.fetchall(query, *params)

                users = []
                for row in rows:
                    users.append({
                        "id": row[0],
                        "username": row[1] or "N/A",
                        "name": f"{row[2] or ''} {row[3] or ''}".strip() or "N/A",
                        "is_premium": bool(row[6]),
                        "total_translations": row[4] or 0,
                        "created_at": str(row[5]) if row[5] else None,
                        "is_blocked": bool(row[7]) if row[7] is not None else False
                    })

                # Get total count with same filters
                count_query = f"SELECT COUNT(*) FROM users u {where_clause}"
                total_row = await conn.fetchone(count_query, *params[:-2])  # Exclude LIMIT/OFFSET params
                total = total_row[0] if total_row else 0

            return web.json_response({
                "users": users,
                "total": total,
                "page": page,
                "per_page": per_page
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)

    # Add routes
    aiohttp_app.router.add_get('/admin', serve_admin_index)
    aiohttp_app.router.add_get('/admin/', serve_admin_index)

    # Static files (CSS, JS) - accessible without admin check for WebApp to load
    aiohttp_app.router.add_get('/static/{filename:.+}', serve_static)
    aiohttp_app.router.add_get('/admin/{filename:.+}', serve_static)

    # Logs endpoints
    async def get_translation_logs(request):
        """Get translation logs"""
        try:
            check_admin(request)

            from bot.database import db
            from bot.db_adapter import db_adapter

            page = int(request.query.get('page', 1))
            per_page = int(request.query.get('per_page', 20))
            filter_type = request.query.get('filter', 'all')
            search = request.query.get('search', '').strip()

            # Build WHERE clause based on filter and search
            where_conditions = []
            params = []

            if filter_type == "voice":
                where_conditions.append("is_voice = TRUE")
            elif filter_type == "text":
                where_conditions.append("is_voice = FALSE")

            if search:
                # Search in username, source_text, and translation
                where_conditions.append("(u.username ILIKE ? OR th.source_text ILIKE ? OR th.basic_translation ILIKE ?)")
                search_pattern = f"%{search}%"
                params.extend([search_pattern, search_pattern, search_pattern])

            where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""

            # Add pagination params
            params.extend([per_page, (page-1)*per_page])

            async with db_adapter.get_connection() as conn:
                rows = await conn.fetchall(
                    f"""SELECT th.id, th.user_id, u.username, th.source_language, th.target_language,
                               th.source_text, th.basic_translation, th.created_at, th.is_voice
                       FROM translation_history th
                       LEFT JOIN users u ON th.user_id = u.user_id
                       {where_clause}
                       ORDER BY th.created_at DESC
                       LIMIT ? OFFSET ?""",
                    *params
                )

                logs = []
                for row in rows:
                    logs.append({
                        "id": row[0],
                        "user_id": row[1],
                        "username": row[2] or "Unknown",
                        "source_lang": row[3] or "auto",
                        "target_lang": row[4] or "en",
                        "source_text": row[5][:100] if row[5] else "",  # First 100 chars
                        "translation": row[6][:100] if row[6] else "",
                        "created_at": str(row[7]) if row[7] else None,
                        "is_voice": bool(row[8])
                    })

                # Get total count (reuse where_clause and search params)
                count_params = params[:-2]  # Exclude LIMIT and OFFSET params
                count_query = f"""SELECT COUNT(*) FROM translation_history th
                                  LEFT JOIN users u ON th.user_id = u.user_id
                                  {where_clause}"""
                total_row = await conn.fetchone(count_query, *count_params)
                total = total_row[0] if total_row else 0

            return web.json_response({
                "logs": logs,
                "total": total,
                "page": page,
                "per_page": per_page
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)

    async def get_language_stats(request):
        """Get language usage statistics"""
        try:
            check_admin(request)

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
            check_admin(request)

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

    async def block_user_endpoint(request):
        """Block user"""
        try:
            check_admin(request)

            from bot.database import db

            user_id = int(request.match_info['user_id'])
            success = await db.block_user(user_id)

            if success:
                return web.json_response({"success": True, "message": "User blocked successfully"})
            else:
                return web.json_response({"error": "Failed to block user"}, status=500)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)

    async def unblock_user_endpoint(request):
        """Unblock user"""
        try:
            check_admin(request)

            from bot.database import db

            user_id = int(request.match_info['user_id'])
            success = await db.unblock_user(user_id)

            if success:
                return web.json_response({"success": True, "message": "User unblocked successfully"})
            else:
                return web.json_response({"error": "Failed to unblock user"}, status=500)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)

    async def get_user_history(request):
        """Get translation history for specific user"""
        try:
            check_admin(request)

            from bot.database import db
            from bot.db_adapter import db_adapter

            user_id = int(request.match_info['user_id'])
            limit = int(request.query.get('limit', 10))

            async with db_adapter.get_connection() as conn:
                rows = await conn.fetchall(
                    """SELECT th.id, th.source_language, th.target_language,
                              th.source_text, th.basic_translation, th.created_at, th.is_voice
                       FROM translation_history th
                       WHERE th.user_id = ?
                       ORDER BY th.created_at DESC
                       LIMIT ?""",
                    user_id, limit
                )

                history = []
                for row in rows:
                    history.append({
                        "id": row[0],
                        "source_lang": row[1] or "auto",
                        "target_lang": row[2] or "en",
                        "source_text": row[3][:100] if row[3] else "",  # First 100 chars
                        "translation": row[4][:100] if row[4] else "",
                        "created_at": str(row[5]) if row[5] else None,
                        "is_voice": bool(row[6])
                    })

            return web.json_response({
                "user_id": user_id,
                "history": history,
                "total": len(history)
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)

    # Feedback endpoints
    async def get_feedback(request):
        """Get all feedback with optional status filter"""
        try:
            from bot.database import db

            status = request.query.get('status', None)
            limit = int(request.query.get('limit', 100))

            feedback_list = await db.get_all_feedback(status=status, limit=limit)

            return web.json_response({
                "feedback": feedback_list,
                "total": len(feedback_list)
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)

    async def update_feedback_status(request):
        """Update feedback status"""
        try:
            from bot.database import db

            feedback_id = int(request.match_info['feedback_id'])
            data = await request.json()
            new_status = data.get('status')

            if new_status not in ['new', 'reviewed', 'resolved']:
                return web.json_response({"error": "Invalid status"}, status=400)

            success = await db.update_feedback_status(feedback_id, new_status)

            if success:
                return web.json_response({"success": True, "message": "Status updated"})
            else:
                return web.json_response({"error": "Failed to update status"}, status=500)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)

    async def get_admin_logs_endpoint(request):
        """Get admin action logs"""
        try:
            check_admin(request)  # Check admin access

            from bot.database import db

            # Get query parameters
            admin_user_id = request.query.get('admin_user_id')
            action = request.query.get('action')
            limit = int(request.query.get('limit', 100))

            # Convert admin_user_id to int if provided
            if admin_user_id:
                admin_user_id = int(admin_user_id)

            # Get logs from database
            logs = await db.get_admin_logs(
                admin_user_id=admin_user_id,
                action=action,
                limit=limit
            )

            return web.json_response({
                "logs": logs,
                "total": len(logs)
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)

    async def grant_premium_endpoint(request):
        """Grant premium subscription to user for 1 day"""
        try:
            admin_id = check_admin(request)

            from bot.database import db

            user_id = int(request.match_info['user_id'])

            # Activate 1-day subscription
            success = await db.activate_subscription(
                user_id=user_id,
                subscription_type='daily',
                payment_id='admin_grant',
                amount=0.0
            )

            if success:
                # Log admin action
                await db.log_admin_action(
                    admin_user_id=admin_id,
                    action='grant_premium',
                    target_user_id=user_id,
                    details={'duration': '1 day', 'method': 'admin_panel'}
                )

                return web.json_response({
                    "success": True,
                    "message": "Premium granted for 1 day"
                })
            else:
                return web.json_response({"error": "Failed to grant premium"}, status=500)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({"error": str(e)}, status=500)

    # API routes
    aiohttp_app.router.add_get('/api/stats/', get_stats)
    aiohttp_app.router.add_get('/api/stats/daily', get_daily_stats)
    aiohttp_app.router.add_get('/api/stats/languages', get_language_stats)
    aiohttp_app.router.add_get('/api/stats/performance', get_performance_stats)
    aiohttp_app.router.add_get('/api/users/', get_users)
    aiohttp_app.router.add_get('/api/users/{user_id}/history', get_user_history)
    aiohttp_app.router.add_post('/api/users/{user_id}/block', block_user_endpoint)
    aiohttp_app.router.add_post('/api/users/{user_id}/unblock', unblock_user_endpoint)
    aiohttp_app.router.add_post('/api/users/{user_id}/premium', grant_premium_endpoint)
    aiohttp_app.router.add_get('/api/logs/translations', get_translation_logs)
    aiohttp_app.router.add_get('/api/feedback', get_feedback)
    aiohttp_app.router.add_post('/api/feedback/{feedback_id}/status', update_feedback_status)
    aiohttp_app.router.add_get('/api/admin-logs', get_admin_logs_endpoint)

    return aiohttp_app
