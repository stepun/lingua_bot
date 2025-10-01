#!/usr/bin/env python3
"""Migrate data from Beget SQLite to Railway PostgreSQL"""

import asyncio
import aiosqlite
import asyncpg
import os
from datetime import datetime

# Database paths
SQLITE_DB = "/tmp/beget_bot.db"
# Use DATABASE_URL for local, or DATABASE_PUBLIC_URL for Railway
POSTGRES_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE_PUBLIC_URL", "postgresql://postgres:NtLFItrylcyGPGHIqllCxepVRNTSkHYG@hopper.proxy.rlwy.net:52905/railway")

def parse_datetime(dt_str):
    """Parse datetime string from SQLite"""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str)
    except:
        return None

def parse_date(dt_str):
    """Parse date string from SQLite"""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str).date()
    except:
        return None

async def migrate_users(sqlite_conn, pg_conn):
    """Migrate users table"""
    print("Migrating users...")

    cursor = await sqlite_conn.execute("""
        SELECT user_id, username, first_name, last_name, language_code,
               interface_language, target_language, translation_style,
               is_premium, premium_until, free_translations_today,
               last_translation_date, total_translations, created_at, updated_at
        FROM users
    """)
    users = await cursor.fetchall()

    count = 0
    for user in users:
        try:
            # Convert types for PostgreSQL
            user_data = list(user)
            user_data[8] = bool(user_data[8])  # is_premium
            user_data[9] = parse_datetime(user_data[9])  # premium_until
            user_data[11] = parse_date(user_data[11])  # last_translation_date
            user_data[13] = parse_datetime(user_data[13])  # created_at
            user_data[14] = parse_datetime(user_data[14])  # updated_at

            await pg_conn.execute("""
                INSERT INTO users (
                    user_id, username, first_name, last_name, language_code,
                    interface_language, target_language, translation_style,
                    is_premium, premium_until, free_translations_today,
                    last_translation_date, total_translations, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (user_id) DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    total_translations = EXCLUDED.total_translations,
                    updated_at = EXCLUDED.updated_at
            """, *user_data)
            count += 1
        except Exception as e:
            print(f"Error migrating user {user[0]}: {e}")

    print(f"Migrated {count} users")
    return count

async def migrate_translation_history(sqlite_conn, pg_conn):
    """Migrate translation_history table"""
    print("Migrating translation history...")

    cursor = await sqlite_conn.execute("""
        SELECT user_id, source_text, source_language, translated_text,
               basic_translation, enhanced_translation, alternatives,
               target_language, translation_style, is_voice, created_at
        FROM translation_history
    """)
    records = await cursor.fetchall()

    count = 0
    for record in records:
        try:
            # Convert types
            rec_data = list(record)
            rec_data[9] = bool(rec_data[9])  # is_voice
            rec_data[10] = parse_datetime(rec_data[10])  # created_at

            await pg_conn.execute("""
                INSERT INTO translation_history (
                    user_id, source_text, source_language, translated_text,
                    basic_translation, enhanced_translation, alternatives,
                    target_language, translation_style, is_voice, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """, *rec_data)
            count += 1
        except Exception as e:
            print(f"Error migrating translation: {e}")

    print(f"Migrated {count} translation records")
    return count

async def migrate_subscriptions(sqlite_conn, pg_conn):
    """Migrate subscriptions table"""
    print("Migrating subscriptions...")

    cursor = await sqlite_conn.execute("""
        SELECT user_id, subscription_type, amount, currency,
               payment_id, status, started_at, expires_at, created_at
        FROM subscriptions
    """)
    subs = await cursor.fetchall()

    count = 0
    for sub in subs:
        try:
            # Convert types
            sub_data = list(sub)
            sub_data[6] = parse_datetime(sub_data[6])  # started_at
            sub_data[7] = parse_datetime(sub_data[7])  # expires_at
            sub_data[8] = parse_datetime(sub_data[8])  # created_at

            await pg_conn.execute("""
                INSERT INTO subscriptions (
                    user_id, subscription_type, amount, currency,
                    payment_id, status, started_at, expires_at, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """, *sub_data)
            count += 1
        except Exception as e:
            print(f"Error migrating subscription: {e}")

    print(f"Migrated {count} subscriptions")
    return count

async def migrate_user_settings(sqlite_conn, pg_conn):
    """Migrate user_settings table"""
    print("Migrating user settings...")

    cursor = await sqlite_conn.execute("""
        SELECT user_id, auto_voice, save_history, notifications_enabled,
               voice_speed, voice_type, created_at, updated_at
        FROM user_settings
    """)
    settings = await cursor.fetchall()

    count = 0
    for setting in settings:
        try:
            # Convert types
            set_data = list(setting)
            set_data[1] = bool(set_data[1])  # auto_voice
            set_data[2] = bool(set_data[2])  # save_history
            set_data[3] = bool(set_data[3])  # notifications_enabled
            set_data[6] = parse_datetime(set_data[6])  # created_at
            set_data[7] = parse_datetime(set_data[7])  # updated_at

            await pg_conn.execute("""
                INSERT INTO user_settings (
                    user_id, auto_voice, save_history, notifications_enabled,
                    voice_speed, voice_type, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (user_id) DO UPDATE SET
                    auto_voice = EXCLUDED.auto_voice,
                    save_history = EXCLUDED.save_history,
                    notifications_enabled = EXCLUDED.notifications_enabled,
                    voice_speed = EXCLUDED.voice_speed,
                    voice_type = EXCLUDED.voice_type,
                    updated_at = EXCLUDED.updated_at
            """, *set_data)
            count += 1
        except Exception as e:
            print(f"Error migrating user settings: {e}")

    print(f"Migrated {count} user settings")
    return count

async def main():
    print(f"Starting migration from {SQLITE_DB} to PostgreSQL")
    print(f"PostgreSQL URL: {POSTGRES_URL[:50]}...")

    # Connect to databases
    sqlite_conn = await aiosqlite.connect(SQLITE_DB)
    pg_conn = await asyncpg.connect(POSTGRES_URL)

    try:
        # Run migrations
        users_count = await migrate_users(sqlite_conn, pg_conn)
        settings_count = await migrate_user_settings(sqlite_conn, pg_conn)
        subs_count = await migrate_subscriptions(sqlite_conn, pg_conn)
        history_count = await migrate_translation_history(sqlite_conn, pg_conn)

        print("\n=== Migration Summary ===")
        print(f"Users: {users_count}")
        print(f"User Settings: {settings_count}")
        print(f"Subscriptions: {subs_count}")
        print(f"Translation History: {history_count}")
        print("=========================")

    finally:
        await sqlite_conn.close()
        await pg_conn.close()

if __name__ == "__main__":
    asyncio.run(main())
