import asyncio
import aiosqlite
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from config import config
from bot.db_adapter import db_adapter

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        if not db_adapter.is_postgres:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def init(self):
        """Initialize database tables"""
        async with db_adapter.get_connection() as conn:
            serial_type = db_adapter.get_serial_type()
            bool_type = db_adapter.get_boolean_type()
            ts_type = db_adapter.get_timestamp_type()

            # Users table
            if db_adapter.is_postgres:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        language_code TEXT DEFAULT 'ru',
                        interface_language TEXT DEFAULT 'ru',
                        target_language TEXT DEFAULT 'en',
                        translation_style TEXT DEFAULT 'informal',
                        is_premium {bool_type} DEFAULT FALSE,
                        premium_until {ts_type},
                        free_translations_today INTEGER DEFAULT 0,
                        last_translation_date DATE,
                        total_translations INTEGER DEFAULT 0,
                        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        updated_at {ts_type} DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            else:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        language_code TEXT DEFAULT 'ru',
                        interface_language TEXT DEFAULT 'ru',
                        target_language TEXT DEFAULT 'en',
                        translation_style TEXT DEFAULT 'informal',
                        is_premium {bool_type} DEFAULT 0,
                        premium_until {ts_type},
                        free_translations_today INTEGER DEFAULT 0,
                        last_translation_date DATE,
                        total_translations INTEGER DEFAULT 0,
                        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        updated_at {ts_type} DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

            # Translation history table
            if db_adapter.is_postgres:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS translation_history (
                        id {serial_type},
                        user_id BIGINT,
                        source_text TEXT,
                        source_language TEXT,
                        translated_text TEXT,
                        basic_translation TEXT,
                        enhanced_translation TEXT,
                        alternatives TEXT,
                        target_language TEXT,
                        translation_style TEXT,
                        is_voice {bool_type} DEFAULT FALSE,
                        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
            else:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS translation_history (
                        id {serial_type},
                        user_id INTEGER,
                        source_text TEXT,
                        source_language TEXT,
                        translated_text TEXT,
                        basic_translation TEXT,
                        enhanced_translation TEXT,
                        alternatives TEXT,
                        target_language TEXT,
                        translation_style TEXT,
                        is_voice {bool_type} DEFAULT 0,
                        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

            # Subscriptions table
            if db_adapter.is_postgres:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        id {serial_type},
                        user_id BIGINT,
                        subscription_type TEXT,
                        amount REAL,
                        currency TEXT DEFAULT 'RUB',
                        payment_id TEXT,
                        status TEXT,
                        started_at {ts_type},
                        expires_at {ts_type},
                        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
            else:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS subscriptions (
                        id {serial_type},
                        user_id INTEGER,
                        subscription_type TEXT,
                        amount REAL,
                        currency TEXT DEFAULT 'RUB',
                        payment_id TEXT,
                        status TEXT,
                        started_at {ts_type},
                        expires_at {ts_type},
                        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

            # User settings table
            if db_adapter.is_postgres:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id BIGINT PRIMARY KEY,
                        auto_voice {bool_type} DEFAULT FALSE,
                        save_history {bool_type} DEFAULT TRUE,
                        notifications_enabled {bool_type} DEFAULT TRUE,
                        voice_speed REAL DEFAULT 1.0,
                        voice_type TEXT DEFAULT 'alloy',
                        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        updated_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
            else:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id INTEGER PRIMARY KEY,
                        auto_voice {bool_type} DEFAULT 0,
                        save_history {bool_type} DEFAULT 1,
                        notifications_enabled {bool_type} DEFAULT 1,
                        voice_speed REAL DEFAULT 1.0,
                        voice_type TEXT DEFAULT 'alloy',
                        created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        updated_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

            # Statistics table
            if db_adapter.is_postgres:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS statistics (
                        id {serial_type},
                        date DATE UNIQUE,
                        total_users INTEGER DEFAULT 0,
                        active_users INTEGER DEFAULT 0,
                        premium_users INTEGER DEFAULT 0,
                        total_translations INTEGER DEFAULT 0,
                        voice_translations INTEGER DEFAULT 0,
                        revenue REAL DEFAULT 0
                    )
                ''')
            else:
                await conn.execute(f'''
                    CREATE TABLE IF NOT EXISTS statistics (
                        id {serial_type},
                        date DATE UNIQUE,
                        total_users INTEGER DEFAULT 0,
                        active_users INTEGER DEFAULT 0,
                        premium_users INTEGER DEFAULT 0,
                        total_translations INTEGER DEFAULT 0,
                        voice_translations INTEGER DEFAULT 0,
                        revenue REAL DEFAULT 0
                    )
                ''')

            # Migration: Add new columns if they don't exist (only for SQLite)
            if not db_adapter.is_postgres:
                try:
                    await conn.execute('ALTER TABLE translation_history ADD COLUMN basic_translation TEXT')
                except:
                    pass  # Column already exists

                try:
                    await conn.execute('ALTER TABLE translation_history ADD COLUMN enhanced_translation TEXT')
                except:
                    pass  # Column already exists

                try:
                    await conn.execute('ALTER TABLE translation_history ADD COLUMN alternatives TEXT')
                except:
                    pass  # Column already exists

            await conn.commit()

    async def add_user(self, user_id: int, username: str = None, first_name: str = None,
                      last_name: str = None, language_code: str = 'ru') -> bool:
        """Add new user or update existing"""
        from config import config

        # Check if user is admin
        is_admin = user_id in config.ADMIN_IDS

        async with db_adapter.get_connection() as conn:
            # Check if user exists
            existing_user = await conn.fetchone('SELECT user_id, target_language, is_premium, premium_until FROM users WHERE user_id = ?', user_id)

            if existing_user:
                # User exists - update and check subscription expiry
                if is_admin:
                    # Admin - always premium
                    premium_status = True
                    premium_until = datetime.now() + timedelta(days=36500)  # 100 years for admin
                    await conn.execute('''
                        UPDATE users SET
                            username = ?, first_name = ?, last_name = ?, language_code = ?,
                            interface_language = ?, is_premium = ?, premium_until = ?, updated_at = ?
                        WHERE user_id = ?
                    ''', username, first_name, last_name, language_code,
                         language_code, premium_status, premium_until, datetime.now(), user_id)
                else:
                    # Regular user - check if subscription expired
                    current_premium_until = existing_user[3]  # premium_until from SELECT

                    # Check if subscription is expired
                    now = datetime.now()
                    subscription_expired = False
                    if current_premium_until:
                        try:
                            # Parse premium_until (can be string or datetime)
                            if isinstance(current_premium_until, str):
                                premium_until_dt = datetime.fromisoformat(current_premium_until.replace('Z', '+00:00'))
                            else:
                                premium_until_dt = current_premium_until

                            subscription_expired = premium_until_dt <= now
                        except:
                            subscription_expired = True

                    if subscription_expired:
                        # Reset to non-premium
                        premium_false = "FALSE" if db_adapter.is_postgres else "0"
                        await conn.execute(f'''
                            UPDATE users SET
                                username = ?, first_name = ?, last_name = ?, language_code = ?,
                                interface_language = ?, is_premium = {premium_false}, premium_until = NULL, updated_at = ?
                            WHERE user_id = ?
                        ''', username, first_name, last_name, language_code,
                             language_code, datetime.now(), user_id)
                    else:
                        # Don't change premium status if not expired
                        await conn.execute('''
                            UPDATE users SET
                                username = ?, first_name = ?, last_name = ?, language_code = ?,
                                interface_language = ?, updated_at = ?
                            WHERE user_id = ?
                        ''', username, first_name, last_name, language_code,
                             language_code, datetime.now(), user_id)
            else:
                # New user - insert with default values
                premium_status = is_admin
                premium_until = datetime.now() + timedelta(days=36500) if is_admin else None

                await conn.execute('''
                    INSERT INTO users (
                        user_id, username, first_name, last_name, language_code,
                        interface_language, target_language, is_premium, premium_until, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', user_id, username, first_name, last_name, language_code,
                     language_code, 'en', premium_status, premium_until, datetime.now())

            # Initialize user settings (use UPSERT for PostgreSQL compatibility)
            if db_adapter.is_postgres:
                await conn.execute('''
                    INSERT INTO user_settings (user_id) VALUES (?)
                    ON CONFLICT (user_id) DO NOTHING
                ''', user_id)
            else:
                await conn.execute('''
                    INSERT OR IGNORE INTO user_settings (user_id) VALUES (?)
                ''', user_id)

            await conn.commit()
            return True

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information"""
        async with db_adapter.get_connection() as conn:
            cursor = await conn.execute('''
                SELECT u.*, s.auto_voice, s.save_history, s.notifications_enabled,
                       s.voice_speed, s.voice_type
                FROM users u
                LEFT JOIN user_settings s ON u.user_id = s.user_id
                WHERE u.user_id = ?
            ''', user_id)
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_user_language(self, user_id: int, target_language: str) -> bool:
        """Update user's target translation language"""
        async with db_adapter.get_connection() as conn:
            await conn.execute('''
                UPDATE users
                SET target_language = ?, updated_at = ?
                WHERE user_id = ?
            ''', target_language, datetime.now(), user_id)
            await conn.commit()
            return True

    async def update_user_style(self, user_id: int, style: str) -> bool:
        """Update user's translation style"""
        async with db_adapter.get_connection() as conn:
            await conn.execute('''
                UPDATE users
                SET translation_style = ?, updated_at = ?
                WHERE user_id = ?
            ''', style, datetime.now(), user_id)
            await conn.commit()
            return True

    async def check_daily_limit(self, user_id: int) -> tuple[bool, int]:
        """Check if user has reached daily translation limit"""
        async with db_adapter.get_connection() as conn:
            cursor = await conn.execute('''
                SELECT is_premium, free_translations_today, last_translation_date,
                       premium_until
                FROM users WHERE user_id = ?
            ''', user_id)
            row = await cursor.fetchone()

            if not row:
                return False, 0

            is_premium, translations_today, last_date, premium_until = row

            # Check if premium is still valid
            if is_premium and premium_until:
                premium_until = datetime.fromisoformat(premium_until)
                if premium_until < datetime.now():
                    # Premium expired
                    premium_false = "FALSE" if db_adapter.is_postgres else "0"
                    await conn.execute(f'''
                        UPDATE users SET is_premium = {premium_false} WHERE user_id = ?
                    ''', user_id)
                    await conn.commit()
                    is_premium = False

            # Premium users have unlimited translations
            if is_premium:
                return True, -1

            # Reset counter if it's a new day
            today = datetime.now().date()
            if last_date:
                last_date = datetime.fromisoformat(last_date).date()
                if last_date < today:
                    translations_today = 0
                    await conn.execute('''
                        UPDATE users
                        SET free_translations_today = 0, last_translation_date = ?
                        WHERE user_id = ?
                    ''', today, user_id)
                    await conn.commit()

            remaining = config.FREE_DAILY_LIMIT - translations_today
            return remaining > 0, remaining

    async def increment_translation_count(self, user_id: int) -> bool:
        """Increment user's translation count"""
        async with db_adapter.get_connection() as conn:
            today = datetime.now().date()
            await conn.execute('''
                UPDATE users
                SET free_translations_today = free_translations_today + 1,
                    total_translations = total_translations + 1,
                    last_translation_date = ?,
                    updated_at = ?
                WHERE user_id = ?
            ''', today, datetime.now(), user_id)
            await conn.commit()
            return True

    async def add_translation_history(self, user_id: int, source_text: str,
                                     source_language: str, translated_text: str,
                                     target_language: str, style: str = 'informal',
                                     is_voice: bool = False,
                                     basic_translation: str = None,
                                     enhanced_translation: str = None,
                                     alternatives: list = None) -> bool:
        """Add translation to history"""
        async with db_adapter.get_connection() as conn:
            # Check if history saving is enabled
            cursor = await conn.execute('''
                SELECT save_history FROM user_settings WHERE user_id = ?
            ''', user_id)
            row = await cursor.fetchone()

            if row and row[0]:
                # Convert alternatives list to JSON string for storage
                alternatives_json = None
                if alternatives:
                    import json
                    alternatives_json = json.dumps(alternatives, ensure_ascii=False)

                await conn.execute('''
                    INSERT INTO translation_history (
                        user_id, source_text, source_language, translated_text,
                        basic_translation, enhanced_translation, alternatives,
                        target_language, translation_style, is_voice
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', user_id, source_text, source_language, translated_text,
                     basic_translation, enhanced_translation, alternatives_json,
                     target_language, style, is_voice)

                # Clean old history (keep only last MAX_HISTORY_ITEMS)
                await conn.execute('''
                    DELETE FROM translation_history
                    WHERE user_id = ? AND id NOT IN (
                        SELECT id FROM translation_history
                        WHERE user_id = ?
                        ORDER BY created_at DESC
                        LIMIT ?
                    )
                ''', user_id, user_id, config.MAX_HISTORY_ITEMS)

                await conn.commit()
            return True

    async def get_user_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's translation history"""
        async with db_adapter.get_connection() as conn:
            cursor = await conn.execute('''
                SELECT * FROM translation_history
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', user_id, limit)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def clear_user_history(self, user_id: int) -> bool:
        """Clear user's translation history"""
        async with db_adapter.get_connection() as conn:
            await conn.execute('''
                DELETE FROM translation_history WHERE user_id = ?
            ''', user_id)
            await conn.commit()
            return True

    async def activate_subscription(self, user_id: int, subscription_type: str,
                                   payment_id: str, amount: float) -> bool:
        """Activate user's premium subscription"""
        async with db_adapter.get_connection() as conn:
            now = datetime.now()
            if subscription_type == 'daily':
                expires_at = now + timedelta(days=1)
            elif subscription_type == 'monthly':
                expires_at = now + timedelta(days=30)
            else:  # yearly
                expires_at = now + timedelta(days=365)

            # Add subscription record
            await conn.execute('''
                INSERT INTO subscriptions (
                    user_id, subscription_type, amount, payment_id,
                    status, started_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', user_id, subscription_type, amount, payment_id,
                 'active', now, expires_at)

            # Update user premium status
            premium_value = "TRUE" if db_adapter.is_postgres else "1"
            await conn.execute(f'''
                UPDATE users
                SET is_premium = {premium_value}, premium_until = ?
                WHERE user_id = ?
            ''', expires_at, user_id)

            await conn.commit()
            return True

    async def get_statistics(self, date: datetime = None) -> Dict[str, Any]:
        """Get statistics for a specific date or today"""
        if not date:
            date = datetime.now().date()

        async with db_adapter.get_connection() as conn:
            # Build boolean comparison based on database type
            premium_check = "is_premium = TRUE" if db_adapter.is_postgres else "is_premium = 1"
            voice_check = "is_voice = TRUE" if db_adapter.is_postgres else "is_voice = 1"

            # Get user statistics
            cursor = await conn.execute(f'''
                SELECT
                    COUNT(*) as total_users,
                    SUM(CASE WHEN last_translation_date = ? THEN 1 ELSE 0 END) as active_users,
                    SUM(CASE WHEN {premium_check} THEN 1 ELSE 0 END) as premium_users
                FROM users
            ''', date)
            user_stats = await cursor.fetchone()

            # Get translation statistics
            cursor = await conn.execute(f'''
                SELECT
                    COUNT(*) as total_translations,
                    SUM(CASE WHEN {voice_check} THEN 1 ELSE 0 END) as voice_translations
                FROM translation_history
                WHERE DATE(created_at) = ?
            ''', date)
            trans_stats = await cursor.fetchone()

            # Get revenue
            cursor = await conn.execute('''
                SELECT SUM(amount) as revenue
                FROM subscriptions
                WHERE DATE(created_at) = ? AND status = 'active'
            ''', date)
            revenue = await cursor.fetchone()

            return {
                'date': date,
                'total_users': user_stats[0] or 0,
                'active_users': user_stats[1] or 0,
                'premium_users': user_stats[2] or 0,
                'total_translations': trans_stats[0] or 0,
                'voice_translations': trans_stats[1] or 0,
                'revenue': revenue[0] or 0
            }

    async def update_user_settings(self, user_id: int, **settings) -> bool:
        """Update user settings"""
        async with db_adapter.get_connection() as conn:
            valid_settings = ['auto_voice', 'save_history', 'notifications_enabled',
                            'voice_speed', 'voice_type']
            updates = []
            values = []

            for key, value in settings.items():
                if key in valid_settings:
                    updates.append(f"{key} = ?")
                    values.append(value)

            if updates:
                values.extend([datetime.now(), user_id])
                query = f'''
                    UPDATE user_settings
                    SET {', '.join(updates)}, updated_at = ?
                    WHERE user_id = ?
                '''
                await conn.execute(query, *values)
                await conn.commit()
            return True

    async def get_user_count(self) -> int:
        """Get total user count"""
        async with db_adapter.get_connection() as conn:
            cursor = await conn.execute('SELECT COUNT(*) FROM users')
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def get_premium_user_count(self) -> int:
        """Get premium user count"""
        async with db_adapter.get_connection() as conn:
            premium_check = "is_premium = TRUE" if db_adapter.is_postgres else "is_premium = 1"
            cursor = await conn.execute(f'''
                SELECT COUNT(*) FROM users
                WHERE {premium_check} AND (premium_until IS NULL OR premium_until > ?)
            ''', datetime.now())
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def update_user_subscription(self, user_id: int, is_premium: bool,
                                     subscription_type: str, subscription_end: float):
        """Update user subscription status"""
        premium_until = datetime.fromtimestamp(subscription_end) if subscription_end else None

        async with db_adapter.get_connection() as conn:
            try:
                await conn.execute('''
                    UPDATE users
                    SET is_premium = ?, premium_until = ?, updated_at = ?
                    WHERE user_id = ?
                ''', is_premium, premium_until, datetime.now(), user_id)
                await conn.commit()
                return True
            except Exception as e:
                print(f"Error updating subscription: {e}")
                return False

# Create global database instance
db = Database()