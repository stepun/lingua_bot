"""Feedback handlers for admin panel"""

from aiohttp import web
from admin_app.auth import check_admin_with_permission


async def get_feedback(request):
    """Get all feedback with optional status filter"""
    from aiohttp import web as aiohttp_web

    try:
        await check_admin_with_permission(request, 'view_feedback')

        from bot.database import db

        status = request.query.get('status', None)
        limit = int(request.query.get('limit', 100))

        feedback_list = await db.get_all_feedback(status=status, limit=limit)

        return web.json_response({
            "feedback": feedback_list,
            "total": len(feedback_list)
        })
    except aiohttp_web.HTTPException:
        raise  # Re-raise HTTP exceptions (403, 404, etc.)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)


async def update_feedback_status(request):
    """Update feedback status"""
    try:
        admin_id, _, _ = await check_admin_with_permission(request, 'update_feedback')

        from bot.database import db

        feedback_id = int(request.match_info['feedback_id'])
        data = await request.json()
        new_status = data.get('status')

        if new_status not in ['new', 'reviewed', 'resolved']:
            return web.json_response({"error": "Invalid status"}, status=400)

        success = await db.update_feedback_status(feedback_id, new_status)

        if success:
            # Log admin action
            await db.log_admin_action(
                admin_user_id=admin_id,
                action='update_feedback',
                target_user_id=None,
                details={
                    'feedback_id': feedback_id,
                    'new_status': new_status
                }
            )

            return web.json_response({"success": True, "message": "Status updated"})
        else:
            return web.json_response({"error": "Failed to update status"}, status=500)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)
