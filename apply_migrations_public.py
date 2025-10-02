#!/usr/bin/env python3
"""Apply migrations via public Railway URL"""
import asyncio
import asyncpg

PUBLIC_DB_URL = "postgresql://postgres:NtLFItrylcyGPGHIqllCxepVRNTSkHYG@hopper.proxy.rlwy.net:52905/railway"

async def main():
    print("🔗 Connecting to Railway database...")
    conn = await asyncpg.connect(PUBLIC_DB_URL)

    try:
        # Check current migrations
        print("\n📋 Current migrations:")
        rows = await conn.fetch("SELECT version, applied_at FROM schema_migrations ORDER BY applied_at")
        for row in rows:
            print(f"   ✓ {row['version']} (applied at {row['applied_at']})")

        # Apply migration 004: Reset migration 003
        print("\n🔄 Applying migration 004: Reset migration 003...")
        deleted = await conn.execute("DELETE FROM schema_migrations WHERE version = '003_remove_premium_fields.sql'")
        print(f"   Deleted: {deleted}")

        # Apply migration 003: Remove premium fields
        print("\n🔄 Applying migration 003: Remove premium fields...")
        await conn.execute("ALTER TABLE users DROP COLUMN IF EXISTS is_premium")
        await conn.execute("ALTER TABLE users DROP COLUMN IF EXISTS premium_until")
        print("   ✓ Columns dropped")

        # Mark migrations as applied
        await conn.execute("INSERT INTO schema_migrations (version) VALUES ('003_remove_premium_fields.sql') ON CONFLICT (version) DO NOTHING")
        await conn.execute("INSERT INTO schema_migrations (version) VALUES ('004_reset_migration_003.sql') ON CONFLICT (version) DO NOTHING")
        print("   ✓ Migrations 003 and 004 marked as applied")

        # Apply migration 005: Add test field
        print("\n🔄 Applying migration 005: Add test field...")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS test TEXT")
        await conn.execute("INSERT INTO schema_migrations (version) VALUES ('005_add_test_field.sql') ON CONFLICT (version) DO NOTHING")
        print("   ✓ Test field added")

        # Show final state
        print("\n✅ Final migrations state:")
        rows = await conn.fetch("SELECT version, applied_at FROM schema_migrations ORDER BY applied_at")
        for row in rows:
            print(f"   ✓ {row['version']} (applied at {row['applied_at']})")

        # Check test field exists
        print("\n🧪 Verifying test field:")
        field = await conn.fetchrow("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'test'
        """)
        if field:
            print(f"   ✅ Field exists: {field['column_name']} ({field['data_type']})")
        else:
            print("   ❌ Field NOT found!")

    finally:
        await conn.close()

    print("\n✅ Migration process completed!")

if __name__ == "__main__":
    asyncio.run(main())
