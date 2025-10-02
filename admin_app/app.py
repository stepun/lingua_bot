"""aiohttp Admin Panel Application"""

from pathlib import Path
from aiohttp import web

# Import handlers
from admin_app.handlers import (
    get_stats,
    get_daily_stats,
    get_language_stats,
    get_performance_stats,
    get_users,
    block_user_endpoint,
    unblock_user_endpoint,
    grant_premium_endpoint,
    send_message_endpoint,
    get_user_history,
    get_translation_logs,
    get_feedback,
    update_feedback_status,
    get_admin_logs_endpoint,
    get_admin_roles_endpoint,
    assign_role_endpoint,
    remove_role_endpoint,
    get_current_user_role_endpoint
)


def setup_admin_routes(aiohttp_app):
    """Setup admin panel routes in aiohttp app"""
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

    # Add routes for serving HTML and static files
    aiohttp_app.router.add_get('/admin', serve_admin_index)
    aiohttp_app.router.add_get('/admin/', serve_admin_index)

    # Static files (CSS, JS) - accessible without admin check for WebApp to load
    aiohttp_app.router.add_get('/static/{filename:.+}', serve_static)
    aiohttp_app.router.add_get('/admin/{filename:.+}', serve_static)

    # API routes - Statistics
    aiohttp_app.router.add_get('/api/stats/', get_stats)
    aiohttp_app.router.add_get('/api/stats/daily', get_daily_stats)
    aiohttp_app.router.add_get('/api/stats/languages', get_language_stats)
    aiohttp_app.router.add_get('/api/stats/performance', get_performance_stats)

    # API routes - Users
    aiohttp_app.router.add_get('/api/users/', get_users)
    aiohttp_app.router.add_get('/api/users/{user_id}/history', get_user_history)
    aiohttp_app.router.add_post('/api/users/{user_id}/block', block_user_endpoint)
    aiohttp_app.router.add_post('/api/users/{user_id}/unblock', unblock_user_endpoint)
    aiohttp_app.router.add_post('/api/users/{user_id}/premium', grant_premium_endpoint)
    aiohttp_app.router.add_post('/api/users/{user_id}/send-message', send_message_endpoint)

    # API routes - Logs
    aiohttp_app.router.add_get('/api/logs/translations', get_translation_logs)

    # API routes - Feedback
    aiohttp_app.router.add_get('/api/feedback', get_feedback)
    aiohttp_app.router.add_post('/api/feedback/{feedback_id}/status', update_feedback_status)

    # API routes - Admin logs
    aiohttp_app.router.add_get('/api/admin-logs', get_admin_logs_endpoint)

    # API routes - Admin roles
    aiohttp_app.router.add_get('/api/admin-roles', get_admin_roles_endpoint)
    aiohttp_app.router.add_post('/api/admin-roles', assign_role_endpoint)
    aiohttp_app.router.add_delete('/api/admin-roles/{user_id}', remove_role_endpoint)
    aiohttp_app.router.add_get('/api/admin-roles/current', get_current_user_role_endpoint)

    return aiohttp_app
