"""Database adapter for SQLite and PostgreSQL"""

import os
import aiosqlite
import asyncpg
from typing import Optional, Any
from contextlib import asynccontextmanager


class DatabaseAdapter:
    """Adapter for different database backends"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.is_postgres = self.database_url and self.database_url.startswith("postgres")
        self.db_path = os.getenv("DATABASE_PATH", "data/bot.db")
        self._pool: Optional[asyncpg.Pool] = None

    async def init_pool(self):
        """Initialize connection pool for PostgreSQL"""
        if self.is_postgres and not self._pool:
            self._pool = await asyncpg.create_pool(self.database_url)

    async def close_pool(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def get_connection(self):
        """Get database connection (context manager)"""
        if self.is_postgres:
            if not self._pool:
                await self.init_pool()
            async with self._pool.acquire() as conn:
                yield PostgreSQLConnection(conn)
        else:
            async with aiosqlite.connect(self.db_path) as conn:
                yield SQLiteConnection(conn)

    def placeholder(self, index: int) -> str:
        """Get parameter placeholder for query"""
        if self.is_postgres:
            return f"${index}"
        else:
            return "?"

    def get_serial_type(self) -> str:
        """Get auto-increment type"""
        if self.is_postgres:
            return "SERIAL PRIMARY KEY"
        else:
            return "INTEGER PRIMARY KEY AUTOINCREMENT"

    def get_boolean_type(self) -> str:
        """Get boolean type"""
        if self.is_postgres:
            return "BOOLEAN"
        else:
            return "BOOLEAN"

    def get_timestamp_type(self) -> str:
        """Get timestamp type"""
        if self.is_postgres:
            return "TIMESTAMP"
        else:
            return "TIMESTAMP"


class SQLiteConnection:
    """Wrapper for SQLite connection"""

    def __init__(self, conn):
        self.conn = conn
        self.is_postgres = False

    async def execute(self, query: str, *args):
        """Execute query"""
        return await self.conn.execute(query, args if args else ())

    async def fetchone(self, query: str, *args):
        """Fetch one row"""
        cursor = await self.execute(query, *args)
        return await cursor.fetchone()

    async def fetchall(self, query: str, *args):
        """Fetch all rows"""
        cursor = await self.execute(query, *args)
        return await cursor.fetchall()

    async def commit(self):
        """Commit transaction"""
        await self.conn.commit()


class PostgreSQLCursor:
    """Cursor-like wrapper for PostgreSQL query results"""

    def __init__(self, conn, query, args):
        self.conn = conn
        self.query = query
        self.args = args

    async def fetchone(self):
        """Fetch one row"""
        return await self.conn.fetchrow(self.query, *self.args)

    async def fetchall(self):
        """Fetch all rows"""
        return await self.conn.fetch(self.query, *self.args)


class PostgreSQLConnection:
    """Wrapper for PostgreSQL connection"""

    def __init__(self, conn):
        self.conn = conn
        self.is_postgres = True

    async def execute(self, query: str, *args):
        """Execute query - returns cursor-like object"""
        # Convert ? to $1, $2, etc for PostgreSQL
        pg_query = self._convert_placeholders(query)
        # Return cursor-like object for compatibility
        return PostgreSQLCursor(self.conn, pg_query, args)

    async def fetchone(self, query: str, *args):
        """Fetch one row"""
        pg_query = self._convert_placeholders(query)
        return await self.conn.fetchrow(pg_query, *args)

    async def fetchall(self, query: str, *args):
        """Fetch all rows"""
        pg_query = self._convert_placeholders(query)
        return await self.conn.fetch(pg_query, *args)

    async def commit(self):
        """Commit transaction (no-op for PostgreSQL, autocommit by default)"""
        pass

    def _convert_placeholders(self, query: str) -> str:
        """Convert ? placeholders to $1, $2, etc"""
        result = []
        param_index = 1
        i = 0
        in_string = False
        string_char = None

        while i < len(query):
            char = query[i]

            # Handle string literals
            if char in ('"', "'"):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
                result.append(char)
                i += 1
                continue

            # Replace ? with $n outside of strings
            if char == '?' and not in_string:
                result.append(f'${param_index}')
                param_index += 1
            else:
                result.append(char)

            i += 1

        return ''.join(result)


# Global adapter instance
db_adapter = DatabaseAdapter()
