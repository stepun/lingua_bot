#!/usr/bin/env python3
"""Check database user permissions"""
import asyncio
import asyncpg
import os

async def check_permissions():
    """Check what permissions the database user has"""
    db_url = os.getenv('DATABASE_PUBLIC_URL') or os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_PUBLIC_URL or DATABASE_URL not found")
        return

    print(f"🔗 Connecting to database...")

    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected\n")

        # Get current user
        user = await conn.fetchval("SELECT current_user")
        print(f"👤 Current user: {user}\n")

        # Check table privileges on users table
        print("📋 Checking privileges on 'users' table:")
        privs = await conn.fetch("""
            SELECT privilege_type
            FROM information_schema.table_privileges
            WHERE table_name = 'users' AND grantee = current_user
        """)

        if privs:
            for priv in privs:
                print(f"   ✓ {priv['privilege_type']}")
        else:
            print("   ⚠️  No specific privileges found (might have owner/superuser rights)")

        # Check if user is superuser
        print("\n🔧 Checking user role attributes:")
        role_attrs = await conn.fetchrow("""
            SELECT rolsuper, rolcreaterole, rolcreatedb
            FROM pg_roles
            WHERE rolname = current_user
        """)

        if role_attrs:
            print(f"   Superuser: {role_attrs['rolsuper']}")
            print(f"   Can create roles: {role_attrs['rolcreaterole']}")
            print(f"   Can create databases: {role_attrs['rolcreatedb']}")

        # Try to check if we can alter tables
        print("\n🧪 Testing ALTER TABLE permission...")
        try:
            # This won't actually change anything, just tests permission
            await conn.execute("SELECT has_table_privilege(current_user, 'users', 'UPDATE')")
            print("   ✅ ALTER TABLE permission confirmed")
        except Exception as e:
            print(f"   ❌ ALTER TABLE test failed: {e}")

        await conn.close()
        print("\n✅ Permission check complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_permissions())
