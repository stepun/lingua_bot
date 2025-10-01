"""FastAPI Admin Panel Application"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json

from admin_app.auth import validate_telegram_webapp_data, is_admin
from admin_app.api import stats, users, logs


def setup_admin_routes(aiohttp_app):
    """Setup admin panel routes in aiohttp app"""
    from aiohttp import web

    # Get static directory
    static_dir = Path(__file__).parent / "static"

    # Serve index.html at root
    async def serve_admin_index(request):
        # Check admin access for HTML page too
        try:
            check_admin(request)
        except web.HTTPForbidden as e:
            return web.Response(
                text=f"Access Denied: {e.text}\n\nOnly admins can access this panel.",
                status=403
            )

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
        """Check if request is from admin"""
        from config import config

        # Get user_id from query params (passed from Telegram WebApp)
        user_id = request.query.get('user_id')

        if not user_id:
            raise web.HTTPForbidden(text="Access denied: user_id required")

        try:
            user_id = int(user_id)
        except ValueError:
            raise web.HTTPForbidden(text="Access denied: invalid user_id")

        if user_id not in config.ADMIN_IDS:
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

            page = int(request.query.get('page', 1))
            per_page = int(request.query.get('per_page', 10))

            # Get users directly from database with SQL
            import aiosqlite
            async with aiosqlite.connect(db.db_path) as conn:
                cursor = await conn.execute(
                    """SELECT user_id, username, first_name, last_name,
                              is_premium, total_translations, created_at
                       FROM users
                       ORDER BY created_at DESC
                       LIMIT ? OFFSET ?""",
                    (per_page, (page-1)*per_page)
                )
                rows = await cursor.fetchall()

                users = []
                for row in rows:
                    users.append({
                        "id": row[0],
                        "username": row[1] or "N/A",
                        "name": f"{row[2] or ''} {row[3] or ''}".strip() or "N/A",
                        "is_premium": bool(row[4]),
                        "total_translations": row[5] or 0,
                        "created_at": row[6]
                    })

            total = await db.get_user_count()

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
            import aiosqlite

            page = int(request.query.get('page', 1))
            per_page = int(request.query.get('per_page', 20))
            filter_type = request.query.get('filter', 'all')

            # Build WHERE clause based on filter
            where_clause = ""
            if filter_type == "voice":
                where_clause = "WHERE is_voice = 1"
            elif filter_type == "text":
                where_clause = "WHERE is_voice = 0"

            async with aiosqlite.connect(db.db_path) as conn:
                cursor = await conn.execute(
                    f"""SELECT th.id, th.user_id, u.username, th.source_lang, th.target_lang,
                               th.source_text, th.basic_translation, th.created_at, th.is_voice
                       FROM translation_history th
                       LEFT JOIN users u ON th.user_id = u.user_id
                       {where_clause}
                       ORDER BY th.created_at DESC
                       LIMIT ? OFFSET ?""",
                    (per_page, (page-1)*per_page)
                )
                rows = await cursor.fetchall()

                logs = []
                for row in rows:
                    logs.append({
                        "id": row[0],
                        "user_id": row[1],
                        "username": row[2] or "Unknown",
                        "source_lang": row[3],
                        "target_lang": row[4],
                        "source_text": row[5][:100] if row[5] else "",  # First 100 chars
                        "translation": row[6][:100] if row[6] else "",
                        "created_at": row[7],
                        "is_voice": bool(row[8])
                    })

                # Get total count
                cursor = await conn.execute(
                    f"SELECT COUNT(*) FROM translation_history {where_clause}"
                )
                total = (await cursor.fetchone())[0]

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
            import aiosqlite

            async with aiosqlite.connect(db.db_path) as conn:
                # Source languages
                cursor = await conn.execute(
                    """SELECT source_lang, COUNT(*) as count
                       FROM translation_history
                       GROUP BY source_lang
                       ORDER BY count DESC
                       LIMIT 10"""
                )
                source_langs = [{"lang": row[0], "count": row[1]} for row in await cursor.fetchall()]

                # Target languages
                cursor = await conn.execute(
                    """SELECT target_lang, COUNT(*) as count
                       FROM translation_history
                       GROUP BY target_lang
                       ORDER BY count DESC
                       LIMIT 10"""
                )
                target_langs = [{"lang": row[0], "count": row[1]} for row in await cursor.fetchall()]

            return web.json_response({
                "source_languages": source_langs,
                "target_languages": target_langs
            })
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)

    # API routes
    aiohttp_app.router.add_get('/api/stats/', get_stats)
    aiohttp_app.router.add_get('/api/stats/daily', get_daily_stats)
    aiohttp_app.router.add_get('/api/stats/languages', get_language_stats)
    aiohttp_app.router.add_get('/api/users/', get_users)
    aiohttp_app.router.add_get('/api/logs/translations', get_translation_logs)

    return aiohttp_app

# Initialize FastAPI app
app = FastAPI(
    title="LinguaBot Admin Panel",
    description="Admin panel for LinguaBot Telegram translator",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(stats.router)
app.include_router(users.router)
app.include_router(logs.router)

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Authentication dependency
async def verify_admin(request: Request):
    """Verify that request is from authorized admin"""
    # Get authorization header
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("tma "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Extract init data
    init_data = auth_header[4:]  # Remove "tma " prefix

    # Validate Telegram data
    validated_data = validate_telegram_webapp_data(init_data)

    if not validated_data:
        raise HTTPException(status_code=401, detail="Invalid Telegram data")

    # Extract user data
    user_data = json.loads(validated_data.get("user", "{}"))
    user_id = user_data.get("id")

    if not user_id or not is_admin(user_id):
        raise HTTPException(status_code=403, detail="Access denied: not an admin")

    return user_id


@app.get("/")
async def root():
    """Root endpoint - serves the mini-app HTML"""
    html_file = Path(__file__).parent / "static" / "index.html"

    if not html_file.exists():
        return HTMLResponse("""
        <html>
            <head><title>LinguaBot Admin</title></head>
            <body>
                <h1>Admin Panel</h1>
                <p>Frontend not yet deployed. API is available at /docs</p>
            </body>
        </html>
        """)

    with open(html_file, 'r', encoding='utf-8') as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "linguabot-admin"}


@app.get("/api/me")
async def get_current_user(user_id: int = Depends(verify_admin)):
    """Get current authenticated admin user info"""
    from bot.database import Database
    db = Database()

    user = await db.get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user_id,
        "username": user.get("username"),
        "first_name": user.get("first_name"),
        "is_admin": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
