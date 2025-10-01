#!/usr/bin/env python3
"""Manually apply database migrations"""
import asyncio
from bot.database import Database

async def main():
    print("🔄 Starting manual migration process...")
    db = Database()
    await db.initialize()
    await db.apply_migrations()
    print("✅ Migration process completed")

if __name__ == "__main__":
    asyncio.run(main())
