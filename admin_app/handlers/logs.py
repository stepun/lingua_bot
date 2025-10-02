"""Translation logs handlers for admin panel"""

from aiohttp import web
from admin_app.auth import check_admin_with_permission


async def get_translation_logs(request):
    """Get translation logs"""
    from aiohttp import web as aiohttp_web

    try:
        await check_admin_with_permission(request, 'view_logs')

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
    except aiohttp_web.HTTPException:
        raise  # Re-raise HTTP exceptions (403, 404, etc.)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)
