import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from config import config
from bot.db_adapter import db_adapter

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        # PostgreSQL-only system, no local path needed

    async def init(self):
        """Initialize database tables"""
        async with db_adapter.get_connection() as conn:
            serial_type = db_adapter.get_serial_type()
            bool_type = db_adapter.get_boolean_type()
            ts_type = db_adapter.get_timestamp_type()

            # Users table (PostgreSQL-only)
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
                    is_blocked {bool_type} DEFAULT FALSE,
                    free_translations_today INTEGER DEFAULT 0,
                    last_translation_date DATE,
                    total_translations INTEGER DEFAULT 0,
                    created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                    updated_at {ts_type} DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Translation history table (PostgreSQL-only)
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
                    processing_time_ms INTEGER,
                    status TEXT DEFAULT 'success',
                    error_message TEXT,
                    created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Subscriptions table (PostgreSQL-only)
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

            # User settings table (PostgreSQL-only)
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

            # Statistics table (PostgreSQL-only)
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

            # Feedback table (PostgreSQL-only)
            await conn.execute(f'''
                CREATE TABLE IF NOT EXISTS feedback (
                    id {serial_type},
                    user_id BIGINT,
                    message TEXT NOT NULL,
                    status TEXT DEFAULT 'new',
                    created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                    updated_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Admin actions table (PostgreSQL-only)
            await conn.execute(f'''
                CREATE TABLE IF NOT EXISTS admin_actions (
                    id {serial_type},
                    admin_user_id BIGINT NOT NULL,
                    action TEXT NOT NULL,
                    target_user_id BIGINT,
                    details TEXT,
                    created_at {ts_type} DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (admin_user_id) REFERENCES users (user_id),
                    FOREIGN KEY (target_user_id) REFERENCES users (user_id)
                )
            ''')

            # Schema migrations table (PostgreSQL-only)
            await conn.execute(f'''
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version TEXT PRIMARY KEY,
                    applied_at {ts_type} DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            await conn.commit()

        # Apply migrations after initial schema setup
        # DISABLED: Causes Railway deployment to hang - apply manually via railway run
        # await self.apply_migrations()

        # Auto-repair schema if migrations were marked as applied but columns are missing
        # await self.verify_and_repair_schema()

    async def apply_migrations(self):
        """Apply pending database migrations from migrations/ folder"""
        import os
        import glob

        migrations_dir = Path(__file__).parent.parent / 'migrations'
        print(f"[MIGRATIONS] Looking for migrations in: {migrations_dir}")
        print(f"[MIGRATIONS] Directory exists: {migrations_dir.exists()}")

        if not migrations_dir.exists():
            print("[MIGRATIONS] No migrations directory found, skipping...")
            return

        # Get all .sql migration files sorted by version
        migration_files = sorted(glob.glob(str(migrations_dir / '*.sql')))
        print(f"[MIGRATIONS] Found {len(migration_files)} migration files: {[os.path.basename(f) for f in migration_files]}")

        # Additional debug info for migration detection
        if migrations_dir.exists():
            import os as _os
            all_files = _os.listdir(migrations_dir)
            print(f"[MIGRATIONS] All files in migrations dir: {all_files}")

        if not migration_files:
            print("[MIGRATIONS] No migration files found")
            return

        async with db_adapter.get_connection() as conn:
            # Get applied migrations
            applied = set()
            try:
                rows = await conn.fetchall('SELECT version FROM schema_migrations')
                applied = {row['version'] for row in rows}
                print(f"[MIGRATIONS] Already applied: {sorted(applied)}")
            except Exception as e:
                # Table might not exist yet on first run, that's OK
                print(f"[MIGRATIONS] Could not read schema_migrations table (might not exist yet): {e}")
                pass

            # Apply pending migrations
            for migration_file in migration_files:
                version = os.path.basename(migration_file)

                if version in applied:
                    print(f"[MIGRATIONS] ✓ Skipping {version} (already applied)")
                    continue

                print(f"[MIGRATIONS] Applying {version}...")

                try:
                    # Read migration SQL
                    with open(migration_file, 'r', encoding='utf-8') as f:
                        sql = f.read()

                    # Execute each statement (split by semicolons, excluding comments)
                    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]

                    # Execute all statements in the migration (PostgreSQL autocommit mode)
                    for statement in statements:
                        if statement:
                            print(f"[MIGRATIONS]   Executing: {statement[:80]}...")
                            await conn.execute(statement)

                    # Mark migration as applied
                    await conn.execute(
                        'INSERT INTO schema_migrations (version) VALUES ($1)',
                        version
                    )

                    print(f"[MIGRATIONS] ✅ Applied {version}")

                except Exception as e:
                    print(f"[MIGRATIONS] ❌ Failed to apply {version}: {e}")

                    # Check if this is a "duplicate key" error (migration already recorded but failed)
                    error_str = str(e).lower()
                    if 'duplicate key' in error_str or 'unique constraint' in error_str:
                        print(f"[MIGRATIONS] ⚠️  Migration {version} already recorded but may have failed previously")
                        print(f"[MIGRATIONS] ⚠️  Please verify schema manually or run fix script")
                        # Skip this migration and continue
                        continue

                    # Do NOT continue - stop on first error to prevent cascading failures
                    raise RuntimeError(f"Migration {version} failed: {e}")

    async def verify_and_repair_schema(self):
        """
        Verify schema integrity and repair if migrations were marked as applied
        but columns are missing (due to previous transaction issues)
        PostgreSQL-only system.
        """
        print("[SCHEMA_REPAIR] Verifying schema integrity...")

        async with db_adapter.get_connection() as conn:
            repairs_made = []

            # Check 001_add_is_blocked.sql - users.is_blocked
            try:
                row = await conn.fetchone("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'users' AND column_name = 'is_blocked'
                """)
                if not row:
                    print("[SCHEMA_REPAIR] ⚠️  Column users.is_blocked missing, repairing...")
                    await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT FALSE")
                    repairs_made.append("users.is_blocked")
                    print("[SCHEMA_REPAIR] ✅ Repaired users.is_blocked")
            except Exception as e:
                print(f"[SCHEMA_REPAIR] Error checking users.is_blocked: {e}")

            # Check 002_add_performance_metrics.sql - translation_history columns
            try:
                row = await conn.fetchone("""
                    SELECT COUNT(*) as cnt
                    FROM information_schema.columns
                    WHERE table_name = 'translation_history'
                    AND column_name IN ('processing_time_ms', 'status', 'error_message')
                """)
                missing_count = 3 - (row['cnt'] if row else 0)
                if missing_count > 0:
                    print(f"[SCHEMA_REPAIR] ⚠️  Missing {missing_count} translation_history columns, repairing...")
                    await conn.execute("ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS processing_time_ms INTEGER")
                    await conn.execute("ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'success'")
                    await conn.execute("ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS error_message TEXT")
                    repairs_made.append("translation_history.performance_metrics")
                    print("[SCHEMA_REPAIR] ✅ Repaired translation_history performance columns")
            except Exception as e:
                print(f"[SCHEMA_REPAIR] Error checking translation_history: {e}")

            if repairs_made:
                print(f"[SCHEMA_REPAIR] ✅ Repairs completed: {', '.join(repairs_made)}")
                await conn.commit()
            else:
                print("[SCHEMA_REPAIR] ✅ Schema is healthy, no repairs needed")

    async def add_user(self, user_id: int, username: str = None, first_name: str = None,
                      last_name: str = None, language_code: str = 'ru') -> bool:
        """Add new user or update existing"""
        async with db_adapter.get_connection() as conn:
            # Check if user exists
            existing_user = await conn.fetchone('SELECT user_id, target_language FROM users WHERE user_id = ?', user_id)

            if existing_user:
                # User exists - update basic info only
                await conn.execute('''
                    UPDATE users SET
                        username = ?, first_name = ?, last_name = ?, language_code = ?,
                        interface_language = ?, updated_at = ?
                    WHERE user_id = ?
                ''', username, first_name, last_name, language_code,
                     language_code, datetime.now(), user_id)
            else:
                # New user - insert with default values
                await conn.execute('''
                    INSERT INTO users (
                        user_id, username, first_name, last_name, language_code,
                        interface_language, target_language, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', user_id, username, first_name, last_name, language_code,
                     language_code, 'en', datetime.now())

            # Initialize user settings (PostgreSQL UPSERT)
            await conn.execute('''
                INSERT INTO user_settings (user_id) VALUES (?)
                ON CONFLICT (user_id) DO NOTHING
            ''', user_id)

            await conn.commit()
            return True

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information with dynamic premium status"""
        async with db_adapter.get_connection() as conn:
            cursor = await conn.execute('''
                SELECT u.*, s.auto_voice, s.save_history, s.notifications_enabled,
                       s.voice_speed, s.voice_type
                FROM users u
                LEFT JOIN user_settings s ON u.user_id = s.user_id
                WHERE u.user_id = ?
            ''', user_id)
            row = await cursor.fetchone()
            if not row:
                return None

            user_data = dict(row)

            # Add dynamic premium status from subscriptions table
            cursor_sub = await conn.execute('''
                SELECT expires_at FROM subscriptions
                WHERE user_id = ? AND status = 'active' AND expires_at > ?
                ORDER BY expires_at DESC LIMIT 1
            ''', user_id, datetime.now())
            subscription = await cursor_sub.fetchone()

            user_data['is_premium'] = subscription is not None
            user_data['premium_until'] = subscription['expires_at'] if subscription else None

            return user_data

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
                SELECT free_translations_today, last_translation_date
                FROM users WHERE user_id = ?
            ''', user_id)
            row = await cursor.fetchone()

            if not row:
                return False, 0

            translations_today, last_date = row

            # Check if user has active premium subscription
            cursor_sub = await conn.execute('''
                SELECT expires_at FROM subscriptions
                WHERE user_id = ? AND status = 'active' AND expires_at > ?
                ORDER BY expires_at DESC LIMIT 1
            ''', user_id, datetime.now())
            subscription = await cursor_sub.fetchone()

            is_premium = subscription is not None

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
                                     alternatives: list = None,
                                     processing_time_ms: int = None,
                                     status: str = 'success',
                                     error_message: str = None) -> bool:
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
                        target_language, translation_style, is_voice,
                        processing_time_ms, status, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', user_id, source_text, source_language, translated_text,
                     basic_translation, enhanced_translation, alternatives_json,
                     target_language, style, is_voice,
                     processing_time_ms, status, error_message)

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

            await conn.commit()
            return True

    async def get_statistics(self, date: datetime = None) -> Dict[str, Any]:
        """Get statistics for a specific date or today"""
        if not date:
            date = datetime.now().date()

        async with db_adapter.get_connection() as conn:
            # Get user statistics
            cursor = await conn.execute('''
                SELECT
                    COUNT(*) as total_users,
                    SUM(CASE WHEN last_translation_date = ? THEN 1 ELSE 0 END) as active_users
                FROM users
            ''', date)
            user_stats = await cursor.fetchone()

            # Get premium user count from active subscriptions
            cursor = await conn.execute('''
                SELECT COUNT(DISTINCT user_id) as premium_users
                FROM subscriptions
                WHERE status = 'active' AND expires_at > ?
            ''', datetime.now())
            premium_stats = await cursor.fetchone()

            # Get translation statistics
            cursor = await conn.execute('''
                SELECT
                    COUNT(*) as total_translations,
                    SUM(CASE WHEN is_voice = TRUE THEN 1 ELSE 0 END) as voice_translations
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
                'premium_users': premium_stats[0] or 0,
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
        """Get premium user count from active subscriptions"""
        async with db_adapter.get_connection() as conn:
            cursor = await conn.execute('''
                SELECT COUNT(DISTINCT user_id) FROM subscriptions
                WHERE status = 'active' AND expires_at > ?
            ''', datetime.now())
            result = await cursor.fetchone()
            return result[0] if result else 0

    async def update_user_subscription(self, user_id: int, is_premium: bool,
                                     subscription_type: str, subscription_end: float):
        """Update user subscription status via subscriptions table"""
        expires_at = datetime.fromtimestamp(subscription_end) if subscription_end else None

        async with db_adapter.get_connection() as conn:
            try:
                if is_premium and expires_at:
                    # Add or update subscription
                    now = datetime.now()
                    await conn.execute('''
                        INSERT INTO subscriptions (
                            user_id, subscription_type, amount, payment_id,
                            status, started_at, expires_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', user_id, subscription_type or 'unknown', 0.0, 'legacy_update',
                         'active', now, expires_at)
                else:
                    # Deactivate subscription
                    await conn.execute('''
                        UPDATE subscriptions
                        SET status = 'expired'
                        WHERE user_id = ? AND status = 'active'
                    ''', user_id)

                await conn.commit()
                return True
            except Exception as e:
                print(f"Error updating subscription: {e}")
                return False

    async def block_user(self, user_id: int) -> bool:
        """Block user from using the bot"""
        async with db_adapter.get_connection() as conn:
            try:
                await conn.execute('''
                    UPDATE users
                    SET is_blocked = TRUE, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', user_id)
                await conn.commit()
                return True
            except Exception as e:
                print(f"Error blocking user {user_id}: {e}")
                return False

    async def unblock_user(self, user_id: int) -> bool:
        """Unblock user"""
        async with db_adapter.get_connection() as conn:
            try:
                await conn.execute('''
                    UPDATE users
                    SET is_blocked = FALSE, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', user_id)
                await conn.commit()
                return True
            except Exception as e:
                print(f"Error unblocking user {user_id}: {e}")
                return False

    async def is_user_blocked(self, user_id: int) -> bool:
        """Check if user is blocked"""
        async with db_adapter.get_connection() as conn:
            try:
                row = await conn.fetchone('''
                    SELECT is_blocked FROM users WHERE user_id = ?
                ''', user_id)
                return bool(row[0]) if row else False
            except Exception as e:
                print(f"Error checking if user {user_id} is blocked: {e}")
                return False

    # Feedback methods
    async def add_feedback(self, user_id: int, message: str) -> bool:
        """Add user feedback"""
        async with db_adapter.get_connection() as conn:
            try:
                await conn.execute('''
                    INSERT INTO feedback (user_id, message, status)
                    VALUES ($1, $2, 'new')
                ''', user_id, message)
                await conn.commit()
                return True
            except Exception as e:
                print(f"Error adding feedback from user {user_id}: {e}")
                return False

    async def get_all_feedback(self, status: str = None, limit: int = 100):
        """Get all feedback, optionally filtered by status"""
        async with db_adapter.get_connection() as conn:
            try:
                if status:
                    rows = await conn.fetchall('''
                        SELECT f.id, f.user_id, u.username, u.first_name, u.last_name,
                               f.message, f.status, f.created_at, f.updated_at
                        FROM feedback f
                        LEFT JOIN users u ON f.user_id = u.user_id
                        WHERE f.status = $1
                        ORDER BY f.created_at DESC
                        LIMIT $2
                    ''', status, limit)
                else:
                    rows = await conn.fetchall('''
                        SELECT f.id, f.user_id, u.username, u.first_name, u.last_name,
                               f.message, f.status, f.created_at, f.updated_at
                        FROM feedback f
                        LEFT JOIN users u ON f.user_id = u.user_id
                        ORDER BY f.created_at DESC
                        LIMIT $1
                    ''', limit)

                feedback_list = []
                for row in rows:
                    feedback_list.append({
                        'id': row[0],
                        'user_id': row[1],
                        'username': row[2] or 'Unknown',
                        'user_name': f"{row[3] or ''} {row[4] or ''}".strip() or 'N/A',
                        'message': row[5],
                        'status': row[6],
                        'created_at': row[7].isoformat() if row[7] else None,
                        'updated_at': row[8].isoformat() if row[8] else None
                    })
                return feedback_list
            except Exception as e:
                print(f"Error getting feedback: {e}")
                return []

    async def update_feedback_status(self, feedback_id: int, status: str) -> bool:
        """Update feedback status (new/reviewed/resolved)"""
        async with db_adapter.get_connection() as conn:
            try:
                await conn.execute('''
                    UPDATE feedback
                    SET status = $1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = $2
                ''', status, feedback_id)
                await conn.commit()
                return True
            except Exception as e:
                print(f"Error updating feedback {feedback_id}: {e}")
                return False

    async def get_feedback_count_by_status(self):
        """Get count of feedback by status"""
        async with db_adapter.get_connection() as conn:
            try:
                rows = await conn.fetchall('''
                    SELECT status, COUNT(*) as count
                    FROM feedback
                    GROUP BY status
                ''')
                return {row[0]: row[1] for row in rows}
            except Exception as e:
                print(f"Error getting feedback counts: {e}")
                return {}

    async def log_admin_action(self, admin_user_id: int, action: str, target_user_id: int = None, details: dict = None) -> bool:
        """Log admin action"""
        async with db_adapter.get_connection() as conn:
            try:
                details_json = json.dumps(details) if details else None
                await conn.execute('''
                    INSERT INTO admin_actions (admin_user_id, action, target_user_id, details)
                    VALUES ($1, $2, $3, $4)
                ''', admin_user_id, action, target_user_id, details_json)
                await conn.commit()
                return True
            except Exception as e:
                print(f"Error logging admin action: {e}")
                return False

    async def get_admin_logs(self, admin_user_id: int = None, action: str = None, limit: int = 100):
        """Get admin action logs with optional filters"""
        async with db_adapter.get_connection() as conn:
            try:
                conditions = []
                params = []
                param_count = 1

                if admin_user_id:
                    conditions.append(f"aa.admin_user_id = ${param_count}")
                    params.append(admin_user_id)
                    param_count += 1

                if action:
                    conditions.append(f"aa.action = ${param_count}")
                    params.append(action)
                    param_count += 1

                where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

                params.append(limit)
                query = f'''
                    SELECT aa.id, aa.admin_user_id, u1.username as admin_username, u1.first_name as admin_first_name,
                           aa.action, aa.target_user_id, u2.username as target_username, u2.first_name as target_first_name,
                           aa.details, aa.created_at
                    FROM admin_actions aa
                    LEFT JOIN users u1 ON aa.admin_user_id = u1.user_id
                    LEFT JOIN users u2 ON aa.target_user_id = u2.user_id
                    {where_clause}
                    ORDER BY aa.created_at DESC
                    LIMIT ${param_count}
                '''

                rows = await conn.fetchall(query, *params)

                logs = []
                for row in rows:
                    logs.append({
                        'id': row[0],
                        'admin_user_id': row[1],
                        'admin_username': row[2] or 'Unknown',
                        'admin_name': row[3] or 'N/A',
                        'action': row[4],
                        'target_user_id': row[5],
                        'target_username': row[6] or 'Unknown' if row[5] else None,
                        'target_name': row[7] or 'N/A' if row[5] else None,
                        'details': json.loads(row[8]) if row[8] else {},
                        'created_at': row[9].isoformat() if row[9] else None
                    })
                return logs
            except Exception as e:
                print(f"Error getting admin logs: {e}")
                return []

# Create global database instance
db = Database()