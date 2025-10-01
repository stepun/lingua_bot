#!/usr/bin/env python3
"""
Запуск админ-панели локально (отдельно от бота)
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env.local
load_dotenv('.env.local', override=True)

sys.path.append(str(Path(__file__).parent))

from aiohttp import web
from admin_app.app import setup_admin_routes

async def init_app():
    app = web.Application()
    setup_admin_routes(app)
    return app

if __name__ == '__main__':
    port = int(os.getenv('ADMIN_PORT', 8080))
    print(f"🚀 Starting Admin Panel on http://localhost:{port}")
    print(f"📊 Open: http://localhost:{port}/admin?user_id=120962578")

    web.run_app(init_app(), host='0.0.0.0', port=port)
