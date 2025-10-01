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

    # Add routes
    aiohttp_app.router.add_get('/admin', serve_admin_index)
    aiohttp_app.router.add_get('/admin/', serve_admin_index)
    aiohttp_app.router.add_get('/admin/{filename:.+}', serve_static)

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
