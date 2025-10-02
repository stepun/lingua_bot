"""Database adapter for PostgreSQL only"""

import os
import asyncpg
from typing import Optional
from contextlib import asynccontextmanager


class DatabaseAdapter:
    """Adapter for PostgreSQL database"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        self._pool: Optional[asyncpg.Pool] = None

    async def init_pool(self):
        """Initialize connection pool for PostgreSQL"""
        if not self._pool:
            self._pool = await asyncpg.create_pool(self.database_url)

    async def close_pool(self):
        """Close connection pool"""
        if self._pool:
            await self._pool.close()
            self._pool = None

    @asynccontextmanager
    async def get_connection(self):
        """Get database connection (context manager)"""
        if not self._pool:
            await self.init_pool()
        async with self._pool.acquire() as conn:
            yield PostgreSQLConnection(conn)

    def placeholder(self, index: int) -> str:
        """Get parameter placeholder for query"""
        return f"${index}"

    def get_serial_type(self) -> str:
        """Get auto-increment type"""
        return "SERIAL PRIMARY KEY"

    def get_boolean_type(self) -> str:
        """Get boolean type"""
        return "BOOLEAN"

    def get_timestamp_type(self) -> str:
        """Get timestamp type"""
        return "TIMESTAMP"


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
        """Execute query - returns cursor-like object or status"""
        # Convert ? to $1, $2, etc for PostgreSQL
        pg_query = self._convert_placeholders(query)

        # Check if this is a DDL/DML statement that doesn't return rows
        query_upper = pg_query.strip().upper()
        if any(query_upper.startswith(cmd) for cmd in ['CREATE', 'ALTER', 'DROP', 'INSERT', 'UPDATE', 'DELETE']):
            # Execute directly and return status
            if args:
                return await self.conn.execute(pg_query, *args)
            else:
                return await self.conn.execute(pg_query)

        # Return cursor-like object for SELECT queries
        return PostgreSQLCursor(self.conn, pg_query, args)

    async def fetchone(self, query: str, *args):
        """Fetch one row"""
        pg_query = self._convert_placeholders(query)
        return await self.conn.fetchrow(pg_query, *args)

    async def fetchall(self, query: str, *args):
        """Fetch all rows"""
        pg_query = self._convert_placeholders(query)
        return await self.conn.fetch(pg_query, *args)

    async def fetch(self, query: str, *args):
        """Fetch all rows (alias for fetchall)"""
        return await self.fetchall(query, *args)

    async def commit(self):
        """Commit transaction (no-op for PostgreSQL, autocommit by default)"""
        pass

    def transaction(self):
        """Return transaction context manager from underlying asyncpg connection"""
        return self.conn.transaction()

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
