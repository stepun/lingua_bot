"""User management handlers for admin panel"""

from aiohttp import web
from admin_app.auth import check_admin_with_permission


async def get_users(request):
    """Get users list with pagination"""
    from aiohttp import web as aiohttp_web

    try:
        await check_admin_with_permission(request, 'view_users')  # Check admin access

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
    except aiohttp_web.HTTPException:
        raise  # Re-raise HTTP exceptions (403, 404, etc.)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)


async def block_user_endpoint(request):
    """Block user"""
    try:
        admin_id, _, _ = await check_admin_with_permission(request, 'block_user')

        from bot.database import db

        user_id = int(request.match_info['user_id'])
        success = await db.block_user(user_id)

        if success:
            # Log admin action
            await db.log_admin_action(
                admin_user_id=admin_id,
                action='ban_user',
                target_user_id=user_id,
                details={'method': 'admin_panel'}
            )

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
        admin_id, _, _ = await check_admin_with_permission(request, 'block_user')

        from bot.database import db

        user_id = int(request.match_info['user_id'])
        success = await db.unblock_user(user_id)

        if success:
            # Log admin action
            await db.log_admin_action(
                admin_user_id=admin_id,
                action='unban_user',
                target_user_id=user_id,
                details={'method': 'admin_panel'}
            )

            return web.json_response({"success": True, "message": "User unblocked successfully"})
        else:
            return web.json_response({"error": "Failed to unblock user"}, status=500)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)


async def grant_premium_endpoint(request):
    """Grant premium subscription to user for 1 day"""
    try:
        admin_id, _, _ = await check_admin_with_permission(request, 'grant_premium')

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


async def send_message_endpoint(request):
    """Send message to user via bot"""
    try:
        admin_id, _, _ = await check_admin_with_permission(request, 'send_message')

        from bot.database import db
        from aiogram import Bot
        from config import config

        user_id = int(request.match_info['user_id'])
        data = await request.json()
        message_text = data.get('message', '').strip()

        if not message_text:
            return web.json_response({"error": "Message text is required"}, status=400)

        # Get bot instance
        bot = Bot(token=config.BOT_TOKEN)

        try:
            # Send message to user
            await bot.send_message(
                chat_id=user_id,
                text=f"📩 <b>Message from admin:</b>\n\n{message_text}",
                parse_mode="HTML"
            )

            # Log admin action
            await db.log_admin_action(
                admin_user_id=admin_id,
                action='send_message',
                target_user_id=user_id,
                details={
                    'message_preview': message_text[:100],
                    'message_length': len(message_text)
                }
            )

            await bot.session.close()

            return web.json_response({
                "success": True,
                "message": "Message sent successfully"
            })
        except Exception as send_error:
            await bot.session.close()
            error_msg = str(send_error)

            # Check if user hasn't started conversation with bot
            if "bot can't initiate conversation" in error_msg or "Forbidden" in error_msg:
                return web.json_response({
                    "error": f"User hasn't started conversation with bot. Ask user to send /start first. Details: {error_msg}"
                }, status=400)

            return web.json_response({
                "error": f"Failed to send message: {error_msg}"
            }, status=500)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)


async def get_user_history(request):
    """Get translation history for specific user"""
    try:
        admin_id, _, _ = await check_admin_with_permission(request, 'view_history')

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

        # Log admin action
        await db.log_admin_action(
            admin_user_id=admin_id,
            action='view_history',
            target_user_id=user_id,
            details={'limit': limit, 'results': len(history)}
        )

        return web.json_response({
            "user_id": user_id,
            "history": history,
            "total": len(history)
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)
