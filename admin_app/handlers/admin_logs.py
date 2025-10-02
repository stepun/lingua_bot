"""Admin logs handlers for admin panel"""

from aiohttp import web
from admin_app.auth import check_admin_with_permission


async def get_admin_logs_endpoint(request):
    """Get admin action logs"""
    from aiohttp import web as aiohttp_web

    try:
        await check_admin_with_permission(request, 'view_admin_logs')  # Check admin access

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
    except aiohttp_web.HTTPException:
        raise  # Re-raise HTTP exceptions (403, 404, etc.)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)
